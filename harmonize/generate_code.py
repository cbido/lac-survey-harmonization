"""Ask an LLM to write the recoding code for each harmonized variable of a survey.

Input: the reviewed gold standard (which raw variables feed each target), the target
schema (meaning, type, allowed codes) and the data dictionary entries of those raw
variables only. Output: one DuckDB SQL expression per target, with a short note and the
assumptions made, saved as YAML so a person can read and edit it:

    harmonize/code/<survey>.yml

The expressions are executed and tested by harmonize/build_harmonized.py. Nothing is
trusted because the model wrote it.

Usage:
    python harmonize/generate_code.py --survey CHL_2022
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
csv.field_size_limit(sys.maxsize)

from harmonize.propose_mappings import DEFAULT_MODEL, load_env, parse_response  # noqa: E402

SYSTEM = (
    "You write harmonization code for household surveys. For each target variable you get "
    "its definition and the raw survey variables approved for building it. Write one DuckDB "
    "SQL expression per target that computes it from those raw variables, for a table with "
    "one row per person. Follow the target's codes exactly. Preserve missing values: when "
    "the inputs do not allow a value, return NULL, never a guess."
)

INSTRUCTIONS = """Rules for every expression:
- Use only the raw variables listed for that target, by their exact names.
- One scalar SQL expression (CASE, arithmetic, COALESCE, casts). No SELECT, no subqueries, no window functions.
- Sums of income components treat a missing component as zero, and return NULL when every component is missing.
- Household-level targets are repeated on each person row of the household, like the raw household variables.
- If two alternative sets of raw variables are offered, use the one that matches the target definition best and say which in the note.
- If the target cannot be computed faithfully from these variables, set "sql" to "NULL" and explain in the note.

Return a JSON array with one object per target, in the same order:
{"target_var": str,
 "sql": str,
 "uses": [str],           # raw variables the expression reads
 "note": str,             # one or two sentences on what the code does
 "assumptions": str}      # choices a reviewer should check, or ""
Return only the JSON array."""


def describe_sources(names: list[str], dictionary: dict[str, dict], max_codes: int = 40) -> str:
    lines = []
    for name in names:
        entry = dictionary.get(name)
        if not entry:
            lines.append(f"  {name}: (not in the dictionary)")
            continue
        line = f"  {name} [{entry.get('dtype', '')}]: {entry.get('label', '')}"
        codes = json.loads(entry.get("value_labels") or "{}")
        if codes:
            shown = list(codes.items())[:max_codes]
            line += " | codes: " + "; ".join(f"{k}={v}" for k, v in shown)
            if len(codes) > max_codes:
                line += f"; ... ({len(codes)} codes in total)"
        lines.append(line)
    return "\n".join(lines)


def describe_target(target: dict, gold_row: dict, dictionary: dict[str, dict], feedback: str = "") -> str:
    text = f"TARGET {target['name']} ({target['level']}, {target['type']}): {target['description']}"
    if target.get("values"):
        text += "\n  target codes: " + "; ".join(f"{k}={v}" for k, v in target["values"].items())
    if target.get("range"):
        text += f"\n  valid range: {target['range']}"
    primary = [v for v in gold_row["source_vars"].split(";") if v]
    alternative = [v for v in gold_row.get("alt_source_vars", "").split(";") if v]
    text += "\n approved raw variables:\n" + describe_sources(primary, dictionary)
    if alternative:
        text += "\n accepted alternative set:\n" + describe_sources(alternative, dictionary)
    if feedback:
        text += f"\n a previous attempt was tested on the data and needs fixing: {feedback}"
    return text


def build_prompt(targets: list[dict], gold: dict[str, dict], dictionary: dict[str, dict],
                 feedback: dict[str, str] | None = None) -> str:
    feedback = feedback or {}
    blocks = [describe_target(t, gold[t["name"]], dictionary, feedback.get(t["name"], "")) for t in targets]
    return "\n\n".join(blocks) + "\n\n" + INSTRUCTIONS


def generate(survey: str, schema: list[dict], gold: dict[str, dict], dictionary: dict[str, dict],
             call_llm, batch_size: int = 6, only: list[str] | None = None,
             feedback: dict[str, str] | None = None) -> list[dict]:
    targets = [t for t in schema if gold.get(t["name"], {}).get("status") == "mapped"]
    if only:
        targets = [t for t in targets if t["name"] in only]
    out = []
    for start in range(0, len(targets), batch_size):
        batch = targets[start : start + batch_size]
        answers = {a.get("target_var"): a for a in parse_response(call_llm(SYSTEM, build_prompt(batch, gold, dictionary, feedback)))}
        for t in batch:
            a = answers.get(t["name"], {})
            allowed = set(gold[t["name"]]["source_vars"].split(";")) | set(gold[t["name"]].get("alt_source_vars", "").split(";"))
            uses = [str(u).lower() for u in a.get("uses", [])]
            out.append(
                {
                    "target_var": t["name"],
                    "sql": a.get("sql", "NULL"),
                    "uses": uses,
                    "not_approved": sorted(set(uses) - allowed),
                    "note": a.get("note", "no answer from the model"),
                    "assumptions": a.get("assumptions", ""),
                    "written_by": "model",
                }
            )
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--survey", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--batch-size", type=int, default=6)
    ap.add_argument("--fix", help="YAML file mapping target -> what the tests found. Only those targets are "
                                  "written again, and the rest of the code file is kept.")
    args = ap.parse_args()

    with open("config/target_schema.yml", encoding="utf-8") as f:
        schema = yaml.safe_load(f)["variables"]
    with open(f"validate/gold/{args.survey}_gold.csv", newline="", encoding="utf-8") as f:
        gold = {row["target_var"]: row for row in csv.DictReader(f)}
    with open(f"data/dictionaries/{args.survey}.csv", newline="", encoding="utf-8") as f:
        dictionary = {row["variable"]: row for row in csv.DictReader(f)}

    import anthropic

    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set. Export it or put it in a .env file at the repo root.")
    client, usage = anthropic.Anthropic(), {"input": 0, "output": 0, "calls": 0}

    def call(system: str, prompt: str) -> str:
        reply = client.messages.create(model=args.model, max_tokens=6000, system=system,
                                       messages=[{"role": "user", "content": prompt}])
        usage["input"] += reply.usage.input_tokens
        usage["output"] += reply.usage.output_tokens
        usage["calls"] += 1
        return "".join(b.text for b in reply.content if b.type == "text")

    out = Path("harmonize/code") / f"{args.survey}.yml"
    feedback = {}
    if args.fix:
        with open(args.fix, encoding="utf-8") as f:
            feedback = yaml.safe_load(f)
    rows = generate(args.survey, schema, gold, dictionary, call, args.batch_size, list(feedback) or None, feedback)
    if args.fix:
        fixed = {r["target_var"]: r for r in rows}
        previous = yaml.safe_load(out.read_text(encoding="utf-8"))["variables"]
        rows = []
        for old in previous:
            new = fixed.pop(old["target_var"], None)
            if new:
                new["previous_sql"] = old["sql"]
                new["fixed_because"] = feedback[old["target_var"]]
                new["written_by"] = "model, second attempt after a failed check"
            rows.append(new or old)
        rows += list(fixed.values())
    out.parent.mkdir(parents=True, exist_ok=True)
    header = (
        f"# Recoding code for {args.survey}, written by {args.model} from the reviewed gold standard.\n"
        "# Each expression is DuckDB SQL over the person-level table. Edit by hand where needed and\n"
        "# set written_by to your name: harmonize/build_harmonized.py runs whatever is in this file.\n"
    )
    out.write_text(header + yaml.safe_dump({"survey": args.survey, "model": args.model, "variables": rows},
                                           allow_unicode=True, sort_keys=False, width=110), encoding="utf-8")
    flagged = [r["target_var"] for r in rows if r["not_approved"]]
    print(f"{args.survey}: {len(rows)} expressions -> {out}")
    print(f"  {usage['calls']} calls, {usage['input']} input and {usage['output']} output tokens")
    print(f"  expressions reading a variable that was not approved: {flagged or 'none'}")
    (out.with_suffix(".usage.json")).write_text(json.dumps({"model": args.model, **usage}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
