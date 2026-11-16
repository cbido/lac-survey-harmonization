"""Code open-text occupation and industry answers with an LLM, to compare with the
codes the statistics office assigned.

Casen publishes the interviewer's text (occupation title, tasks, what the workplace
does) next to the office's own codes: ISCO-08 at four digits (CIUO-08.CL) and a
122-category list based on ISIC Rev.4. The model sees the three texts and the two code
lists taken from the survey's data dictionary. It never sees the office's codes.

A random sample of coded workers is drawn, sent in batches, and saved row by row to

    data/coding/<survey>_coded.csv        (local only: it holds survey text)

Batches already on disk are skipped, so an interrupted run can be resumed.
coding/evaluate_coding.py scores the result.

Usage:
    python coding/code_occupation_industry.py --survey CHL_2022 --n 1500
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import duckdb
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
csv.field_size_limit(sys.maxsize)

from harmonize.propose_mappings import DEFAULT_MODEL, load_env, parse_response  # noqa: E402

UNCODABLE = -66

SYSTEM = (
    "You are a classification coder for a household survey. You read what a worker said "
    "about the job and assign the occupation code and the industry code from the lists "
    "you are given. Use only codes that appear in those lists."
)

RULES = """For each case you get the occupation title, the tasks the person described, and what
the workplace does. Assign:
- "occ": the four-digit occupation code that fits the title and tasks best. Tasks decide
  when the title is vague. Armed forces codes have three digits.
- "ind": the industry code of the workplace. It describes what the establishment does,
  and the worker's own tasks do not change it.
- If the text does not allow a classification, use -66.
- "occ_conf" and "ind_conf": your confidence from 0 to 1 that the code is right at its
  most detailed level.

Return a JSON array with one object per case, in the same order:
{"id": int, "occ": int, "occ_conf": float, "ind": int, "ind_conf": float}
Return only the JSON array."""


def load_frame(dictionary_csv: str, variable: str) -> dict[int, str]:
    """Positive codes and labels of a coded variable, from the survey's data dictionary."""
    with open(dictionary_csv, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["variable"] == variable:
                labels = json.loads(row["value_labels"] or "{}")
                return {int(k): v for k, v in labels.items() if int(k) > 0}
    raise KeyError(f"{variable} is not in {dictionary_csv}")


def format_frames(occ: dict[int, str], ind: dict[int, str]) -> str:
    occ_lines = "\n".join(f"{code}: {label}" for code, label in sorted(occ.items()))
    ind_lines = "\n".join(f"{code}: {label}" for code, label in sorted(ind.items()))
    return (f"<occupation_codes>\n{occ_lines}\n</occupation_codes>\n\n"
            f"<industry_codes>\n{ind_lines}\n</industry_codes>\n\n{RULES}")


def format_cases(cases: list[dict]) -> str:
    lines = []
    for c in cases:
        lines.append(f'id {c["id"]} | occupation: {c["title"]} | tasks: {c["tasks"]} | workplace: {c["workplace"]}')
    return "<cases>\n" + "\n".join(lines) + "\n</cases>"


def validate(answers: list[dict], cases: list[dict], occ: dict[int, str], ind: dict[int, str]) -> list[dict]:
    """Align answers with the cases sent and flag codes that are not in the lists."""
    by_id = {}
    for a in answers:
        try:
            by_id[int(a.get("id"))] = a
        except (TypeError, ValueError):
            continue
    rows = []
    for c in cases:
        a = by_id.get(c["id"], {})
        row = {"id": c["id"]}
        for field, frame in (("occ", occ), ("ind", ind)):
            try:
                code = int(a.get(field))
            except (TypeError, ValueError):
                code = None
            valid = code is not None and (code in frame or code == UNCODABLE)
            row[f"{field}_model"] = code if valid else ""
            row[f"{field}_invalid"] = "" if valid or code is None else code
            row[f"{field}_conf"] = a.get(f"{field}_conf", "") if valid else ""
        rows.append(row)
    return rows


def draw_sample(parquet: str, cfg: dict, n: int, seed: int) -> list[dict]:
    """Random sample of workers whose occupation and industry the office coded.

    Rows are ordered by a hash of the person key and the seed, so the same seed always
    gives the same sample and a smaller n is a prefix of a larger one.
    """
    v = cfg["variables"]
    key = " || '-' || ".join(f"CAST({k} AS VARCHAR)" for k in cfg["key"])
    query = f"""
        SELECT row_number() OVER (ORDER BY h, k) AS id, title, tasks, workplace, occ_office, ind_office, weight
        FROM (
            SELECT {key} AS k, hash({key} || '-{int(seed)}') AS h,
                   {v['title']} AS title, {v['tasks']} AS tasks, {v['workplace']} AS workplace,
                   {v['occ_code']} AS occ_office, {v['ind_code']} AS ind_office, {v['weight']} AS weight
            FROM '{parquet}'
            WHERE {v['occ_code']} > 0 AND {v['ind_code']} > 0
              AND length(trim({v['title']})) > 0 AND length(trim({v['workplace']})) > 0
        )
        ORDER BY h, k
        LIMIT {int(n)}"""
    cols = ["id", "title", "tasks", "workplace", "occ_office", "ind_office", "weight"]
    return [dict(zip(cols, r)) for r in duckdb.connect().execute(query).fetchall()]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--survey", required=True)
    ap.add_argument("--n", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=2022)
    ap.add_argument("--batch-size", type=int, default=50)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()

    with open("config/surveys.yml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)["surveys"][args.survey]["coding"]
    dictionary = f"data/dictionaries/{args.survey}.csv"
    occ = load_frame(dictionary, cfg["variables"]["occ_code"])
    ind = load_frame(dictionary, cfg["variables"]["ind_code"])
    frames = format_frames(occ, ind)

    out = Path("data/coding") / f"{args.survey}_coded.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    sample = draw_sample(f"data/parquet/{args.survey}.parquet", cfg, args.n, args.seed)
    done = set()
    if out.exists():
        with open(out, newline="", encoding="utf-8") as f:
            done = {int(r["id"]) for r in csv.DictReader(f)}
    todo = [c for c in sample if c["id"] not in done]
    batches = [todo[i:i + args.batch_size] for i in range(0, len(todo), args.batch_size)]
    print(f"{len(sample)} cases sampled, {len(done)} already coded, {len(batches)} batches to send")
    if not batches:
        return

    import anthropic

    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set. Export it or put it in a .env file at the repo root.")
    client = anthropic.Anthropic()
    usage = []

    def code_batch(cases: list[dict]) -> list[dict]:
        reply = client.messages.create(
            model=args.model, max_tokens=5000, system=SYSTEM,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": frames, "cache_control": {"type": "ephemeral"}},
                {"type": "text", "text": format_cases(cases)},
            ]}],
        )
        u = reply.usage
        usage.append({"input": u.input_tokens,
                      "cache_write": getattr(u, "cache_creation_input_tokens", 0) or 0,
                      "cache_read": getattr(u, "cache_read_input_tokens", 0) or 0,
                      "output": u.output_tokens})
        text = "".join(b.text for b in reply.content if b.type == "text")
        coded = {r["id"]: r for r in validate(parse_response(text), cases, occ, ind)}
        return [{**c, **coded[c["id"]]} for c in cases]

    fields = ["id", "title", "tasks", "workplace", "occ_office", "ind_office", "weight",
              "occ_model", "occ_conf", "occ_invalid", "ind_model", "ind_conf", "ind_invalid"]
    new_file = not out.exists()
    with open(out, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if new_file:
            writer.writeheader()

        def save(rows: list[dict]) -> None:
            writer.writerows(rows)
            f.flush()

        save(code_batch(batches[0]))            # la primera llamada escribe el caché
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for rows in pool.map(code_batch, batches[1:]):
                save(rows)

    usage_file = Path("coding/output") / f"{args.survey}_coding.usage.json"
    usage_file.parent.mkdir(parents=True, exist_ok=True)
    previous = json.loads(usage_file.read_text())["calls"] if usage_file.exists() else []
    calls = previous + usage
    totals = {k: sum(c[k] for c in calls) for k in ("input", "cache_write", "cache_read", "output")}
    usage_file.write_text(json.dumps({"model": args.model, "n_calls": len(calls), "totals": totals, "calls": calls}, indent=2))
    print(f"wrote {out}", totals)


if __name__ == "__main__":
    main()
