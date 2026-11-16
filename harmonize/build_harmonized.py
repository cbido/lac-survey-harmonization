"""Run the recoding code of a survey and write its harmonized table.

Every expression in harmonize/code/<survey>.yml is executed on its own first and tested:

    sql_error        the expression does not run
    invalid_values   it returns a code or a value outside what the target schema allows
    all_missing      it runs and returns no value at all
    ok               it runs and every value is valid

A variable that passes can still carry a warning: almost no rows with a value, or a code
of the target schema that never appears. Those are the cases where code runs and is wrong.

Only expressions that pass go into the table. The rest are left out as missing columns
and listed in the report, so a failure is visible and never silently filled in.

Output:
    data/harmonized/<survey>.parquet      one row per person, harmonized variables
    docs/harmonized_<survey>.md           status, coverage, weighted distribution and the
                                          model's note and assumptions for every target

Usage:
    python harmonize/build_harmonized.py --survey CHL_2022
"""
from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import yaml

MAX_CODES_SHOWN = 12
LOW_COVERAGE = 0.05  # share of rows with a value below which a variable is flagged


def load(survey: str) -> tuple[dict, list[dict], list[dict]]:
    with open("config/surveys.yml", encoding="utf-8") as f:
        spec = yaml.safe_load(f)["surveys"][survey]
    with open("config/target_schema.yml", encoding="utf-8") as f:
        schema = yaml.safe_load(f)["variables"]
    with open(f"harmonize/code/{survey}.yml", encoding="utf-8") as f:
        code = yaml.safe_load(f)["variables"]
    return spec, schema, code


def constants(survey: str, spec: dict) -> dict[str, str]:
    """Targets that are fixed for the whole survey and need no model."""
    return {"pais_c": f"'{survey.split('_')[0]}'", "anio_c": str(int(spec["year"]))}


def test_expression(con, source: str, sql: str, target: dict) -> dict:
    """Run one expression and check its values against the target schema."""
    result = {"status": "ok", "detail": "", "n": 0, "n_valid": 0}
    try:
        n, n_valid = con.execute(f"SELECT COUNT(*), COUNT(v) FROM (SELECT ({sql}) AS v FROM {source})").fetchone()
    except Exception as err:  # duckdb raises several error types
        return {**result, "status": "sql_error", "detail": str(err).splitlines()[0][:200]}
    result.update(n=n, n_valid=n_valid)
    if n_valid == 0:
        return {**result, "status": "all_missing"}
    problems = []
    if target.get("values"):
        allowed = ", ".join(repr(k) if isinstance(k, str) else str(k) for k in target["values"])
        bad = con.execute(
            f"SELECT COUNT(*) FROM (SELECT ({sql}) AS v FROM {source}) WHERE v IS NOT NULL AND v NOT IN ({allowed})"
        ).fetchone()[0]
        if bad:
            problems.append(f"{bad} rows with a code outside the schema")
    if target.get("range"):
        low, high = target["range"]
        clauses = ([f"v < {low}"] if low is not None else []) + ([f"v > {high}"] if high is not None else [])
        bad = con.execute(
            f"SELECT COUNT(*) FROM (SELECT ({sql}) AS v FROM {source}) WHERE {' OR '.join(clauses)}"
        ).fetchone()[0]
        if bad:
            problems.append(f"{bad} rows outside the range {target['range']}")
    if problems:
        return {**result, "status": "invalid_values", "detail": "; ".join(problems)}
    result["warning"] = "; ".join(warnings(con, source, sql, target, n, n_valid))
    return result


def warnings(con, source: str, sql: str, target: dict, n: int, n_valid: int) -> list[str]:
    """Signs that an expression runs and is still wrong. They do not block the variable."""
    out = []
    if n_valid / n < LOW_COVERAGE:
        out.append(f"only {100 * n_valid / n:.1f}% of rows have a value")
    expected = list(target.get("values", {}))
    if not expected and target.get("range") and target["type"] == "int" and None not in target["range"]:
        low, high = target["range"]
        expected = list(range(low, high + 1)) if high - low <= 12 else []
    if expected:
        seen = {r[0] for r in con.execute(f"SELECT DISTINCT ({sql}) FROM {source}").fetchall()}
        never = [c for c in expected if c not in seen]
        if never and len(never) < len(expected):
            out.append(f"codes never produced: {never}")
    return out


def summarize(con, table: str, name: str, target: dict, weight: str | None) -> str:
    """Weighted distribution for coded variables, weighted mean for the rest."""
    w = weight if weight else "1"
    if target["type"] == "str":
        return ", ".join(str(r[0]) for r in con.execute(f"SELECT DISTINCT {name} FROM {table} LIMIT 5").fetchall())
    distinct = con.execute(f"SELECT COUNT(DISTINCT {name}) FROM {table}").fetchone()[0]
    if target.get("values") or distinct <= MAX_CODES_SHOWN:
        rows = con.execute(
            f"""SELECT {name}, 100.0 * SUM({w}) / SUM(SUM({w})) OVER () FROM {table}
                WHERE {name} IS NOT NULL GROUP BY 1 ORDER BY 1"""
        ).fetchall()
        labels = target.get("values", {})
        return "; ".join(f"{labels.get(int(v), int(v)) if float(v).is_integer() else v}: {p:.1f}%" for v, p in rows)
    mean, low, high = con.execute(
        f"SELECT SUM({name} * {w}) / SUM(CASE WHEN {name} IS NOT NULL THEN {w} END), MIN({name}), MAX({name}) FROM {table}"
    ).fetchone()
    return f"weighted mean {mean:,.1f} (min {low:,.0f}, max {high:,.0f})"


def build(survey: str) -> None:
    spec, schema, code = load(survey)
    targets = {t["name"]: t for t in schema}
    written = {c["target_var"]: c for c in code}
    con = duckdb.connect()
    source = f"read_parquet('data/parquet/{survey}.parquet')"

    expressions = dict(constants(survey, spec))
    report = {}
    for name, target in targets.items():
        if name in expressions:
            report[name] = {"status": "ok", "detail": "", "by": "config", "note": "Fixed for the whole survey.", "assumptions": ""}
            continue
        entry = written.get(name)
        if not entry:
            report[name] = {"status": "not_built", "detail": "no approved raw variables", "by": "", "note": "", "assumptions": ""}
            continue
        base = {"by": entry.get("written_by", "model"), "note": entry.get("note", ""), "assumptions": entry.get("assumptions", "")}
        if entry["sql"].strip().upper() == "NULL":
            report[name] = {"status": "declined", "detail": "the model returned no code", **base}
            continue
        result = test_expression(con, source, entry["sql"], target)
        report[name] = {**result, **base}
        if result["status"] == "ok":
            expressions[name] = entry["sql"]

    # comuna comes from a separate official file, joined by household and person identifiers
    select = ",\n  ".join(f"({sql}) AS {name}" for name, sql in expressions.items())
    comuna_path = Path(f"data/parquet/{survey}_comuna.parquet")
    join, extra = "", ""
    if comuna_path.exists():
        join = f"LEFT JOIN read_parquet('{comuna_path}') c USING (folio, id_persona)"
        extra = ",\n  c.comuna AS comuna_raw, c.expc AS factor_comuna_raw"
    for alias, raw in spec.get("benchmarks", {}).items():  # official variables carried untouched
        extra += f",\n  s.{raw} AS {alias}"
    out = Path("data/harmonized") / f"{survey}.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"COPY (SELECT {select}{extra} FROM {source} s {join}) TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)")

    table = f"read_parquet('{out}')"
    n_rows = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    weight = "factor_ci" if "factor_ci" in expressions else None
    counts: dict[str, int] = {}
    lines = [
        f"# Harmonized table: {survey}",
        "",
        f"Generated by `harmonize/build_harmonized.py` from `harmonize/code/{survey}.yml`. {n_rows:,} persons.",
        "",
        "| target | status | written by | non-missing | weighted distribution or mean | note | assumptions to check |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, r in report.items():
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        coverage = summary = ""
        if name in expressions:
            valid = con.execute(f"SELECT COUNT({name}) FROM {table}").fetchone()[0]
            coverage = f"{100 * valid / n_rows:.1f}%"
            summary = summarize(con, table, name, targets[name], None if name in ("factor_ci", "factor_ch") else weight)
        status = r["status"] + (f": {r['detail']}" if r["detail"] else "") + (f" (check: {r['warning']})" if r.get("warning") else "")
        clean = lambda s: str(s).replace("|", "/").replace("\n", " ")  # noqa: E731
        lines.append(f"| {name} | {clean(status)} | {r['by']} | {coverage} | {clean(summary)} | {clean(r['note'])} | {clean(r['assumptions'])} |")
    lines.insert(4, "Status: " + ", ".join(f"{n} {k}" for k, n in sorted(counts.items())) + ".")
    lines.insert(5, "")
    Path("docs").mkdir(exist_ok=True)
    Path(f"docs/harmonized_{survey}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"{survey}: {n_rows:,} rows, {len(expressions)} harmonized variables -> {out}")
    print("  " + ", ".join(f"{n} {k}" for k, n in sorted(counts.items())))
    for name, r in report.items():
        if r["status"] not in ("ok", "not_built"):
            print(f"  {name}: {r['status']} {r['detail']}")
        elif r.get("warning"):
            print(f"  {name}: ok, but check: {r['warning']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--survey", required=True)
    args = ap.parse_args()
    build(args.survey)


if __name__ == "__main__":
    main()
