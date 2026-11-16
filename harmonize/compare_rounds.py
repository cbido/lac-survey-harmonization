"""Compare the reference mappings across survey rounds and countries.

Reads the gold files in a folder and reports, for the variables in the target schema:

  - how many extracted raw-variable names exist in each survey's data dictionary
    (a check on the gold extraction itself);
  - within each country, where the status changes between rounds (a question appears
    or drops out) and where the raw source variables change (a question is renamed
    or renumbered);
  - across countries, which target variables the reference maps everywhere.

The round-to-round changes are the cases where carrying last round's mapping forward
would fail, which makes them the natural test for the model.

Survey ids are <country>_<year>, e.g. CHL_2017.

Usage:
    python harmonize/compare_rounds.py --gold-dir validate/gold --out docs/reference_across_rounds.md
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd
import yaml


def _count(value: str) -> int:
    return len([v for v in str(value).split(";") if v.strip()])


def load_gold(gold_dir: str, targets: list[str]) -> dict[str, pd.DataFrame]:
    """Return one table per survey, indexed by target variable and limited to the schema.

    A reviewed <survey>_gold.csv takes precedence over its draft.
    """
    files: dict[str, Path] = {}
    for path in sorted(Path(gold_dir).glob("*_gold*.csv")):
        survey = re.sub(r"_gold(_draft)?$", "", path.stem)
        if survey not in files or not path.stem.endswith("_draft"):
            files[survey] = path
    gold = {}
    for survey, path in sorted(files.items()):
        table = pd.read_csv(path, dtype=str).fillna("").set_index("target_var")
        gold[survey] = table.reindex(targets).fillna("")
    return gold


def name_check(gold: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for survey, table in gold.items():
        checked = "names_checked" in table.columns and (table["names_checked"] == "yes").any()
        found = int(table["source_vars"].map(_count).sum())
        missing = int(table["not_in_dictionary"].map(_count).sum()) if "not_in_dictionary" in table.columns else 0
        rows.append(
            {
                "survey": survey,
                "checked": "yes" if checked else "no",
                "names_found": found if checked else "",
                "names_not_found": missing if checked else "",
                "share_found": f"{found / (found + missing):.1%}" if checked and found + missing else "",
            }
        )
    return pd.DataFrame(rows)


def status_summary(gold: dict[str, pd.DataFrame]) -> pd.DataFrame:
    order = ["mapped", "not_available", "derived", "constant", ""]
    counts = pd.DataFrame({s: t["status"].value_counts() for s, t in gold.items()}).reindex(order).fillna(0).astype(int)
    counts.index = [i or "not in program" for i in counts.index]
    counts = counts[(counts.T != 0).any()]
    return counts.rename_axis("status").reset_index()


def within_country(gold: dict[str, pd.DataFrame]) -> dict[str, dict]:
    countries: dict[str, list[str]] = {}
    for survey in gold:
        countries.setdefault(survey.split("_")[0], []).append(survey)
    out = {}
    for country, surveys in countries.items():
        status = pd.DataFrame({s: gold[s]["status"] for s in surveys})
        sources = pd.DataFrame({s: gold[s]["source_vars"] for s in surveys})
        always_mapped = (status == "mapped").all(axis=1)
        out[country] = {
            "surveys": surveys,
            "status_changes": status[status.nunique(axis=1) > 1].rename_axis("target_var").reset_index(),
            "source_changes": sources[always_mapped & (sources.nunique(axis=1) > 1)].rename_axis("target_var").reset_index(),
            "n_always_mapped": int(always_mapped.sum()),
        }
    return out


def across_countries(gold: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Per target variable, the number of rounds in each country where it has a raw mapping."""
    countries = sorted({s.split("_")[0] for s in gold})
    table = pd.DataFrame(index=next(iter(gold.values())).index)
    for country in countries:
        surveys = [s for s in gold if s.startswith(country + "_")]
        mapped = sum((gold[s]["status"] == "mapped").astype(int) for s in surveys)
        table[country] = mapped.astype(str) + "/" + str(len(surveys))
    everywhere = pd.concat([(gold[s]["status"] == "mapped") for s in gold], axis=1).all(axis=1)
    table["mapped_in_every_survey"] = everywhere.map({True: "yes", False: ""})
    return table.rename_axis("target_var").reset_index()


def table(frame: pd.DataFrame) -> str:
    header = "| " + " | ".join(str(c) for c in frame.columns) + " |"
    rule = "|" + "|".join("---" for _ in frame.columns) + "|"
    body = ["| " + " | ".join(str(v).replace(";", ", ") for v in row) + " |" for row in frame.itertuples(index=False)]
    return "\n".join([header, rule, *body])


def to_markdown(gold: dict[str, pd.DataFrame]) -> str:
    cross = across_countries(gold)
    n_everywhere = int((cross["mapped_in_every_survey"] == "yes").sum())
    parts = [
        "# Reference mappings across rounds and countries",
        "",
        "Built from the gold files in `validate/gold/` by `harmonize/compare_rounds.py`.",
        "Draft files are parser output and still need manual review.",
        "",
        "## Extracted names checked against each survey's data dictionary",
        "",
        table(name_check(gold)),
        "",
        "## Target variables by status",
        "",
        table(status_summary(gold)),
        "",
    ]
    for country, res in within_country(gold).items():
        if len(res["surveys"]) < 2:
            continue
        n_status, n_source = len(res["status_changes"]), len(res["source_changes"])
        parts += [
            f"## {country}: status changes between rounds ({n_status})",
            "",
            table(res["status_changes"]) if n_status else "None.",
            "",
            f"## {country}: same concept, different raw variables ({n_source} of {res['n_always_mapped']} mapped in every round)",
            "",
            table(res["source_changes"]) if n_source else "None.",
            "",
        ]
    parts += [
        f"## Coverage across countries ({n_everywhere} of {len(cross)} targets mapped in every survey)",
        "",
        "Cells show the number of rounds with a raw mapping out of the rounds in scope.",
        "",
        table(cross),
        "",
    ]
    return "\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gold-dir", default="validate/gold")
    ap.add_argument("--schema", default="config/target_schema.yml")
    ap.add_argument("--out", default="docs/reference_across_rounds.md")
    args = ap.parse_args()

    with open(args.schema, encoding="utf-8") as f:
        targets = [v["name"] for v in yaml.safe_load(f)["variables"]]
    report = to_markdown(load_gold(args.gold_dir, targets))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(report, encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
