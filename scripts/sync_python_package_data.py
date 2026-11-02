#!/usr/bin/env python3
"""Copy canonical spec/engine/vectors into packages/python packaged data."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "packages" / "python" / "src" / "numberwords"
DATA = PKG / "data"


def main() -> int:
    mapping = [
        (ROOT / "reference" / "engine.py", PKG / "engine.py"),
        (ROOT / "languages" / "mizo.yaml", DATA / "languages" / "mizo.yaml"),
        (
            ROOT / "spec" / "language-cardinal.schema.json",
            DATA / "spec" / "language-cardinal.schema.json",
        ),
        (
            ROOT / "vectors" / "mizo-0-100.json",
            DATA / "vectors" / "mizo-0-100.json",
        ),
    ]
    for src, dest in mapping:
        if not src.is_file():
            print(f"missing source: {src}", file=sys.stderr)
            return 1
        dest.parent.mkdir(parents=True, exist_ok=True)
        text = src.read_text(encoding="utf-8")
        if src.name == "engine.py":
            text = _adapt_engine_paths(text)
        dest.write_text(text, encoding="utf-8")
        print(f"synced {src.relative_to(ROOT)} → {dest.relative_to(ROOT)}")
    return 0


def _adapt_engine_paths(text: str) -> str:
    """Rewrite reference path constants for the packaged module layout."""
    old = '''REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = REPO_ROOT / "spec" / "language-cardinal.schema.json"
DEFAULT_LANGUAGES = REPO_ROOT / "languages"'''
    new = '''# Packaged data lives next to this module; monorepo checkout may also
# expose the same files at the repository root.
_PACKAGE_DATA = Path(__file__).resolve().parent / "data"
_REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SCHEMA = (
    _PACKAGE_DATA / "spec" / "language-cardinal.schema.json"
    if (_PACKAGE_DATA / "spec" / "language-cardinal.schema.json").is_file()
    else _REPO_ROOT / "spec" / "language-cardinal.schema.json"
)
DEFAULT_LANGUAGES = (
    _PACKAGE_DATA / "languages"
    if (_PACKAGE_DATA / "languages").is_dir()
    else _REPO_ROOT / "languages"
)
DEFAULT_VECTORS = _PACKAGE_DATA / "vectors"'''
    if old not in text:
        raise SystemExit("engine.py path block not found; sync script needs update")
    return text.replace(old, new, 1)


if __name__ == "__main__":
    raise SystemExit(main())
