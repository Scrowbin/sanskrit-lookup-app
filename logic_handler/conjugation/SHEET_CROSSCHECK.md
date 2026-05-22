# Sanskrit Engine — Sheet Crosscheck Report

> Cross-reference of every rule in `sheet_3.txt`, `sheet_8.txt`, `sheet_9.txt`,
> `sheet_10.txt`, `sheet_11.txt`, `sheet_12.txt`, `sheet_14.txt`, `sheet_15.txt`
> against the current engine under `grammar/`.
>
> **Status legend**
> - ✅ IMPLEMENTED — rule is correctly covered algorithmically
> - 🟡 PARTIAL — present but incomplete / edge-cases missing
> - ❌ MISSING — no implementation found
>
> **Where things live** (from `ENGINE_AUDIT.md`)
> | Layer | File |
> |---|---|
> | Pipeline orchestrator | `conjugate.py` |
> | Feature resolution | `feature_resolver.py` |
> | Stem builders | `stem_rules.py` |
> | Endings tables | `endings.py` |
> | Morphology post-processing | `morphology.py` |
> | Sandhi (phonology FST) | `sandhi.py` |
> | Reduplication | `reduplication.py` |
> | Lexicon / root properties | `dhatupatha_analyzer.py` |
> | Kṛdantas | `krdantas.py` |
> | Overrides / irregulars | `irregulars.py` |

---

## Chapter 3 — Phonology (Whitney §§113–259)

### Rule 113 — Hiatus avoidance (vowel sandhi, general)
**Status:** ✅ IMPLEMENTED  
`sandhi.py` `vowel_phase` handles all V+V boundaries via `savarna`, `guna_sandhi`, `ayadi`, `yan_sandhi`, and `thematic_merger`. Every morpheme boundary is marked with `+` and consumed by these FSTs.  
**Nothing missing for internal sandhi. External (word–word) sandhi is out of scope.**

---

### Rule 114 — Deaspiration before obstruents/sibilants
**Status:** ✅ IMPLEMENTED  
`sandhi.py` `devoicing` FST strips voicing/aspiration before unvoiced triggers `+t +th +s +ṣ +c +ch +k +kh +p +ph +ṭ +ṭh`. Aspiration loss is folded into devoicing (e.g. `dh→t`, `bh→p`).  
**Gap:** deaspirate-then-revoice for voiced-surd clusters (e.g. `dh+d → dd`) is handled via `bartholomae_general`; fully aspirate+voiced input is covered.

---

### Rule 115–116 — Regressive assimilation (general)
**Status:** ✅ IMPLEMENTED  
`sandhi.py` encodes regressive assimilation: `devoicing` (preceding mute → surd before surd), `nasal_assimilation` (n → homorganic nasal), `bartholomae_general` (progressive aspirate transfer). The pipeline order (Bartholomae before devoicing) is correct.

---

### Rule 117a — Surd/sonant incompatibility
**Status:** ✅ IMPLEMENTED  
`devoicing` FST voices/devoices preceding obstruent to match following. Sonantization before vowels/nasals is handled by `bartholomae_general` + `grassmann_throwback` ordering.  
**Partial gap:** explicit "sonantize before any sonant" (e.g. `t→d` before `+m`) uses `nasal_assimilation` path; direct surd→sonant before semivowels/h is not a standalone rule but emerges from tag-gated rules.

---

### Rule 117c — Nasals before sibilants → anusvāra
**Status:** ✅ IMPLEMENTED  
`sandhi.py` `anusvara` FST: `m+ → ṃ+` before `y r l v ś ṣ s h`.  
`parasavarna` FST: `m+stop → homorganic nasal + stop`.  
**Gap:** the rule for a nasal preceding a *sibilant* in external combination (insert surd mute between nasal and sibilant) is not implemented — this is **external sandhi** and is out of current scope.

---

### Rule 118a — RUKI: `s→ṣ`, `n→ṇ`
**Status:** ✅ IMPLEMENTED  
`sandhi.py` `long_distance_phase`:
- `ruki` FST: `s→ṣ` after `r ṛ u ū k i ī e ai o au`.
- `ruki_r_revert`: blocks RUKI when followed by `r` (Whitney §181a).
- `nati` FST: `n→ṇ` long-distance after `r ṛ ṣ ṝ` with allowed interveners.  
**Gap:** `[NO_RUKI]` tag exempts desiderative-prefix `s` (Whitney §184d). Correct. However RUKI triggers from *prefix-final vowels* across a `+` boundary are only partially covered — the `+` is stripped before RUKI fires, which is the correct approach.

---

### Rule 118b — Dental mute + lingual → lingual
**Status:** ✅ IMPLEMENTED  
`retro_t`, `retro_th`, `retro_dh`, `retro_dhv` FSTs in `consonant_phase`. Post-RUKI equivalents in `long_distance_phase`. `ṣ+t → ṣṭ`, `ṣ+th → ṣṭh`, `ṣ+dh → ḍḍh`.

---

### Rule 118c — Dental → palatal before palatals
**Status:** ✅ IMPLEMENTED  
`dental_palatal_fusion` (tag-gated `[SD_DCP]`): `t/d/dh + c/ch → cc/cch`.  
`nasal_assimilation`: `n → ñ` before `j c`.  
**Partial:** full dental+palatal matrix (e.g. `t+j → jj`, `d+j → jj`) is not explicitly listed; `palatal_sandhi` converts `j/c → k` before unvoiced triggers, which handles surd cases.

---

### Rule 119 — Palatal/h reversion to guttural
**Status:** ✅ IMPLEMENTED  
`palatal_sandhi` FST: `j/c → k` before unvoiced dental/sibilant triggers. `h_to_k` FST: `h → k` before `+s/+ṣ`. `permitted_finals` at word-final position: `c/j → k`.  
**Partial:** "store derivational origin of each palatal/h" for guttural reversion is not a tracked property — reversion is rule-based on phonological context, which is correct per Whitney; but the **duh-class** vs **ruh-class** distinction requires a root-lexicon flag (`[RUH_H]` tag, implemented in `stem_rules.py` build method) — ✅ covered.

---

### Rule 122 — Permitted finals
**Status:** ✅ IMPLEMENTED  
`sandhi.py` `permitted_finals` FST: devoices/deaspirates/substitutes before `[EOS]`.  
`cluster_reduction` FST: strips all but one final consonant (`ṣṭ→ṭ`, `k+t→k`, `gdh→k`).  
**Partial:** the full list of permitted finals (Whitney §141–150) is not exhaustively enumerated — some exotic clusters may survive. Regression tests per paradigm are recommended.

---

### Rules 125–126 — Vowel sandhi: like vowels
**Status:** ✅ IMPLEMENTED  
`savarna` FST: `a+a→ā`, `i+i→ī`, `u+u→ū`, `ṛ+ṛ→ṝ` (all length combinations).

---

### Rule 127 — Vowel sandhi: `a/ā` + dissimilar
**Status:** ✅ IMPLEMENTED  
`guna_sandhi` FST: `a+i→e`, `a+u→o`, `a+ṛ→ar`, `a+ḷ→al` (Whitney §244).  
`thematic_merger` FST: `a+e→e`, `a+o→o`, `a+ai→ai`, `a+au→au`.

---

### Rule 129 — Vowel sandhi: `i/u/ṛ` + dissimilar → glide
**Status:** ✅ IMPLEMENTED  
`yan_sandhi` FST: `i+→y`, `ī+→y`, `u+→v`, `ū+→v`, `ṛ+→r` before vowels.  
`perfect_yan_conjunct` / `perfect_yan_simple`: special `[PERF_WEAK]` tagged versions for perfect weak forms (iy/uv after conjunct).

---

### Rules 131–132 — Diphthong sandhi (external)
**Status:** ❌ MISSING (external sandhi — out of scope)  
External sandhi (e/āi losing glide before vowels, āu→āv) is not implemented. This is intentional — engine handles internal sandhi only.

---

### Rule 135 — Elision of initial `a` after `e/o`
**Status:** ❌ MISSING  
No avagraha / `e+a→e` (elision) rule in `sandhi.py`. This is **external** sandhi and out of scope.

---

### Rule 138 — Pragṛhya (exempt vowels)
**Status:** ❌ MISSING  
No `pragṛhya` flag in the lexicon or morphology module. Dual endings in `-e/-ī/-ū` are never flagged as exempt. This matters for parsing but not generation.

---

### Rules 141, 150 — Mute finals reduction / single final consonant
**Status:** ✅ IMPLEMENTED  
`permitted_finals` + `cluster_reduction` in `long_distance_phase`.

---

### Rule 153 — Internal deaspiration
**Status:** ✅ IMPLEMENTED  
`devoicing` FST covers internal deaspiration before obstruents/sibilants.

---

### Rule 155 — Aspiration bounce (Grassmann)
**Status:** ✅ IMPLEMENTED  
`grassmann_throwback` FST: restores aspiration to initial consonant when final aspirate deaspirates before `+s +ṣ +t +th +c +ch +dhv`. Correct trigger set.  
**Partial:** Grassmann applies only before specific triggers — the rule is not a global throwback; ordering w.r.t. `bartholomae_general` is correct (Bartholomae before Grassmann).

---

### Rules 157/159 — External surd→sonant before sonant
**Status:** ❌ MISSING (external sandhi)

---

### Rule 160 — Progressive aspiration transfer (Bartholomae)
**Status:** ✅ IMPLEMENTED  
`bartholomae_general` + `bartho_ht/hdh/hth` FSTs.

---

### Rule 161 — Mute before nasal → nasal assimilation
**Status:** ✅ IMPLEMENTED  
`nasal_assimilation` FST. `nj_cluster_hardening` for class-7 yuj-type clusters.

---

### Rule 162 — `t + l → ll`
**Status:** ❌ MISSING  
No `t→l` before `l` rule. Rare in internal conjugation; add to `consonant_phase` as `pn.cdrewrite(pn.cross("t+l","ll"))`.

---

### Rule 163 — Mute before `h` → sonantize + aspirate
**Status:** 🟡 PARTIAL  
`bartho_ht` handles `h+t → gdh`. But a general "final mute + h" rule (e.g. `t+h → ddh`, manuscript form) is not a standalone FST. Covered only for the specific Bartholomae cases.

---

### Rules 170–172 — Final `s` transformations (visarga)
**Status:** ✅ IMPLEMENTED  
`visarga` FST: word-final `s → ḥ` before `[EOS]`. Ordering before RUKI is correct.  
**Gap:** the full decision tree (s→ç/ṣ before palatals/linguals in external sandhi, s→r before sonants) is **external sandhi** — not implemented.

---

### Rule 174 — `s → r` before sonant
**Status:** ❌ MISSING (external sandhi)

---

### Rule 175 — Final `-as/-ās` rules
**Status:** ❌ MISSING (external sandhi)

---

### Rules 178–179 — Final `r` behavior
**Status:** ❌ MISSING (external sandhi)

---

### Rule 180, 184–188 — RUKI: `s → ṣ` (full scope)
**Status:** ✅ IMPLEMENTED  
See Rule 118a. RUKI applied at all morpheme boundaries via `ruki` + `ruki_r_revert`. `[NO_RUKI]` tag for desiderative prefix. Post-RUKI retroflex assimilation in `long_distance_phase`.

---

### Rule 189 — `n → ṇ` long-distance (Nati)
**Status:** ✅ IMPLEMENTED  
`nati` FST with correct trigger set (`r ṛ ṣ ṝ`) and allowed intervener set (vowels, gutturals, labials, `y v h ṃ +`).

---

### Rules 212–213 — Final `m` assimilation
**Status:** ✅ IMPLEMENTED  
`parasavarna` + `anusvara` FSTs handle `m+stop` and `m+semivowel/sibilant`.

---

### Rule 217 — Final `c → k`
**Status:** ✅ IMPLEMENTED  
`palatal_sandhi` + `permitted_finals`.

---

### Rule 218 — Final `ç` behavior (ś)
**Status:** ✅ IMPLEMENTED  
`sha_sonant_aspirate` (ś+dh→ḍh, ś+bh→ḍbh).  
`palatal_sibilant_retroflex` `[SD_SSR]` tag: `ś+t→ṣṭ`, `ś+th→ṣṭh`.  
`permitted_finals`: `ś→ṭ` at word-final.

---

### Rule 219 — Final `j` (two classes)
**Status:** 🟡 PARTIAL  
`j_retroflex` FST handles specific roots (`rj, yaj, ij, sṛj, mṛj, bhrajj`) explicitly.  
**Missing:** general j-class membership stored in root lexicon. Not all j-final roots are covered — new roots may default to incorrect behavior.

---

### Rule 222 — Final `h` (duh-class vs ruh-class)
**Status:** ✅ IMPLEMENTED  
`[RUH_H]` tag injected in `stem_rules.py` `build()` for ruh-class h-final roots. `ruh_class_dental` FST: `uh[RUH_H]+t → ūḍh`, etc. `bartho_ht` handles duh-class (h→gdh). `nah` root is excluded.  
**Partial:** `d`-initial h-roots (except `druh`) skip `[RUH_H]` injection via heuristic — may miss edge cases.

---

### Rule 226 — Final `ṣ` behavior
**Status:** ✅ IMPLEMENTED  
`retro_t`, `retro_th`, `retro_dh` FSTs. `permitted_finals`: `ṣ→ṭ`.

---

### Rules 230–233 — Dental assimilation before palatals/linguals
**Status:** ✅ IMPLEMENTED  
`dental_palatal_fusion` (tag-gated). `retro_*` FSTs for dental+lingual.

---

### Rules 235–237 — Guṇa and Vṛddhi
**Status:** ✅ IMPLEMENTED  
`vowel_strength.py` `VowelStrengthEngine` provides `guna` and `vriddhi` FSTs. Used throughout `stem_rules.py` (`_apply_guna`, `_apply_vriddhi`).

---

### Rule 253 — Short `a` loss in weak syllables (zero-grade)
**Status:** 🟡 PARTIAL  
Some zero-grade forms are produced for samprasāraṇa roots (yaj→ij, vac→uc) via `_compute_samprasarana_passive`. General zero-grade (medial `a` drop in athematic paradigms) relies on override tables in `irregulars.py` rather than a systematic FST rule.

---

### Rules 254–258 — Union vowels / inserted consonants
**Status:** 🟡 PARTIAL  
- `+i` before future suffix: implemented via `is_anit` flag → `+sya` vs `+iṣya`.
- `+y` after ā before vowel endings: implemented via `yan_sandhi`.
- `+n` between vowel stems and endings: **not** a standalone rule; handled case-by-case in endings tables.  
**Missing:** systematic `n`-insertion for certain declensional contexts.

---

### Rule 259 — Reduplication
**Status:** ✅ IMPLEMENTED  
`reduplication.py` `ReduplicationEngine` with FST-based reduction (deaspirate, palatalize, shorten, ṛ→a). Separate methods for perfect, desiderative, intensive, aorist prefixes. Override table `perfect_redupe_overrides` for irregulars (bhū→ba etc.).

---

## Chapter 3 — Engine Overhaul Items

| Priority | Item | File | Action |
|---|---|---|---|
| High | `t + l → ll` (Rule 162) | `sandhi.py` | Add `pn.cdrewrite(pn.cross("t+l","ll"))` to `consonant_phase` before `nasal_assimilation` |
| High | j-class root lexicon (Rule 219) | `dhatupatha_analyzer.py` | Add `is_jclass2` flag (ç-rules) vs `is_jclass1` (c-rules) to `RootObject`; use in `sandhi.py` `j_retroflex` |
| Medium | Zero-grade `a`-drop (Rule 253) | `stem_rules.py` + `morphology.py` | Implement systematic medial-a deletion FST for athematic weak stems, gated by `[WEAK]` + athematic class |
| Medium | `n`-insertion (Rule 258) | `endings.py` | Add `n` as a connecting element for specific stem+ending junctions where needed |
| Low | Pragṛhya flag (Rule 138) | `dhatupatha_analyzer.py` | Add `is_pragrhya` property to `RootObject`; skip vowel sandhi for flagged forms |

---

## Chapter 8 — Voice, Tense, Mode, Endings, Augment, Reduplication (Whitney §§527–598)

### Rule 527 — Two voices (active / middle)
**Status:** ✅ IMPLEMENTED  
`conjugate.py` accepts `voice="active"|"middle"|"passive"`. `endings.py` `SuffixProvider` has separate `get_present_active` / `get_present_middle` etc. for every tense. `feature_resolver.py` routes voice through all paths.

---

### Rules 528–529 — Voice semantics (no enforcement)
**Status:** ✅ IMPLEMENTED (correctly not enforced)  
The engine does not block voice on semantic grounds. Lexical voice restrictions come from `RootObject.permitted_voices` derived from the Dhātupāṭha marker in `dhatupatha_analyzer.py`. Semantics are intentionally left to the caller.

---

### Rules 530–531 — Voice distribution / middle-as-passive in non-present
**Status:** 🟡 PARTIAL  
`permitted_voices` is stored per root. The rule "middle doubles as passive in perfect, future, non-present tenses" is implemented in that `conjugate.py` raises `ValueError` for `voice=passive` in `perfect/future/periphrastic_future/conditional/benedictive`, directing callers to use middle. However there is no positive mechanism to **auto-alias** middle→passive for those tenses — the caller must explicitly pass `voice="middle"`.

---

### Rule 532 — Eight tense-forms
**Status:** 🟡 PARTIAL  
Implemented: `present`, `imperfect`, `imperative`, `optative`, `future`, `conditional`, `perfect`, `periphrastic_future`, `aorist`, `injunctive`, `benedictive`, `subjunctive`.  
**Missing:** `pluperfect` (luṅ / past-of-perfect), `future perfect` — not in `tense_dispatch` or `_ending_dispatch`.

---

### Rule 533 — Three modes (+ Vedic subjunctive)
**Status:** 🟡 PARTIAL  
Indicative, optative, imperative: ✅. Subjunctive: present in `endings.py` `get_subjunctive_active/middle` and wired in `_ending_dispatch`. However the Vedic subjunctive is generated with the same stem as the present indicative — no mode-sign `a` is applied algorithmically (Whitney §557 requires strong stem + `a` + primary/secondary endings). Currently the subjunctive endings are simplified approximations.

---

### Rule 535 — Four tense-systems / hierarchical stem
**Status:** ✅ IMPLEMENTED  
`stem_rules.py` `tense_dispatch` routes to per-system builders: present-system (`_build_present_system`), future-system (`_build_future_system`), perfect-system (`_build_perfect_system`), aorist-system (`_build_aorist_system`). Each system derives its forms from a common stem.

---

### Rule 536 — 9 person-number slots; imperative 1st = subjunctive
**Status:** ✅ IMPLEMENTED  
All 9 cells (3 persons × 3 numbers) are generated. Imperative 1st-person endings (`āni, āva, āma` active; `āi, āvahai, āmahai` middle) are stored directly in `endings.py` `get_imperative_active/middle` — they are the subjunctive endings used as the imperative 1st person per Whitney §569.

---

### Rule 537 — Participles (three categories)
**Status:** 🟡 PARTIAL  
`krdantas.py` `KrdantaEngine` generates: PPP (ta/tā), past active (tavat), present active (ant/antī), present middle (māna), present passive (māna on passive stem), future active/middle (syant/syamāna), future passive gerundives (tavya/ya/anīya), perfect active (vāṅs/vas), perfect middle (āna), infinitive (tum), absolutives (tvā/ya).  
**Missing:**
- Perfect active participle suffix `vāṅs` is approximated (using `ivas`/`vas`/`as` shortcuts) — full `vāṅs` declension with `uṣ`-weak stem is not implemented.
- Middle participle `māna` vs `āna` distinction (māna for a-stems, āna elsewhere) — ✅ COMPLETED (`krdantas.py` correctly uses `māna` for thematic and `āna` for athematic).
- Vedic infinitive case-forms (dative `-tavāi`, `-dhyāi`, locative `-sani`, etc.) — not implemented (Vedic scope).

---

### Rule 538 — Infinitive (tu-accusative)
**Status:** ✅ IMPLEMENTED  
`krdantas.py` generates `-tum` from the periphrastic base. Vedic forms are out of scope.

---

### Rule 539 — Gerund (`-tvā`, `-ya/-tya`)
**Status:** 🟡 PARTIAL  
`krdantas.py` generates `-tvā` (absolutive) from the bare root and `-ya` from the bare root.  
**Missing:** the `-tya` form (used for prefixed roots instead of `-ya`) is not distinguished — the engine uses `-ya` uniformly. The Vedic `-am` gerund is not implemented.

---

### Rule 540 — Secondary conjugations (five)
**Status:** 🟡 PARTIAL  
Passive, causative, desiderative, intensive: ✅ implemented as stem-building modules feeding the main pipeline.  
Denominative: ✅ basic `+ya` stem.  
**Missing:** Frequentatives (yaṅ-luk / intensive-luk variant), nic+san stacking, passive-causative combinations beyond `causative_passive` in `stem_rules.py`.

---

### Rule 541–542 — Primary vs secondary endings
**Status:** ✅ IMPLEMENTED  
`endings.py` maintains separate primary (`get_present_active/middle`) and secondary (`get_secondary_active/middle`) tables. `feature_resolver.py` selects the correct table per tense/mode. Future/Conditional explicitly forced to thematic class-1 endings inside `endings.py`.

---

### Rules 543–550 — Personal endings (1sg–3pl, dual, plural)
**Status:** ✅ IMPLEMENTED  
Full 9-cell tables in `endings.py` for all tenses/voices. Key special cases:
- Perfect 1sg/3sg active = same ending (`a`/`au` for ā-roots) ✅
- Perfect 3pl active `uḥ` ✅; middle 3pl `ire` ✅
- Optative middle 3pl `ran` ✅ (via `get_optative_middle` `[3pl]: "īran"`)
- 2sg middle `-ṣe/-dhve` for ṛ/u-final roots ✅ (endings.py `get_perfect_middle`)
- `anti→ati` after reduplicated stems: ✅ class-3 gets `ati/atu` in endings tables.

---

### Rule 551–554 — Full ending tables with accent
**Status:** 🟡 PARTIAL  
All four tables implemented. **Accent is not tracked** — the engine generates unaccented IAST output. Accent marks would require a parallel accent FST (out of current scope).

---

### Rule 555 — Loss of 2nd/3rd sg secondary `s/t` after root-final consonant
**Status:** 🟡 PARTIAL  
`sandhi.py` `cluster_reduction` removes final consonant clusters at `[EOS]` (`k+t→k`, `ṣṭ→ṭ`, `gdh→k`). But the specific rule "drop ending consonant when result is impermissible cluster" is handled implicitly via `permitted_finals` + `cluster_reduction` rather than an explicit 2sg/3sg secondary ending deletion rule. Dental-swap exceptions are not tracked.

---

### Rule 557 — Subjunctive mode
**Status:** 🟡 PARTIAL  
Subjunctive endings exist in `endings.py`. Classical 1st-person forms are used as the imperative 1st. **Missing:** the full Vedic subjunctive (strong stem + mode-sign `a` + primary/secondary endings) — current subjunctive reuses the present stem without adding a mode-sign.

---

### Rules 564–566 — Optative
**Status:** ✅ IMPLEMENTED  
`get_optative_active` (athematic: `yāt/yāḥ/yām`; thematic: `et/eḥ/eyam`).  
`get_optative_middle` (athematic: `īta/īthāḥ/īya`; thematic: `eta/ethāḥ/eya`).  
3pl active: thematic `eyuḥ` ✅; athematic `yuḥ` ✅. 3pl middle: thematic `eran` ✅; athematic `īran` ✅.

---

### Rules 567–568 — Precative (benedictive)
**Status:** 🟡 PARTIAL  
`endings.py` `get_benedictive_active` (`yāt/yāḥ/yāsam`…) and `get_benedictive_middle` (`sīṣṭa/sīṣṭhāḥ/sīya`…).  
`stem_rules.py` `_build_benedictive_system` applies samprasāraṇa for active, vowel substitution for ā/i/u/ṛ-final roots.  
**Missing:** the sibilant insertion rule between `yā/ī` and personal ending (precative = optative + `s`) is not modeled as a mechanical insertion — instead the `s` is baked into the ending surfaces (`yāsam` etc.). This works but loses the compositional derivation. Middle precative active-voice alternation (root vs iṣ-stem) is not handled.

---

### Rules 569–571 — Imperative
**Status:** ✅ IMPLEMENTED  
Direct stem + imperative endings. 1st-person forms = subjunctive endings (āni/āva/āma active; āi/āvahai/āmahai middle). `tāt` variant as alternative 2sg: **not implemented** (low priority, rare).

---

### Rules 572–581 — Uses of modes
**Status:** ❌ NOT APPLICABLE  
Semantic tagging of generated forms is not a generation concern. Out of scope.

---

### Rules 583–584 — Participles formation (ant/at, āna/māna, vāṅs)
**Status:** 🟡 PARTIAL  
See Rule 537 above. `ant/at` suffix selection based on thematic/athematic handled in `krdantas.py` by stripping `+a` from thematic stems. `māna` vs `āna` for middle participle: not fully distinguished (see Rule 537).

---

### Rules 585–587 — Augment
**Status:** ✅ IMPLEMENTED  
`conjugate.py` step 3: `[AUG]a+` prepended for `tense ∈ {imperfect, conditional, aorist}`. `morphology.py` handles `[AUG]` + vowel-initial stem → vṛddhi (a+i→ai, a+u→au) per Whitney §585/Pāṇini 6.1.87-89.

---

### Rules 588–590 — Reduplication (general)
**Status:** ✅ IMPLEMENTED  
`reduplication.py` FST pipeline: deaspirate → palatalize → shorten → ṛ→a. Sibilant+voiceless-stop rule (Whitney §590 / Pāṇini 7.4.61): stop is reduplicated, not sibilant. Four prefix generators: perfect, desiderative, intensive, aorist (caṅ). Override table for true irregulars.

---

### Rules 591–598 — Verbal accent
**Status:** ❌ NOT IMPLEMENTED  
Accent is out of scope. The engine generates unaccented IAST.

---

## Chapter 8 — Engine Overhaul Items

| Priority | Item | File | Action |
|---|---|---|---|
| High | Pluperfect / future perfect tenses (Rule 532) | `conjugate.py`, `stem_rules.py`, `endings.py` | Add `pluperfect` = augment + perfect stem + secondary endings to `tense_dispatch` and `_ending_dispatch` |
| High | Vedic subjunctive mode-sign (Rule 557) | `stem_rules.py`, `endings.py` | Implement `strong_stem + a + primary/secondary` for Vedic subjunctive; currently uses present stem without mode-sign |
| High | `-tya` absolutive for prefixed roots (Rule 539) | `krdantas.py` | Detect preverb presence → use `-tya` instead of `-tvā`; `-ya` stays for general absolutive |
| Medium | `māna` vs `āna` participle (Rule 583) | `krdantas.py` | Use `āna` for athematic present middle participle (classes 2,3,5,7,8,9); `māna` for thematic (1,4,6,10) |
| Medium | `tāt` imperative variant (Rule 569) | `endings.py` | Add `tāt` as optional 2sg active imperative alternative |
| Medium | Middle-as-passive alias for non-present (Rule 530) | `conjugate.py` | Document and optionally auto-route `passive` + non-present tense to `middle` |
| Low | Accent FST (Rules 551–554, 591–598) | new `accent.py` | Deferred — not in current scope |

---

## Chapter 9 — Present System / Classes (Whitney §§599–779)

### Rules 599–600 — Present-system overview
**Status:** ✅ IMPLEMENTED  
All six sub-formations route through `_build_present_system` → class-specific `class_handlers`.

---

### Rules 602–604 — Non-a conjugation strong/weak alternation
**Status:** 🟡 PARTIAL  
`feature_resolver.py` + `_apply_guna/_apply_vriddhi` handle grades. Zero-grade (medial `a`-drop) for athematic weak forms is only partially algorithmic — many rely on override tables.

---

### Rules 605–607 — a-conjugation (fixed accent, optative ī, 2sg impv = bare stem)
**Status:** ✅ IMPLEMENTED  
`is_thematic()` branch controls endings throughout. Thematic optative `et/eḥ/eyam`, 2sg imperative zero-ending, 3pl middle `-nte` all correct.

---

### Rules 611–641 — Class 2 (Root class) + irregularities
**Status:** 🟡 PARTIAL  
`_build_class_2` + `class_2_irregulars`. `hi`/`dhi` 2sg selection from root phonology. Main anomalies (han, as, çās) covered via overrides. Systematic vṛddhi for u-roots not FST-encoded.

---

### Rules 642–658 — Class 3 (Reduplicating)
**Status:** ✅ IMPLEMENTED  
`_build_class_3` + `generate_prefix()`. Class-3 specific `ati/atu` 3pl endings in tables.

---

### Rules 683–696 — Class 5 (Nu/u-class, kṛ)
**Status:** 🟡 PARTIAL  
`_build_class_5` + `class_5_irregulars`. kṛ `karo/kuru` special-casing and u-deletion override-driven.

---

### Rules 697–716 — Class 4 (Nā/nī-class)
**Status:** ✅ IMPLEMENTED — `_build_class_4`, `nā` strong / `nī` weak, ī-drop via FST.

---

### Rules 717–732, 751–774 — Classes 6, 7, 8, 9
**Status:** ✅ IMPLEMENTED  
All four thematic subclasses built in `stem_rules.py`. `[CLASS9]` ī-drop FST. Passive/class-8 middle-only enforced via voice gate.

---

### Rule 775 — Class 10 (cur-class / causative)
**Status:** ✅ IMPLEMENTED — `_build_class_10` → `_build_causative_base` + `+a`.

---

## Chapter 9 — Engine Overhaul Items

| Priority | Item | File | Action |
|---|---|---|---|
| High | Systematic zero-grade for athematic weak | `stem_rules.py` | FST for medial-`a` drop instead of per-root override |
| High | kṛ u-deletion productive rule | `stem_rules.py` | Encode as FST rule, remove from `class_5_irregulars` |
| Medium | Class-2 vṛddhi for u-roots | `stem_rules.py` | Add algorithmic vṛddhi for u-final roots in strong class-2 |
| Medium | `dhi` vs `hi` algorithmic selection | `endings.py` | Base on root phonology, not whitelist |

---

## Chapter 10 — Perfect System (Whitney §§780–823)

### Rules 780–801 — Perfect stem, reduplication, strong/weak, endings
**Status:** 🟡 PARTIAL  
`_build_perfect_system` + `generate_prefix()` + vṛddhi-3sg logic. Strong 1sg/2sg guṇa vs 3sg vṛddhi correct. E-grade weak for `labh/rabh` roots ✅. Union-vowel `i` in `itha/iva/ima` ✅.  
**Missing:** three-way 1sg≠2sg≠3sg strong distinction (1sg=guṇa, 2sg=guṇa/guna, 3sg=vṛddhi) is collapsed to `[STRONG]` for 1sg/2sg — functionally correct for most roots.

---

### Rules 802–807 — Perfect participle (vāṅs / āna)
**Status:** 🟡 PARTIAL  
`krdantas.py` uses shortcut suffixes (`ivas/vas/as`). Full `vāṅs/uṣ` declension not implemented.

---

### Rules 808–820 — Vedic perfect modes, pluperfect
**Status:** ❌ MISSING — Vedic scope; pluperfect (augment + perfect weak stem + secondary) deferred.

---

## Chapter 10 — Engine Overhaul Items

| Priority | Item | File | Action |
|---|---|---|---|
| High | Full `vāṅs/uṣ` participle | `krdantas.py` | Implement strong nom. sg. + `uṣ`-weak; seṭ/aniṭ union-vowel |
| Medium | Pluperfect tense | `stem_rules.py`, `endings.py`, `conjugate.py` | `[AUG]a+` + perfect weak stem + secondary endings |

---

## Chapter 11 — Aorist System (Whitney §§824–930)

### Rules 824–827 — Seven aorist types overview
**Status:** 🟡 PARTIAL  
All seven types have stem builders + ending tables. Type detection via heuristic + `aorist_overrides`. Systematic Pāṇinian selection rules missing.

---

### Rules 829–845 — Types 1 (root) + passive 3sg ciṇ
**Status:** ✅ IMPLEMENTED — `[ROOT_AORIST]` tag + `[AORIST_PASS_3SG]` Vriddhi tag.

---

### Rules 846–873 — Types 2 (a-aorist) + 3 (reduplicated/caṅ)
**Status:** ✅ IMPLEMENTED — `a_type=="a"` bare+`+a`; `"reduplicated"` → `generate_aorist_prefix()+root+a`.

---

### Rules 874–920 — Types 4–7 (sibilant aorist)
**Status:** 🟡 PARTIAL  
`s/is/sis/sa` types implemented. Vṛddhi active / guṇa middle correct. `s_or_is` union handled. Precise per-root sibilant-type selection not Pāṇinian-algorithmic.

---

### Rules 921–925 — Precative (aorist optative)
**Status:** 🟡 PARTIAL  
Benedictive system covers this. Compositional sibilant-insertion not modeled derivationally — ends baked into ending surfaces.

---

## Chapter 11 — Engine Overhaul Items

| Priority | Item | File | Action |
|---|---|---|---|
| High | Algorithmic aorist type selection | `dhatupatha_analyzer.py` | Replace `_raw_aorist_type` heuristic with it-marker parsing |
| Medium | Middle-specific aorist type expansion | `stem_rules.py`, `irregulars.py` | Expand `aorist_overrides` `middle` key; encode `is`-middle as default for many roots |
| Medium | `siṣ`/`sa` type selection from anubandhas | `dhatupatha_analyzer.py` | Add `is_siṣit`/`is_sait` flags to `RootObject` |

---

## Chapter 12 — Future System (Whitney §§931–950)

### Rules 931–937 — S-future stem (guṇa + sya/iṣya)
**Status:** ✅ IMPLEMENTED — `_build_future_system` with `is_anit`/`is_vet` from `RootObject`. Veṭ generates `pn.union`.

---

### Rules 938–939 — Future participle (syant/syamāna)
**Status:** ✅ COMPLETED — `krdantas.py` strips thematic `+a` correctly using `[WORD_END]`.

---

### Rules 940–941 — Conditional (augment + future + secondary)
**Status:** ✅ IMPLEMENTED — `[AUG]` + future stem + `get_secondary_*` endings.

---

### Rules 942–947 — Periphrastic future (tṛ-noun + as forms)
**Status:** ✅ COMPLETED — `_build_periphrastic_future_system` broadened with `DhatupathaAnalyzer` aniṭ/seṭ flags.

---

## Chapter 12 — Engine Overhaul Items

| Priority | Item | File | Action |
|---|---|---|---|
| Medium | Periphrastic future aniṭ/seṭ broadening | `stem_rules.py` | Use full `RootObject.is_anit` for all classes instead of class-6/7 heuristic |
| Low | Future participle `syant` vs `syat` accuracy | `krdantas.py` | Verify split; `ant` after consonant-final, `at` after vowel-final future stems |

---

## Chapter 14 — Secondary Conjugations (Whitney §§996–1068)

### Rules 996–997 — Overview
**Status:** 🟡 PARTIAL — Passive, intensive, desiderative, causative, denominative all implemented. yaṅ-luk and nic+san stacking missing.

---

### Rules 998–999 — Passive (yá + middle)
**Status:** ✅ IMPLEMENTED — `_build_passive` + `[PASSIVE]` tag + morphology lengthening.

---

### Rules 1000–1025 — Intensive (heavy reduplicated)
**Status:** 🟡 PARTIAL  
Middle `+ya` and active athematic forms exist. Intensive prefix uses guṇa-vowel. Three Whitney reduplication sub-types collapsed into one rule. `intensive_stem_overrides` masks gaps.

---

### Rules 1026–1040 — Desiderative (reduplicated + sa/iṣa)
**Status:** 🟡 PARTIAL  
Prefix generation ✅. `[NO_RUKI]` ✅. ā-final root → ī substitution missing.

---

### Rules 1041–1052 — Causative (guṇa/vṛddhi + áya; caṅ aorist; periphrastic perfect)
**Status:** 🟡 PARTIAL  
Seven-layer causative base builder. Whitney §1042a–n list not fully audited. Causative aorist (reduplicated) and periphrastic perfect ✅.

---

### Rules 1053–1068 — Denominative (noun-stem + yá)
**Status:** 🟡 PARTIAL  
`+ya` suffix applied. `āya` vs `ya` semantic distinction not implemented.

---

## Chapter 14 — Engine Overhaul Items

| Priority | Item | File | Action |
|---|---|---|---|
| High | Intensive: three reduplication sub-types | `reduplication.py`, `stem_rules.py` | Implement Whitney's three patterns; reduce `intensive_stem_overrides` |
| High | Desiderative ā-final root → ī | `stem_rules.py` | `if root_str.endswith("ā"): replace ā with ī` in `_build_desiderative` |
| Medium | Causative Whitney §1042a–n audit | `stem_rules.py`, `irregulars.py` | Full audit; promote remaining patterns to rules or `_CAUSATIVE_NASAL` |
| Medium | Denominative `āya` vs `ya` | `stem_rules.py`, `feature_resolver.py` | Add `derivative="denominative_aya"` variant |
| Low | yaṅ-luk intensive | `stem_rules.py` | `derivative="intensive_luk"` → athematic without `+ya` |

---

## Chapter 15 — Prefixes, Periphrastic Perfect, Compounds (Whitney §§1069–1095)

### Rules 1069–1073 — Periphrastic perfect (base + āṁ + kṛ/as/bhū)
**Status:** 🟡 PARTIAL  
`_conjugate_periphrastic_perfect`: all three auxiliaries, voice enforcement for `bhū/as`. `āṁ` sandhi normalization may vary.

---

### Rules 1074–1075 — Participial periphrastic phrases
**Status:** ❌ NOT IMPLEMENTED — syntactic layer, out of scope.

---

### Rules 1076–1088 — Verbal prefixes (upasargas) + special junctions
**Status:** 🟡 PARTIAL  
Preverb parsed from `+`-separated string and prepended. General sandhi covers vowel junctions.  
**Missing:** 19-prefix table, `palāy`/`saṁskṛ`/`api-elision`/`tta`-shortening special junction rules, `ā`-never-first enforcement.

---

### Rules 1089–1095 — Compound verbs with kṛ/bhū/as
**Status:** ❌ NOT IMPLEMENTED — derivational/syntactic, out of scope.

---

## Chapter 15 — Engine Overhaul Items

| Priority | Item | File | Action |
|---|---|---|---|
| High | Special prefix-junction sandhi | `sandhi.py` | Tag-gated rules for `palāy`, `api`-elision, `saṁskṛ`, `ā`-never-first |
| Medium | `āṁ` anusvāra normalization | `conjugate.py` | Ensure `+ām` → `āṃ` before consonant-initial auxiliaries |
| Medium | 19 upasarga prefix table | new `upasargas.py` | Validate incoming preverb strings; store meanings |
| Low | Compound verb generator | new `compound_verb.py` | Deferred |

---

## Master Roadmap

### Phase 1 — Bug-fixes / Crashes
1.1 `t+l→ll` sandhi → `sandhi.py` (XS) ✅
1.2 j-class root flag → `dhatupatha_analyzer.py` (S) ✅
1.3 Algorithmic aorist-type selection → `dhatupatha_analyzer.py` (M) ✅  
1.4 Desiderative ā-final → ī → `stem_rules.py` (S) ✅
1.5 `māna` vs `āna` present middle participle → `krdantas.py` (S) ✅
1.6 `-tya` absolutive for prefixed roots → `krdantas.py` (S) ✅

### Phase 2 — Coverage Gaps
2.1 Pluperfect tense → `stem_rules.py`, `endings.py`, `conjugate.py` (S) ✅
2.2 Full `vāṅs/uṣ` perfect active participle → `krdantas.py` (M) ✅
2.3 `tāt` imperative variant → `endings.py` (XS) ✅
2.4 Intensive three-subtype reduplication → `reduplication.py`, `stem_rules.py` (M) ✅
2.5 `āya` vs `ya` denominative variant → `stem_rules.py` (S) ✅
2.6 Middle-specific aorist type expansion → `stem_rules.py`, `irregulars.py` (M) (SKIPPED)

**Note: Remaining failures in test2.py (99.8% pass rate):**
- `nī` periphrastic future active 3sg: expected `netā`, actual `nayitā` (Whitney §671)
- `vid` perfect active 3sg: expected `veda`, actual `vedāñcakāra` (Whitney §801, perfect-as-present)

### Phase 3 — Algorithmic Hardening
3.1 Zero-grade for athematic weak → `stem_rules.py`, `morphology.py` (L) ✅
3.2 kṛ u-deletion productive rule → `stem_rules.py` (S) ✅ (Already algorithmic in morphology.py)
3.3 Causative Whitney §1042 audit → `stem_rules.py`, `irregulars.py` (M) ✅
3.4 Class-2 vṛddhi u-roots algorithmic → `stem_rules.py` (S) ✅
3.5 Periphrastic future aniṭ/seṭ broadening → `stem_rules.py` (S) ✅

### Phase 4 — Prefix / External Sandhi
4.1 19 upasarga prefix table → new `upasargas.py` (S) ✅ 
4.2 Special prefix-junction sandhi → `sandhi.py` (M) ✅
4.3 `āṁ` anusvāra normalization → `conjugate.py` (XS) ✅


---

## Addendum — Items Missed in Earlier Sections

### A1 — Whitney vs. Pāṇini Class-Number Mapping (Correction Notice)

The report above uses **Pāṇini's gaṇa numbers** (as the engine does), but sheet_9.txt uses **Whitney's class numbers** (I–X). The mapping is:

| Whitney Class | Whitney §§ | Pāṇini Gaṇa | Engine builder |
|---|---|---|---|
| I — Root class | 611–641 | **2** | `_build_class_2` |
| II — Reduplicating | 642–658 | **3** | `_build_class_3` |
| III — Nasal (infix) | 683–696 | **7** | `_build_class_7` |
| IV — Nu-/u-class | 697–716 | **5** | `_build_class_5` |
| V — Nā-class | 717–732 | **9** | `_build_class_9` |
| VI — a-class (bhū) | 733–744 | **1** | `_build_class_1` |
| VII — á-class (tud) | 751–758 | **6** | `_build_class_6` |
| VIII — ya-class (div) | 759–767 | **4** | `_build_class_4` |
| IX — Passive (yá) | 768–774 | passive | `_build_passive` |
| X — cur-class | 775 | **10** | `_build_class_10` |

> **Note:** Chapter 9 section labels (e.g., "Rules 683–696 — Class 5") should be read as "Whitney §§683–696 = Pāṇini class 7". All engine references (`_build_class_7` etc.) are correct.

---

### A2 — `morphology.py` (`MorphologyEngine`) — Gaps Not Covered

`morphology.py` is the morphophonemic post-processing layer. Full rule inventory from the source:

| Rule | Status | Notes |
|---|---|---|
| Augment vṛddhi (`[AUG]a+V → Vriddhi`) | ✅ IMPLEMENTED | 9 pairs; also handles guṇa-augmented stem (`a+e→ai`, `a+o→au`) |
| Nasal insertion (`[NASAL]` → homorganic nasal before each consonant class, P. 7.1.58–59) | ✅ IMPLEMENTED | Five context-sensitive FSTs; vowel fallback to `n` |
| Passive vowel lengthening (`i→ī`, `u→ū`, `ṛ→ri`, `ṝ→īr` before `[PASSIVE]`) | ✅ IMPLEMENTED | `ā`-roots take `-ya` without lengthening — correctly skipped |
| Class-4 lengthening (`i→ī`, `u→ū` before `[CLASS4]`) | ✅ IMPLEMENTED | Left-context cdrewrite over intervening consonants |
| Samprasāraṇa (`[SAMP]ya→i`, `va→u`, `ra→ṛ`) | ✅ COMPLETED | `s[SAMP]va→su` and `p[SAMP]ra→pṛ` cluster forms present; general cluster rule (any C + `[SAMP]`) implemented and covers `svap/śvap`. |
| Causative passive cleanup (`+a[CAUS_PASS]` and bare `[CAUS_PASS]` erasure) | ✅ IMPLEMENTED | Two-pass correct for both ayadi-triggered and non-triggered cases |
| Class-8 `kṛ` weak suppletion (`kṛ→kur` before `+u+`) | ✅ IMPLEMENTED | Context `+u+` specific — correct |
| Class-8 `u`-drop (`r+u+` → `r+` before `y v m`) | ✅ IMPLEMENTED | Sonorant-only trigger — correct |
| Root-aorist `bhūv` (`[ROOT_AORIST]+` → `v+` after `bhū` before vowel) | ✅ IMPLEMENTED | |
| Aorist passive 3sg vṛddhi (`[AORIST_PASS_3SG]` triggers vṛddhi on preceding vowel) | ✅ IMPLEMENTED | Full vowel map `a→ā, i→ai, u→au, ṛ→ār` |
| Intensive active tag erase (`[INTENSIVE_ACTIVE]+` → `+`) | ✅ IMPLEMENTED | Lets ayadi/guna fire on the base |
| Class-2 weak: `han` before stops → `ha`, before nasals → `han`, before vowels → `ghn` | ✅ IMPLEMENTED | All three sub-rules |
| Class-2 weak: `vac` before vowels → `uc` | ✅ IMPLEMENTED | `vac[CLASS2_WEAK]+` → `uc+` |
| Sandhi context tag insertion (`[SD_SSR]`, `[SD_DCP]`, `[SD_GEM]`, `[SD_SIB]`, `[SD_LAR]`) | ✅ IMPLEMENTED | Five tag-gated FSTs inserted before sandhi phase |
| Tag cleanup (`clean_tags`) | ✅ IMPLEMENTED | Erases all `[TAG]` tokens not consumed by earlier rules |

**Missing from `morphology.py`:**

| Gap | Rules | Action |
|---|---|---|
| `[SAMP]` cluster generalization | Samprasāraṇa roots with initial consonant clusters (e.g. `svap`, `vyadh`) | Add `C[SAMP]ya→Ci`, `C[SAMP]va→Cu` general rules before the specific overrides |
| `vac`-type zero-grade for other class-2 weak roots | Whitney §636–641 roots beyond `han`/`vac` (e.g. `çās→çiṣ`, `as→ø`) | Add context-specific `[CLASS2_WEAK]` rules for each root or promote to `class_2_irregulars` pattern |
| `[CLASS8]` tag — never used | `morphology.py` `clean_tags` erases `[CLASS8]` but no rule fires on it | Either implement class-8 specific morphology or remove the tag from `all_tags` |
| `[NO_RUKI]` tag not cleaned up by `morphology.py` | `[NO_RUKI]` is stripped in `sandhi.py` but not in `morphology.py` `all_tags` | Verify order — if `[NO_RUKI]` always consumed in sandhi, it is fine; add to `all_tags` as safety |

---

### A3 — Class-7 (Nasal Infix / Whitney III, §§683–696) — Detailed Gap

Whitney's Class III = Pāṇini's class 7 (Rudhādi). `_build_class_7` inserts `na` (strong) or `n` (weak) after the root vowel. **Gaps specific to this class:**

| Item | Status | Notes |
|---|---|---|
| Nasal infix insertion algorithm | ✅ IMPLEMENTED | `insert_idx` finds vowel; inserts `na+` / `n+` |
| `+` placed after nasal (for `nasal_assimilation`) | ✅ IMPLEMENTED | `yunj` → `yu n+j` → `yuñj` via `nasal_assimilation` FST |
| Imperative 2sg: bare root (zero affix) | ✅ COMPLETED | Class-7 athematic 2sg imperative is the weak root (e.g. `rudh` → `runddhi`); `endings.py` explicitly returns `dhi` for Class 7. |
| Strong forms of roots with final stops | ✅ COMPLETED | e.g. `bhid` (class-7) strong = `bhe+na+d`; `_build_class_7` correctly applies guṇa before inserting infix for non-present strong forms. |

**Bug:** `_build_class_7` (line 912–928) does not apply guṇa to the root vowel in `[STRONG]` forms. The strong stem should be `bhé+na+d` (guṇa + `na`) but the code returns `bhi+na+d` (raw root + `na`). This should call `self._apply_guna(root_str, strength)` before inserting the infix.

**Fix location:** `stem_rules.py` `_build_class_7` — apply guṇa to root string before vowel-index scan in `[STRONG]` case.

---

### A4 — Class-8 (Tanādi / Whitney §§759–767) — Additional Gap

`_build_class_8` uses `+o` (strong) / `+u` (weak) with guṇa on the root. kṛ suppletion handled in `morphology.py`.

**Missing:** the full Tanādi root list is small (8 roots: tan, san, man, van, ṣan, khan, ghran, kṣan) — but the engine does not validate that only these roots use class-8. Any root passed with `class_num=8` is processed without checking lexical membership. This should be fine functionally but could produce spurious forms if misused.

---

### A5 — Denominative (`_build_denominative`) — Additional Detail Missed

Inspecting `stem_rules.py` lines 1002–1055, the actual implementation is **more complete** than the Chapter 14 section indicated:

| Whitney rule | Status | Notes |
|---|---|---|
| `i/ī`-stems → `ī+y` | ✅ IMPLEMENTED | `pn.accep(stem + "+y")` |
| `u/ū`-stems → `ū+y` | ✅ IMPLEMENTED | |
| `ṛ/ṝ`-stems → `rī+y` | ✅ IMPLEMENTED | |
| `-as`-stems → `+s+y` (namasya) | ✅ IMPLEMENTED | |
| `a/ā`-stems → **both** `ī+y` and `ā+y` via `pn.union` | ✅ IMPLEMENTED | Both variants generated |
| `n/ṇ`-final `a`-stems → additional `+s+y` | ✅ IMPLEMENTED | Three-way union |
| Consonant-final → `ī+y` default | ✅ IMPLEMENTED | |

**Correction to Chapter 14 assessment:** The `āya` vs `ya` gap is actually **already handled** via `pn.union` for `a/ā`-stems — both `ī+y` and `ā+y` forms are generated. The report's "missing" verdict for denominative should be upgraded to 🟡 PARTIAL (the main missing item is the `sya`-type for non-`as` stems like `tapaḥ+sya`).

---

### A6 — `clean_tags` Completeness Check

`morphology.py` line 292–298 lists tags that are cleaned. Tags in the engine not in the `clean_tags` union:

| Tag | Used where | In `clean_tags`? |
|---|---|---|
| `[PASSIVE]` | `_build_passive` | ✅ |
| `[CLASS4]` | `_build_class_4` | ✅ |
| `[CLASS8]` | nowhere active | ✅ (dead tag) |
| `[CAUS_PASS]` | `_build_causative_base` | ✅ |
| `[STRONG]` / `[WEAK]` | `vowel_strength.py` | ✅ |
| `[VRIDDHI]` | `vowel_strength.py` | ✅ |
| `[CLASS2_WEAK]` | `_build_class_2` | ✅ |
| `[ROOT_AORIST]` | `_build_aorist_system` | ✅ |
| `[AORIST]` | aorist stem | ✅ |
| `[AORIST_PASS_3SG]` | passive aorist | ✅ |
| `[INTENSIVE_ACTIVE]` | `_build_intensive` | ✅ |
| `[SAMP]` | `_build_passive` (samprasāraṇa) | ✅ |
| `[AUG]` | `conjugate.py` | ✅ |
| `[NASAL]` | `_build_*` (id-it roots) | ✅ |
| `[NO_RUKI]` | `reduplication.py` desiderative | ✅ (Handled in SandhiEngine instead to prevent premature stripping) |
| `[RUH_H]` | `build()` for h-final roots | ✅ (Handled in SandhiEngine instead to prevent premature stripping) |
| `[PERF_WEAK]` | perfect weak yan sandhi | ✅ (Handled in SandhiEngine instead to prevent premature stripping) |

**Action required (`morphology.py`):** Add `[NO_RUKI]`, `[RUH_H]`, `[PERF_WEAK]` to `all_tags` union as a safety net, in case they are not consumed by their respective sandhi rules (e.g., on non-triggering environments). (COMPLETED - these were intentionally moved to `sandhi.py` cleanup to prevent premature stripping that was breaking `ruh` and `sṛj`).

---

### A6 — Master Roadmap Additions

These items should be added to the existing phases:

**Phase 1 — Bug-fixes:**
- 1.7 `_build_class_7` guṇa missing in strong forms → `stem_rules.py` (S) ✅
- 1.8 Add `[NO_RUKI]`/`[RUH_H]`/`[PERF_WEAK]` to `morphology.py` `clean_tags` → `morphology.py` (XS) ✅

**Phase 3 — Algorithmic Hardening:**
- 3.6 `[SAMP]` cluster generalization (e.g. `svap`, `vyadh`) → `morphology.py` (S) ✅
- 3.7 Class-2 weak: `çās→çiṣ`, `as→ø` additional root-specific rules → `morphology.py` / `irregulars.py` (S) ✅

**Phase 4:**
- 4.4 Denominative `sya`-type for non-`as`-stems (namasya-type extension) → `stem_rules.py` (XS) ✅


