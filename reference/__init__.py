"""Reference numberwords engine: YAML lexicon + rules → number ↔ text."""

from .engine import (
    LanguageSpec,
    NumberwordsError,
    OutOfRangeError,
    ParseError,
    SpecError,
    load_language,
    number_to_text,
    text_to_number,
)

__all__ = [
    "LanguageSpec",
    "NumberwordsError",
    "OutOfRangeError",
    "ParseError",
    "SpecError",
    "load_language",
    "number_to_text",
    "text_to_number",
]

__version__ = "0.1.0"
