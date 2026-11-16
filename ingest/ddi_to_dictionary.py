"""Build a survey's data dictionary from its DDI codebook (the XML that statistics
offices publish in their NADA / ANDA microdata catalogs).

The codebook is public metadata: variable names, labels, categories and, in most
cases, the literal question text. It gives the mapping step everything it needs
before any microdata is downloaded.

Output has the same columns as ingest/to_parquet.py, plus the source file of each
variable and its question text. Counts of missing and distinct values stay empty.

Usage:
    python ingest/ddi_to_dictionary.py --survey BOL_2021 \
        --ddi data/metadata/BOL_2021_ddi.xml --out data/dictionaries/BOL_2021.csv
"""
from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

COLUMNS = ["variable", "label", "dtype", "n_missing", "n_unique", "value_labels", "file", "question"]


def _clean(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child(element, name: str):
    return next((c for c in element if _local(c.tag) == name), None)


def _text(element, *path: str) -> str:
    for name in path:
        if element is None:
            return ""
        element = _child(element, name)
    return _clean("".join(element.itertext())) if element is not None else ""


def parse_ddi(path: str) -> pd.DataFrame:
    root = ET.parse(path).getroot()
    files = {}
    for node in root.iter():
        if _local(node.tag) == "fileDscr":
            name = _text(node, "fileTxt", "fileName")
            files[node.get("ID")] = re.sub(r"\.NSDstat$", "", name)

    rows: dict[str, dict] = {}
    for var in root.iter():
        if _local(var.tag) != "var":
            continue
        name = (var.get("name") or "").strip().lower()
        if not name:
            continue
        source = files.get(var.get("files"), var.get("files") or "")
        if name in rows:  # same variable in several files (identifiers, weights)
            if source and source not in rows[name]["file"].split(";"):
                rows[name]["file"] += ";" + source
            continue
        codes = {}
        for cat in var:
            if _local(cat.tag) == "catgry":
                value, label = _text(cat, "catValu"), _text(cat, "labl")
                if value and label:
                    codes[value] = label
        fmt = _child(var, "varFormat")
        rows[name] = {
            "variable": name,
            "label": _text(var, "labl"),
            "dtype": (fmt.get("type") if fmt is not None else "") or "",
            "n_missing": "",
            "n_unique": "",
            "value_labels": json.dumps(codes, ensure_ascii=False),
            "file": source,
            "question": _text(var, "qstn", "qstnLit"),
        }
    return pd.DataFrame(list(rows.values()), columns=COLUMNS)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--survey", required=True)
    ap.add_argument("--ddi", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    dictionary = parse_ddi(args.ddi)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    dictionary.to_csv(args.out, index=False)
    n_files = dictionary["file"].str.split(";").explode().nunique()
    print(f"{args.survey}: {len(dictionary)} variables from {n_files} files -> {args.out}")
    print(f"  with value labels: {(dictionary['value_labels'] != '{}').sum()}, with question text: {(dictionary['question'] != '').sum()}")


if __name__ == "__main__":
    main()
