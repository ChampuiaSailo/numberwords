"""Small CLI for number ↔ Mizo words."""

from __future__ import annotations

import argparse
import sys

from .convert import (
    MAX,
    MIN,
    MizoNumberError,
    number_to_words,
    words_to_number,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mizo-numberwords",
        description=(
            "Convert whole numbers ↔ Mizo (Lushai) number words "
            f"({MIN} .. {MAX:,})."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_to = sub.add_parser("to-words", help="number → Mizo words")
    p_to.add_argument("number", help="integer, e.g. 42 or 9_999_999_999")

    p_from = sub.add_parser("to-number", help="Mizo words → number")
    p_from.add_argument(
        "words",
        nargs="+",
        help="Mizo phrase, e.g. sawmhnih pahnih",
    )

    p_rt = sub.add_parser(
        "roundtrip",
        help="print number → words → number (sanity check)",
    )
    p_rt.add_argument("number", help="integer to round-trip")

    args = parser.parse_args(argv)

    try:
        if args.command == "to-words":
            print(number_to_words(args.number))
        elif args.command == "to-number":
            print(words_to_number(" ".join(args.words)))
        elif args.command == "roundtrip":
            words = number_to_words(args.number)
            back = words_to_number(words)
            print(f"{args.number} → {words} → {back}")
            if int(str(args.number).replace("_", "").replace(",", "")) != back:
                return 2
        return 0
    except MizoNumberError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())