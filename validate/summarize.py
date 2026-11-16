"""Score every survey that has model proposals and write one summary.

For each survey with a file in harmonize/proposals/, the proposals are scored against
the draft gold and, when a reviewed gold file exists, against that too. Output:

  validate/reports/<survey>_eval.md     per-survey report against the draft gold, and
                                        <survey>_eval_reviewed.md once a reviewed gold exists
  docs/results.md                       one table for all surveys, token usage, and a
                                        comparison of targets whose raw variables change
                                        between rounds with targets that keep them

Usage:
    python validate/summarize.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validate.evaluate_mappings import evaluate, split_vars, to_markdown  # noqa: E402

GOLD, PROPOSALS, REPORTS = Path("validate/gold"), Path("harmonize/proposals"), Path("validate/reports")


def golds_for(survey: str) -> list[tuple[pd.DataFrame, str]]:
    """The draft (the reference as parsed) always, and the reviewed gold when it exists."""
    out = [(pd.read_csv(GOLD / f"{survey}_gold_draft.csv", dtype=str), "draft")]
    reviewed = GOLD / f"{survey}_gold.csv"
    if reviewed.exists():
        out.append((pd.read_csv(reviewed, dtype=str), "reviewed"))
    return out


def fmt(x) -> str:
    return "" if pd.isna(x) else f"{x:.2f}"


def table(frame: pd.DataFrame) -> str:
    header = "| " + " | ".join(str(c) for c in frame.columns) + " |"
    rule = "|" + "|".join("---" for _ in frame.columns) + "|"
    return "\n".join([header, rule] + ["| " + " | ".join(str(v) for v in row) + " |" for row in frame.itertuples(index=False)])


def main() -> None:
    surveys = sorted(p.stem for p in PROPOSALS.glob("*.csv"))
    REPORTS.mkdir(parents=True, exist_ok=True)
    rows, usage_rows, aligned = [], [], {}
    for survey in surveys:
        proposals = pd.read_csv(PROPOSALS / f"{survey}.csv", dtype=str)
        for gold, kind in golds_for(survey):
            gold = gold[gold["target_var"].isin(proposals["target_var"])]
            res = evaluate(gold, proposals)
            if kind == "draft":
                aligned[survey] = res["aligned"].set_index("target_var")
            suffix = "" if kind == "draft" else "_reviewed"
            report = to_markdown(f"{survey} ({kind} gold)", res["availability"], res["sources"], res["by_domain"], res["triage"], res["errors"])
            (REPORTS / f"{survey}_eval{suffix}.md").write_text(report, encoding="utf-8")
            av, src = res["availability"], res["sources"]
            rows.append(
                {
                    "survey": survey, "gold": kind, "targets scored": av["n"],
                    "availability accuracy": fmt(av["accuracy"]), "source precision": fmt(src["precision"]),
                    "source recall": fmt(src["recall"]), "exact match": fmt(src["exact_match"]),
                    "covers gold": fmt(src["covers_gold"]), "any overlap": fmt(src["any_overlap"]),
                    "invented names": int((proposals["invalid_sources"].fillna("") != "").sum()),
                }
            )
        usage_path = PROPOSALS / f"{survey}.usage.json"
        if usage_path.exists():
            u = json.loads(usage_path.read_text())
            usage_rows.append({"survey": survey, "model": u["model"], "calls": u["calls"], "input": u["input"],
                               "cache write": u["cache_write"], "cache read": u["cache_read"], "output": u["output"]})

    # targets whose gold raw variables change between rounds of a country vs targets that keep them
    stability = []
    for country in sorted({s.split("_")[0] for s in surveys}):
        rounds = [s for s in surveys if s.startswith(country + "_")]
        if len(rounds) < 2:
            continue
        common = set.intersection(*[set(aligned[s].index[aligned[s]["gold_available"]]) for s in rounds])
        for label, keep in (("same raw variables in every round", True), ("raw variables change between rounds", False)):
            targets = [t for t in common if (len({aligned[s].loc[t, "gold_set"] for s in rounds}) == 1) == keep]
            cells = pd.concat([aligned[s].loc[targets] for s in rounds]) if targets else pd.DataFrame()
            stability.append(
                {
                    "country": country, "targets": label, "n targets": len(targets),
                    "exact match": fmt(cells["exact"].mean()) if len(cells) else "",
                    "covers gold": fmt(cells["covers_gold"].mean()) if len(cells) else "",
                    "any overlap": fmt(cells["any_overlap"].mean()) if len(cells) else "",
                }
            )

    usage = pd.DataFrame(usage_rows)
    if len(usage):
        total = {"survey": "total", "model": "", **{c: int(usage[c].sum()) for c in ("calls", "input", "cache write", "cache read", "output")}}
        usage = pd.concat([usage, pd.DataFrame([total])], ignore_index=True)
    n_reviewed = sum(r["gold"] == "reviewed" for r in rows)
    lines = [
        "# Results",
        "",
        "Generated by `validate/summarize.py`.",
        "",
        "Rows marked **draft** are scored against the IDB program as parsed, with no manual check: they",
        "describe agreement with the reference, not accuracy. Rows marked **reviewed** are scored against",
        f"the gold standard after a person settled each disagreement ({n_reviewed} of {len(surveys)} surveys so far).",
        "The reviewer saw the model's answer, so a reviewed row is an upper reading and the draft row a",
        "lower one.",
        "",
        "## Agreement with the gold standard",
        "",
        table(pd.DataFrame(rows)),
        "",
        "- exact match: the proposal names exactly the gold variables",
        "- covers gold: the proposal names every gold variable, possibly with extras",
        "- any overlap: the proposal shares at least one variable with the gold",
        "",
        "## Does it matter when variables are renamed between rounds?",
        "",
        "Targets mapped in every round of a country, split by whether the gold raw variables",
        "are the same in every round. Rates pool all rounds of the country.",
        "",
        table(pd.DataFrame(stability)),
        "",
        "This split does not isolate the effect of renaming. The targets that keep their raw",
        "variables are mostly identifiers, weights and other single-variable items, and the",
        "ones that change include the income aggregates built from many components, so the",
        "two groups differ in difficulty as well.",
        "",
        "## Token usage",
        "",
        table(usage) if len(usage) else "No usage files found.",
        "",
    ]
    Path("docs").mkdir(exist_ok=True)
    Path("docs/results.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[7:]))


if __name__ == "__main__":
    main()
