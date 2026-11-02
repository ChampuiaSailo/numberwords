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
| [`packages/python/`](packages/python/) | Installable `numberwords` package (passes vectors) |
| `mizo_numberwords/` | Earlier wide-range converter (kept for reference) |

## Quick start

```bash
pip install -e "packages/python[dev]"

python3 -m numberwords to-words 42
# sawmli pahnih

python3 -m numberwords to-number sawmhnih pahnih
# 22

python3 -m reference roundtrip 100   # in-repo reference CLI
# 100 → za → 100

python3 scripts/generate_vectors.py mizo
python3 -m pytest tests packages/python/tests
```

After changing `languages/`, `spec/`, `vectors/`, or `reference/engine.py`, refresh the package copy:

```bash
python3 scripts/sync_python_package_data.py
```

## Status

- **Done (0–100 Mizo):** CLDR borrow note, JSON Schema, `languages/mizo.yaml`, reference engine, conformance vectors, round-trips, Python package.
- **Deferred:** extend range (hundreds, thousands, …) and add an npm target.
