# Sanskrit conjugation engine audit (current state)

This file summarizes what’s missing/incomplete in the current verb-conjugation engine under `logic_handler/conjugation/grammar/`, what rules appear partial or absent (Paninian / Whitney / general grammar), where hardcoding or risky practices show up, and a suggested roadmap.

Scope note: this is a *code audit* based on the current implementation (not a philological proof). Where I reference “missing rules”, it means “not represented in the code paths I could find”, not “doesn’t exist in Sanskrit”.

## What’s missing (why it’s not yet a complete verb conjugator)

### Coverage of the conjugation space
- **Not all lakāras / tense-mood systems are implemented**.
  - Implemented (as named in code): `present`, `imperfect`, `imperative`, `optative`, `future`, `conditional`, `perfect`, `periphrastic_future`, `aorist`, `injunctive`, `benedictive`, `subjunctive` (see `grammar/conjugate.py`, `_ending_dispatch` and `grammar/stem_rules.py`, `tense_dispatch`).
  - Missing/unclear in code:
    - **Pluperfect** (luṅ? / classical “past perfect” usage), **future perfect**, **conditional perfect**, etc. (not present in `tense_dispatch` / `_ending_dispatch`).
    - **Periphrastic perfect** exists, but selection logic is simplified (see below).
    - **Comprehensive Vedic-only systems** are only partially represented (subjunctive exists, but many Vedic alternations are not).
- **Pada selection and root-wise voice restrictions are not fully modeled**.
  - Example: “ātmanepada-only roots” exist in test description, but in the engine there isn’t a robust “pada governance” layer that blocks/redirects illegal parasma/ātman forms per root and tense (beyond the passive/tenses impossibility check in `conjugate.py`).
- **Derivative system is incomplete**.
  - Supported derivatives in API: `causative`, `desiderative`, `intensive`, `denominative` (see `feature_resolver.py`, docstring in `conjugate.py`).
  - Missing (commonly expected in a “complete engine”):
    - **Frequentatives** (yaṅ-luk / intensive variants), **nic + san stacking**, **passive causative varieties**, multiple sanādi chains.
    - **Classical secondary derivations** (e.g. desiderative + causative, etc.), if desired.
- **Kṛdantas are only a partial subsystem**.
  - `grammar/krdantas.py` produces a “block” containing a handful of participles/indeclinables, but it is:
    - incomplete in inventory (many participles and suffix families are missing),
    - heavily dependent on `krdanta_overrides` for suppletives,
    - not integrated as a first-class morphological system with consistent stem derivation rules.

### Phonology / sandhi completeness
- **Sandhi is implemented as internal morpheme-boundary rewrite rules**, but it is not a full sandhi engine:
  - limited vowel sandhi set (`thematic_merger`, `savarna`, `guna_sandhi`, `ayadi`, `yan_sandhi`, plus a class-9 special).
  - limited consonant sandhi set (some Bartholomae, Grassmann-ish rewrite, devoicing, retroflexion, anusvāra/parasavarṇa, a few specific retro rules, RUKI, nati, and final visarga).
  - **External sandhi** is not a target here, but even for internal sandhi there are many missing cluster rules and conditioned alternations.
- **Tag-driven phonology is limited**.
  - The engine uses abstract tags like `[PASSIVE]`, `[CLASS4]`, `[ROOT_AORIST]`, `[AORIST_PASS_3SG]`, `[INTENSIVE_ACTIVE]` and then erases them in `MorphologyEngine`. This is a good pattern, but the set of tags and the rules that interpret them are currently small relative to what’s needed.

### Lexicon + morphology integration gaps
- `dhatupatha_analyzer.py` provides Aniṭ/Veṭ and an aorist-type guess from a CSV, but:
  - **aorist classification** is simplified to a small set and uses heuristics (`_raw_aorist_type`), not a fuller Paninian derivation pipeline.
  - **periphrastic perfect detection** is simplified to “root-initial long vowel” + some flags (`takes_periphrastic_perfect`) and class/derivative checks in `feature_resolver.py`.
  - other lexically-governed features (pada, it-augments, nasal-infix behaviors, root alternations) are not fully centralized in `RootObject`.

## Rules that appear incomplete or missing (Paninian / Whitney / general grammar)

This section is “what the code currently covers” vs “what appears absent”.

### Present system (classes 1–10)
Implemented at a high level:
- `StemBuilder` has per-class stem constructors for classes 1–10 in `stem_rules.py`.
- Endings are table-driven in `endings.py` with thematic/athematic branching.

Likely incomplete/missing:
- **A much broader set of class-specific stem alternations** (root-specific strengthening/weakening patterns, guṇa blocking, samprasāraṇa in additional environments, special class-2 and class-3 internal alternations beyond the few irregulars).
- **Systematic pada governance** (which roots take which endings in which tense/mood) and constraints by class/meaning.
- **More complete nati / ṣatva / retroflexion interactions** (some are present, but the coverage is not comprehensive).

### Passive (present-system passive in -ya-)
Implemented:
- Passive stem builder uses `_build_passive` and optional samprasāraṇa for a small whitelist (`_SAMPRASARANA_ROOTS`) in `stem_rules.py`.
- Some passive vowel handling is in `morphology.py` via `[PASSIVE]` tag mapping for i/u/ṛ/ṝ.
- Several passive stems are forced via `passive_stem_overrides` in `irregulars.py`.

Likely incomplete/missing:
- **Full passive formation rules across all root types**, especially:
  - handling of ṛ-roots and other vocalic alternations beyond the current simplistic `("ṛ[PASSIVE]" -> "ri")` mapping,
  - broader samprasāraṇa coverage beyond a small whitelist,
  - interaction of passive with class-markers and derived stems (more than the current special cases).

### Future system (simple + periphrastic future)
Implemented:
- Simple future/conditional via `_build_future_system` (mostly guṇa + `+iṣya` or `+sya`), with Aniṭ/Veṭ from dhātupāṭha + overrides in `future_stem_overrides`.
- Periphrastic future via `_build_periphrastic_future_system` with `periphrastic_stem_overrides`.

Likely incomplete/missing:
- **iṭ/īṭ augment behavior** and broader seṭ/aniṭ conditioning beyond the current approach.
- A more principled **tā/tṛ/ās** handling by stem class and phonology (currently done in endings tables and stem building, but coverage is thin).

### Perfect system
Implemented:
- A reduplication engine (`reduplication.py`) with a few Paninian-style reductions as FST rewrites.
- Perfect stem formation in `StemBuilder._build_perfect_system` including:
  - strong vs weak handling,
  - some vowel shortening for weak,
  - special-case irregular stems (`perfect_stem_overrides`) and reduplication prefix overrides (`perfect_redupe_overrides`).

Likely incomplete/missing:
- **Systematic perfect weak/strong alternations** for many root phonology types.
- **More complete handling of perfect of derived bases** (desiderative perfect was added, but intensive perfect and others are not systematically derived).
- **Broader set of perfect sandhi/phonology** (e.g. internal vowel and consonant changes that depend on endings).

### Aorist / injunctive system
Implemented:
- Aorist type detection (heuristic + overrides) and stem construction for types `s`, `is`, `sa`, `a`, `reduplicated`, `root`.
- Ending tables for active/middle/passive aorist.
- Special tag for passive aorist 3sg and a Vr̥ddhi trigger in `morphology.py`.

Likely incomplete/missing:
- A much broader inventory of aorist subtypes and root-wise selection rules.
- Systematic treatment of injunctive (right now it largely reuses aorist machinery; additionally there is a benchmark-driven augmentation quirk in `feature_resolver.py` for 1sg active injunctive).

### Benedictive / subjunctive
Implemented in a minimal way (stem building + ending tables).

Likely incomplete:
- Many root-conditioned alternations and historic/Vedic-only patterns are not represented.

### Intensive (yaṅ)
Implemented:
- `ReduplicationEngine.generate_intensive_prefix()` exists.
- `StemBuilder._build_intensive()` exists and supports “middle” (adds `+ya`) and “active” (athematic-ish, uses `[INTENSIVE_ACTIVE]` tag).
- `intensive_stem_overrides` exists and is already used as a large escape hatch.

Likely incomplete/missing:
- The intensive system is one of the biggest remaining accuracy gaps in `test.py` when `use_db=False`.
- It needs a more complete rule set for:
  - choosing the right base (often not simple “prefix + root”),
  - active vs middle stem shapes,
  - connecting-vowel behavior and interaction with endings.

## Hardcoded behavior / ill-advised practices observed

### Heavy reliance on overrides (irregular tables)
`grammar/irregulars.py` contains many override dictionaries:
- class-level present stems (`class_1_irregulars`, `class_2_irregulars`, `class_3_irregulars`, `class_5_irregulars`)
- passive stem overrides
- causative stem irregulars
- perfect reduplication overrides and perfect stem overrides
- aorist overrides
- future/periphrastic-future overrides
- desiderative/intensive overrides
- kṛdanta overrides

This is not “wrong” for Sanskrit, but it becomes ill-advised when:
- an override is used where a productive rule exists and could be encoded once,
- a growing override list becomes the main mechanism of correctness,
- overrides are added to match a single dataset without clarifying their grammatical status.

### Benchmark-driven special casing inside core logic
Examples:
- `feature_resolver.py` includes a special rule:
  - injunctive `1sg active` gets augment “because roots.csv stores some cells that way”.
  - This is a dataset-normalization concern, not a grammar rule, and ideally should live in the benchmark harness normalization layer (or be gated behind a “compatibility mode”).

### Mixing of concerns: generation vs validation vs fallback
The codebase includes an INRIA lookup mechanism (`inria_lookup.py`) and `use_db` flag in `conjugate.py`.
- This is valuable as a *runtime* fallback and cross-check.
- However, it can easily leak into “testing correctness” if not carefully isolated.
- Recommended practice: keep benchmarks always `use_db=False`, and keep fallback strictly opt-in at runtime.

### Sandhi and morphology rules are partially ad-hoc
Sandhi/morphology are expressed as rewrite transducers (good), but:
- several rules are “single example motivated” (e.g. `d+dh -> ddh` to enable `addhi`),
- ordering assumptions are fragile (a common issue in rewrite pipelines).

### Limited explicit citation of sources in-code
Some docstrings cite Whitney sections (e.g. desiderative future: “Whitney 1032”, perfect discussion sections), but many special behaviors and overrides lack explicit citations.
Given your guideline (“Add sources like Whitney 129.b when used”), this is an area to improve.

### Data/lexicon heuristics that may not scale
`dhatupatha_analyzer.py`:
- `_raw_aorist_type` is a heuristic mapping from anubandhas/phonology to only a few aorist types.
- `_find_raw` uses string prefix stripping and fallbacks “any class match”.
This is pragmatic, but a “complete” engine will likely need:
- better indexing,
- a more faithful extraction of it-markers and derived properties,
- clearer separation of “lexicon truth” vs “fallback heuristics”.

## Next steps to move toward a complete engine (recommended roadmap)

### 1) Define the target spec and scope
- Decide whether “complete” means:
  - classical Sanskrit only, or include Vedic systems (subjunctive/injunctive behavior etc.),
  - which derivatives are in-scope,
  - whether external sandhi and accent are in-scope.

### 2) Separate three layers cleanly
- **(A) Grammar generator**: produces forms from rules (no dataset fallbacks).
- **(B) Lexicon layer**: root properties (pada, seṭ/aniṭ/veṭ, aorist type, periphrastic perfect flags, irregular stems).
- **(C) Compatibility/normalization**: dataset-specific quirks (e.g. how `roots.csv` encodes particular cells, visarga normalization, homonym markers).

### 3) Systematically close the biggest rule gaps first
Based on current benchmark failure clustering (`test.py` in pure-rule mode):
- **Intensive (yaṅ)**: implement a more faithful rule system; restrict overrides to true lexical exceptions.
- **Perfect system**: expand weak/strong stem rules and ending-conditioned alternations; reduce reliance on `perfect_stem_overrides`.
- **Aorist middle**: broaden aorist subtype handling and middle-specific type selection (currently mostly via overrides).
- **Passive**: expand samprasāraṇa and vocalic alternations with proper conditioning; keep overrides only where truly necessary.

### 4) Improve traceability and debuggability
- Use `SanskritConjugator.debug_conjugate()` more broadly to pinpoint where paths diverge (stem vs morphology vs sandhi vs endings).
- Add a small “rule provenance” mechanism (even just docstring references + consistent citations near rules) so exceptions can be justified.

### 5) Reduce override surface area by promoting productive rules
- When an override list grows, first check if those items share a pattern that can be encoded as:
  - a new tag interpreted in `MorphologyEngine`, or
  - a new systematic stem builder rule in `StemBuilder`, or
  - a lexicon feature in `RootObject`.

## Quick inventory of “where things live” (for future work)
- **Pipeline**: `grammar/conjugate.py`
- **Feature resolution (class/strength/augment/periphrastic selection)**: `grammar/feature_resolver.py`
- **Stems (class systems + tense systems + derivatives)**: `grammar/stem_rules.py`
- **Endings tables**: `grammar/endings.py`
- **Morphology post-processing (tag interpretation)**: `grammar/morphology.py`
- **Sandhi**: `grammar/sandhi.py`
- **Reduplication**: `grammar/reduplication.py`
- **Lexicon-derived root properties**: `grammar/dhatupatha_analyzer.py`
- **Kṛdantas block generator**: `grammar/krdantas.py`
- **Irregulars/overrides**: `grammar/irregulars.py`

