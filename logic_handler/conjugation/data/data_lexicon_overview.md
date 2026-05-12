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