"""Rebuild everything that comes from the IDB reference programs.

1. Clones the programs needed for the surveys in config/surveys.yml into reference/
   (not committed).
2. Writes a draft gold standard per survey to validate/gold/, checking every extracted
   variable name against the survey's data dictionary when one exists.
3. Writes the comparison across rounds and countries to docs/reference_across_rounds.md.

Usage:
    python scripts/build_reference.py
"""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harmonize.compare_rounds import main as compare_main  # noqa: E402
from harmonize.extract_gold_from_idb import build_gold, read_dictionary  # noqa: E402

DEST = Path("reference/idb_harmonization")


def clone(repo: str, folders: list[str]) -> None:
    if not (DEST / ".git").exists():
        DEST.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", repo, str(DEST)], check=True)
    subprocess.run(["git", "-C", str(DEST), "sparse-checkout", "set", *folders, "_DOCS"], check=True)


def main() -> None:
    with open("config/surveys.yml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    surveys = cfg["surveys"]
    clone(cfg["idb_repo"], sorted({str(Path(s["idb_program"]).parent) for s in surveys.values()}))

    for survey, spec in surveys.items():
        dictionary_path = Path("data/dictionaries") / f"{survey}.csv"
        dictionary = read_dictionary(str(dictionary_path)) if dictionary_path.exists() else None
        text = (DEST / spec["idb_program"]).read_text(encoding="utf-8", errors="replace")
        rows = build_gold(text, survey, dictionary)
        out = Path("validate/gold") / f"{survey}_gold_draft.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        checked = "names checked against the dictionary" if dictionary else "no dictionary yet, names unchecked"
        print(f"{survey}: {len(rows)} harmonized variables ({checked})")

    sys.argv = ["compare_rounds.py"]
    compare_main()


if __name__ == "__main__":
    main()
