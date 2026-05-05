import pynini as pn
from alphabet import ALPHABET

class MorphologyEngine:
    """Suffix-conditioned morphophonemic adjustments applied *after* stem construction.

    Order matters — rules are applied left-to-right:
        1. Passive vowel lengthening  ([PASSIVE] → lengthened vowel)
        2. Class-4 internal lengthening ([CLASS4] i → ī before +ya)
        3. Causative passive trigger erased ([CAUS_PASS] → ε)
           The +a that preceded [CAUS_PASS] already triggered ayadi in sandhi;
           we erase the tag and the stray 'a' here (a[CAUS_PASS] → ε).
        4. Class-8 kṛ weak suppletion  (bare "kṛ" → "kur" before +u)
        5. Class-8 u-contraction: "r+u+" before consonant → "r+"
           (kur+u+vaḥ → kurvaḥ; kur+u+maḥ → kurmaḥ)
        6. Erase all remaining abstract tags
    """

    def __init__(self):
        sig = ALPHABET.sigma_star
        self._build_rules(sig)

    def _build_rules(self, sig):
        # ── 0. Augment vriddhi coalescence ──────────────────────────────
        # Whitney §135 / Pāṇini 6.1.87-89: augment a + vowel-initial stem
        # yields vriddhi coalescence, NOT guna.
        # [AUG]a+i/ī → ai, [AUG]a+u/ū → au, [AUG]a+ṛ/ṝ → ār, [AUG]a+a/ā → ā
        self.augment_vriddhi = pn.cdrewrite(
            pn.string_map([
                ("[AUG]a+i",  "ai"), ("[AUG]a+ī",  "ai"),
                ("[AUG]a+u",  "au"), ("[AUG]a+ū",  "au"),
                ("[AUG]a+ṛ",  "ār"), ("[AUG]a+ṝ",  "ār"),
                ("[AUG]a+a",  "ā"),  ("[AUG]a+ā",  "ā"),

                # this shit is pre gemini
                # ("[AUG]a+e",  "e"),   # a+e → e (already guna-form; rare)
                # ("[AUG]a+o",  "o"),   # a+o → o (already guna-form; rare)

                # If StemBuilder already applied Guna, the augment meets e, o, or ar.
                # Pāṇini dictates the augment still forces Vriddhi here.
                ("[AUG]a+e",  "ai"),  # a + e -> ai
                ("[AUG]a+o",  "au"),  # a + o -> au
                ("[AUG]a+ar", "ār"),  # a + ar -> ār (guna of ṛ)
                ("[AUG]a+al", "āl"),  # a + al -> āl (guna of ḷ)
            ]),
            "", "", sig
        )
        # Erase unused [AUG] tag (when augment precedes consonant-initial stem)
        self.augment_erase = pn.cdrewrite(
            pn.cross("[AUG]", ""), "", "", sig
        )
        # ── 0.5. Nasal insertion (Pāṇini 7.1.58-59, Whitney §150-152) ───────────
        # Id-it (I-marked) roots receive a homorganic nasal before consonant suffixes.
        # The nasal is determined by the following consonant (parasavarṇa rule):
        #   Before p/ph/b/bh/m → m
        #   Before t/th/d/dh/n → n
        #   Before ṭ/ṭh/ḍ/ḍh/ṇ → ṇ
        #   Before k/kh/g/gh/ṅ → ṅ
        #   Before c/ch/j/jh/ñ → ñ
        # Example: [NASAL]muc → muc + m before +chaṭ → muñc+chaṭ
        self.nasal_m_insertion = pn.cdrewrite(
            pn.cross("[NASAL]", "m"),
            "",
            pn.union("p", "ph", "b", "bh", "m"),
            sig
        )
        self.nasal_n_insertion = pn.cdrewrite(
            pn.cross("[NASAL]", "n"),
            "",
            pn.union("t", "th", "d", "dh", "n"),
            sig
        )
        self.nasal_retroflex_insertion = pn.cdrewrite(
            pn.cross("[NASAL]", "ṇ"),
            "",
            pn.union("ṭ", "ṭh", "ḍ", "ḍh", "ṇ"),
            sig
        )
        self.nasal_velar_insertion = pn.cdrewrite(
            pn.cross("[NASAL]", "ṅ"),
            "",
            pn.union("k", "kh", "g", "gh", "ṅ"),
            sig
        )
        self.nasal_palatal_insertion = pn.cdrewrite(
            pn.cross("[NASAL]", "ñ"),
            "",
            pn.union("c", "ch", "j", "jh", "ñ"),
            sig
        )
        # Fallback: if [NASAL] is followed by a vowel, it becomes n
        # (rare but theoretically possible in some constructions)
        self.nasal_vowel_fallback = pn.cdrewrite(
            pn.cross("[NASAL]", "n"),  # default to n for vowel-initial suffixes
            "",
            ALPHABET.vowels,
            sig
        )
        # ── 1. Passive vowel lengthening ──────────────────────────────────────
        self.passive_vowels = pn.cdrewrite(
            pn.string_map([
                ("i[PASSIVE]",  "ī"),
                ("u[PASSIVE]",  "ū"),
                ("ṛ[PASSIVE]",  "ri"),
                ("ṝ[PASSIVE]",  "īr"),
                # a/ā roots take -ya- without lengthening; no rule needed
            ]),
            "", "", sig
        )

        # ── 2. Class-4 (Divyādi) internal lengthening ─────────────────────────
        # The stem is built as root + [CLASS4] + +ya, e.g. "div[CLASS4]+ya".
        # We want to lengthen the LAST short i/u in the root before [CLASS4].
        # Strategy: use two rules —
        #   (a) shorten_tag: cross "i[CLASS4]" → "ī" (fires if vowel directly before tag)
        #   (b) lengthen_via_tag: cross "i" → "ī" in leftward context up to [CLASS4]
        # Simplest correct approach: apply guna/lengthening on the whole root string
        # by replacing i→ī when [CLASS4] is somewhere to the right.
        # cdrewrite left-context "" / right-context: any consonants then [CLASS4]
        _any_cons = pn.closure(ALPHABET.consonants)
        self.class4_lengthening = pn.cdrewrite(
            pn.string_map([("i", "ī"), ("u", "ū")]),
            "",
            _any_cons + pn.accep("[CLASS4]"),
            sig
        )

        # ── 2.5. Samprasāraṇa ────────────────────────────────────────────────
        # Converts semivowels to vowels in weak contexts for specific roots (e.g. vac -> uc)
        self.samprasarana = pn.cdrewrite(
            pn.string_map([
                ("[SAMP]ya", "i"),   # yaj -> i + j -> ij
                ("[SAMP]va", "u"),   # vap -> u + p -> up
                ("[SAMP]ra", "ṛ"),   # grah -> gṛh
                
                # Handle cases where a consonant precedes the semivowel (e.g., svap)
                # s + [SAMP]va -> su
                ("s[SAMP]va", "su"), 
                ("p[SAMP]ra", "pṛ"), 
            ]),
            "", "", sig
        )

        # ── 3. Causative passive: erase the ayadi-trigger 'a' and the tag ─────
        # The cl10 passive stem is: vriddhi(root) + "+a[CAUS_PASS]+ya"
        # Case A – diphthong-final vŕ̥ddhi (bhū→bhau):
        #   ayadi fires: bhau + +a → bhāv, consuming the boundary '+a'.
        #   Remaining: bhāv + [CAUS_PASS] + +ya. Just erase the tag.
        # Case B – consonant-final vŕ̥ddhi (ād):
        #   No ayadi fires. String: ād + +a + [CAUS_PASS] + +ya.
        #   Must erase '+a[CAUS_PASS]' as a unit (the stray trigger vowel).
        # Two-pass: erase '+a[CAUS_PASS]' first (Case B), then any bare '[CAUS_PASS]' (Case A).
        self.caus_pass_erase_with_a = pn.cdrewrite(
            pn.cross("+a[CAUS_PASS]", ""), "", "", sig
        )
        self.caus_pass_erase = pn.cdrewrite(
            pn.cross("[CAUS_PASS]", ""), "", "", sig
        )

        # ── 4. Class-8 kṛ weak suppletion ─────────────────────────────────────
        # In weak forms of kṛ (class 8), the root becomes "kur" before -u-.
        self.class8_suppletion = pn.cdrewrite(
            pn.cross("kṛ", "kur"),
            "",
            "+u+",    # only fires before the class-8 weak affix (+u+)
            sig
        )

        # Class-8 u-contraction: drop -u- affix before sonorant-initial endings.
        # Sanskrit rule: class-8 weak -u- drops before endings starting with
        # semivowels/nasals (y, v, m) but NOT before stops (t, th, ...) or
        # vowels (where yan sandhi fires instead: kur+u+e → kurve).
        # Using explicit union avoids pynini sigma ambiguity with ALPHABET.consonants.
        self.class8_u_drop = pn.cdrewrite(
            pn.cross("r+u+", "r+"),
            "",
            pn.union("y", "v", "m"),
            sig
        )
        # ── 5. Root Aorist exceptions ─────────────────────────────────────────
        # √bhū + [ROOT_AORIST] + vowel → bhūv + vowel (e.g. abhūvam)
        self.root_aorist_bhuv = pn.cdrewrite(
            pn.cross("[ROOT_AORIST]+", "v+"),
            "bhū",
            ALPHABET.vowels,
            sig
        )

        # ── 6. Erase all abstract tags ─────────────────────────────────────────
        # Aorist Passive 3sg Vriddhi (e.g. bhū → bhāv before [AORIST_PASS_3SG])
        vriddhi_map = pn.string_map([
            ("a", "ā"), ("i", "ai"), ("ī", "ai"), ("u", "au"), ("ū", "au"), ("ṛ", "ār")
        ])
        # Lookahead allows any structural tags or boundaries before the 3sg marker
        tag_or_boundary = pn.union(*ALPHABET.tags_list, "+")
        self.aorist_pass_vriddhi = pn.cdrewrite(
            vriddhi_map,
            "",
            pn.closure(ALPHABET.consonants) + tag_or_boundary.star + "[AORIST_PASS_3SG]",
            sig
        )

        # Intensive Active: erase [INTENSIVE_ACTIVE] tag before the boundary
        # (the ī connecting vowel is rare and root-specific; handled via irregulars)
        self.intensive_i_it = pn.cdrewrite(
            pn.cross("[INTENSIVE_ACTIVE]+", "+"),
            "", "", sig
        )

        # ── 7. Class 2 Weak overrides ───────────────────────────────────────
        # han: 'n' drops before stops (t, th, s, etc.) but STAYS before nasals (m, n).
        # Whitney §636: han before consonant endings: ha- (stops) but han- (nasals).
        # Rule A: han[CLASS2_WEAK]+ before a STOP consonant → ha+
        _stops = pn.union("t", "th", "d", "dh", "k", "kh", "g", "gh",
                          "p", "ph", "b", "bh", "c", "j", "s", "ś", "ṣ")
        self.class2_weak_cons = pn.cdrewrite(
            pn.cross("han[CLASS2_WEAK]+", "ha+"),
            "",
            _stops,
            sig
        )
        # Rule B: han[CLASS2_WEAK]+ before a NASAL → han+ (n retained)
        _nasals = pn.union("m", "n", "ṇ", "ṅ")
        self.class2_weak_nasal = pn.cdrewrite(
            pn.cross("han[CLASS2_WEAK]+", "han+"),
            "",
            _nasals,
            sig
        )
        # Rule C: han[CLASS2_WEAK]+ before a VOWEL → ghn+ (Grassmann throwback)
        self.class2_weak_vowel = pn.cdrewrite(
            pn.cross("han[CLASS2_WEAK]+", "ghn+"),
            "",
            ALPHABET.vowels,
            sig
        )
        self.class2_weak_vac = pn.cdrewrite(
            pn.cross("vac[CLASS2_WEAK]+", "uc+"),
            "",
            ALPHABET.vowels,
            sig
        )

        all_tags = pn.union(
            "[PASSIVE]", "[CLASS4]", "[CLASS8]", "[CAUS_PASS]",
            "[STRONG]",  "[WEAK]",   "[VRIDDHI]", "[CLASS2_WEAK]",
            "[ROOT_AORIST]", "[AORIST]", "[AORIST_PASS_3SG]", "[INTENSIVE_ACTIVE]",
            "[SAMP]", "[AUG]", "[NASAL]"
        )
        self.clean_tags = pn.cdrewrite(pn.cross(all_tags, ""), "", "", sig)

    def apply_all(self, fst: pn.Fst, debug: bool = False) -> pn.Fst:
        """Apply all morphological adjustments in order."""
        if debug:
            rules = [
                ("augment_vriddhi",          self.augment_vriddhi),
                ("augment_erase",            self.augment_erase),
                ("samprasarana",             self.samprasarana),
                ("passive_vowels",           self.passive_vowels),
                ("class4_lengthening",       self.class4_lengthening),
                ("caus_pass_erase_with_a",   self.caus_pass_erase_with_a),
                ("caus_pass_erase",          self.caus_pass_erase),
                ("class8_suppletion",        self.class8_suppletion),
                ("class8_u_drop",            self.class8_u_drop),
                ("root_aorist_bhuv",         self.root_aorist_bhuv),
                ("aorist_pass_vriddhi",      self.aorist_pass_vriddhi),
                ("intensive_i_it",           self.intensive_i_it),
                ("class2_weak_nasal",        self.class2_weak_nasal),
                ("class2_weak_cons",         self.class2_weak_cons),
                ("class2_weak_vowel",        self.class2_weak_vowel),
                ("class2_weak_vac",          self.class2_weak_vac),
                ("clean_tags",               self.clean_tags),
            ]
            print("  [morphology]")
            for name, rule_fst in rules:
                fst = (fst @ rule_fst).optimize()
                if fst.num_states() == 0:
                    print(f"    ❌ {name}: FST went EMPTY")
                    return fst
                try:
                    print(f"    ✅ {name}: '{fst.string()}'")
                except Exception:
                    try:
                        sp = pn.shortestpath(fst).string()
                        print(f"    ⚠️  {name}: ambiguous, shortest='{sp}'")
                    except Exception:
                        print(f"    ⚠️  {name}: ambiguous")
            return fst
        return (
            fst
            @ self.augment_vriddhi
            @ self.augment_erase
            @ self.nasal_m_insertion
            @ self.nasal_n_insertion
            @ self.nasal_retroflex_insertion
            @ self.nasal_velar_insertion
            @ self.nasal_palatal_insertion
            @ self.nasal_vowel_fallback
            @ self.samprasarana
            @ self.passive_vowels
            @ self.class4_lengthening
            @ self.caus_pass_erase_with_a
            @ self.caus_pass_erase
            @ self.class8_suppletion
            @ self.class8_u_drop
            @ self.root_aorist_bhuv
            @ self.aorist_pass_vriddhi
            @ self.intensive_i_it
            @ self.class2_weak_nasal
            @ self.class2_weak_cons
            @ self.class2_weak_vowel
            @ self.class2_weak_vac
            @ self.clean_tags
        )