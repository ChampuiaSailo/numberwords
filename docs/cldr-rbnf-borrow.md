# What numberwords borrows from CLDR RBNF

Short design note for the first (0–100) slice of numberwords. Sources are cited at the end.

## What CLDR RBNF is

Unicode CLDR’s **Rule-Based Number Formatting (RBNF)** is the LDML mechanism for mapping numbers to spelled-out (and related) text. Rules live in groupings such as `SpelloutRules`, `OrdinalRules`, and `NumberingSystemRules`. Each public or private ruleset is an ordered list of base-value rules; the engine picks the greatest base ≤ the current value and may recurse via substitutions.

ICU’s RBNF (the runtime CLDR targets) adds the familiar substitution vocabulary:

| Token | Role (normal rule) |
|------:|--------------------|
| `<<`  | format the quotient after dividing by the rule’s divisor |
| `>>`  | format the remainder |
| `[…]` | omit bracketed text when the value is an exact multiple of the divisor |

Example shape (English spellout sketch from UTS #35): literal digit rules, then `20: twenty[->>];`, then `100: << hundred[ >>];`, then thousands/millions with the same quotient/remainder idea.

## Ideas we adopt

1. **Locale-scoped spellout data, not hard-coded converters**  
   Language forms live in data files (`languages/*.yaml`), validated by a schema — the same separation CLDR keeps between locale XML and the RBNF engine.

2. **Ordered base-value rules**  
   Composition is driven by descending bases (100 → tens band → teens → 10 → units), mirroring RBNF’s “greatest applicable base” selection instead of a flat 0…N lookup table alone.

3. **Quotient / remainder recursion**  
   Scales (e.g. Mizo `sawm` = 10, `za` = 100) combine a coefficient (or bare scale for 1) with an optional remainder, the same conceptual split as `<<` / `>>`.

4. **Optional remainder text**  
   Like RBNF `[…]`, remainder material is omitted on exact multiples (`sawmhnih`, not `sawmhnih` + empty unit).

5. **Bidirectional intent**  
   ICU RBNF formats *and* parses. numberwords requires `number → text` and `text → number` with round-trip vectors as the contract across packages.

6. **Public vs private structure**  
   Lexicon (literals, stems, scale forms) is the private building material; named composition rules are the public spellout surface — analogous to private vs public rulesets.

## Ideas we deliberately do *not* copy (yet)

- Full ICU RBNF string syntax (`<<`, `>>`, `%ruleset`, plural `$(…)$`) as the authoring format — YAML + JSON Schema is easier to validate and generate vectors from for a small range.
- Gendered/cased spellout variants and ordinals — out of scope for Mizo 0–100 cardinals.
- Algorithmic non-decimal numbering systems (Roman, etc.).
- Shipping inside CLDR XML; we keep a project-native schema under `spec/`.

## Spec-format stance for 0–100

The first schema (`spec/language-cardinal.schema.json`) formalises:

- language metadata + inclusive integer range  
- lexicon (zero, unit full forms, stems, scale words)  
- ordered composition rules with explicit join/remainder policies  
- cited sources on the language file  

Conformance vectors under `vectors/` are the portable oracle; engines and language packages must match them.

## Sources

- [UTS #35 / LDML Part 3: Numbers — § Rule-Based Number Formatting](https://unicode.org/reports/tr35/tr35-numbers.html#Rule-Based_Number_Formatting)
- [ICU User Guide — RuleBasedNumberFormat](https://unicode-org.github.io/icu/userguide/format_parse/numbers/rbnf.html)
- [CLDR numbering systems overview](https://cldr.unicode.org/index/cldr-spec/numbering) (algorithmic systems point at RBNF rulesets)
