"""CLI: python -m numberwords to-words|to-number|roundtrip."""

from __future__ import annotations

import argparse
import sys

from .engine import NumberwordsError, load_language, number_to_text, text_to_number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="numberwords",
        description="Spec-driven number ↔ words (default language: mizo, 0–100).",
    )
    parser.add_argument(
        "-l",
        "--language",
        default="mizo",
        help="language id or YAML path (default: mizo)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_to = sub.add_parser("to-words", help="number → text")
    p_to.add_argument("number")

    p_from = sub.add_parser("to-number", help="text → number")
    p_from.add_argument("words", nargs="+")

    p_rt = sub.add_parser("roundtrip", help="number → text → number")
    p_rt.add_argument("number")

    args = parser.parse_args(argv)
    spec = load_language(args.language)

    try:
        if args.command == "to-words":
            print(number_to_text(args.number, spec))
        elif args.command == "to-number":
            print(text_to_number(" ".join(args.words), spec))
        elif args.command == "roundtrip":
            words = number_to_text(args.number, spec)
            back = text_to_number(words, spec)
            print(f"{args.number} → {words} → {back}")
            if int(str(args.number).replace("_", "").replace(",", "")) != back:
                return 2
        return 0
    except NumberwordsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
