"""Ask an LLM to propose, for each target variable in the harmonized schema,
which raw survey variables it should be built from.

Input is the survey's data dictionary only (names, labels, value labels).
Output is a CSV with one row per target variable and empty review columns,
so that a person accepts, edits or rejects every proposal before it is used.

Usage:
    export ANTHROPIC_API_KEY=...
    python harmonize/propose_mappings.py --survey CHL_2022 \
        --dictionary data/dictionaries/CHL_2022.csv \
        --out harmonize/proposals/CHL_2022.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path
from typing import Callable

import yaml

csv.field_size_limit(sys.maxsize)  # value-label fields can be very long (comunas, occupations)

DEFAULT_MODEL = os.environ.get("LLM_MODEL", "claude-sonnet-5-5")

SYSTEM = (
    "You harmonize Latin American household surveys. You receive the data "
    "dictionary of one survey and a list of target variables from a common "
    "schema. For each target variable, name the raw survey variables needed to "
    "build it. Use only variable names that appear in the dictionary. If the "
    "survey does not collect the information, say so instead of guessing."
)

INSTRUCTIONS = """Return a JSON array with one object per target variable, in the same order:
{"target_var": str,
 "status": "mapped" | "not_available",
 "source_vars": [str],          # raw variable names, empty if not_available
 "confidence": number,          # 0 to 1
 "rationale": str}              # one sentence
Return only the JSON array."""

OUT_FIELDS = [
    "survey", "target_var", "domain", "status", "source_vars", "confidence",
    "rationale", "invalid_sources", "model", "review_status", "reviewer_note",
]


def load_schema(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["variables"]


def load_dictionary(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def format_dictionary(rows: list[dict], max_value_labels: int = 12, max_question: int = 160) -> str:
    """One line per raw variable: name, label, question text if it adds something, codes."""
    lines = []
    for r in rows:
        label = (r.get("label") or "").strip()
        line = f"{r['variable']}: {label}"
        question = (r.get("question") or "").strip()
        if question and question.lower() != label.lower():
            line += " | Q: " + question[:max_question]
        codes = json.loads(r.get("value_labels") or "{}")
        if codes:
            shown = list(codes.items())[:max_value_labels]
            line += " | " + "; ".join(f"{k}={v}" for k, v in shown)
            if len(codes) > max_value_labels:
                line += "; ..."
        lines.append(line)
    return "\n".join(lines)


def format_targets(targets: list[dict]) -> str:
    lines = []
    for t in targets:
        line = f"{t['name']} ({t['level']}, {t['type']}): {t['description']}"
        if t.get("values"):
            line += " | codes: " + "; ".join(f"{k}={v}" for k, v in t["values"].items())
        lines.append(line)
    return "\n".join(lines)


def build_prompt(dictionary_text: str, targets: list[dict]) -> str:
    return (
        f"<data_dictionary>\n{dictionary_text}\n</data_dictionary>\n\n"
        f"<target_variables>\n{format_targets(targets)}\n</target_variables>\n\n"
        f"{INSTRUCTIONS}"
    )


def parse_response(text: str) -> list[dict]:
    """Extract the JSON array from the model reply."""
    match = re.search(r"\[.*\]", text, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON array found in the model reply")
    return json.loads(match.group(0))


def validate(proposals: list[dict], targets: list[dict], known_vars: set[str]) -> list[dict]:
    """Align proposals with the requested targets and drop invented variable names."""
    by_target = {p.get("target_var"): p for p in proposals}
    rows = []
    for t in targets:
        p = by_target.get(t["name"], {})
        sources = [str(s).lower() for s in p.get("source_vars", [])]
        valid = [s for s in sources if s in known_vars]
        invalid = [s for s in sources if s not in known_vars]
        status = p.get("status", "no_answer")
        if status == "mapped" and not valid:
            status = "no_valid_source"
        rows.append(
            {
                "target_var": t["name"],
                "domain": t["domain"],
                "status": status,
                "source_vars": ";".join(sorted(valid)),
                "confidence": p.get("confidence", ""),
                "rationale": p.get("rationale", ""),
                "invalid_sources": ";".join(sorted(invalid)),
            }
        )
    return rows


def load_env(path: str = ".env") -> None:
    """Read KEY=value lines from a local .env file (never committed) into the environment."""
    env = Path(path)
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


DICTIONARY_END = "</data_dictionary>\n\n"


def anthropic_caller(model: str, usage: list[dict] | None = None) -> Callable[[str, str], str]:
    """Return a function that sends one prompt to the API.

    The data dictionary is the same in every batch of a survey, so it is marked for
    prompt caching and only the first call pays for it in full. Token counts of each
    call are appended to `usage`.
    """
    import anthropic

    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set. Export it or put it in a .env file at the repo root.")
    client = anthropic.Anthropic()

    def call(system: str, prompt: str) -> str:
        head, sep, tail = prompt.partition(DICTIONARY_END)
        if sep:
            content = [
                {"type": "text", "text": head + sep, "cache_control": {"type": "ephemeral"}},
                {"type": "text", "text": tail},
            ]
        else:
            content = prompt
        reply = client.messages.create(
            model=model,
            max_tokens=4000,
            system=system,
            messages=[{"role": "user", "content": content}],
        )
        if usage is not None:
            u = reply.usage
            usage.append(
                {
                    "input": u.input_tokens,
                    "cache_write": getattr(u, "cache_creation_input_tokens", 0) or 0,
                    "cache_read": getattr(u, "cache_read_input_tokens", 0) or 0,
                    "output": u.output_tokens,
                }
            )
        return "".join(block.text for block in reply.content if block.type == "text")

    return call


def propose(
    survey: str,
    dictionary: list[dict],
    schema: list[dict],
    call_llm: Callable[[str, str], str],
    model: str,
    batch_size: int = 10,
) -> list[dict]:
    known = {r["variable"].lower() for r in dictionary}
    dictionary_text = format_dictionary(dictionary)
    rows = []
    for start in range(0, len(schema), batch_size):
        targets = schema[start : start + batch_size]
        reply = call_llm(SYSTEM, build_prompt(dictionary_text, targets))
        for row in validate(parse_response(reply), targets, known):
            rows.append({"survey": survey, "model": model, "review_status": "", "reviewer_note": "", **row})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--survey", required=True)
    ap.add_argument("--dictionary", required=True)
    ap.add_argument("--schema", default="config/target_schema.yml")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--batch-size", type=int, default=10)
    args = ap.parse_args()

    usage: list[dict] = []
    rows = propose(
        args.survey,
        load_dictionary(args.dictionary),
        load_schema(args.schema),
        anthropic_caller(args.model, usage),
        args.model,
        args.batch_size,
    )
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    n_invalid = sum(bool(r["invalid_sources"]) for r in rows)
    print(f"{args.survey}: {len(rows)} proposals -> {args.out}")
    print(f"  proposals naming a variable that is not in the dictionary: {n_invalid}")
    totals = {k: sum(u[k] for u in usage) for k in ("input", "cache_write", "cache_read", "output")}
    usage_path = Path(args.out).with_suffix(".usage.json")
    usage_path.write_text(json.dumps({"model": args.model, "calls": len(usage), **totals}, indent=2), encoding="utf-8")
    print(f"  {len(usage)} calls | tokens: {totals} -> {usage_path}")


if __name__ == "__main__":
    main()
