"""Packaged numberwords must pass the Mizo 0–100 conformance vectors."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from numberwords import (
    OutOfRangeError,
    load_language,
    number_to_text,
    text_to_number,
)

DATA = Path(__file__).resolve().parents[1] / "src" / "numberwords" / "data"
VECTORS = DATA / "vectors" / "mizo-0-100.json"


@pytest.fixture(scope="module")
def spec():
    return load_language("mizo")


@pytest.fixture(scope="module")
def vectors():
    data = json.loads(VECTORS.read_text(encoding="utf-8"))
    assert data["count"] == 101
    return data


def test_packaged_language_loads(spec):
    assert spec.language_id == "mizo"
    assert spec.min_value == 0
    assert spec.max_value == 100


def test_all_vectors(spec, vectors):
    for row in vectors["vectors"]:
        assert number_to_text(row["n"], spec) == row["text"]
        assert text_to_number(row["text"], spec) == row["n"]


def test_roundtrip_property(spec):
    for n in range(0, 101):
        assert text_to_number(number_to_text(n, spec), spec) == n


def test_aliases(spec):
    from numberwords import number_to_words, words_to_number

    assert number_to_words(11, spec) == "sawmpakhat"
    assert words_to_number("za", spec) == 100


def test_out_of_range(spec):
    with pytest.raises(OutOfRangeError):
        number_to_text(101, spec)
