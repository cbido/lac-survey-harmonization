"""Score the model's occupation and industry codes against the statistics office's codes.

Agreement is reported at each level of the classification, with a simple reference
method beside it: a lookup table that gives each occupation title (or workplace text)
the code the office assigned most often to that same text among all other workers.
The office's code is a human coder's decision and not the truth, so this measures
agreement with the office.

Usage:
    python coding/evaluate_coding.py --survey CHL_2022
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import duckdb
import yaml

csv.field_size_limit(sys.maxsize)

# ISIC Rev.4: division (two digits) to section. Casen's list adds two divisions of its own
# (04 in mining, 48 in commerce), so those ranges are one wider than in ISIC.
SECTIONS = [("A", 1, 3), ("B", 4, 9), ("C", 10, 33), ("D", 35, 35), ("E", 36, 39), ("F", 41, 43),
            ("G", 45, 48), ("H", 49, 53), ("I", 55, 56), ("J", 58, 63), ("K", 64, 66), ("L", 68, 68),
            ("M", 69, 75), ("N", 77, 82), ("O", 84, 84), ("P", 85, 85), ("Q", 86, 88), ("R", 90, 93),
            ("S", 94, 96), ("T", 97, 98), ("U", 99, 99)]

ISCO_MAJOR = {"0": "Armed forces", "1": "Managers", "2": "Professionals", "3": "Technicians",
              "4": "Clerical support", "5": "Service and sales", "6": "Skilled agricultural",
              "7": "Craft and trades", "8": "Plant and machine operators", "9": "Elementary"}


def isco_levels(code) -> dict[str, str] | None:
    """Major, sub-major, minor and unit group of an ISCO-08 code. Armed forces codes are zero-padded."""
    try:
        code = int(code)
    except (TypeError, ValueError):
        return None
    if code <= 0:
        return None
    s = str(code).zfill(4)
    return {"1 digit": s[:1], "2 digits": s[:2], "3 digits": s[:3], "4 digits": s}


def isic_levels(code) -> dict[str, str] | None:
    """Section, division and survey category of an ISIC Rev.4 based code."""
    try:
        code = int(code)
    except (TypeError, ValueError):
        return None
    if code <= 0:
        return None
    s = str(code).zfill(4)
    division = int(s[:2])
    section = next((name for name, lo, hi in SECTIONS if lo <= division <= hi), None)
    return {"section": section or "?", "division": s[:2], "survey category": s}


def normalize(text) -> str:
    return " ".join(str(text or "").lower().split())


def agreement(pairs: list[tuple], levels_of, weights: list[float] | None = None) -> dict[str, dict]:
    """Share of cases where two codes agree at each level. A missing code never agrees."""
    weights = weights or [1.0] * len(pairs)
    out = {}
    first = next((levels_of(a) for a, _ in pairs if levels_of(a)), None)
    for level in (first or {}):
        hits = [1.0 if (levels_of(a) and levels_of(b) and levels_of(a)[level] == levels_of(b)[level]) else 0.0
                for a, b in pairs]
        n = len(hits)
        p = sum(hits) / n if n else float("nan")
        se = math.sqrt(p * (1 - p) / n) if n else float("nan")
        total = sum(weights)
        out[level] = {"agreement": p, "lower": p - 1.96 * se, "upper": p + 1.96 * se,
                      "weighted": sum(h * w for h, w in zip(hits, weights)) / total if total else float("nan")}
    return out


def kappa(pairs: list[tuple]) -> float:
    """Cohen's kappa for two sets of labels."""
    n = len(pairs)
    if not n:
        return float("nan")
    observed = sum(a == b for a, b in pairs) / n
    left, right = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    expected = sum(left[k] * right.get(k, 0) for k in left) / (n * n)
    return (observed - expected) / (1 - expected) if expected < 1 else float("nan")


def triage(rows: list[dict], field: str, levels_of, level: str, thresholds=(0.5, 0.7, 0.9)) -> list[dict]:
    """Coverage and agreement among cases at or above each confidence threshold."""
    out = []
    for t in thresholds:
        kept = [r for r in rows if _float(r[f"{field}_conf"]) >= t]
        hits = [1 for r in kept
                if levels_of(r[f"{field}_office"]) and levels_of(r[f"{field}_model"])
                and levels_of(r[f"{field}_office"])[level] == levels_of(r[f"{field}_model"])[level]]
        out.append({"threshold": t, "coverage": len(kept) / len(rows) if rows else float("nan"),
                    "agreement": len(hits) / len(kept) if kept else float("nan"), "n": len(kept)})
    return out


def _float(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return -1.0


def lookup_codes(parquet: str, text_var: str, code_var: str, sample_texts: list[str],
                 sample_office: list[int]) -> list[int | None]:
    """Most frequent office code for the same text among all other workers.

    Each sampled case is taken out of its own text's counts, so a text that appears once
    in the file gets no code.
    """
    con = duckdb.connect()
    counts: dict[str, Counter] = defaultdict(Counter)
    query = (f"SELECT lower(trim({text_var})), {code_var}, count(*) FROM '{parquet}' "
             f"WHERE {code_var} > 0 AND length(trim({text_var})) > 0 GROUP BY 1, 2")
    for text, code, n in con.execute(query).fetchall():
        counts[normalize(text)][int(code)] += n
    out = []
    for text, office in zip(sample_texts, sample_office):
        c = Counter(counts.get(normalize(text), {}))
        c[int(office)] -= 1
        c = +c
        out.append(min(c, key=lambda code: (-c[code], code)) if c else None)   # empates: el código menor
    return out


def table(rows: list[list], header: list[str]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(lines)


def pct(x: float) -> str:
    return "" if x != x else f"{100 * x:.1f}%"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--survey", required=True)
    args = ap.parse_args()

    with open("config/surveys.yml", encoding="utf-8") as f:
        v = yaml.safe_load(f)["surveys"][args.survey]["coding"]["variables"]
    with open(f"data/coding/{args.survey}_coded.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    parquet = f"data/parquet/{args.survey}.parquet"
    weights = [float(r["weight"]) for r in rows]
    n = len(rows)

    lookup = {
        "occ": lookup_codes(parquet, v["title"], v["occ_code"], [r["title"] for r in rows],
                            [int(r["occ_office"]) for r in rows]),
        "ind": lookup_codes(parquet, v["workplace"], v["ind_code"], [r["workplace"] for r in rows],
                            [int(r["ind_office"]) for r in rows]),
    }

    out = [f"# Occupation and industry coding: {args.survey}", "",
           f"Generated by `coding/evaluate_coding.py`. {n:,} workers drawn at random from those whose "
           "occupation and industry the statistics office coded. Agreement is with the office's code.", ""]
    summary, extra = [], {}
    for field, name, levels_of, top, detail in (
            ("occ", "Occupation (ISCO-08)", isco_levels, "1 digit", "4 digits"),
            ("ind", "Industry (ISIC Rev.4 based list)", isic_levels, "section", "survey category")):
        model_pairs = [(r[f"{field}_office"], r[f"{field}_model"]) for r in rows]
        look_pairs = [(r[f"{field}_office"], code) for r, code in zip(rows, lookup[field])]
        covered = [code is not None for code in lookup[field]]
        m = agreement(model_pairs, levels_of, weights)
        lk = agreement(look_pairs, levels_of, weights)
        lk_cov = agreement([p for p, c in zip(look_pairs, covered) if c], levels_of)
        invalid = sum(1 for r in rows if r[f"{field}_invalid"] != "")
        uncodable = sum(1 for r in rows if r[f"{field}_model"] == "-66")
        unanswered = sum(1 for r in rows if r[f"{field}_model"] == "" and r[f"{field}_invalid"] == "")

        out += [f"## {name}", "",
                table([[level, pct(m[level]["agreement"]),
                        f'{pct(m[level]["lower"])} to {pct(m[level]["upper"])}', pct(m[level]["weighted"]),
                        pct(lk[level]["agreement"]), pct(lk_cov[level]["agreement"])] for level in m],
                      ["Level", "Model", "95% interval", "Model, weighted", "Lookup table, all cases",
                       "Lookup table, cases it can code"]), "",
                f"The lookup table can code {pct(sum(covered) / n)} of cases. The model returned a code outside "
                f"the list in {invalid} cases, said the text could not be classified in {uncodable}, and gave "
                f"no answer in {unanswered}. All of these count as disagreement.", ""]

        # el modelo dentro y fuera de lo que cubre la tabla, y los dos métodos combinados
        inside = agreement([p for p, c in zip(model_pairs, covered) if c], levels_of)
        outside = agreement([p for p, c in zip(model_pairs, covered) if not c], levels_of)
        hybrid = agreement([lp if c else mp for mp, lp, c in zip(model_pairs, look_pairs, covered)], levels_of)
        out += ["The same comparison split by whether the lookup table has seen the text:", "",
                table([[level, pct(lk_cov[level]["agreement"]), pct(inside[level]["agreement"]),
                        pct(outside[level]["agreement"]), pct(hybrid[level]["agreement"])] for level in m],
                      ["Level", "Lookup table, text seen before", "Model, text seen before",
                       "Model, text not seen before", "Lookup table where it has the text, model otherwise"]), ""]
        for level in m:
            extra[(field, level)] = {"model_text_seen": round(inside[level]["agreement"], 4),
                                     "model_text_not_seen": round(outside[level]["agreement"], 4),
                                     "lookup_then_model": round(hybrid[level]["agreement"], 4)}

        tops = [(levels_of(a)[top], (levels_of(b) or {}).get(top, "none")) for a, b in model_pairs]
        out += [f"Cohen's kappa at the top level ({top}): {kappa(tops):.2f}.", ""]

        by_group = defaultdict(lambda: [0, 0, 0])
        for (a, b) in model_pairs:
            la, lb = levels_of(a), levels_of(b)
            g = la[top]
            by_group[g][0] += 1
            by_group[g][1] += int(bool(lb) and lb[top] == la[top])
            by_group[g][2] += int(bool(lb) and lb[detail] == la[detail])
        label = (lambda g: f"{g} {ISCO_MAJOR.get(g, '')}".strip()) if field == "occ" else (lambda g: g)
        out += [f"Agreement by the office's {top} group:", "",
                table([[label(g), c[0], pct(c[1] / c[0]), pct(c[2] / c[0])] for g, c in sorted(by_group.items())],
                      ["Group (office code)", "Cases", f"Same {top}", f"Same {detail}"]), ""]

        out += ["How much could be accepted without review, by the model's own confidence:", "",
                table([[f'{t["threshold"]:.1f}', t["n"], pct(t["coverage"]), pct(t["agreement"])]
                       for t in triage(rows, field, levels_of, detail)],
                      ["Confidence at or above", "Cases", "Share of cases", f"Agreement at {detail}"]), ""]

        for level in m:
            summary.append({"classification": field, "level": level, "n": n,
                            "model": round(m[level]["agreement"], 4), "model_lower": round(m[level]["lower"], 4),
                            "model_upper": round(m[level]["upper"], 4), "model_weighted": round(m[level]["weighted"], 4),
                            "lookup_all": round(lk[level]["agreement"], 4),
                            "lookup_coverage": round(sum(covered) / n, 4),
                            "lookup_when_covered": round(lk_cov[level]["agreement"], 4),
                            **extra[(field, level)]})

    out_dir = Path("coding/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{args.survey}_coding_eval.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    with open(out_dir / f"{args.survey}_coding_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)
    print("\n".join(out))


if __name__ == "__main__":
    main()
