# numberwords

Spec-driven number ↔ words conversion, starting with **Mizo (Lushai)** for integers **0–100**.

The legacy ad-hoc package under `mizo_numberwords/` still covers a wider range; new work is **YAML lexicon + JSON Schema + conformance vectors**, with portable engines/packages consuming that data.

## Layout

| Path | Role |
|------|------|
| [`docs/cldr-rbnf-borrow.md`](docs/cldr-rbnf-borrow.md) | What we borrow from Unicode CLDR RBNF |
| [`docs/spec-format.md`](docs/spec-format.md) | Language cardinal YAML format (0–100) |
| [`spec/language-cardinal.schema.json`](spec/language-cardinal.schema.json) | JSON Schema for language files |
| [`languages/mizo.yaml`](languages/mizo.yaml) | Mizo lexicon + rules for 0–100 |
| [`vectors/mizo-0-100.json`](vectors/mizo-0-100.json) | 101 conformance pairs `{n, text}` |
| [`reference/`](reference/) | Spec-driven reference engine (`number → text`, `text → number`) |
| `packages/python/` | Installable Python package (follow-up) |
| `mizo_numberwords/` | Earlier wide-range converter (kept for reference) |

## Quick start (reference engine)

```bash
pip install pyyaml jsonschema   # schema validation on load
python -m reference to-words 42
# sawmli pahnih

python -m reference to-number sawmhnih pahnih
# 22

python -m reference roundtrip 100
# 100 → za → 100

python scripts/generate_vectors.py mizo
pytest tests/test_reference_engine.py
```

## Status

- **Done:** CLDR borrow note, schema, Mizo 0–100 YAML, reference engine, vectors, round-trip tests.
- **Follow-ups:** installable Python package; later hundreds/thousands and npm.
