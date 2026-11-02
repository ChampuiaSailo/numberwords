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
| `vectors/` | Generated conformance pairs (engine PR) |
| `reference/` | Reference engine (engine PR) |
| `packages/python/` | First target package (package PR) |
| `mizo_numberwords/` | Earlier wide-range converter (kept for reference) |

## Quick check (legacy CLI)

```bash
python main.py to-words 42
# sawmli pahnih
```

## Status

- **Done in data/spec:** CLDR borrow note, schema, Mizo 0–100 YAML with sources.
- **Follow-ups:** reference engine + vectors, Python package passing vectors; later hundreds/thousands and npm.
