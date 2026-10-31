"""
Mizo (Lushai) cardinal number ↔ words for integers 0 .. 9_999_999_999.

Canonical emission uses everyday unmarked Latin orthography. Parsing accepts
whitespace/hyphen variants, optional linker *leh*, common final -h on nuai/
maktaduai, tone diacritics, and a few documented alternate spellings.
"""

from __future__ import annotations

import re
import unicodedata
from typing import List, Optional, Sequence, Tuple, Union

MIN = 0
MAX = 9_999_999_999

UNITS_FULL = {
    1: "pakhat",
    2: "pahnih",
    3: "pathum",
    4: "pali",
    5: "panga",
    6: "paruk",
    7: "pasarih",
    8: "pariat",
    9: "pakua",
}

STEMS = {
    1: "khat",
    2: "hnih",
    3: "thum",
    4: "li",
    5: "nga",
    6: "ruk",
    7: "sarih",
    8: "riat",
    9: "kua",
}

FULL_TO_DIGIT = {v: k for k, v in UNITS_FULL.items()}
STEM_TO_DIGIT = {v: k for k, v in STEMS.items()}

SCALES: Sequence[Tuple[int, str, bool]] = (
    (1_000_000_000, "tluklehdingawn", False),
    (100_000_000, "vaibelchhetak", False),
    (10_000_000, "vaibelchhia", False),
    (1_000_000, "maktaduai", False),
    (100_000, "nuai", True),
    (10_000, "sing", True),
    (1_000, "sang", True),
    (100, "za", False),
    (10, "sawm", False),
)


class MizoNumberError(ValueError):
    """Base error for Mizo number conversion."""


class OutOfRangeError(MizoNumberError):
    """Integer outside 0 .. 9_999_999_999 or non-integer numeric input."""


class ParseError(MizoNumberError):
    """Word phrase could not be parsed as a Mizo cardinal in range."""


def number_to_words(n: Union[int, float, str]) -> str:
    """Convert a whole number in [0, 9_999_999_999] to Mizo words."""
    value = _coerce_int(n)
    if value < MIN or value > MAX:
        raise OutOfRangeError(
            f"number out of range: {value} (allowed {MIN}..{MAX})"
        )
    if value == 0:
        return "bial"

    parts: List[str] = []
    remaining = value

    for scale, name, use_khat in SCALES:
        digit = remaining // scale
        remaining %= scale
        if digit == 0:
            continue

        if scale == 10:
            if digit == 1 and remaining > 0:
                parts.append("sawm" + UNITS_FULL[remaining])
                remaining = 0
            elif digit == 1:
                parts.append("sawm")
            else:
                parts.append("sawm" + STEMS[digit])
            continue

        if digit == 1:
            if use_khat:
                parts.append(name + "khat")
            else:
                parts.append(name)
        else:
            parts.append(name + STEMS[digit])

    if remaining > 0:
        parts.append(UNITS_FULL[remaining])

    return " ".join(parts)


def words_to_number(text: str) -> int:
    """Parse a Mizo cardinal phrase into an int in [0, 9_999_999_999]."""
    if not isinstance(text, str):
        raise ParseError(f"expected string, got {type(text).__name__}")

    normalized = _normalize_phrase(text)
    if not normalized:
        raise ParseError("empty input")

    if normalized in {"bial", "zero"}:
        return 0

    tokens = _tokenize(normalized)
    if not tokens:
        raise ParseError("empty input after normalization")

    total = 0
    used_scales: set[int] = set()
    i = 0
    n = len(tokens)

    while i < n:
        tok = tokens[i]

        if tok in FULL_TO_DIGIT:
            if i != n - 1:
                raise ParseError(
                    f"unexpected unit {tok!r} before end of phrase"
                )
            total += FULL_TO_DIGIT[tok]
            i += 1
            break

        matched = _match_scale_token(tok)
        if matched is None:
            raise ParseError(f"unrecognized token {tok!r}")

        scale, digit = matched
        if scale in used_scales:
            raise ParseError(f"duplicate scale for {scale}")
        if used_scales and scale >= min(used_scales):
            raise ParseError(
                f"scales out of order near {tok!r} (expected descending)"
            )
        used_scales.add(scale)

        if scale == 10 and digit >= 11:
            total += digit
            i += 1
            if i < n and tokens[i] in FULL_TO_DIGIT:
                raise ParseError("extra unit after teen form")
            continue

        total += digit * scale
        i += 1

        if scale == 10 and i < n and tokens[i] in FULL_TO_DIGIT:
            total += FULL_TO_DIGIT[tokens[i]]
            i += 1
            if i < n:
                raise ParseError("trailing tokens after units")
            break

    if i < n:
        raise ParseError(f"trailing unparsed tokens: {' '.join(tokens[i:])}")

    if total < MIN or total > MAX:
        raise OutOfRangeError(
            f"parsed value out of range: {total} (allowed {MIN}..{MAX})"
        )
    return total


def _coerce_int(n: Union[int, float, str]) -> int:
    if isinstance(n, bool):
        raise OutOfRangeError("boolean is not a valid whole number")
    if isinstance(n, int):
        return n
    if isinstance(n, float):
        if not n.is_integer():
            raise OutOfRangeError(f"non-integer number: {n}")
        return int(n)
    if isinstance(n, str):
        s = n.strip().replace("_", "").replace(",", "")
        if not s or not re.fullmatch(r"[+-]?\d+", s):
            raise OutOfRangeError(f"not an integer literal: {n!r}")
        return int(s)
    raise OutOfRangeError(f"unsupported number type: {type(n).__name__}")


_TONE_TRANS = str.maketrans(
    {
        "á": "a", "à": "a", "â": "a", "ä": "a", "ǎ": "a", "ȧ": "a", "ạ": "a", "ã": "a",
        "é": "e", "è": "e", "ê": "e", "ë": "e", "ě": "e", "ė": "e", "ẹ": "e",
        "í": "i", "ì": "i", "î": "i", "ï": "i", "ǐ": "i", "ị": "i", "ĩ": "i",
        "ó": "o", "ò": "o", "ô": "o", "ö": "o", "ǒ": "o", "ọ": "o",
        "ú": "u", "ù": "u", "û": "u", "ü": "u", "ǔ": "u", "ů": "u", "ụ": "u", "ũ": "u",
        "ṅ": "n", "ṭ": "t",
    }
)


def _strip_diacritics(s: str) -> str:
    s = s.translate(_TONE_TRANS)
    decomposed = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _normalize_phrase(text: str) -> str:
    s = text.strip().lower()
    s = _strip_diacritics(s)
    s = re.sub(r"\btluk\s+leh\s+dingawn\b", "tluklehdingawn", s)
    s = re.sub(r"\bleh\b", " ", s)
    s = re.sub(r"[‐‑‒–—―\-_/]+", " ", s)
    s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\bpalnih\b", "pahnih", s)
    return s


def _tokenize(normalized: str) -> List[str]:
    raw = normalized.split()
    out: List[str] = []
    i = 0
    while i < len(raw):
        a = raw[i]
        if i + 1 < len(raw):
            b = raw[i + 1]
            glued = a + b
            if b == "khat" and _match_scale_token(a + "khat") is not None:
                out.append(a + "khat")
                i += 2
                continue
            if a == "sawm" and b in FULL_TO_DIGIT:
                out.append("sawm" + b)
                i += 2
                continue
            if _match_scale_token(glued) is not None:
                out.append(glued)
                i += 2
                continue
            if a in {"vaibelchhe", "vaibelchhia"} and b == "khat":
                out.append("vaibelchhetak" if a == "vaibelchhe" else "vaibelchhiakhat")
                i += 2
                continue
            if a == "vaibelchhe" and b in STEM_TO_DIGIT:
                out.append("vaibelchhetak" + b)
                i += 2
                continue
        if a in {"nuaih", "maktaduaih"}:
            a = a[:-1]
        out.append(a)
        i += 1
    return out


def _match_scale_token(tok: str) -> Optional[Tuple[int, int]]:
    variants = [tok]
    if tok.startswith("nuaih"):
        variants.append("nuai" + tok[5:])
    if tok.startswith("maktaduaih"):
        variants.append("maktaduai" + tok[10:])

    for candidate in variants:
        if candidate.startswith("sawm"):
            rest = candidate[4:]
            if rest == "":
                return 10, 1
            if rest in FULL_TO_DIGIT:
                return 10, 10 + FULL_TO_DIGIT[rest]
            if rest in STEM_TO_DIGIT:
                return 10, STEM_TO_DIGIT[rest]
            if rest == "khat":
                return 10, 1

        for scale, name, _use_khat in SCALES:
            if scale == 10:
                continue
            if candidate == name or candidate == name + "khat":
                return scale, 1
            if candidate.startswith(name):
                rest = candidate[len(name):]
                if rest in STEM_TO_DIGIT:
                    return scale, STEM_TO_DIGIT[rest]
                if rest == "khat":
                    return scale, 1
    return None