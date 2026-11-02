"""
Spec-driven cardinal engine for the numberwords language-cardinal schema.

Implements number → text and text → number for the v1 rule patterns
(literal_scale, units_full, scale_full_concat, scale_stem_remainder).
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Union

import yaml

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - optional at runtime if pre-validated
    Draft202012Validator = None  # type: ignore[misc, assignment]


# Packaged data lives next to this module; monorepo checkout may also
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
DEFAULT_VECTORS = _PACKAGE_DATA / "vectors"


class NumberwordsError(ValueError):
    """Base error for the reference engine."""


class SpecError(NumberwordsError):
    """Language file failed to load or validate."""


class OutOfRangeError(NumberwordsError):
    """Integer outside the language file's declared range."""


class ParseError(NumberwordsError):
    """Phrase could not be parsed as a canonical (or accepted) cardinal."""


@dataclass(frozen=True)
class LanguageSpec:
    """Loaded, validated language cardinal slice."""

    raw: Mapping[str, Any]
    path: Optional[Path] = None

    @property
    def language_id(self) -> str:
        return str(self.raw["language"]["id"])

    @property
    def min_value(self) -> int:
        return int(self.raw["range"]["min"])

    @property
    def max_value(self) -> int:
        return int(self.raw["range"]["max"])

    @property
    def lexicon(self) -> Mapping[str, Any]:
        return self.raw["lexicon"]

    @property
    def rules(self) -> list[Mapping[str, Any]]:
        return list(self.raw["rules"])


def load_language(
    source: Union[str, Path, Mapping[str, Any]],
    *,
    schema_path: Union[str, Path, None] = None,
    validate: bool = True,
) -> LanguageSpec:
    """Load a language YAML/JSON mapping and optionally validate it."""
    path: Optional[Path] = None
    if isinstance(source, Mapping):
        data = dict(source)
    else:
        path = Path(source)
        if not path.is_file():
            candidate = DEFAULT_LANGUAGES / f"{source}.yaml"
            if candidate.is_file():
                path = candidate
            else:
                raise SpecError(f"language file not found: {source!r}")
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() in {".yaml", ".yml"}:
            data = yaml.safe_load(text)
        else:
            data = json.loads(text)
        if not isinstance(data, dict):
            raise SpecError(f"language root must be a mapping: {path}")

    if int(data["range"]["max"]) < int(data["range"]["min"]):
        raise SpecError("range.max must be >= range.min")

    bases = [int(rule["base"]) for rule in data["rules"]]
    if bases != sorted(bases, reverse=True):
        raise SpecError("rules must be listed in descending base order")

    if validate:
        _validate_against_schema(data, schema_path)

    return LanguageSpec(raw=data, path=path)


def _validate_against_schema(
    data: Mapping[str, Any],
    schema_path: Union[str, Path, None],
) -> None:
    if Draft202012Validator is None:
        raise SpecError(
            "jsonschema is required to validate language files; "
            "install jsonschema or pass validate=False"
        )
    path = Path(schema_path) if schema_path else DEFAULT_SCHEMA
    schema = json.loads(path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    if errors:
        first = errors[0]
        where = "/".join(str(p) for p in first.absolute_path) or "<root>"
        raise SpecError(f"schema validation failed at {where}: {first.message}")


def number_to_text(n: Union[int, str], spec: LanguageSpec) -> str:
    """Convert an integer in the language range to canonical cardinal text."""
    value = _coerce_int(n)
    if value < spec.min_value or value > spec.max_value:
        raise OutOfRangeError(
            f"number out of range: {value} "
            f"(allowed {spec.min_value}..{spec.max_value})"
        )
    if value == 0:
        return str(spec.lexicon["zero"])

    for rule in spec.rules:
        base = int(rule["base"])
        if value >= base:
            return _apply_pattern(value, rule["pattern"], spec.lexicon)

    raise SpecError(f"no rule matched value {value} in {spec.language_id}")


def text_to_number(text: str, spec: LanguageSpec) -> int:
    """Parse cardinal text into an int (accepts light orthographic variants)."""
    if not isinstance(text, str):
        raise ParseError(f"expected string, got {type(text).__name__}")

    normalized = _normalize_phrase(text)
    if not normalized:
        raise ParseError("empty input")

    zero = _normalize_token(str(spec.lexicon["zero"]))
    if normalized == zero or normalized == "zero":
        value = 0
    else:
        value = _parse_positive(normalized, spec)

    if value < spec.min_value or value > spec.max_value:
        raise OutOfRangeError(
            f"parsed value out of range: {value} "
            f"(allowed {spec.min_value}..{spec.max_value})"
        )
    return value


def _apply_pattern(
    value: int,
    pattern: Mapping[str, Any],
    lexicon: Mapping[str, Any],
) -> str:
    ptype = pattern["type"]

    if ptype == "literal_scale":
        scale = int(pattern["scale"])
        if value != scale:
            raise SpecError(
                f"literal_scale rule for {scale} cannot format {value}"
            )
        return _scale_form(lexicon, scale)

    if ptype == "units_full":
        if value < 1 or value > 9:
            raise SpecError(f"units_full cannot format {value}")
        return str(lexicon["units_full"][str(value)])

    if ptype == "scale_full_concat":
        scale = int(pattern["scale"])
        coeff, rem = divmod(value, scale)
        if coeff != 1 or rem < 1 or rem > 9:
            raise SpecError(f"scale_full_concat cannot format {value}")
        return _scale_form(lexicon, scale) + str(lexicon["units_full"][str(rem)])

    if ptype == "scale_stem_remainder":
        scale = int(pattern["scale"])
        coeff, rem = divmod(value, scale)
        if coeff < 2 or coeff > 9:
            raise SpecError(f"scale_stem_remainder cannot format {value}")
        if pattern.get("coefficient") != "stem":
            raise SpecError("only coefficient=stem is supported in v1")
        if pattern.get("scale_join") != "concat":
            raise SpecError("only scale_join=concat is supported in v1")
        head = _scale_form(lexicon, scale) + str(lexicon["stems"][str(coeff)])
        if rem == 0:
            return head
        rem_spec = pattern["remainder"]
        if rem_spec.get("form") != "units_full":
            raise SpecError("only remainder.form=units_full is supported in v1")
        unit = str(lexicon["units_full"][str(rem)])
        return head + str(rem_spec.get("separator", " ")) + unit

    raise SpecError(f"unsupported pattern type: {ptype!r}")


def _scale_form(lexicon: Mapping[str, Any], scale: int) -> str:
    key = str(scale)
    scales = lexicon["scales"]
    if key not in scales:
        raise SpecError(f"missing lexicon.scales[{key}]")
    return str(scales[key])


def _parse_positive(normalized: str, spec: LanguageSpec) -> int:
    """Greedy parse using the same morphology the emitter uses."""
    lex = spec.lexicon
    units_full = {_normalize_token(v): int(k) for k, v in lex["units_full"].items()}
    stems = {_normalize_token(v): int(k) for k, v in lex["stems"].items()}
    scales = {_normalize_token(v): int(k) for k, v in lex["scales"].items()}

    if normalized in units_full:
        return units_full[normalized]
    if normalized in scales:
        return scales[normalized]

    tokens = _tokenize(normalized, scales, stems, units_full)
    if not tokens:
        raise ParseError("empty input after normalization")

    total = 0
    i = 0
    n = len(tokens)
    while i < n:
        tok = tokens[i]

        if tok in units_full:
            if i != n - 1:
                raise ParseError(f"unexpected unit {tok!r} before end of phrase")
            total += units_full[tok]
            i += 1
            break

        matched = _match_scale_token(tok, scales, stems, units_full)
        if matched is None:
            raise ParseError(f"unrecognized token {tok!r}")

        scale, digit = matched
        # For scale==10: digit is 1 (bare), 2..9 (stem coeff), or 11..19 (teen).
        if scale == 10 and digit >= 11:
            total += digit
            i += 1
            if i < n and tokens[i] in units_full:
                raise ParseError("extra unit after teen form")
            continue

        total += digit * scale
        i += 1
        if scale == 10 and i < n and tokens[i] in units_full:
            total += units_full[tokens[i]]
            i += 1
            if i < n:
                raise ParseError("trailing tokens after units")
            break

    if i < n:
        raise ParseError(f"trailing unparsed tokens: {' '.join(tokens[i:])}")
    return total


def _tokenize(
    normalized: str,
    scales: Mapping[str, int],
    stems: Mapping[str, int],
    units_full: Mapping[str, int],
) -> list[str]:
    """Split and glue scale+stem / scale+full-unit pairs when written spaced."""
    raw = normalized.split()
    out: list[str] = []
    i = 0
    while i < len(raw):
        a = raw[i]
        if i + 1 < len(raw):
            b = raw[i + 1]
            glued = a + b
            if a in scales and b in units_full and scales[a] == 10:
                out.append(glued)
                i += 2
                continue
            if a in scales and b in stems:
                out.append(glued)
                i += 2
                continue
            if _match_scale_token(glued, scales, stems, units_full) is not None:
                out.append(glued)
                i += 2
                continue
        out.append(a)
        i += 1
    return out


def _match_scale_token(
    tok: str,
    scales: Mapping[str, int],
    stems: Mapping[str, int],
    units_full: Mapping[str, int],
) -> Optional[tuple[int, int]]:
    """Return (scale, digit) for a glued token.

    digit is the multiplier for ``total += digit * scale``, except teens
    (scale 10 with a glued full unit) which return absolute values 11..19.
    """
    for scale_form, scale in sorted(scales.items(), key=lambda kv: -len(kv[0])):
        if tok == scale_form:
            return scale, 1

        if not tok.startswith(scale_form):
            continue
        rest = tok[len(scale_form) :]
        if not rest:
            return scale, 1

        if rest in units_full and scale == 10:
            return scale, 10 + units_full[rest]

        if rest in stems:
            return scale, stems[rest]

        if rest == "khat":
            return scale, 1

    return None


_TONE_TRANS = str.maketrans(
    {
        "á": "a", "à": "a", "â": "a", "ä": "a", "ǎ": "a", "ȧ": "a", "ạ": "a", "ã": "a",
        "é": "e", "è": "e", "ê": "e", "ë": "e", "ě": "e", "ė": "e", "ẹ": "e",
        "í": "i", "ì": "i", "î": "i", "ï": "i", "ǐ": "i", "ị": "i", "ĩ": "i",
        "ó": "o", "ò": "o", "ô": "o", "ö": "o", "ǒ": "o", "ọ": "o",
        "ú": "u", "ù": "u", "û": "u", "ü": "u", "ǔ": "u", "ů": "u", "ụ": "u", "ũ": "u",
        "ṅ": "n", "ṭ": "t",
        "ü": "u", "ö": "o",
    }
)


def _strip_diacritics(s: str) -> str:
    s = s.translate(_TONE_TRANS)
    decomposed = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _normalize_token(s: str) -> str:
    return _strip_diacritics(s.strip().lower())


def _normalize_phrase(text: str) -> str:
    s = _normalize_token(text)
    # Optional linker "leh" (and) — accepted in input, not emitted.
    s = re.sub(r"\bleh\b", " ", s)
    s = re.sub(r"[‐‑‒–—―\-_/]+", " ", s)
    s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)
    s = re.sub(r"\s+", " ", s).strip()
    # CIIL typo / variant
    s = re.sub(r"\bpalnih\b", "pahnih", s)

    # Glue common teen/tens splits: "sawm pakhat" → try also as separate tokens;
    # keep spaces for compound tens ("sawmhnih pakhat"). Also accept
    # "sawm hnih" → glue to sawmhnih when second token is a known stem.
    return s


def _coerce_int(n: Union[int, str]) -> int:
    if isinstance(n, bool):
        raise OutOfRangeError("boolean is not a valid whole number")
    if isinstance(n, int):
        return n
    if isinstance(n, str):
        s = n.strip().replace("_", "").replace(",", "")
        if not s or not re.fullmatch(r"[+-]?\d+", s):
            raise OutOfRangeError(f"not an integer literal: {n!r}")
        return int(s)
    raise OutOfRangeError(f"unsupported number type: {type(n).__name__}")
