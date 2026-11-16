"""Download every open file listed in config/sources.yml into data/.

Files that need a form or an account are listed at the end with the page to visit.
A hash of each downloaded file is kept in data/checksums.csv, so a later run shows
whether the statistics office has replaced a file.

Usage:
    python scripts/download_data.py                 # everything open
    python scripts/download_data.py --survey CHL_2017 --kind microdata comuna
    python scripts/download_data.py --list          # show the manifest, download nothing
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

CHECKSUMS = Path("data/checksums.csv")


def load_manifest(path: str = "config/sources.yml") -> list[dict]:
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    bases = {k: v["base"] for k, v in cfg.items() if isinstance(v, dict) and "base" in v}
    files = []
    for item in cfg["files"]:
        url = item["url"]
        for country, base in bases.items():
            url = url.replace("{" + country + "}", base)
        files.append({**item, "url": url})
    return files


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch(url: str, dest: Path) -> None:
    """Download to a temporary file first, so a failed transfer leaves nothing half-written."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    safe_url = urllib.parse.quote(url, safe=":/?=&%+()")
    request = urllib.request.Request(safe_url, headers={"User-Agent": "lac-survey-harmonization/0.1"})
    tmp = dest.with_name(dest.name + ".part")
    with urllib.request.urlopen(request, timeout=120) as response, open(tmp, "wb") as out:
        if "text/html" in response.headers.get("Content-Type", "") and dest.suffix.lower() != ".html":
            raise urllib.error.URLError("the server returned a web page, not the file")
        shutil.copyfileobj(response, out)
    tmp.replace(dest)


def read_checksums() -> dict[str, str]:
    if not CHECKSUMS.exists():
        return {}
    with open(CHECKSUMS, newline="", encoding="utf-8") as f:
        return {row["path"]: row["sha256"] for row in csv.DictReader(f)}


def write_checksums(known: dict[str, str]) -> None:
    CHECKSUMS.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKSUMS, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["path", "sha256"])
        writer.writerows(sorted(known.items()))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--survey", nargs="*", help="Limit to these survey ids")
    ap.add_argument("--kind", nargs="*", help="Limit to these kinds: microdata comuna questionnaire codebook metadata")
    ap.add_argument("--list", action="store_true", help="Print the manifest and exit")
    ap.add_argument("--force", action="store_true", help="Download again even if the file exists")
    args = ap.parse_args()

    files = [
        f for f in load_manifest()
        if (not args.survey or f["survey"] in args.survey) and (not args.kind or f["kind"] in args.kind)
    ]
    if args.list:
        for f in files:
            print(f"{f['survey']:9} {f['kind']:13} {f['access']:8} {f['path']}")
        return

    known, manual, failed = read_checksums(), [], []
    for f in files:
        if f["access"] != "open":
            manual.append(f)
            continue
        dest = Path(f["path"])
        if dest.exists() and not args.force:
            status = "exists"
        else:
            try:
                fetch(f["url"], dest)
                status = "downloaded"
            except (urllib.error.URLError, OSError) as err:
                failed.append((f, err))
                print(f"FAILED      {f['path']}  ({err})")
                continue
        digest = sha256(dest)
        if known.get(f["path"]) not in (None, digest):
            status += ", CHANGED since last run"
        known[f["path"]] = digest
        print(f"{status:11} {f['path']}  ({dest.stat().st_size / 1e6:.1f} MB)")
    write_checksums(known)

    if manual:
        print("\nTo download by hand:")
        for f in manual:
            print(f"  {f['survey']} {f['kind']} ({f['access']}): {f['url']}  ->  {f['path']}")
    if failed:
        print(f"\n{len(failed)} file(s) failed. See the notes in config/sources.yml.")


if __name__ == "__main__":
    main()
