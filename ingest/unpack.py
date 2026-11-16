"""Unpack the downloaded archives under data/raw/ into data/raw/<survey>/unpacked/.

Zip files are handled directly. Casen 2015 and 2017 are published as .rar, which
needs `unar` or `unrar` on the machine (macOS: `brew install unar`).

Usage:
    python ingest/unpack.py                # every archive under data/raw
    python ingest/unpack.py --survey CHL_2022
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import zipfile
from pathlib import Path


def unpack_zip(archive: Path, dest: Path) -> list[Path]:
    out = []
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            name = Path(info.filename).name
            if info.is_dir() or not name or name.startswith("._") or "__MACOSX" in info.filename:
                continue
            target = dest / name
            if not target.exists() or target.stat().st_size != info.file_size:
                with z.open(info) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
            out.append(target)
    return out


def unpack_rar(archive: Path, dest: Path) -> list[Path]:
    before = set(dest.iterdir())
    if shutil.which("unar"):
        subprocess.run(["unar", "-force-overwrite", "-no-directory", "-output-directory", str(dest), str(archive)], check=True)
    elif shutil.which("unrar"):
        subprocess.run(["unrar", "e", "-o+", str(archive), str(dest) + "/"], check=True)
    else:
        raise RuntimeError(f"{archive.name} is a .rar file: install unar or unrar and run again")
    return sorted(set(dest.iterdir()) - before)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw-dir", default="data/raw")
    ap.add_argument("--survey", nargs="*")
    args = ap.parse_args()

    for survey_dir in sorted(Path(args.raw_dir).iterdir()):
        if not survey_dir.is_dir() or (args.survey and survey_dir.name not in args.survey):
            continue
        dest = survey_dir / "unpacked"
        for archive in sorted(survey_dir.glob("*")):
            suffix = archive.suffix.lower()
            if suffix not in (".zip", ".rar"):
                continue
            dest.mkdir(exist_ok=True)
            try:
                files = unpack_zip(archive, dest) if suffix == ".zip" else unpack_rar(archive, dest)
            except RuntimeError as err:
                print(f"SKIPPED  {err}")
                continue
            for f in files:
                print(f"{survey_dir.name}: {f.name} ({f.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
