# Sanskrit Engine Phonology Audit
## Cross-referenced against Whitney Chapter 3 Rules Table

This audit compares the current FST engine (`sandhi.py`, `morphology.py`,
`vowel_strength.py`, `reduplication.py`, `alphabet.py`, `conjugate.py`) against
the phonological rules extracted from Whitney's Chapter 3.  Each section
identifies: what the rule requires, what the engine currently does, the gap or
bug, and a recommended fix.  Severity ratings:

- **CRITICAL** — produces wrong forms or crashes
- **MAJOR** — produces forms that fail tests; needs rule encoding
- **MODERATE** — partially correct; needs extension or edge-case handling
- **MINOR** — missing optional variants or incomplete coverage
- **ARCH** — architectural or coding-practice problem regardless of correctness

---

## 1. Vowel Sandhi

### 1.1 Like-vowel coalescence (Whitney §125–126) — MODERATE
**Rule:** Two adjacent identical vowels (same quality, any length) → long vowel.
`a+a=ā, i+i=ī, u+u=ū, ṛ+ṛ=ṝ`.

**Engine (`sandhi.py → savarna`):**
```python
# i+i is intentionally excluded — comment says "perfect weak yan handles it"
self.savarna = pn.cdrewrite(pn.string_map([
    ("a+a", "ā"), ("a+ā", "ā"), ("ā+a", "ā"), ("ā+ā", "ā"),
    ("i+ī", "ī"), ("ī+i", "ī"), ("ī+ī", "ī"),
    ...
```

**Gap:** `i+i → ī` is intentionally absent. The comment says *"perfect weak yan
handles it"*, but `yan_sandhi` only fires `i+ → y` **before vowels** (right-
context `ALPHABET.vowels`). When the second `i` is the leftmost vowel of a
suffix (a common slot), both rules may apply or neither. The interaction is
undocumented and untested. If the present-system `3pl middle -ire` follows an
`i`-final stem, `savarna` must fire first, not `yan`.

**Fix:** Add `("i+i", "ī")` to `savarna`; document that it takes priority over
`yan_sandhi` because `savarna` runs first in the pipeline. Add a regression test
for `i`-final roots + `-ire`.

---

### 1.2 `a/ā + dissimilar vowel` (Whitney §127) — MODERATE
**Rule:** `a/ā + i/ī → e`, `a/ā + u/ū → o`, `a/ā + ṛ/ṝ → ar`, `a/ā + ḷ/ḹ → al`,
`a/ā + e/ai → ai`, `a/ā + o/au → au`.

**Engine (`sandhi.py → guna_sandhi`):**  Covers the `a+i/ī → e`, `a+u/ū → o`,
`a+ṛ → ar`, `a+ḷ → al` cases correctly.

**Thematic merger covers `a + diphthong`** (`a+e→e`, `a+o→o`, `a+ai→ai`,
`a+au→au`).

**Gap — Rule 136a (Whitney augment vṛddhi):** The Whitney rule says that when
the augment `a` is followed by a vowel-initial stem, the combination yields
**vṛddhi** (`ai, au, ār`), not guṇa (`e, o, ar`). The engine correctly handles
this via `[AUG]` tag + `augment_vriddhi` in `morphology.py`. However:

1. `[AUG]a+ā → ā` is in the map, but `[AUG]a+e → ai` and `[AUG]a+o → au` are
   also present. The issue is that vṛddhi after augment applies only when the
   **root vowel** is `i/u/ṛ`; if the root has already undergone guṇa (e, o, ar),
   the augment should yield vṛddhi of the **original** vowel, not the guṇa form.
   Encoding `[AUG]a+ar → ār` is correct; `[AUG]a+al → āl` is correct. But
   `[AUG]a+e → ai` effectively reverses guṇa-then-augment ordering — this is
   only correct if the stem FST emits `e` (guṇa already applied) and the augment
   is prepended afterwards. The pipeline order in `conjugate.py` prepends the
   augment **after** the stem FST is built, so `stem = a+` + `(e-stem)`. This
   works numerically but is **phonologically backwards**: the rule should be
   `a + i → ai` (augment meets the root vowel), not `a + e → ai` (augment meets
   guṇa). The engine produces correct output in practice via table look-up, but
   the architecture is opaque and will break on edge cases (e.g. diphthong-initial
   roots such as `edh`, `īḍ`).

**Recommended fix:** Do not apply guṇa before prepending the augment in the
imperfect/aorist path. Apply the augment at the raw root vowel level, then
trigger vṛddhi directly via rule 136a. This is a moderate architectural refactor
of how `f.augment` interacts with `StemBuilder`.

---

### 1.3 `i/u/ṛ` → semivowel before dissimilar vowel (Whitney §129) — MODERATE
**Rule:** Final `i/ī → y`, `u/ū → v`, `ṛ → r` before a dissimilar vowel.
Whitney §129a: *sometimes `iy/uv` instead of `y/v`* when preceded by a conjunct
consonant.

**Engine (`sandhi.py → yan_sandhi`):**  Implements `i→y, ī→y, u→v, ū→v, ṛ→r`
globally before `ALPHABET.vowels`. The `perfect_yan_conjunct` rule adds `iy/uv`
after a conjunct.

**Gap:** `perfect_yan_conjunct` uses `conjunct = consonants + "" + consonants`
as left-context, but that pattern is not well-formed as a pynini FST context.
In `cdrewrite`, the left context must match what **immediately precedes** the
rewrite target. A two-consonant context requires a proper closure or alternation.
The pattern as written likely does not fire for all intended inputs.

**Fix:** Rewrite the conjunct context using proper FST idiom:
```python
any_cons = ALPHABET.consonants
conjunct_context = any_cons + any_cons  # two consecutive consonants directly before
```
and verify with a test case for `√vij` (class 7, middle perfect: `vivijur` vs
`vivijiyur`).

---

### 1.4 Diphthong sandhi / ayadi (Whitney §131–132) — MAJOR
**Rule (internal):** `e/o/ai/au + V → ay/av/āy/āv`.
**Rule (external):** `e/ai + V → a + hiatus` (the y-element is dropped);
`o/au + V → av` (v retained). After final `e/o`, following initial `a` is
elided (Whitney §135).

**Engine (`sandhi.py → ayadi`):**
```python
self.ayadi = pn.cdrewrite(
    pn.string_map([("e+", "ay"), ("o+", "av"), ("ai+", "āy"), ("au+", "āv")]),
    "", pn.union(ALPHABET.vowels, "y"), self.sig
)
```

**Gaps:**
1. **This fires for both internal and external sandhi** with no distinction. The
   engine is a word-internal morpheme-boundary engine, so this is acceptable for
   current scope — but the comment in `sandhi.py` docstring does not state this
   limitation. When external sandhi is added, a dialect flag will be needed.
2. **Whitney §135 elision** (`e/o + a → e/o` + avagraha) is not implemented.
   Currently `e + +a` would go through `thematic_merger` and collapse to `e`,
   which numerically produces the same form but for the wrong reason (it looks
   like same-diphthong absorption, not the §135 rule). This will matter once
   the engine is extended to sandhi across word boundaries.
3. **No avagraha marker** is output. This is acceptable if IPA/IAST output
   only, but document it explicitly.

---

### 1.5 Pragṛhya (exempt vowels, Whitney §138) — MAJOR MISSING
**Rule:** Dual endings in `ī/ū/e`, pronoun `amī`, certain Vedic locatives,
protracted vowels, and interjection-finals are **exempt from all vowel sandhi**.

**Engine:** No pragṛhya flag exists anywhere. Dual endings `(ī, e)` will
currently undergo `savarna` or `yan_sandhi` erroneously when followed by an
initial vowel in the next word.

**Fix (priority: external sandhi scope):** Add a `[PRAGRHYA]` tag in
`alphabet.py`. Emit this tag from the endings table for dual forms (`-ī`, `-e`,
`-ū`). In `sandhi.py`, add a rule that **erases** `[PRAGRHYA]` but leaves the
vowel untouched (i.e., the tag acts as a sandhi-inhibitor). Required before any
external sandhi work.

---

## 2. Consonant Sandhi

### 2.1 Permitted word-finals (Whitney §122, §141, §150) — CRITICAL gap
**Rule (§122/§141/§150):** A word may end in at most **one** consonant. That
consonant must be a non-aspirate surd mute (`k, ṭ, t, p`), a nasal (`n, m, ṇ`),
visarga, or anusvāra. Aspirates, sibilants (except via visarga), sonant mutes,
and palatals are forbidden word-finally.

**Engine:** `cluster_reduction` in `sandhi.py` partially handles this:
```python
self.cluster_reduction = pn.cdrewrite(
    pn.string_map([("ṣṭ", "ṭ"), ("k+t", "k"), ("gdh", "k")]),
    "", pn.union("[EOS]", "+[EOS]"), self.sig
)
```

**Gaps:**
1. Only three specific clusters are reduced. **Arbitrary clusters** at word-final
   are not reduced. For example, `vak+s` → `vaks[EOS]` would not reduce to
   `vāk` correctly.
2. **Final sibilants → visarga** is handled by `visarga` rule, which is correct.
   But final **palatal mutes** (`c, j`) are not reverted to `k` before
   `[EOS]`. Whitney §142: final `c → k`. This reversion is missing.
3. **Final aspirates** (e.g. `dh → t`, `bh → p`) must be de-aspirated in
   word-final position. The `devoicing` rule only fires before `unvoiced_triggers`
   (surd suffix initials), not before `[EOS]`. Add `[EOS]` to the devoicing
   trigger set.
4. **Sonant finals** (`d, b, g, j`) must also become surd before `[EOS]`. Same
   fix: add `[EOS]` to `devoicing` trigger set.
5. **Rule 150 (single-consonant):** There is no general cluster truncation at
   `[EOS]`. Final `sṭ → ṭ`, `sth → t`, `ṭh → ṭ`, etc. need rules or a general
   stripping routine.

**Fix:** Add comprehensive permitted-finals normalization as a dedicated phase
that runs *before* visarga, using `[EOS]` as the anchor. Sequence:
1. Palatal reversion: `c/j → k` before `[EOS]`.
2. Sibilant → visarga (already present).
3. Devoicing + de-aspiration before `[EOS]`.
4. Cluster reduction to single consonant (Whitney §150: drop rightmost until
   one remains). A loop-based FST composition or priority rewriting achieves this.

---

### 2.2 Aspiration throwback / Grassmann's Law (Whitney §155) — MAJOR
**Rule (§155):** Specific roots (`dah, dih, duh, druh, bandh, bādh, budh, dabh`
etc.) — when their **final** aspirate is deaspirated (before a surd or word-
final), the initial consonant of the root **restores aspiration**. This is
sometimes called Grassmann's Law throwback.

**Engine (`sandhi.py → grassmann_throwback`):**
```python
self.grassmann_throwback = pn.cdrewrite(
    pn.string_map([("b", "bh"), ("d", "dh"), ("g", "gh")]),
    "", ALPHABET.vowels + pn.union("gh","dh","bh","h","gdh") + throwback_triggers,
    self.sig
)
```

**Critical bug:** The right-context requires the initial consonant to be
*followed by a vowel and then an aspirate and then a trigger*. This pattern is
not how Grassmann's Law works. The law is about **two aspirates in the same
root**. The trigger is: the **second** (final) aspirate is being deaspirated by
a suffix, causing the **first** (initial) aspirate of the root to also
deaspirate (or in the throwback direction: when the final is already de-
aspirated by sandhi, the initial re-aspirates).

The current right-context combines vowels + aspirate + surd trigger, which would
only match things like `b...bh...+t`. This is too narrow and will miss most
cases. More importantly, it encodes the wrong direction: it tries to *aspirate*
`b→bh` in a context that includes an aspirate to the right, which is the wrong
directionality.

Whitney §155 (correctly stated):
- Root has **initial** `dh/bh/gh` (aspirate).
- Root's **final** consonant was originally aspirate but has been deaspirated by
  a following suffix.
- When the final aspirate deaspirates, the initial aspirate is **restored** if
  the two aspirates share the same root syllable.

Example: `√duh` class 2, 2sg impv active: `dugdhi`.
- `duh + dhi → duh+dhi` → Bartholomae → `dug+dhi` → throwback restores initial:
  `dhug+dhi` → `dugdhi`... actually Whitney gives `dugdha` for PPP. This
  interaction requires root-level tracking.

**Fix:** This rule needs a root-level flag (`is_initial_aspirate`) rather than a
pure FST rewrite. The root's initial consonant should aspirate when the FST
detects that the root's final aspirate has been de-aspirated. Add
`is_duh_class: bool` to `RootObject` (citing Whitney §155b) and implement the
aspiration restoration as a morphology tag `[ASPIRE_INIT]` on roots that carry
it.

---

### 2.3 Bartholomae's Law (Whitney §160) — MODERATE
**Rule (§160):** Final sonant aspirate (`gh, dh, bh, jh`) + dental `t/th` →
the root-final consonant deaspirates and voices; the dental assimilates and
aspirates: `gh+t→gdh`, `dh+t→ddh`, `bh+t→bdh`. The **aspiration transfers
forward** (progressive assimilation).

**Engine:**
```python
self.bartholomae_general = pn.cdrewrite(pn.string_map([
    ("bh+t","bdh"), ("bh+th","bdh"),
    ("dh+t","ddh"), ("dh+th","ddh"),
    ("gh+t","gdh"), ("gh+th","gdh"),
    ...
```

**This is correctly implemented for the main cases.** However:

**Gaps:**
1. Whitney §160a: `h` (representing original `gh` in roots like `√dah, √dih`) follows
   the same law. The `bartho_ht` rule (`h+t→gdh`) handles this, but only for
   bare `h`, not for `ruh/vah` class where the `h` is final after a sonorant.
   The `bartho_hth`, `bartho_hdh` rules exist but ordering relative to the
   `h_to_k` rule is fragile: `h_to_k` fires `h→k` before `+s/+ṣ` after vowels,
   which may interfere with Bartholomae paths if `+s` is not the suffix here.
2. Whitney §160c: `dadh` (from √dhā) follows the **normal (surd)** method, not
   Bartholomae. The engine does not special-case `dadh + t → datt(a)`. This is
   currently likely handled via `perfect_stem_overrides` but should be documented
   as a rule-based exception citing §160c.
3. **Rule ordering:** `bartholomae_general` must run **before** `devoicing` and
   before `palatal_sandhi`. The current ordering in `consonant_phase` appears
   correct, but it should be documented explicitly.

---

### 2.4 Surd/sonant assimilation (Whitney §117a, §157/159) — MAJOR gap
**Rule (§157/159, external):** In external combination, a final surd is
**voiced** before a sonant initial (vowel, semivowel, nasal, sonant mute).

**Engine:** `devoicing` rule fires before `unvoiced_triggers` (surd initials).
There is **no voicing rule** (surd→sonant before sonant). The current engine
handles only the internal case partially.

**Gap:** `vāk + ā- → vāg + ā-`, `tad + hi → tad + dhi` (rule 163). The
external voicing rule is absent. This is a known scope limitation (no external
sandhi), but it means any compound verb forms with preverb junctions ending in a
surd will be wrong before vowel-initial preverbs. For example, `ud + √i → udi`
requires `d` to be sonant (it already is), but `at + √i → `ad+i` requires `t→d`.

**Fix:** For the preverb junction case (within `conjugate.py`, where preverbs
are concatenated with `+`), add a voicing rule that fires before vowel/nasal/
semivowel/sonant-mute **at a preverb boundary**. This is internal to the engine's
scope.

---

### 2.5 Final c reversion (Whitney §217) — MAJOR MISSING
**Rule (§217):** Root-final `c` before obstruents/sibilants → `k`. Then `k`
follows standard k-combination rules.

**Engine:** `palatal_sandhi` converts `j/c → k` before `unvoiced_triggers`
(surd dentals/sibilants etc.). This partially covers it.

**Gap:** `palatal_sandhi` targets **surds** (`+t, +th, +s, +ṣ, +c, +ch, +k,
+kh, +p, +ph, +ṭ, +ṭh`) but not `[EOS]` and not **sonant** obstruents. Whitney
§217a says in **external** combination, `c→k` first, then `k` sonantizes before
a sonant-initial word. The engine misses:
- `c → k` before `[EOS]`
- `c → g` before sonant initials (after first converting to `k`, then applying
  voicing rule §157)

---

### 2.6 Final ç (ś) behaviour (Whitney §218) — MAJOR MISSING
**Rule (§218):**
- `ś + s → kṣ`
- `ś + t/th → ṣṭ/ṣṭh` (retroflexion)
- `ś + dh/bh/su/final → ṭ/ḍ` (becomes lingual mute)

**Engine:**
- `palatal_sibilant_retroflex` (tag-gated `[SD_SSR]`) handles `ś+t → ṣṭ` — ✅
- Sibilant cluster `ś[SD_SIB]+s → kṣ` (tag-gated) — ✅ for this case
- **Missing:** `ś + dh → ḍh`, `ś + bh → ḍ`, `ś + final → ṭ`. The engine has
  no rule for `ś` before voiced aspirates or at `[EOS]`.

**Fix:** Add rules for `ś` before voiced aspirates and at word-final. These
should be added to `consonant_phase`:
```python
# Whitney §218: ś + dh → ḍh; ś + bh → ḍ; ś + final → ṭ
("ś+dh", "ḍh"), ("ś+bh", "ḍ")
```
And add `ś → ṭ` before `[EOS]` in the permitted-finals normalization pass.

---

### 2.7 Final j: two classes (Whitney §219) — MAJOR MISSING
**Rule (§219):** Root-final `j` divides into two classes:
- **yuj-class** (~20 roots): treated like final `c` → `k` before surds, `g`
  before sonants.
- **mṛj-class** (~7 roots: `mṛj, sṛj, bhrajj, rāj, etc.`): treated like `ś`
  → `ṣ/ṭ` environment-depending.

**Engine:** `j_retroflex` handles a few specific `rj`, `yaj`, `ij` patterns
explicitly. `palatal_sandhi` converts `j → k` before unvoiced triggers. The
`mṛj`-class is not separated.

**Gap:** There is no `j`-class membership in `RootObject`. The engine currently
applies `j → k` to all j-final roots via `palatal_sandhi`, which is correct for
yuj-class but wrong for mṛj-class (`sṛj+ta → sraṣṭa`, not `srakt`).

**Fix:** Add `is_mrj_class: bool` flag to `RootObject`. Populate from a small
explicit list (Whitney §219c lists ~7 roots). In `consonant_phase`, add a
`[MRJ]`-tagged rule that applies `ç`-type reversion before the general `j→k`
palatal sandhi rule fires.

---

### 2.8 Final h: two classes (Whitney §222) — MAJOR MISSING
**Rule (§222):**
- **duh-class** (roots: `duh, muh, druh, snuh, snih`): `h → gh` → follow
  `gh`-combination rules.
- **ruh-class** (roots: `vah, sah, mih, rih, guh, ruh, nah, dah, dih`):
  `h + dental t/th/dh` → complex: remove `h`, lengthen preceding short vowel,
  change dental to lingual sonant aspirate. E.g. `ruh + ta → rūḍha`.

**Engine:** The `bartho_ht / bartho_hdh / bartho_hth` rules fire for `h+t/dh`
and produce `gdh`. This is only correct for **duh-class** roots. For ruh-class
the expected output is `ūḍha`, `āḍha`, etc. — the engine will produce wrong
forms.

**Gap:** There is no `h`-class membership in `RootObject`. All `h`-final roots
go through the Bartholomae rules.

**Fix:** Add `is_ruh_class: bool` to `RootObject`. Populate from Whitney §222b
list. Implement the ruh-class transformation as a morphology tag `[RUH_H]` that
triggers: vowel lengthening + h-deletion + dental→lingual-aspirate. The
interaction with Bartholomae must be ordered (ruh-class check fires **before**
Bartholomae).

---

### 2.9 Final ṣ behaviour (Whitney §226) — MODERATE MISSING
**Rule (§226):**
- `ṣ + t/th → ṣṭ/ṣṭh` (already implemented via `retro_t / retro_th`)
- `ṣ + dh → ḍḍh` (Whitney §226b — double lingual aspirate)
- `ṣ + bh/su/final → ṭ/ḍ`

**Engine:** `retro_t` and `retro_th` cover `ṣ+t→ṣṭ` and `ṣ+th→ṣṭh`. `retro_dhv`
covers `ṣ+dhv→ḍhv`. But `ṣ + dh → ḍḍh` and `ṣ + final → ṭ` are not implemented.

**Fix:** Add `("ṣ+dh", "ḍḍh")` to the consonant rules. Add `ṣ → ṭ` at `[EOS]`
in the permitted-finals normalization pass.

---

### 2.10 Deaspiration before obstruents (Whitney §114, §153) — MODERATE
**Rule (§153):** An aspirate mute loses aspiration before another non-nasal mute
or sibilant (internal combination).

**Engine:** `ReduplicationEngine.deaspirate` applies aspiration loss within the
reduplication prefix — but this is only for the prefix, not for stem-suffix
boundaries. The `morphology.py` `nasal_*` insertion rules and other rules don't
de-aspirate aspirates before following obstruents at morpheme boundaries.

**Gap:** If an aspirate-final root is followed by a surd-initial suffix, the
engine relies on Bartholomae and `devoicing` to handle this, but de-aspiration
itself (`bh → b`, `dh → d` before surd mute) is not implemented as a rule.
Bartholomae handles `aspirate + t/th` specifically but not `aspirate + k/p/c`
etc.

**Fix:** Add a rule in `consonant_phase` for aspirate + non-nasal mute/sibilant
→ de-aspirated form. This must run **after** Bartholomae (to avoid interfering
with `bh+t → bdh`).

---

### 2.11 Nasal combinability and anusvāra (Whitney §117c, §212–213) — MODERATE
**Rule (§117c / §212):** Nasal `m` before a consonant becomes anusvāra; then
assimilates to the class of the following stop. Before semivowels / sibilants /
h it remains anusvāra `ṃ`.

**Engine:**
- `parasavarna` maps `m + stop → class nasal` ✅
- `anusvara` maps `m + semivowel/sibilant → ṃ` ✅
- `gamya_fix` explicitly reverses `gam+ya → gaṃya` back to `gam+ya` ❌

**Bug in `gamya_fix`:** Whitney §993 says `saṃgamya` (with anusvāra) is the
expected form. The fix reverts to `gam+y` explicitly, which will then cycle back
through `anusvara` on the next pass. This creates a feedback loop and is
semantically wrong. The correct form uses anusvāra or nasal assimilation.
**Remove `gamya_fix`** and document the correct treatment.

**Gap (Whitney §117c, external):** Before a sibilant in external combination, a
nasal + surd stop must be inserted between the nasal and the sibilant. This is
not implemented (external scope).

---

## 3. Long-Distance Rules

### 3.1 RUKI rule (Whitney §180, §184–188) — MODERATE
**Rule (§180):** `s → ṣ` immediately after `i, ī, u, ū, e, o, ai, au, k, r, ṛ`
(not `a, ā`); blocked by following `r` or at word-final position.

**Engine (`sandhi.py → ruki`):**
```python
ruki_triggers = pn.union("ṛ","r","u","ū","k","i","ī","e","ai","o","au")
self.ruki = pn.cdrewrite(pn.cross("s","ṣ"), ruki_triggers + pn.accep("+").star, "", self.sig)
```

**Gaps:**
1. **Blocking by following `r` is not implemented.** Whitney §181a says the
   change is blocked if `s` is followed by `r`. Add a negative lookahead or a
   counter-rule that reverts `ṣ → s` when followed by `r`.
2. **Word-final blocking** (RUKI does not apply to final `s` that becomes
   visarga) is unclear in the pipeline. The `visarga` rule runs **after** RUKI
   in `long_distance_phase`. If RUKI fires first on a final `s`, the `visarga`
   rule would then change `ṣ → ḥ` (sibilant → visarga). This chain is:
   `(vocalic trigger)s[EOS] → ṣ[EOS] → ḥ` which produces visarga for RUKI-
   affected finals — but the correct form is also visarga, so the output is
   accidentally correct. Document this so it isn't accidentally broken.
3. **Rule §184d exception:** In the desiderative, the reduplicated initial `s`
   is **exempt** from RUKI. No exemption tag exists. When a desiderative like
   `susrūṣā` is built, the `s` in the reduplication prefix after `u` would
   incorrectly become `ṣ`. Add `[NO_RUKI]` tag to desiderative reduplication
   prefixes.

---

### 3.2 Nati (Whitney §189) — MODERATE
**Rule (§189):** `n → ṇ` long-distance: if `ṣ/r/ṛ` precedes in the same word,
with no blocking consonant in between (palatals except `y`, linguals, dentals
block it).

**Engine:**
```python
triggers = pn.union("r","ṛ","ṣ","ṝ")
allowed_interveners = pn.union(
    ALPHABET.vowels, ALPHABET.gutturals, ALPHABET.labials,
    "y","v","h","ṃ","+"
).star.optimize()
self.nati = pn.cdrewrite(pn.cross("n","ṇ"), triggers + allowed_interveners, ...)
```

**Gaps:**
1. **`ṝ` (long ṛ)** is listed as a trigger in `triggers` but `ṝ` triggers nati
   in Whitney too — ✅ covered.
2. **`ṣ` as blocker:** Whitney says linguals block nati. `ṣ` is a lingual
   sibilant — if a second `ṣ` appears between the trigger `ṣ/r` and the target
   `n`, the second `ṣ` should block. But `ṣ` is not in the `allowed_interveners`
   set (correct — its absence means it blocks), BUT the trigger itself is `ṣ`.
   This means `ṣ...ṣ...n` would not trigger nati because the second `ṣ` blocks.
   This is correct per Whitney §189 footnote. ✅
3. **`ṅ, ñ` as potential outputs:** Only `n` targets are handled; `ṇ` is not
   targeted for further nati. This is correct.
4. **Performance risk:** `allowed_interveners.star.optimize()` builds a closure
   over a union of phonemes. This is a potentially exponential FST if the
   alphabet is large. Benchmark compilation time and consider a more efficient
   representation.

---

## 4. Vowel Strength: Guṇa / Vṛddhi (Whitney §235–237)

### 4.1 Guṇa in heavy syllables (Whitney §240) — MISSING
**Rule (§240):** Guṇa does **not** apply to a short vowel in a heavy syllable
ending in a consonant cluster. Example: `vind` (class 6) — the `i` is in a
heavy syllable and does not take guṇa in certain forms.

**Engine (`vowel_strength.py → apply_guna`):**
The guṇa FST fires on any vowel before `[STRONG]` regardless of syllable weight.
There is no syllable-weight check.

**Fix:** Before applying guṇa, compute syllable weight: if the root vowel is
short and followed by two or more consonants before the `[STRONG]` tag,
suppress guṇa. This requires either:
(a) A phonological weight-checker function in `VowelStrengthEngine`, or
(b) A `[HEAVY]` tag emitted by `StemBuilder` when the phonological context
warrants it, which gates a `no_guna_if_heavy` rule before `apply_guna`.

---

### 4.2 Vṛddhi map completeness — MINOR
**Engine (`vowel_strength.py → vriddhi_map`):**
```python
vriddhi_map = pn.string_map([
    ("a","ā"), ("i","ai"), ("ī","ai"), ("u","au"), ("ū","au"), ("ṛ","ār"), ("ṝ","ār"),
])
```
Missing: `ḷ → āl` (ḷ's vṛddhi). Whitney §237: `ḷ → āl`. Add `("ḷ","āl")`.

---

## 5. Reduplication (Whitney §259)

### 5.1 Reduplication of vowel-initial roots — MODERATE
**Rule (Whitney §590, §788):** Vowel-initial roots reduplicate by lengthening
the initial vowel (not by prefixing a consonant), e.g. `√ā + perf → ā` (uses
periphrastic). `√uc` → `uvoca`.

**Engine (`reduplication.py → _extract_initial_syllable`):**
The function always starts with the first consonant. For vowel-initial roots it
would start with the vowel (no consonant precedes). The syllable returned would
be just the vowel (`a`, `i`, etc.). Then `_reduce_via_fst` would apply
shortening/palatalization to just the vowel.

**Gap:** No special handling for vowel-initial roots. The result would be an
unreduced vowel prefix, which is wrong — vowel-initial roots take the
periphrastic perfect or have suppletive reduplication (e.g. `√uc → uvoca`).
These should be caught by `takes_periphrastic_perfect` in `dhatupatha_analyzer.py`,
which does detect vowel-initial roots. Verify that **all** vowel-initial roots
are caught by `_check_periphrastic` before `generate_prefix` is called on them.

---

### 5.2 Sibilant + stop reduplication order (Whitney §590) — IMPLEMENTED ✅
The sibilant `+ voiceless-stop → stop is reduplicated` rule is correctly
implemented in `_extract_initial_syllable` (Pāṇini 7.4.61). ✅

---

### 5.3 Desiderative exemption from RUKI (Whitney §184d) — MISSING
As noted in §3.1 above. The `generate_desiderative_prefix` does not emit any
`[NO_RUKI]` guard tag on the prefix consonant.

---

## 6. Architectural and Coding Issues

### 6.1 `[EOS]` tag is in `alphabet.py` but never emitted — CRITICAL ARCH
`alphabet.py` lists `[EOS]` in `tags_list`. `sandhi.py` uses it in `visarga`
and `cluster_reduction` rules:
```python
self.visarga = pn.cdrewrite(pn.string_map([("s","ḥ"),("ṣ","ḥ")]),
    "", pn.union("[EOS]","+[EOS]"), self.sig)
```
But **no rule in `morphology.py` or `conjugate.py` ever appends `[EOS]`** to
the end of the FST chain. `[EOS]` is never in the actual string, so these rules
**never fire**. The visarga rule therefore produces no visarga at all in the
current engine.

**Verification:** Check any form that should end in `ḥ` (e.g. `bhavati` ends in
`i`, fine; but `√as` 3sg present active `asti` ends in `i`; what about
`√as` 2sg `asi`? And 3sg nominal forms — different pipeline). For verb forms,
test `√pac` imperative 2sg active: `pacatāt` (no final `s`), `√pac` 3sg
present: `pacati` (no final `s`). The `ḥ` issue mainly affects noun-ending and
some verbal forms. **Audit which verb forms should end in visarga and verify
they do.**

**Fix:** Append `+[EOS]` to the combined FST in `conjugate.py` before calling
`sandhi.apply_all()`, or alternatively append it at the end of `MorphologyEngine.apply_all()`.
Ensure `clean_boundaries` in `sandhi.py` erases `[EOS]` at the very end.

---

### 6.2 `gamya_fix` introduces a rule-loop — CRITICAL BUG
```python
self.gamya_fix = pn.cdrewrite(
    pn.cross("gaṃ+y", "gam+y"), "", "", self.sig
)
```
This rule fires **after** `anusvara` (which wrote `gaṃ+y`). But `gam+y` will
then be re-processed by `anusvara` in a subsequent composition pass if the FST
is applied iteratively. In `cdrewrite`-based pipelines this is not a loop in the
mathematical sense (rules are applied once in a single linear pass), but the
logic is inverted: the intended grammar says `gam+ya → saṃgamya` **with**
anusvāra (Whitney §993 actually gives `saṃ+gam+ya → saṃgamya`). The fix undoes
the phonologically correct output. **Remove `gamya_fix`.**

---

### 6.3 No `[EOS]` means `cluster_reduction` and `visarga` are dead code — CRITICAL BUG
Consequence of 6.1: All rules triggered on `[EOS]` or `+[EOS]` are dead code.
This is a silent correctness failure — the engine does not crash, it just silently
omits visarga from all final-position transformations. This explains why
word-final forms like `√as` 3pl `santi` (which has no `s`, fine) but
`√as` 2sg `asi` → should be fine, but `√as + 3sg → asti` shows this is not
about `ḥ` for verb conjugation… **however `[EOS]` is also used in `grassmann_throwback`**
as a trigger context, meaning Grassmann's Law also never fires at word-final
position.

---

### 6.4 Sandhi tag architecture: ordering assumption fragility — ARCH
The `[SD_*]` tags are inserted by `MorphologyEngine.sd_boundary_tagging` (end of
`apply_all`) and consumed by `SandhiEngine.consonant_phase`. The ordering
relies on:
1. `morphology.apply_all()` completes fully (including `clean_tags`).
2. `sandhi.apply_all()` begins.

Between these two, the `[SD_*]` tags survive. But `clean_tags` in morphology
explicitly erases tags — it does **not** erase `[SD_*]` tags (correctly). This
is documented in the class docstring, but it is a fragile implicit contract.

**Risk:** If anyone adds a new tag (e.g. `[NEW_TAG]`) to `clean_tags`, they must
remember not to include `[SD_*]` variants. There is no enforcement.

**Fix:** Separate `clean_tags` into two FSTs: `clean_morph_tags` (everything
except `[SD_*]`) and `clean_sd_tags` (called at the end of `consonant_phase`
before `long_distance_phase`). This makes the contract explicit and avoids silent
breakage.

---

### 6.5 `shortestpath` appears in debug branches — ARCH (policy violation)
The `CLAUDE.md` states: *"DO NOT implement the shortest path trick"*. The debug
branches in both `MorphologyEngine.apply_all(debug=True)` and
`SandhiEngine._apply_rules_with_trace` fall back to `pn.shortestpath(fst)`:
```python
try:
    sp = pn.shortestpath(fst).string()
    print(f"    ⚠️  {name}: ambiguous, shortest='{sp}'")
```
While this is in a `print`/debug path and not returned to the caller, it still
calls `shortestpath`. Per project guidelines, **remove or guard** this with a
comment marking it as *display-only* and documenting why it is acceptable in a
debug context.

---

### 6.6 `lru_cache` on `conjugate` with mutable default argument — ARCH BUG
```python
@lru_cache(maxsize=4096)
def conjugate(self, root_str, class_num, person, number,
              voice="active", tense="present", derivative=None,
              use_db=True, auxiliary="kṛ") -> list[str] | str:
```
`lru_cache` on an instance method does **not** cache per-instance — it caches on
`self` as well as the other arguments. Since `self` is the same singleton
`SanskritConjugator`, this works. But the cache key includes `use_db=True` by
default. If the same form is called once with `use_db=True` and once with
`use_db=False`, the cache will return the first call's result for the second —
silently wrong in testing contexts. **Always pass `use_db=False` explicitly in
tests**, and consider splitting the cache into a `use_db=False`-only path.

---

### 6.7 `_stem_cache` is never invalidated — ARCH
The `_stem_cache` dict grows without bound on a long-running server. For a
language server or API, this is a memory leak. Use `functools.lru_cache` with a
`maxsize` on `_get_stem` instead of a plain dict, or document the intended
lifecycle.

---

### 6.8 `_find_raw` pass-2 fallback is too permissive — ARCH
```python
# Pass 2: any class
for entry in self._entries:
    clean = _clean(entry['raw'])
    for cand in candidates:
        if clean.startswith(cand):
            return entry
```
Pass 2 returns the first matching root regardless of class. For a root that
appears in multiple ganas (e.g. `√yaj` in class 1 and class 4), this returns
whichever entry appears first in the CSV. The result is that the wrong class's
flags (aniṭ, voice, aorist type) are used for the requested class. This silently
produces wrong forms without any warning.

**Fix:** Log a warning when pass 2 fires (the engine is using a cross-class
fallback) and include the root, requested class, and matched class in the warning.
Optionally, return `None` from pass 2 and let the caller handle unknown roots
explicitly rather than silently using wrong data.

---

### 6.9 Missing rule citations in sandhi.py — MINOR (policy)
Per `CLAUDE.md`: *"Add sources like Whitney 129.b when used."* The following
rules have no Whitney citation:
- `thematic_merger` — should cite Whitney §126 / §131
- `d_dh_gemination` — should cite Whitney §228 or Pāṇini 8.4.46
- `nj_cluster_hardening` — no citation; this appears to be a class-7 specific
  rule, cite Whitney §620 or Pāṇini source
- `velar_nasal` — should cite Whitney §212 / parasavarṇa
- All `retro_*` rules — cite Whitney §198 or Pāṇini 8.4.41
- `ksha_t_simplify` — cite Whitney §221 (kṣ+t→kt)
- `h_to_k` — cite Whitney §222 / Pāṇini 8.2.31

---

### 6.10 `alphabet.py` sigma_star includes `+` as a character — ARCH NOTE
The morpheme boundary `+` is part of `sigma_star`. This means `cdrewrite` rules
can accidentally match across morpheme boundaries if a rule does not explicitly
include or exclude `+`. Most rules use explicit `+` in patterns which is fine,
but `savarna`, `guna_sandhi`, and `yan_sandhi` fire on patterns like `a+ā` where
the `+` is the morpheme boundary — this is intentional. However, a rule that
matches just `"aa"` would **not** match `"a+a"` which is correct. Verify all
vowel rules explicitly use the `+` boundary in patterns.

---

## 7. Rules Table Items With No Engine Representation

The following Whitney §§ from the rules table have **no corresponding code**
anywhere in the current engine:

| Whitney §§ | Rule | Severity |
|---|---|---|
| §113 | Hiatus is forbidden; every non-initial syllable starts with a consonant | MINOR (scope: external sandhi) |
| §117c | Nasal before sibilant → anusvāra (internal) + insert surd externally | MODERATE |
| §118b | Dental mute lingualization before a lingual | MAJOR |
| §119 / §222 | Palatal/h two-class reversion (full matrix) | MAJOR |
| §122 / §141 / §150 | Permitted-finals normalization (full rule set) | CRITICAL |
| §135 | e/o + initial a → elision (avagraha) | MINOR (external) |
| §138 | Pragṛhya (exempt vowels) | MAJOR |
| §153 | General internal deaspiration before obstruents | MODERATE |
| §155 | Aspiration throwback / Grassmann root-flag | MAJOR |
| §157 / §159 | External surd→sonant voicing before sonant | MAJOR (external) |
| §161 | Final mute + nasal → class nasal (external) | MODERATE (external) |
| §162 | t + l → ll | MINOR |
| §163 | Final mute + h → sonant + aspiration (external) | MINOR (external) |
| §170–172 | Final `s` decision tree (full) | MODERATE |
| §174 | `s → r` before sonant (not after a/ā) | MODERATE |
| §175 | Final `as/ās` rules | MODERATE |
| §178–179 | Final `r` behavior | MODERATE |
| §184d | Desiderative exemption from RUKI | MAJOR |
| §218 (partial) | ś + dh/bh/final → lingual mute | MAJOR |
| §219 | j two-class membership | MAJOR |
| §222 | h two-class membership (ruh-class) | MAJOR |
| §226b | ṣ + dh → ḍḍh | MODERATE |
| §240 | Guṇa blocked in heavy syllable | MAJOR |
| §253 | Short a loss in weak syllables (zero grade) | MAJOR |
| §254–258 | Union vowels and inserted consonants (y/n insertion) | MODERATE |

---

## 8. Recommended Priority Order for Fixes

### Phase 1 — Stop Silent Failures (do first)
1. Fix `[EOS]` emission in `conjugate.py` so `visarga`, `cluster_reduction`,
   and `grassmann_throwback` actually fire (§6.1, §6.3).
2. Remove `gamya_fix` (§6.2).
3. Fix `_find_raw` pass-2 to warn/fail loudly (§6.8).
4. Add `("i+i","ī")` to `savarna` (§1.1).
5. Add `ḷ → āl` to vṛddhi map (§4.2).

### Phase 2 — Core Phonology Gaps (next sprint)
6. Implement permitted-finals normalization: palatal reversion §217, aspirate/
   sonant devoicing at `[EOS]`, single-consonant reduction §150 (§2.1, §2.5).
7. Implement `h`-class membership in `RootObject` + ruh-class transformation
   §222 (§2.8).
8. Implement `j`-class membership in `RootObject` + mṛj-class rules §219 (§2.7).
9. Fix Grassmann's Law rule logic (§2.2).
10. Add `ś + dh/bh/final → lingual` (§2.6).

### Phase 3 — Important Edge Cases
11. Syllable-weight check for guṇa blocking §240 (§4.1).
12. Zero-grade short-`a` loss §253 — needed for `han` weak forms (§7).
13. Pragṛhya flag for dual endings §138 (§1.5).
14. RUKI blocking by following `r` §181a (§3.1).
15. Desiderative RUKI exemption §184d (§5.3).

### Phase 4 — Architecture Cleanup
16. Separate `clean_morph_tags` / `clean_sd_tags` (§6.4).
17. Replace `_stem_cache` dict with `lru_cache` (§6.7).
18. Add Whitney citations to all uncited sandhi rules (§6.9).
19. Document `shortestpath` usage in debug branches (§6.5).
20. Audit `lru_cache` + `use_db` interaction (§6.6).
