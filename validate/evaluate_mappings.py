"""Score LLM-proposed variable mappings against a gold standard.

Both files have one row per (survey, target_var) with columns
    status       mapped | not_available | (gold only) derived, constant
    source_vars  raw variable names separated by ';'

Three questions are answered:
  1. Availability: does the model know when the survey lacks the information?
  2. Sources: when a variable is available, does it pick the right raw variables?
     Scored on (target, source) pairs: precision, recall, F1. Also the share of
     targets where the proposal matches the gold set exactly (exact_match), contains
     every gold variable, possibly with extras (covers_gold), or shares at least one.
  3. Triage: if only proposals above a confidence threshold are auto-accepted,
     how many are covered and how often are they exactly right?

Gold rows with status derived or constant are skipped: they are built from
other harmonized variables or fixed values, so there is no raw mapping to find.

Usage:
    python validate/evaluate_mappings.py \
        --gold validate/gold/CHL_2022_gold.csv \
        --proposals harmonize/proposals/CHL_2022.csv \
        --report validate/reports/CHL_2022_eval.md
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

SCORED_GOLD = {"mapped", "not_available"}
THRESHOLDS = (0.5, 0.7, 0.9)


def split_vars(value) -> frozenset[str]:
    if pd.isna(value) or not str(value).strip():
        return frozenset()
    return frozenset(v.strip().lower() for v in str(value).split(";") if v.strip())


def _closest(gold: frozenset, alternative: frozenset, proposed: frozenset) -> frozenset:
    """Of two accepted variable sets, the one that overlaps more with the proposal (Jaccard)."""
    if not alternative:
        return gold

    def jaccard(a: frozenset) -> float:
        return len(a & proposed) / len(a | proposed) if a | proposed else 1.0

    return alternative if jaccard(alternative) > jaccard(gold) else gold


def prf(tp: int, fp: int, fn: int) -> dict:
    precision = tp / (tp + fp) if tp + fp else float("nan")
    recall = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else float("nan")
    return {"precision": precision, "recall": recall, "f1": f1}


def align(gold: pd.DataFrame, proposals: pd.DataFrame) -> pd.DataFrame:
    """One row per scored gold variable, with the matching proposal alongside."""
    gold = gold[gold["status"].isin(SCORED_GOLD)].copy()
    keep = ["survey", "target_var", "status", "source_vars"]
    extra = [c for c in ("domain", "confidence") if c in proposals.columns]
    alt = ["alt_source_vars"] if "alt_source_vars" in gold.columns else []
    merged = gold[keep + alt].merge(
        proposals[keep + extra], on=["survey", "target_var"], how="left", suffixes=("_gold", "_llm")
    )
    merged["llm_set"] = merged["source_vars_llm"].map(split_vars)
    merged["gold_set"] = merged["source_vars_gold"].map(split_vars)
    if alt:
        # a reviewed gold file may accept a second set of variables: score against the closer one
        merged["gold_set"] = [
            _closest(g, split_vars(a), p)
            for g, a, p in zip(merged["gold_set"], merged["alt_source_vars"], merged["llm_set"])
        ]
    merged["status_llm"] = merged["status_llm"].fillna("no_answer")
    # anything other than an explicit mapping counts as "not available" for scoring
    merged["llm_available"] = merged["status_llm"].eq("mapped") & merged["llm_set"].map(bool)
    merged["gold_available"] = merged["status_gold"].eq("mapped")
    merged["tp"] = [len(g & p) for g, p in zip(merged["gold_set"], merged["llm_set"])]
    merged["fp"] = [len(p - g) for g, p in zip(merged["gold_set"], merged["llm_set"])]
    merged["fn"] = [len(g - p) for g, p in zip(merged["gold_set"], merged["llm_set"])]
    merged["exact"] = merged["gold_set"] == merged["llm_set"]
    merged["covers_gold"] = [bool(g) and g <= p for g, p in zip(merged["gold_set"], merged["llm_set"])]
    merged["any_overlap"] = merged["tp"] > 0
    if "confidence" in merged.columns:
        merged["confidence"] = pd.to_numeric(merged["confidence"], errors="coerce")
    return merged


def availability_scores(df: pd.DataFrame) -> dict:
    """Treat 'not available in this survey' as the positive class."""
    gold_na, llm_na = ~df["gold_available"], ~df["llm_available"]
    scores = prf(int((gold_na & llm_na).sum()), int((~gold_na & llm_na).sum()), int((gold_na & ~llm_na).sum()))
    scores["accuracy"] = float((gold_na == llm_na).mean()) if len(df) else float("nan")
    scores["n"] = len(df)
    return scores


def source_scores(df: pd.DataFrame) -> dict:
    """Pair-level scores on variables the gold standard maps to raw variables."""
    mapped = df[df["gold_available"]]
    scores = prf(int(mapped["tp"].sum()), int(mapped["fp"].sum()), int(mapped["fn"].sum()))
    scores["exact_match"] = float(mapped["exact"].mean()) if len(mapped) else float("nan")
    scores["covers_gold"] = float(mapped["covers_gold"].mean()) if len(mapped) else float("nan")
    scores["any_overlap"] = float(mapped["any_overlap"].mean()) if len(mapped) else float("nan")
    scores["n"] = len(mapped)
    return scores


def by_domain(df: pd.DataFrame) -> pd.DataFrame:
    if "domain" not in df.columns:
        return pd.DataFrame()
    rows = []
    for domain, part in df.groupby(df["domain"].fillna("unknown")):
        rows.append({"domain": domain, **source_scores(part), "availability_accuracy": availability_scores(part)["accuracy"]})
    return pd.DataFrame(rows)


def triage(df: pd.DataFrame, thresholds=THRESHOLDS) -> pd.DataFrame:
    """Coverage and exact-match rate if proposals at or above each threshold are auto-accepted."""
    if "confidence" not in df.columns or df["confidence"].isna().all():
        return pd.DataFrame()
    correct = df["exact"] & (df["gold_available"] == df["llm_available"])
    rows = []
    for t in thresholds:
        auto = df["confidence"] >= t
        rows.append(
            {
                "threshold": t,
                "auto_accepted": int(auto.sum()),
                "coverage": float(auto.mean()),
                "exact_among_auto": float(correct[auto].mean()) if auto.any() else float("nan"),
                "sent_to_review": int((~auto).sum()),
            }
        )
    return pd.DataFrame(rows)


def errors(df: pd.DataFrame) -> pd.DataFrame:
    wrong = df[~(df["exact"] & (df["gold_available"] == df["llm_available"]))]
    out = wrong[["survey", "target_var", "status_gold", "source_vars_gold", "status_llm", "source_vars_llm"]]
    return out.fillna("")


def to_markdown(title: str, avail: dict, src: dict, domains: pd.DataFrame, tri: pd.DataFrame, err: pd.DataFrame) -> str:
    def table(frame: pd.DataFrame) -> str:
        frame = frame.copy()
        for col in frame.select_dtypes("float").columns:
            frame[col] = frame[col].map(lambda x: "" if pd.isna(x) else f"{x:.2f}")
        header = "| " + " | ".join(frame.columns) + " |"
        rule = "|" + "|".join("---" for _ in frame.columns) + "|"
        body = ["| " + " | ".join(str(v) for v in row) + " |" for row in frame.itertuples(index=False)]
        return "\n".join([header, rule, *body])

    parts = [f"# Mapping evaluation: {title}", ""]
    parts += ["## Availability (does the survey collect it?)", "", table(pd.DataFrame([avail])), ""]
    parts += ["## Source variables (gold-mapped variables only)", "", table(pd.DataFrame([src])), ""]
    if not domains.empty:
        parts += ["## By domain", "", table(domains), ""]
    if not tri.empty:
        parts += ["## Confidence triage", "", table(tri), ""]
    parts += [f"## Disagreements with the gold standard ({len(err)})", "", table(err) if len(err) else "None.", ""]
    return "\n".join(parts)


def evaluate(gold: pd.DataFrame, proposals: pd.DataFrame) -> dict:
    df = align(gold, proposals)
    return {
        "aligned": df,
        "availability": availability_scores(df),
        "sources": source_scores(df),
        "by_domain": by_domain(df),
        "triage": triage(df),
        "errors": errors(df),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gold", required=True)
    ap.add_argument("--proposals", required=True)
    ap.add_argument("--report", help="Write a Markdown report to this path")
    ap.add_argument("--schema-only", action="store_true", help="Score only target variables present in the proposals file")
    args = ap.parse_args()

    gold = pd.read_csv(args.gold, dtype=str)
    proposals = pd.read_csv(args.proposals, dtype=str)
    if args.schema_only:
        gold = gold[gold["target_var"].isin(proposals["target_var"])]

    res = evaluate(gold, proposals)
    title = ", ".join(sorted(gold["survey"].unique()))
    report = to_markdown(title, res["availability"], res["sources"], res["by_domain"], res["triage"], res["errors"])
    print(report)
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
