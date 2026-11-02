"""Conformance and round-trip tests for the reference engine (Mizo 0–100)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference import (  # noqa: E402
    OutOfRangeError,
    ParseError,
    load_language,
    number_to_text,
    text_to_number,
)

VECTORS = ROOT / "vectors" / "mizo-0-100.json"


@pytest.fixture(scope="module")
def spec():
    return load_language("mizo")


@pytest.fixture(scope="module")
def vectors():
    assert VECTORS.is_file(), f"missing vectors file: {VECTORS}"
    data = json.loads(VECTORS.read_text(encoding="utf-8"))
    assert data["language"] == "mizo"
    assert data["range"] == {"min": 0, "max": 100}
    assert data["count"] == 101
    return data["vectors"]


def test_schema_load(spec):
    assert spec.language_id == "mizo"
    assert spec.min_value == 0
    assert spec.max_value == 100


@pytest.mark.parametrize(
    "n,text",
    [
        (0, "bial"),
        (1, "pakhat"),
        (10, "sawm"),
        (11, "sawmpakhat"),
        (19, "sawmpakua"),
        (20, "sawmhnih"),
        (21, "sawmhnih pakhat"),
        (42, "sawmli pahnih"),
        (100, "za"),
    ],
)
def test_spot_number_to_text(spec, n, text):
    assert number_to_text(n, spec) == text


def test_vectors_match_engine(spec, vectors):
    for row in vectors:
        assert number_to_text(row["n"], spec) == row["text"]


def test_roundtrip_all(spec):
    for n in range(spec.min_value, spec.max_value + 1):
        text = number_to_text(n, spec)
        assert text_to_number(text, spec) == n


def test_vectors_roundtrip(spec, vectors):
    for row in vectors:
        assert text_to_number(row["text"], spec) == row["n"]


@pytest.mark.parametrize(
    "phrase,expected",
    [
        ("sàwmpakhat", 11),
        ("sawm-pakhat", 11),
        ("sawm pakhat", 11),
        ("sawm leh pakhat", 11),
        ("sawm hnih", 20),
        ("sawmhnih pahnih", 22),
        ("SAWMLI PAHNIH", 42),
        ("palnih", 2),  # CIIL variant
        ("zà", 100),
    ],
)
def test_parse_variants(spec, phrase, expected):
    assert text_to_number(phrase, spec) == expected


def test_out_of_range(spec):
    with pytest.raises(OutOfRangeError):
        number_to_text(101, spec)
    with pytest.raises(OutOfRangeError):
        number_to_text(-1, spec)


def test_parse_error(spec):
    with pytest.raises(ParseError):
        text_to_number("not-a-number", spec)


def test_agrees_with_legacy_0_100():
    """Stay aligned with the existing ad-hoc converter on the shared range."""
    from mizo_numberwords import number_to_words

    spec = load_language("mizo")
    for n in range(0, 101):
        assert number_to_text(n, spec) == number_to_words(n)
