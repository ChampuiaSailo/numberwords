# numberwords (Python)

Installable Python package for spec-driven **number ↔ text** conversion.

First language slice: **Mizo (Lushai), integers 0–100**, driven by packaged copies of:

- `languages/mizo.yaml`
- `spec/language-cardinal.schema.json`
- `vectors/mizo-0-100.json`

## Install

From this directory (editable, recommended in the monorepo):

```bash
pip install -e ".[dev]"
```

## Usage

```python
from numberwords import load_language, number_to_text, text_to_number

spec = load_language("mizo")
number_to_text(42, spec)           # 'sawmli pahnih'
text_to_number("sawmhnih pahnih", spec)  # 22
```

CLI:

```bash
numberwords to-words 42
numberwords to-number sawmli pahnih
numberwords roundtrip 100
```

## Tests

```bash
pytest
```

Tests assert the packaged engine matches `data/vectors/mizo-0-100.json` and that every value round-trips.

## Scope

- **In:** 0–100 Mizo cardinals, bidirectional API, vector conformance.
- **Later:** hundreds/thousands+, additional languages, npm package.
