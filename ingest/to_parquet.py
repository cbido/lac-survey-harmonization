"""Convert a raw survey file (.dta or .sav) to Parquet and export its data
dictionary (variable names, labels, value labels, missing and distinct counts) as CSV.

The file is read in chunks, so a 2 GB Stata file converts with a few hundred MB of
memory. Column statistics are computed afterwards with DuckDB on the Parquet file.

The dictionary CSV is what the LLM reads to propose mappings, so no microdata
ever leaves the machine.

Usage:
    python ingest/to_parquet.py --survey CHL_2017 --raw "data/raw/CHL_2017/Casen 2017.dta"
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pyreadstat

READERS = {".dta": pyreadstat.read_dta, ".sav": pyreadstat.read_sav}
ARROW_TYPES = {
    "string": pa.string(),
    "int8": pa.int32(),
    "int16": pa.int32(),
    "int32": pa.int32(),
    "int64": pa.int64(),
    "float": pa.float64(),
    "double": pa.float64(),
}


def reader_for(path: str):
    suffix = Path(path).suffix.lower()
    if suffix not in READERS:
        raise ValueError(f"Unsupported format: {suffix} (expected .dta or .sav)")
    return READERS[suffix]


def arrow_schema(first_chunk: pd.DataFrame, meta) -> pa.Schema:
    """Fix one schema for every chunk, from the types declared in the raw file.

    Inferring types chunk by chunk breaks when a column is entirely missing in one
    chunk. Date columns keep the type pandas gives them. SPSS stores every number
    as a double, so those columns stay float64.
    """
    fields = []
    for name in first_chunk.columns:
        if pd.api.types.is_datetime64_any_dtype(first_chunk[name]):
            arrow_type = pa.timestamp("us")
        elif first_chunk[name].dtype == object and meta.readstat_variable_types.get(name) != "string":
            arrow_type = pa.array(first_chunk[name], from_pandas=True).type  # dates and times
            if pa.types.is_null(arrow_type):
                arrow_type = pa.string()
        else:
            arrow_type = ARROW_TYPES.get(meta.readstat_variable_types.get(name), pa.float64())
        fields.append(pa.field(name.lower(), arrow_type))
    return pa.schema(fields)


def to_table(chunk: pd.DataFrame, schema: pa.Schema) -> pa.Table:
    arrays = []
    for name, field in zip(chunk.columns, schema):
        try:
            arrays.append(pa.array(chunk[name], type=field.type, from_pandas=True))
        except (pa.ArrowInvalid, pa.ArrowTypeError):
            # e.g. a column declared integer that holds fractional values
            arrays.append(pa.array(chunk[name], from_pandas=True).cast(field.type, safe=False))
    return pa.Table.from_arrays(arrays, schema=schema)


def _repair(text, declared: str = "utf-8"):
    """Decode again a text that was read byte for byte (as Latin-1).

    UTF-8 files: drop any character cut off mid-way. Windows-1252 files: bytes that
    the code page does not define become a replacement mark.
    """
    if not isinstance(text, str):
        return text
    raw = text.encode("latin-1", errors="ignore")
    if declared.lower().replace("_", "-") in ("windows-1252", "cp1252"):
        return raw.decode("cp1252", errors="replace")
    return raw.decode("utf-8", errors="ignore")


def _declared_encoding(raw: str) -> str:
    try:
        _, meta = reader_for(raw)(raw, metadataonly=True)
        return meta.file_encoding or "utf-8"
    except (UnicodeDecodeError, pyreadstat.ReadstatError):
        return "utf-8"


def _read_chunks(raw: str, chunksize: int, **kwargs):
    """Yield (data, metadata) for consecutive blocks of rows until the file is exhausted."""
    reader, offset = reader_for(raw), 0
    while True:
        chunk, meta = reader(raw, row_offset=offset, row_limit=chunksize, **kwargs)
        if chunk.empty:
            return
        yield chunk, meta
        offset += len(chunk)


def _write_chunks(raw: str, parquet_path: str, chunksize: int, repair: bool):
    kwargs = {"encoding": "LATIN1"} if repair else {}
    declared = _declared_encoding(raw) if repair else "utf-8"
    writer, schema, meta, n_rows = None, None, None, 0
    try:
        for chunk, chunk_meta in _read_chunks(raw, chunksize, **kwargs):
            if repair:
                for name in chunk.columns:
                    if chunk_meta.readstat_variable_types.get(name) == "string":
                        chunk[name] = chunk[name].map(lambda v: _repair(v, declared))
            if writer is None:
                meta = chunk_meta
                schema = arrow_schema(chunk, meta)
                writer = pq.ParquetWriter(parquet_path, schema, compression="zstd")
            writer.write_table(to_table(chunk, schema))
            n_rows += len(chunk)
    finally:
        if writer is not None:
            writer.close()
    if meta is None:
        raise ValueError(f"No rows read from {raw}")
    if repair:
        meta.column_labels = [_repair(label, declared) for label in meta.column_labels]
        meta.variable_value_labels = {
            var: {code: _repair(label, declared) for code, label in codes.items()}
            for var, codes in meta.variable_value_labels.items()
        }
    return meta, n_rows


def convert(raw: str, parquet_path: str, chunksize: int = 50_000):
    """Write the raw file to Parquet chunk by chunk. Returns (metadata, number of rows).

    Some files hold text that is invalid in their declared encoding (a value truncated
    in the middle of a UTF-8 character, a byte Windows-1252 does not define), which stops
    a strict read. Those files are read again byte for byte and decoded leniently.
    """
    try:
        return _write_chunks(raw, parquet_path, chunksize, repair=False)
    except (UnicodeDecodeError, pyreadstat.ReadstatError):
        print(f"  note: invalid text encoding in {Path(raw).name}, reading again with lenient decoding")
        return _write_chunks(raw, parquet_path, chunksize, repair=True)


def column_stats(parquet_path: str) -> pd.DataFrame:
    """Missing and distinct counts per column, computed by DuckDB without loading the file."""
    con = duckdb.connect()
    columns = [row[0] for row in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{parquet_path}')").fetchall()]
    parts = []
    for i in range(0, len(columns), 100):  # keep each query a manageable width
        batch = columns[i : i + 100]
        select = ", ".join(
            f'COUNT(*) - COUNT("{c}") AS "m_{j}", COUNT(DISTINCT "{c}") AS "u_{j}"' for j, c in enumerate(batch)
        )
        row = con.execute(f"SELECT {select} FROM read_parquet('{parquet_path}')").fetchone()
        parts += [(c, row[2 * j], row[2 * j + 1]) for j, c in enumerate(batch)]
    return pd.DataFrame(parts, columns=["variable", "n_missing", "n_unique"])


def build_dictionary(meta, parquet_path: str) -> pd.DataFrame:
    labels = dict(zip(meta.column_names, meta.column_labels))
    rows = []
    for name in meta.column_names:
        codes = meta.variable_value_labels.get(name, {})
        rows.append(
            {
                "variable": name.lower(),
                "label": labels.get(name) or "",
                "dtype": meta.readstat_variable_types.get(name, ""),
                "value_labels": json.dumps({_code(k): str(v) for k, v in codes.items()}, ensure_ascii=False),
            }
        )
    out = pd.DataFrame(rows).merge(column_stats(parquet_path), on="variable", how="left")
    return out[["variable", "label", "dtype", "n_missing", "n_unique", "value_labels"]]


def _code(value) -> str:
    """Write 1.0 as '1' so codes look the same whatever the storage type."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--survey", required=True, help="Survey id, e.g. CHL_2017")
    ap.add_argument("--raw", required=True, help="Path to the raw .dta or .sav file")
    ap.add_argument("--out-dir", default="data")
    ap.add_argument("--name", help="Output name if different from the survey id, e.g. CHL_2017_comuna")
    ap.add_argument("--chunksize", type=int, default=50_000)
    args = ap.parse_args()

    name = args.name or args.survey
    out = Path(args.out_dir)
    (out / "parquet").mkdir(parents=True, exist_ok=True)
    (out / "dictionaries").mkdir(parents=True, exist_ok=True)
    parquet_path = out / "parquet" / f"{name}.parquet"
    dictionary_path = out / "dictionaries" / f"{name}.csv"

    meta, n_rows = convert(args.raw, str(parquet_path), args.chunksize)
    build_dictionary(meta, str(parquet_path)).to_csv(dictionary_path, index=False)
    print(f"{name}: {n_rows:,} rows, {len(meta.column_names)} variables")
    print(f"  {parquet_path} ({parquet_path.stat().st_size / 1e6:.1f} MB)")
    print(f"  {dictionary_path}")


if __name__ == "__main__":
    main()
