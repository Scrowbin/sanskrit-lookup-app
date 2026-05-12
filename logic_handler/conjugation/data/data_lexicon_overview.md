# Sanskrit Linguistic Data Collection

A comprehensive collection of Sanskrit linguistic data. Different data files are distributed under specific licenses depending on the source that produced them:

- **MW**: Files under the Monier-Williams license. These are built from the *Monier-Williams Sanskrit-English Dictionary* (downloaded 2015-04-08).
- **SHS**: Files under the Sanskrit Heritage Site license. These originated from the Sanskrit Heritage Site's XML documents.
- **LSO**: Files under the learnsanskrit.org license, which are in the public domain.

## The Files (with Headers)
Along with their headers, each file also has its applicable columns appended with corresponding IAST transliteration of their original SLP1 form (for example name and name_IAST)
---

## SHS Files

- **`adverbs.csv` [SHS]**  
  **Headers:** `name, root, pos, modification`  
  `-tvā` gerunds. Generated from `SL_adverbs.xml`.

- **`final.csv` [SHS]**  
  **Headers:** `name, root, pos, modification`  
  Infinitives and `-ya` gerunds. Generated from `SL_final.xml`.

- **`parts.csv` [SHS]**  
  **Headers:** `stem, root, class, mode, voice, modification`  
  Participle stems. Generated from an older version of `SL_parts.xml`.

- **`roots.csv` [SHS]**  
  **Headers:** `name, root, class, person, number, mode, voice, modification`  
  Inflected verbs. Generated from `SL_roots.xml`.
---

## MW Files

- **`prefixed_roots.csv` [MW]**  
  **Headers:** `prefixed_root, prefixes, unprefixed_root, hom`  
  Prefixed verb roots.

- **`unprefixed_roots.csv` [MW]**  
  **Headers:** `root, hom, class, voice`  
  Unprefixed verb roots.

- **`verb-prefixes.csv` [MW]**  
  **Headers:** `name, prefix_type`  
  Verb prefixes.
---

## LSO Files
- **`sandhi-rules.csv` [LSO]**  
  **Headers:** `first, second, result, type`  

  - `first`: First part  
  - `second`: Second part  
  - `result`: Result (may contain space-separated transformations)  
  - `type`: `common`, `internal`, or `external`
  
  Describes sandhi rules of the form `"A + B -> C"`.

---

## Column Types (Condensed)

This is the unified list of all column headers used across the datasets:

- **`class`**: The verb class  
  - `1` to `10` for standard classes (e.g., `1` for `gacchati`, `10` for `corayati`)  
  - `denom` for denominative verbs (e.g., `putrīyati`)

- **`form`**: The actual grammatical form (e.g., `gacchati`)

- **`hom`**: Short for *homonym*; distinguishes identical-sounding roots with different meanings.  
  Contains either an empty string or a number.

- **`mode`**: The verb mode  
  - `aor` (aorist), `ben` (benedictive), `cond` (conditional)  
  - `impv` (imperative), `inj` (injunctive), `ipft` (imperfect)  
  - `opt` (optative), `perf` (perfect), `pfut` (periphrastic future)  
  - `pres` (present), `sfut` (simple future)

- **`modification`**: Specific modification applied to the verb  
  - `caus` (causative), `desid` (desiderative), `intens` (intensive)

- **`number`**: The verb number  
  - `s` (singular), `d` (dual), `p` (plural)

- **`person`**: The verb person  
  - `1` (first), `2` (second), `3` (third)

- **`pos`**: Part of speech  
  - `gerund`, `infinitive`

- **`prefix_type`**: Type of verb prefix  
  - `cvi`, `DAc`, or `other` (excluding *upasargas*)

- **`prefixed_root`**: A prefixed verb root (e.g., `āgam`)

- **`root`**: The base verb root (e.g., `gam`)

- **`stem`**: The nominal stem (e.g., `nara`, `sundara`, `gantavya`)

- **`stem_genders`**: Grammatical genders of the stem  
  - `m`, `f`, `n`  
  - Combinations: `mf`, `fn`, `mn`  
  - `mfn` (any gender, typically adjectives)  
  - `none` (non-gendered stems, e.g., `mad`)

- **`unprefixed_root`**: An unprefixed verb root (e.g., `gam`)

- **`voice`**: The verb voice  
  - `active` (non-passive; often for participles)  
  - `atma` (ātmanepada), `para` (parasmaipada)  
  - `pass` (passive)