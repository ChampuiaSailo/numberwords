"""numberwords — spec-driven number ↔ text (Mizo 0–100 first)."""

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
    "number_to_words",
    "words_to_number",
]

__version__ = "0.1.0"

# Friendly aliases matching the legacy mizo_numberwords API.
number_to_words = number_to_text
words_to_number = text_to_number
