import pynini as pn
from functools import lru_cache
from alphabet import ALPHABET
from vowel_strength import VowelStrengthEngine
from sandhi import SandhiEngine
from stem_rules import StemBuilder
from endings import SuffixProvider
from morphology import MorphologyEngine
from irregulars import ad_imperfect_active_overrides, perfect_bare_tha_roots


# ── Strength evaluation rule table ───────────────────────────────────────────
# Priority-ordered list of (predicate, strength_tag).
# Each predicate is a callable (class_num, person, number, voice, tense) → bool.
# The first matching rule wins.  Written as a module-level constant so it is
# constructed once and never rebuilt per-call.

_STRENGTH_RULES = [
    # 1. Passives always use a weak root
    (lambda c, p, n, v, t: v == "passive",
     "[WEAK]"),

    # 2. Future / Conditional always use strong (Guna) grade
    (lambda c, p, n, v, t: t in ("future", "conditional"),
     "[STRONG]"),

    # 3. Perfect: sg active = strong; everything else = weak
    #    Must come BEFORE thematic-class checks (thematic classes 1/10 would
    #    otherwise always return STRONG, breaking perfect du/pl weak forms).
    (lambda c, p, n, v, t: t == "perfect" and v == "active" and n == "sg",
     "[STRONG]"),
    (lambda c, p, n, v, t: t == "perfect",
     "[WEAK]"),

    # 4. Thematic classes: always strong root (cl4/6 stem_rules ignores grade)
    (lambda c, p, n, v, t: c in (1, 10),
     "[STRONG]"),
    (lambda c, p, n, v, t: c in (4, 6),
     "[WEAK]"),

    # 5. Imperative 1st person: STRONG regardless of voice
    #    Must come BEFORE the middle-voice check so that imperative middle 1sg
    #    gets the strong (guna) stem (karavai, not kurai).
    (lambda c, p, n, v, t: t == "imperative" and p == "1",
     "[STRONG]"),

    # 6. Optative: always weak root grade
    (lambda c, p, n, v, t: t == "optative",
     "[WEAK]"),

    # 7. Middle voice: always weak (applies only after imperative-1 check above)
    (lambda c, p, n, v, t: v == "middle",
     "[WEAK]"),

    # 8. Remaining imperative exceptions
    (lambda c, p, n, v, t: t == "imperative" and p == "2" and n == "sg",
     "[WEAK]"),

    # 8. Singular active = strong (main athematic rule)
    (lambda c, p, n, v, t: n == "sg",
     "[STRONG]"),

    # 9. cl3 imperfect 3pl is exceptionally strong (ajuhavuḥ)
    (lambda c, p, n, v, t: c == 3 and t == "imperfect" and p == "3" and n == "pl",
     "[STRONG]"),

    # 10. Default: weak
    (lambda c, p, n, v, t: True,
     "[WEAK]"),
]


def _evaluate_strength(class_num, person, number, voice, tense):
    """Return '[STRONG]' or '[WEAK]' by scanning the priority rule table."""
    for predicate, tag in _STRENGTH_RULES:
        if predicate(class_num, person, number, voice, tense):
            return tag
    return "[WEAK]"   # unreachable; last rule always matches


class SanskritConjugator:
    """Orchestrates the conjugation pipeline from root to inflected form.

    Pipeline
    --------
        root string
            │
            ▼
        StemBuilder.build()          – class/tense-specific stem FST
            │
            ▼
        augment prefix (a+)          – for imperfect / conditional
            │
            ▼
        + ending (from SuffixProvider)
            │
            ▼
        MorphologyEngine.apply_all() – passive lengthening, class-4/8 suppletion,
            │                          erase abstract tags
            ▼
        SandhiEngine.apply_all()     – vowel sandhi → consonant sandhi →
            │                          long-distance rules → erase boundaries
            ▼
        optimized string

    Caching
    -------
    Stem FSTs are expensive to build.  ``_stem_cache`` stores them keyed on
    ``(root_str, class_num, strength, tense, derivative)`` so repeated calls
    with the same parameters reuse the compiled FST.

    ``conjugate()`` is additionally wrapped with ``lru_cache`` so the final
    IAST string is returned immediately for warm calls without any FST work.
    """

    def __init__(self):
        self.strength_engine = VowelStrengthEngine()
        self.sandhi    = SandhiEngine()
        self.morphology= MorphologyEngine()
        self.stems     = StemBuilder(self.strength_engine)
        self.sigma     = ALPHABET.sigma_star

        # FST stem cache: (root, class, strength, tense, derivative) → FST
        self._stem_cache: dict = {}

        # ── Ending provider dispatch ──────────────────────────────────────────
        # Maps (tense, voice) → SuffixProvider static method.
        self._ending_dispatch = {
            ("present",    "active"):  SuffixProvider.get_present_active,
            ("present",    "middle"):  SuffixProvider.get_present_middle,
            ("imperfect",  "active"):  SuffixProvider.get_secondary_active,
            ("imperfect",  "middle"):  SuffixProvider.get_secondary_middle,
            ("imperative", "active"):  SuffixProvider.get_imperative_active,
            ("imperative", "middle"):  SuffixProvider.get_imperative_middle,
            ("optative",   "active"):  SuffixProvider.get_optative_active,
            ("optative",   "middle"):  SuffixProvider.get_optative_middle,
            # Future / Conditional reuse present / secondary paradigms
            ("future",     "active"):  SuffixProvider.get_present_active,
            ("future",     "middle"):  SuffixProvider.get_present_middle,
            ("conditional","active"):  SuffixProvider.get_secondary_active,
            ("conditional","middle"):  SuffixProvider.get_secondary_middle,
            ("perfect",    "active"):  SuffixProvider.get_perfect_active,
            ("perfect",    "middle"):  SuffixProvider.get_perfect_middle,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Stem FST caching
    # ──────────────────────────────────────────────────────────────────────────

    def _get_stem(self, root_str, class_num, strength, tense, derivative):
        """Return the stem FST, building and caching it on first access."""
        key = (root_str, class_num, strength, tense, derivative)
        if key not in self._stem_cache:
            self._stem_cache[key] = self.stems.build(
                root_str, class_num, strength, tense=tense, derivative=derivative
            )
        return self._stem_cache[key]

    # ──────────────────────────────────────────────────────────────────────────
    # Ending lookup
    # ──────────────────────────────────────────────────────────────────────────

    def _fetch_endings(self, class_num, voice, tense, root_str=None):
        """Return the endings dict for the given tense/voice/class."""
        if voice == "passive":
            return SuffixProvider.get_passive_endings(tense)

        key = (tense, voice)
        provider = self._ending_dispatch.get(key)
        if provider is None:
            raise ValueError(f"No ending table for tense='{tense}' voice='{voice}'.")

        if tense == "perfect":
            endings = provider()
            # ṛ-final roots in the perfect take bare 'va/vahe/ma/mahe' du/pl endings
            # (no connecting 'i') because the ṛ-final root doesn't undergo yan/savarna.
            # cakṛ+va = cakṛva  ✓  (not cakriva via cakṛ+iva → yan ṛ+→r)
            if root_str and root_str[-1] == "ṛ":
                endings = dict(endings)
                if voice == "active":
                    endings["[1du]"] = "va"
                    endings["[1pl]"] = "ma"
                    endings["[2du]"] = "vathuḥ"
                else:  # middle
                    endings["[1du]"] = "vahe"
                    endings["[1pl]"] = "mahe"
            return endings
        # Future/Conditional reuse thematic (class 1) endings
        if tense in ("future", "conditional"):
            return provider(class_num=1)
        return provider(class_num=class_num)


    # ──────────────────────────────────────────────────────────────────────────
    # Main entry point
    # ──────────────────────────────────────────────────────────────────────────

    @lru_cache(maxsize=4096)
    def conjugate(self, root_str, class_num, person, number,
                  voice="active", tense="present"):
        """Return the fully inflected IAST string for the given parameters.

        Parameters
        ----------
        root_str  : IAST root, e.g. "bhū", "kṛ", "hu"
        class_num : verbal class (int, 1–10)
        person    : "1", "2", or "3"
        number    : "sg", "du", or "pl"
        voice     : "active", "middle", or "passive"
        tense     : "present", "imperfect", "imperative", "optative",
                    "future", "conditional", or "perfect"

        Returns
        -------
        str – inflected word in IAST
        """
        strength   = _evaluate_strength(class_num, person, number, voice, tense)
        derivative = "passive" if voice == "passive" else None

        # ── 1. Build / fetch stem ─────────────────────────────────────────────
        stem = self._get_stem(root_str, class_num, strength, tense, derivative)

        # ── 2. Augmentation (a- prefix for past tenses) ───────────────────────
        if tense in ("imperfect", "conditional"):
            stem = pn.accep("a+") + stem

        # ── 3. Attach ending ──────────────────────────────────────────────────
        # Special case: √ad cl-2 imperfect active uses connecting-vowel endings
        if root_str == "ad" and tense == "imperfect" and voice == "active":
            tag      = f"[{person}{number}]"
            override = ad_imperfect_active_overrides.get(tag)
        else:
            override = None

        endings = self._fetch_endings(class_num, voice, tense, root_str=root_str)
        tag     = f"[{person}{number}]"
        if tag not in endings:
            raise ValueError(f"No ending for {tag} in {tense} {voice}.")

        # Perfect 2sg bare-tha override
        if (tense == "perfect" and voice == "active" and person == "2"
                and number == "sg" and root_str in perfect_bare_tha_roots):
            ending = "tha"
        elif override is not None:
            ending = override
        else:
            ending = endings[tag]

        if ending:
            combined = stem + pn.accep("+") + pn.accep(ending)
        else:
            combined = stem

        # ── 4. FST post-processing ────────────────────────────────────────────
        morph_fst  = self.morphology.apply_all(combined)
        sandhi_fst = self.sandhi.apply_all(morph_fst)
        result     = sandhi_fst.optimize()

        return result.string()

    # ──────────────────────────────────────────────────────────────────────────
    # Debug helper
    # ──────────────────────────────────────────────────────────────────────────

    def debug_conjugate(self, root_str, class_num, person, number,
                        voice="active", tense="present"):
        """Step-by-step pipeline trace that shows where the FST first goes empty."""

        def check(label, fst):
            fst = fst.optimize()
            try:
                s = fst.string()
                print(f"  ✅ {label}: '{s}'")
            except Exception:
                sp = pn.shortestpath(fst)
                try:
                    s = sp.string()
                    print(f"  ⚠️  {label}: AMBIGUOUS, shortest='{s}'")
                except Exception:
                    print(f"  ❌ {label}: EMPTY FST")
            return fst

        print(f"\n{'='*50}")
        print(f"DEBUG: {root_str} cl{class_num} {person}{number} {voice} {tense}")
        print(f"{'='*50}")

        strength   = _evaluate_strength(class_num, person, number, voice, tense)
        derivative = "passive" if voice == "passive" else None
        print(f"  Strength tag: {strength}")

        # Step 1 – raw root acceptor
        root_fst = pn.accep(root_str + strength)
        check("1. root_fst", root_fst)

        # Step 2 – guna only
        guna_only = root_fst @ self.strength_engine.get_guna()
        check("2. guna applied", guna_only)

        # Step 3 – full stem
        stem = self._get_stem(root_str, class_num, strength, tense, derivative)
        check("3. stem built", stem)

        # Step 4 – augmentation
        if tense in ("imperfect", "conditional"):
            stem = pn.accep("a+") + stem
            check("4. augmented stem", stem)

        # Step 5 – ending attached
        endings = self._fetch_endings(class_num, voice, tense)
        tag     = f"[{person}{number}]"
        ending  = endings.get(tag, "")
        print(f"  Ending for {tag}: '{ending}'")
        combined = (stem + pn.accep("+") + pn.accep(ending)) if ending else stem
        check("5. stem+ending", combined)

        # Step 6 – morphology
        morph = self.morphology.apply_all(combined)
        check("6. after morphology", morph)

        # Step 7 – sandhi phases
        vowel_done = self.sandhi.vowel_phase(morph)
        check("7a. after vowel_phase", vowel_done)

        cons_done = self.sandhi.consonant_phase(vowel_done)
        check("7b. after consonant_phase", cons_done)

        long_done = self.sandhi.long_distance_phase(cons_done)
        check("7c. after long_distance_phase", long_done)