import pynini as pn
from functools import lru_cache
from alphabet import ALPHABET
from vowel_strength import VowelStrengthEngine
from sandhi import SandhiEngine
from stem_rules import StemBuilder
from endings import SuffixProvider
from morphology import MorphologyEngine

# Derivatives that always use the periphrastic perfect (kṛ auxiliary)
_PERIPHRASTIC_DERIVATIVES = frozenset({"causative", "desiderative", "intensive"})

# Long-vowel phonemes at root-initial position that also force periphrastic perfect
_LONG_VOWEL_INITIALS = frozenset({"ī", "ū", "ṛ", "ṝ", "e", "ai", "o", "au"})


# ── Strength evaluation rule table ───────────────────────────────────────────
# Priority-ordered list of (predicate, strength_tag).
# Each predicate is a callable (class_num, person, number, voice, tense) → bool.
# The first matching rule wins.  Written as a module-level constant so it is
# constructed once and never rebuilt per-call.

_STRENGTH_RULES = [
    # 1. Passives always use a weak root
    (lambda c, p, n, v, t: v == "passive",
     "[WEAK]"),

    # 2. Future / Conditional / Periphrastic Future always use strong (Guna) grade
    (lambda c, p, n, v, t: t in ("future", "conditional", "periphrastic_future"),
     "[STRONG]"),

    # 3. Aorist / Injunctive: active uses strong stem override, middle uses weak
    (lambda c, p, n, v, t: t in ("aorist", "injunctive") and v == "active",
     "[STRONG]"),
    (lambda c, p, n, v, t: t in ("aorist", "injunctive") and v == "middle",
     "[WEAK]"),

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
            ("periphrastic_future", "active"): SuffixProvider.get_periphrastic_future_active,
            ("periphrastic_future", "middle"): SuffixProvider.get_periphrastic_future_middle,
            ("aorist",     "active"):  SuffixProvider.get_aorist_active,
            ("aorist",     "middle"):  SuffixProvider.get_aorist_middle,
            ("aorist",     "passive"): SuffixProvider.get_aorist_middle,
            ("injunctive", "active"):  SuffixProvider.get_aorist_active,
            ("injunctive", "middle"):  SuffixProvider.get_aorist_middle,
            ("injunctive", "passive"): SuffixProvider.get_aorist_middle,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Stem FST caching
    # ──────────────────────────────────────────────────────────────────────────

    def _get_stem(self, root_str, class_num, strength, tense, derivative=None, person=None, number=None):
        """Build the stem FST using StemBuilder."""
        key = (root_str, class_num, strength, tense, derivative, person, number)
        if key not in self._stem_cache:
            self._stem_cache[key] = self.stems.build(
                root_str, class_num, strength, tense=tense, derivative=derivative, person=person, number=number
            )
        return self._stem_cache[key]

    # ──────────────────────────────────────────────────────────────────────────
    # Ending lookup
    # ──────────────────────────────────────────────────────────────────────────

    def _fetch_endings(self, class_num, voice, tense, root_str=None):
        """Return the endings dict for the given tense/voice/class."""
        if voice == "passive":
            if tense in ("aorist", "injunctive"):
                return SuffixProvider.get_aorist_passive(class_num=class_num, root_str=root_str)
            return SuffixProvider.get_passive_endings(tense)

        key = (tense, voice)
        provider = self._ending_dispatch.get(key)
        if provider is None:
            raise ValueError(f"No ending table for tense='{tense}' voice='{voice}'.")

        return provider(class_num=class_num, root_str=root_str, tense=tense)


    # ──────────────────────────────────────────────────────────────────────────
    # Main entry point
    # ──────────────────────────────────────────────────────────────────────────

    @lru_cache(maxsize=4096)
    def conjugate(self, root_str, class_num, person, number, voice="active", tense="present", derivative=None):
        """Conjugate a Sanskrit root.

        Args:
            root_str: IAST string (e.g., "bhū")
            class_num: 1-10
            person: "1", "2", "3"
            number: "sg", "du", "pl"
            voice: "active", "middle", "passive"
            tense: "present", "imperfect", "imperative", "optative", "future",
                   "conditional", "perfect", "periphrastic_future", "aorist", "injunctive"
            derivative: None, "causative"
        """
        # Block morphologically impossible combinations
        if voice == "passive" and tense in ("perfect", "future", "periphrastic_future", "conditional"):
            raise ValueError(f"Impossible combination: voice='{voice}' and tense='{tense}'. These tenses do not have a distinct passive morphological paradigm.")

        # 1. Evaluate stem strength based on grammar rules
        if tense == "perfect":
            is_periphrastic = derivative in _PERIPHRASTIC_DERIVATIVES or class_num == 10
            if not is_periphrastic:
                phonemes = ALPHABET.parse_phonemes(root_str)
                if phonemes and phonemes[0] in _LONG_VOWEL_INITIALS:
                    is_periphrastic = True
            if is_periphrastic:
                return self._conjugate_periphrastic_perfect(
                    root_str, class_num, voice, person, number, derivative
                )

        if derivative == "desiderative":
            # Desiderative bases end in thematic 'a' and conjugate like Class 1
            strength = "[STRONG]"
            effective_class = 1
            if voice == "passive":
                effective_derivative = "desiderative_passive"
            else:
                effective_derivative = "desiderative"
        elif derivative == "intensive":
            # Intensive middle is thematic (Cl 1), active is athematic (Cl 2)
            if voice == "middle":
                strength = "[WEAK]"
                effective_class = 1
                effective_derivative = "intensive_middle"
            else:
                strength = _evaluate_strength(2, person, number, voice, tense)
                effective_class = 3 # Use Class 3 endings for intensive active (e.g. 3pl -ati)
                effective_derivative = "intensive_active"
        elif voice == "passive":
            # Passive 'ya' stem is only for the present system (present, imperfect, imperative, optative)
            # Aorist passive 3sg is a special form (Vriddhi + -i), others use standard aorist middle.
            strength = "[WEAK]"
            effective_class = class_num
            if tense in ("present", "imperfect", "imperative", "optative"):
                effective_derivative = "passive"
            elif tense in ("aorist", "injunctive") and person == "3" and number == "sg":
                effective_derivative = "aorist_passive_3sg"
            else:
                effective_derivative = None
        else:
            strength = _evaluate_strength(class_num, person, number, voice, tense)
            effective_class = class_num
            effective_derivative = derivative

        # ── 1. Build / fetch stem ─────────────────────────────────────────────
        stem = self._get_stem(root_str, effective_class, strength, tense, effective_derivative, person, number)

        # ── 2. Augmentation (a- prefix for past tenses) ───────────────────────
        if tense in ("imperfect", "conditional", "aorist"):
            stem = pn.accep("a+") + stem

        endings = self._fetch_endings(effective_class, voice, tense, root_str=root_str)
        tag     = f"[{person}{number}]"
        if tag not in endings:
            raise ValueError(f"No ending for {tag} in {tense} {voice}.")

        ending = endings[tag]

        if ending:
            combined = stem + pn.accep("+") + pn.accep(ending)
        else:
            combined = stem

        # ── 4. FST post-processing ────────────────────────────────────────────
        morph_fst  = self.morphology.apply_all(combined)
        sandhi_fst = self.sandhi.apply_all(morph_fst)
        result = sandhi_fst.optimize()

        try:
            forms = list(result.paths().ostrings())
            if not forms:
                return "CRASHED: No valid path"
            return " OR ".join(forms)
        except Exception as e:
            # Fallback for complex FSTs or errors
            try:
                return pn.shortestpath(result).string()
            except:
                return f"CRASHED: {str(e)}"

    def _conjugate_periphrastic_perfect(self, root_str, class_num, voice, person, number, derivative=None):
        """Periphrastic perfect: base-stem + \u0101m + auxiliary (kr, bhu, or as)."""
        base_fst = self.stems._build_periphrastic_base(root_str, class_num, derivative)
        # Apply morphology tags then erase boundaries within the base
        base_fst = (base_fst @ self.morphology.clean_tags).optimize()

        # kṛ (Class 8) is the standard auxiliary for periphrastic perfect
        aux_str = self.conjugate("kṛ", 8, person, number, voice, "perfect")
        results = []
        for aux in aux_str.split(" OR "):
            combined = base_fst + pn.accep("+") + pn.accep(aux)
            for form in self.sandhi.apply_all(combined).optimize().paths().ostrings():
                results.append(form)

        return " OR ".join(sorted(set(results))) if results else "CRASHED: No periphrastic forms"

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