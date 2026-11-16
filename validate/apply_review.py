"""Turn a completed review sheet into the reviewed gold standard for a survey.

Starts from the draft gold (the IDB program as parsed) and applies each decision:

    reference   keep the reference mapping
    model       replace it with the model's mapping
    both        keep the reference and record the model's variables as an accepted alternative
    neither     use the variables written in final_source_vars (empty means not available)

Targets that are not in the sheet are the ones where the model and the reference agreed.
They are kept and marked as "agreed", which is weaker evidence than a manual check.

A file validate/review/<survey>_corrections.csv, if present, is applied last. It holds
changes made after the review because a data check proved a decision wrong, each with
its reason, so the original review stays on record.

Because the reviewer sees the model's answer, a reviewed gold file is not independent of
the model. Results are therefore reported against both the untouched reference and the
reviewed gold.

Usage:
    python validate/apply_review.py --survey CHL_2022
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

DECISIONS = {"reference", "model", "both", "neither"}
OUT_COLUMNS = ["survey", "target_var", "status", "source_vars", "alt_source_vars", "reference_status",
               "reference_source_vars", "review_decision", "review_note"]


def clean(value: str) -> str:
    return ";".join(sorted(v.strip().lower() for v in str(value).replace(",", ";").split(";") if v.strip()))


def apply(draft: pd.DataFrame, review: pd.DataFrame, targets: list[str]) -> pd.DataFrame:
    decisions = review.set_index("target_var")
    rows = []
    for _, g in draft[draft["target_var"].isin(targets)].iterrows():
        target = g["target_var"]
        row = {
            "survey": g["survey"], "target_var": target, "status": g["status"], "source_vars": clean(g["source_vars"]),
            "alt_source_vars": "", "reference_status": g["status"], "reference_source_vars": clean(g["source_vars"]),
            "review_decision": "agreed" if g["status"] in ("mapped", "not_available") else "not scored", "review_note": "",
        }
        if target in decisions.index:
            d = decisions.loc[target]
            decision, model_vars = d["decision"].strip().lower(), clean(d["model_vars"])
            row["review_decision"], row["review_note"] = decision, d["note"]
            if decision == "both" and g["status"] != "mapped":
                decision = "model"  # nothing to keep on the reference side
            if decision == "model":
                row["status"] = "mapped" if model_vars else "not_available"
                row["source_vars"] = model_vars
            elif decision == "both":
                row["alt_source_vars"] = model_vars
            elif decision == "neither":
                final = clean(d["final_source_vars"])
                row["status"] = "mapped" if final else "not_available"
                row["source_vars"] = final
        rows.append(row)
    return pd.DataFrame(rows, columns=OUT_COLUMNS)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--survey", required=True)
    ap.add_argument("--review", help="Completed sheet (default validate/review/<survey>_review.csv)")
    args = ap.parse_args()

    review_path = Path(args.review or f"validate/review/{args.survey}_review.csv")
    review = pd.read_csv(review_path, dtype=str, encoding="utf-8-sig").fillna("")
    review["decision"] = review["decision"].str.strip().str.lower()
    pending = review[~review["decision"].isin(DECISIONS)]
    if len(pending):
        print(f"{len(pending)} of {len(review)} rows have no valid decision (use: {', '.join(sorted(DECISIONS))}):")
        print("  " + ", ".join(pending["target_var"]))
        sys.exit(1)

    draft = pd.read_csv(f"validate/gold/{args.survey}_gold_draft.csv", dtype=str).fillna("")
    proposals = pd.read_csv(f"harmonize/proposals/{args.survey}.csv", dtype=str)
    corrections_path = review_path.with_name(f"{args.survey}_corrections.csv")
    if corrections_path.exists():
        corrections = pd.read_csv(corrections_path, dtype=str).fillna("").set_index("target_var")
        review = review.set_index("target_var")
        for target, c in corrections.iterrows():
            review.loc[target, "decision"] = c["decision"].strip().lower()
            review.loc[target, "final_source_vars"] = c["final_source_vars"]
            review.loc[target, "note"] = f"Corrected after review: {c['reason']}"
        review = review.reset_index()
        print(f"   {len(corrections)} correction(s) applied from {corrections_path}")
    gold = apply(draft, review, list(proposals["target_var"]))
    out = Path(f"validate/gold/{args.survey}_gold.csv")
    gold.to_csv(out, index=False)
    print(f"{args.survey}: {len(gold)} targets -> {out}")
    print("   " + ", ".join(f"{n} {k}" for k, n in gold["review_decision"].value_counts().items()))


if __name__ == "__main__":
    main()
