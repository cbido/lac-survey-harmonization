"""Build a draft gold standard of variable mappings from the IDB's public
harmonization programs (Stata do-files).

For every harmonized variable (suffix _c, _ch, _ci) the script records which
raw survey variables the IDB program uses to build it. The result is a DRAFT:
the parser is heuristic and each row needs a human look before it is used
to score an LLM.

Usage:
    python harmonize/extract_gold_from_idb.py \
        --do-file path/to/CHL_2022m11_m12_m1_variablesBID.do \
        --survey CHL_2022 \
        --out validate/gold/CHL_2022_gold_draft.csv \
        [--dictionary data/dictionaries/CHL_2022.csv]
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)  # value-label fields can be very long (comunas, occupations)

HARMONIZED = re.compile(r"^[A-Za-z0-9_]+_(ci|ch|c)$")

STATEMENT = re.compile(
    r"""^\s*
    (?:(?:cap|capture|qui|quietly|noi|noisily)\s+)*
    (?:by(?:s|so|sor|sort)?\s+[^:]+:\s*)?
    (?P<cmd>g(?:e(?:n(?:e(?:r(?:a(?:te?)?)?)?)?)?)?|egen|clonevar|replace)\s+
    (?:(?:byte|int|long|float|double|str\d*)\s+)?
    (?P<target>[A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)\s*
    (?P<expr>.*)$""",
    re.VERBOSE,
)
LABEL = re.compile(r"""^\s*(?:cap(?:ture)?\s+)?label\s+var(?:iable)?\s+(\w+)\s+"([^"]*)""")
IDENT = re.compile(r"[A-Za-z_\x00][A-Za-z0-9_\x00]*")
RESERVED = {"if", "in", "_n", "_N", "_pi", "e"}


def strip_comments(text: str) -> str:
    """Remove Stata comments, keeping line breaks.

    Handles nested /* */ blocks, // comments (which win over a /* that follows
    them on the same line), /// continuations and lines that start with *.
    """
    out, depth, i, n = [], 0, 0, len(text)
    line_start = True
    while i < n:
        ch, pair = text[i], text[i : i + 2]
        if depth > 0:
            if pair == "/*":
                depth += 1
                i += 2
            elif pair == "*/":
                depth -= 1
                i += 2
            else:
                if ch == "\n":
                    out.append("\n")
                    line_start = True
                i += 1
            continue
        if pair == "/*":
            depth += 1
            i += 2
            continue
        if text[i : i + 3] == "///":  # continuation: join with next line
            end = text.find("\n", i)
            i = n if end == -1 else end + 1
            out.append(" ")
            continue
        if pair == "//" and (line_start or text[i - 1] in " \t"):
            end = text.find("\n", i)
            i = n if end == -1 else end
            continue
        if ch == "*" and line_start:
            end = text.find("\n", i)
            i = n if end == -1 else end
            continue
        if ch == "\n":
            line_start = True
        elif ch not in " \t":
            line_start = False
        out.append(ch)
        i += 1
    return "".join(out)


def clean_lines(text: str) -> list[str]:
    return [line for line in strip_comments(text).splitlines() if line.strip()]


def cut_options(expr: str) -> str:
    """Drop egen options (everything after a comma outside parentheses)."""
    depth = 0
    for i, ch in enumerate(expr):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            return expr[:i]
    return expr


def identifiers(expr: str, varlist: bool = False) -> set[str]:
    expr = re.sub(r'"[^"]*"', " ", expr)  # string literals
    if varlist:  # egen arguments: name glued to * is a wildcard, not a product
        expr = re.sub(r"[A-Za-z0-9_]*\*[A-Za-z0-9_*]*", " ", expr)
    expr = re.sub(r"`[^']*'", "\x00", expr)  # local macros -> marker
    found = set()
    for m in IDENT.finditer(expr):
        name = m.group(0)
        if "\x00" in name:  # name built with a macro, cannot be resolved
            continue
        if expr[m.end() :].lstrip().startswith("("):  # function call
            continue
        if m.start() > 0 and (expr[m.start() - 1].isdigit() or expr[m.start() - 1] == "."):
            continue  # 1e5, 2.5e3, .a
        if name in RESERVED:
            continue
        found.add(name)
    return found


def parse_do_file(text: str) -> tuple[dict[str, set[str]], dict[str, list[str]], dict[str, str], set[str]]:
    """Return (dependencies, assigned expressions, labels, created variables).

    "Created" means gen/egen/clonevar. A variable that is only ever the target
    of replace is a raw survey variable being recoded in place.
    """
    deps: dict[str, set[str]] = {}
    exprs: dict[str, list[str]] = {}
    labels: dict[str, str] = {}
    created: set[str] = set()
    for line in clean_lines(text):
        lab = LABEL.match(line)
        if lab:
            labels[lab.group(1)] = lab.group(2).strip()
            continue
        m = STATEMENT.match(line)
        if not m:
            continue
        target, expr = m.group("target"), m.group("expr").strip()
        is_egen = m.group("cmd") == "egen"
        if is_egen:
            expr = cut_options(expr)
        if m.group("cmd") != "replace":
            created.add(target)
        deps.setdefault(target, set()).update(identifiers(expr, varlist=is_egen) - {target})
        exprs.setdefault(target, []).append(expr)
    return deps, exprs, labels, created


def resolve(target: str, deps: dict[str, set[str]], created: set[str]) -> tuple[set[str], set[str]]:
    """Follow intermediate variables down to raw survey variables.

    Returns (raw source variables, harmonized variables it is derived from).
    A name that is never created in the program is taken to be a raw variable.
    """
    raw, derived, seen = set(), set(), set()
    stack = list(deps.get(target, ()))
    while stack:
        name = stack.pop()
        if name in seen:
            continue
        seen.add(name)
        if HARMONIZED.match(name):
            derived.add(name)
        elif name in created:
            stack.extend(deps[name])
        else:
            raw.add(name)
    return raw, derived


def build_gold(text: str, survey: str, dictionary: set[str] | None = None) -> list[dict]:
    deps, exprs, labels, created = parse_do_file(text)
    rows = []
    for target in deps:
        if not HARMONIZED.match(target) or target not in created:
            continue
        raw, derived = resolve(target, deps, created)
        unknown = set()
        if dictionary is not None:
            unknown = {v for v in raw if v.lower() not in dictionary}
            raw -= unknown
        if raw:
            status = "mapped"
        elif derived:
            status = "derived"
        elif all(e.split(" if ")[0].strip() == "." for e in exprs[target]):
            status = "not_available"
        else:
            status = "constant"
        rows.append(
            {
                "survey": survey,
                "target_var": target,
                "status": status,
                "source_vars": ";".join(sorted(raw)),
                "derived_from": ";".join(sorted(derived)),
                "not_in_dictionary": ";".join(sorted(unknown)),
                "names_checked": "yes" if dictionary is not None else "no",
                "idb_label": labels.get(target, ""),
                "reviewed": "",
            }
        )
    return rows


def read_dictionary(path: str | None) -> set[str] | None:
    if not path:
        return None
    with open(path, newline="", encoding="utf-8") as f:
        return {row["variable"].lower() for row in csv.DictReader(f)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--do-file", required=True)
    ap.add_argument("--survey", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dictionary", help="CSV from ingest/to_parquet.py; drops names that are not raw variables")
    args = ap.parse_args()

    text = Path(args.do_file).read_text(encoding="utf-8", errors="replace")
    rows = build_gold(text, args.survey, read_dictionary(args.dictionary))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"{args.survey}: {len(rows)} harmonized variables -> {args.out}")
    for status, n in sorted(counts.items()):
        print(f"  {status:14s} {n}")


if __name__ == "__main__":
    main()
