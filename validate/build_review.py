"""Build one review sheet per survey: every target where the model and the reference disagree.

Each row puts the reference's variables and the model's variables side by side, with
their labels and the model's reasoning, and leaves three columns for the reviewer:

    decision          reference | model | both | neither
    final_source_vars only when the decision is "neither" (the correct variables, ';' separated)
    note              why

Targets where the model and the reference agree are not listed and are accepted as they
are. validate/apply_review.py turns a completed sheet into the reviewed gold file.

Usage:
    python validate/build_review.py                  # every survey with proposals
    python validate/build_review.py --survey CHL_2022
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
csv.field_size_limit(sys.maxsize)

from validate.evaluate_mappings import align  # noqa: E402

COLUMNS = [
    "survey", "target_var", "target_description", "domain", "disagreement",
    "reference_status", "reference_vars", "reference_labels",
    "model_status", "model_vars", "model_labels", "model_confidence", "model_rationale",
    "decision", "final_source_vars", "note",
]


def kind(row) -> str:
    gold, llm = row["gold_set"], row["llm_set"]
    if not row["gold_available"] and row["llm_available"]:
        return "reference: not available, model: maps it"
    if row["gold_available"] and not row["llm_available"]:
        return "reference: maps it, model: not available"
    if gold < llm:
        return "model adds variables"
    if llm < gold:
        return "model omits variables"
    if gold & llm:
        return "partly different variables"
    return "different variables"


def with_labels(variables, labels: dict[str, str], width: int = 90) -> str:
    return "\n".join(f"{v}: {labels.get(v, '(not in dictionary)')[:width]}" for v in sorted(variables))


def build(survey: str, schema: dict[str, dict]) -> pd.DataFrame:
    proposals = pd.read_csv(f"harmonize/proposals/{survey}.csv", dtype=str).fillna("")
    gold = pd.read_csv(f"validate/gold/{survey}_gold_draft.csv", dtype=str).fillna("")
    gold = gold[gold["target_var"].isin(proposals["target_var"])]
    dictionary = pd.read_csv(f"data/dictionaries/{survey}.csv", dtype=str).fillna("")
    labels = dict(zip(dictionary["variable"], dictionary["label"]))
    extra = proposals.set_index("target_var")

    rows = []
    for _, r in align(gold, proposals).iterrows():
        if r["exact"] and r["gold_available"] == r["llm_available"]:
            continue
        target = r["target_var"]
        rows.append(
            {
                "survey": survey,
                "target_var": target,
                "target_description": schema[target]["description"],
                "domain": schema[target]["domain"],
                "disagreement": kind(r),
                "reference_status": r["status_gold"],
                "reference_vars": ";".join(sorted(r["gold_set"])),
                "reference_labels": with_labels(r["gold_set"], labels),
                "model_status": r["status_llm"],
                "model_vars": ";".join(sorted(r["llm_set"])),
                "model_labels": with_labels(r["llm_set"], labels),
                "model_confidence": extra.loc[target, "confidence"],
                "model_rationale": extra.loc[target, "rationale"],
                "decision": "",
                "final_source_vars": "",
                "note": "",
            }
        )
    return pd.DataFrame(rows, columns=COLUMNS)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--survey", nargs="*")
    ap.add_argument("--force", action="store_true", help="Overwrite a sheet that already has decisions")
    args = ap.parse_args()

    with open("config/target_schema.yml", encoding="utf-8") as f:
        schema = {v["name"]: v for v in yaml.safe_load(f)["variables"]}
    surveys = args.survey or sorted(p.stem for p in Path("harmonize/proposals").glob("*.csv"))
    out_dir = Path("validate/review")
    out_dir.mkdir(parents=True, exist_ok=True)
    for survey in surveys:
        out = out_dir / f"{survey}_review.csv"
        if out.exists() and not args.force:
            done = pd.read_csv(out, dtype=str).fillna("")
            if (done["decision"] != "").any():
                print(f"{survey}: {out} already has decisions, left untouched (use --force to rebuild)")
                continue
        sheet = build(survey, schema)
        sheet.to_csv(out, index=False, encoding="utf-8-sig")  # BOM so Excel reads the accents
        print(f"{survey}: {len(sheet)} rows to review -> {out}")
        print("   " + ", ".join(f"{n} {k}" for k, n in sheet["disagreement"].value_counts().items()))


if __name__ == "__main__":
    main()
