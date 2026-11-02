#!/usr/bin/env python3
"""Generate conformance vectors from a language YAML via the reference engine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference import load_language, number_to_text, text_to_number  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "language",
        nargs="?",
        default="mizo",
        help="language id or path to YAML (default: mizo)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output JSON path (default: vectors/<id>-<min>-<max>.json)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify round-trip for every n; do not write unless -o given",
    )
    args = parser.parse_args(argv)

    spec = load_language(args.language)
    pairs = []
    for n in range(spec.min_value, spec.max_value + 1):
        text = number_to_text(n, spec)
        back = text_to_number(text, spec)
        if back != n:
            raise SystemExit(f"round-trip failed: {n} → {text!r} → {back}")
        pairs.append({"n": n, "text": text})

    payload = {
        "language": spec.language_id,
        "bcp47": spec.raw["language"]["bcp47"],
        "range": {"min": spec.min_value, "max": spec.max_value},
        "count": len(pairs),
        "vectors": pairs,
    }

    out = args.output
    if out is None and not args.check:
        out = (
            ROOT
            / "vectors"
            / f"{spec.language_id}-{spec.min_value}-{spec.max_value}.json"
        )

    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {out} ({len(pairs)} vectors)")
    else:
        print(f"ok: {len(pairs)} round-trips for {spec.language_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
