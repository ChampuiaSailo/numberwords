# Language cardinal spec format (0–100)

This documents `spec/language-cardinal.schema.json` and how a language file such as `languages/mizo.yaml` is interpreted.

## File layout

| Path | Role |
|------|------|
| `spec/language-cardinal.schema.json` | JSON Schema (Draft 2020-12) for one language cardinal slice |
| `languages/<id>.yaml` | Locale data conforming to that schema |
| `vectors/<id>-<min>-<max>.json` | Generated conformance pairs `{n, text}` |

## Top-level object

- `schema_version` — semver string of this data shape (`"1.0.0"` for the 0–100 slice).
- `language` — `id`, `bcp47`, display `name`, optional `orthography` note.
- `range` — inclusive `{min, max}` integers the file claims to cover.
- `sources` — bibliography used to verify forms (required, ≥1).
- `lexicon` — atomic strings the rules compose.
- `rules` — ordered list; engine selects the **greatest** `base` ≤ current value (RBNF-style).

## Lexicon

- `zero` — spelling for 0 (outside the unit table).
- `units_full` — map `"1"`…`"9"` → standalone cardinals (Mizo `pakhat`…).
- `stems` — map `"1"`…`"9"` → bound multipliers after a scale (Mizo `khat`…).
- `scales` — map decimal scale value as string (`"10"`, `"100"`, …) → scale morpheme (`sawm`, `za`).

Keys are decimal strings so JSON/YAML objects stay JSON-Schema-friendly.

## Rules

Each rule:

```yaml
- base: 20
  pattern:
    type: scale_stem_remainder
    scale: 10
    coefficient: stem
    scale_join: concat
    remainder:
      form: units_full
      separator: " "
```

Supported `pattern.type` values for v1 (0–100):

| Type | Meaning |
|------|---------|
| `literal_scale` | Emit `lexicon.scales[scale]` with no coefficient (e.g. 10 → `sawm`, 100 → `za`). |
| `units_full` | Emit `lexicon.units_full[n]` for n in 1…9. |
| `scale_full_concat` | Teens-style: `scales[scale]` + `units_full[remainder]` with no separator (11 → `sawmpakhat`). |
| `scale_stem_remainder` | Tens band: `scales[scale]` + `stems[coeff]` (`concat`), then optional remainder via `units_full` and `separator`. |

Rules must be listed in **descending `base`**. The engine walks them in order and applies the first whose `base` ≤ value.

## Canonical text

- Emission uses lexicon strings exactly (no extra spaces, no optional linker).
- Parsing (later packages) may accept documented variants; vectors record **canonical** spellings only.

## Validation

Language YAML must validate against the JSON Schema before vectors are accepted. The reference engine rejects files whose `range` is not covered by the rule set (every integer in range must be producible).
