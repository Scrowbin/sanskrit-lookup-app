import pynini as pn
from alphabet import ALPHABET

class MorphologyEngine:
    """Suffix-conditioned morphophonemic adjustments applied *after* stem construction.

    Order matters — rules are applied left-to-right:
        0. Augment vriddhi / erase [AUG]
        0.5 [NASAL] insertion (P. 7.1.58–59)
        1. Samprasāraṇa, passive vowels, class-4 lengthening, causative passive cleanup
        2. Class-8 suppletion / u-drop, root aorist bhūv, aorist passive vriddhi, intensive
        3. Class-2 weak (han / vac)
        4. **Sandhi context tags** ([SD_DCP], [SD_GEM], …) — see ``sd_boundary_tagging``
        5. Erase remaining morph tags (not [SD_*]; those are stripped in SandhiEngine)
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
        # Converts semivowels to vowels in weak contexts (Whitney §252; Pāṇini 6.1.13–15).
        # Tag [SAMP] is prepended to the whole root by build() when the root
        # takes samprasāraṇa; it marks the position for the below rules.
        #
        # Pattern: [SAMP] + optional initial consonant(s) + semivowel(y/v/r) + a
        # → initial consonant(s) + corresponding vowel (i/u/ṛ).
        # Specific cluster rules run BEFORE the generic tag-initial rules so they
        # take priority when an initial consonant precedes the semivowel.
        self.samprasarana = pn.cdrewrite(
            pn.string_map([
                # ── Roots with initial consonant cluster before semivowel ────
                ("[SAMP]sva", "su"),  # svap → sup (s stays, v→u, a drops)
                ("[SAMP]śva", "śu"),  # śvap → śup (if attested)
                ("[SAMP]pra", "pṛ"),  # prach → pṛch
                ("[SAMP]gra", "gṛ"),  # grah → gṛh
                ("[SAMP]bra", "bṛ"),  # brajj → bṛjj
                ("[SAMP]dra", "dṛ"),  # druh-type if used
                ("[SAMP]vya", "vi"),  # vyadh → vidh, vyac → vic
                ("[SAMP]vyā", "vi"),  # In samprasarana, long vowels also reduce to short
                # ── Simple roots: [SAMP] immediately before semivowel ─────────
                ("[SAMP]ya", "i"),    # yaj → ij, yam → im
                ("[SAMP]yā", "i"),    # jyā → jī (wait, jyā is [SAMP]jyā -> jī, but yā is i)
                ("[SAMP]va", "u"),    # vap → up, vac → uc
                ("[SAMP]vā", "u"),
                ("[SAMP]ra", "ṛ"),    # rah/ran-type
                ("[SAMP]rā", "ṛ"),
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

        # ── 3.5. Class-1 suppletive stems ─────────────────────────────────────
        # Pāṇini 7.3.78: gam -> gacch before ŚaP (class 1 suffix)
        self.class1_suppletion = pn.cdrewrite(
            pn.string_map([
                ("gam[CLASS1_IRR]", "gacch"),
                ("sthā[CLASS1_IRR]", "tiṣṭh"),
                ("pā[CLASS1_IRR]", "pib"),
                ("sad[CLASS1_IRR]", "sīd"),
                ("scand[CLASS1_IRR]", "skand"),
            ]),
            "", "", sig
        )
        # Erase [CLASS1_IRR] if it didn't trigger suppletion
        self.class1_irr_erase = pn.cdrewrite(
            pn.cross("[CLASS1_IRR]", ""), "", "", sig
        )

        # ── 3.8. Class-5 śru weak suppletion ──────────────────────────────────
        # Pāṇini 7.3.80 (śṛṇo ca): śru -> śṛ before class-5 affix nu/no
        self.class5_suppletion = pn.cdrewrite(
            pn.cross("śru", "śṛ"),
            "",
            pn.union("+nu", "+no"),
            sig
        )

        # ── 4. Class-8 kṛ weak suppletion ─────────────────────────────────────
        # In weak forms of kṛ (class 8), the root becomes "kur" before -u-.
        _any_weak_opt = pn.closure(pn.union("[WEAK]", "[PERF_WEAK]"), 0, 1)
        self.class8_suppletion = pn.cdrewrite(
            pn.cross("kṛ", "kur") + pn.cross(_any_weak_opt, ""),
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

        # Class 5/8 optional u-drop: sunuvaḥ OR sunvaḥ (Whitney §715)
        self.class5_8_u_drop_opt = pn.cdrewrite(
            pn.union(pn.cross("n+u+", "n+"), pn.accep("n+u+")),
            "",
            pn.union("v", "m"),
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
        # Aorist Passive 3sg Vriddhi (Pāṇini 7.2.1, 7.2.3) and Guṇa (Pāṇini 7.3.86)
        # Final vowels take vṛddhi (e.g. bhū → bhāv).
        vriddhi_map_final = pn.string_map([
            ("a", "ā"), ("i", "ai"), ("ī", "ai"), ("u", "au"), ("ū", "au"), ("ṛ", "ār"), ("ṝ", "ār")
        ])
        tag_or_boundary = pn.union(*ALPHABET.tags_list, "+")
        
        self.aorist_pass_vriddhi_final = pn.cdrewrite(
            vriddhi_map_final,
            "",
            tag_or_boundary.star + "[AORIST_PASS_3SG]",
            sig
        )
        
        # Medial 'a' takes vṛddhi (e.g. pac → pāc, gam → gām).
        self.aorist_pass_vriddhi_medial_a = pn.cdrewrite(
            pn.cross("a", "ā"),
            "",
            pn.closure(ALPHABET.consonants, 1) + tag_or_boundary.star + "[AORIST_PASS_3SG]",
            sig
        )
        
        # Medial short 'i', 'u', 'ṛ' take guṇa (e.g. budh → bodh, vid → ved).
        guna_map_medial = pn.string_map([
            ("i", "e"), ("u", "o"), ("ṛ", "ar")
        ])
        self.aorist_pass_guna_medial = pn.cdrewrite(
            guna_map_medial,
            "",
            pn.closure(ALPHABET.consonants, 1) + tag_or_boundary.star + "[AORIST_PASS_3SG]",
            sig
        )
        
        # Pāṇini 7.3.33: āto yuk ciṇkṛtoḥ (ā takes yuk before ciṇ)
        self.aorist_pass_yuk = pn.cdrewrite(
            pn.cross("ā", "āy"),
            "",
            tag_or_boundary.star + "[AORIST_PASS_3SG]",
            sig
        )

        # Intensive Active: The optional ī before consonant endings (Whitney §1006c)
        # is now handled directly in conjugate.py because the stem must revert to weak grade,
        # which cannot be done cleanly in a generic string-replacement FST.
        # We simply erase [INTENSIVE_ACTIVE] tag here.
        self.intensive_active_erase = pn.cdrewrite(
            pn.cross("[INTENSIVE_ACTIVE]+", "+"),
            "", "", sig
        )

        # ── 7. Athematic Zero-Grade (Rule 253 / P. 6.4.98, 6.4.111, 6.4.37, 6.4.34) ─
        # Whitney §253: Short 'a' loss in weak syllables.
        _any_weak = pn.union("[WEAK]+", "[PERF_WEAK]+")
        
        # Rule A: as drops 'a' before ANY ending (santi, stas).
        self.zero_grade_as = pn.cdrewrite(
            pn.cross("as", "s") + pn.cross(_any_weak, "+"),
            "", "", sig
        )
        
        # Rule B: gam, jan, khan, ghas, han drop 'a' before VOWEL endings.
        _a_drop_roots = pn.union(
            pn.cross("gam", "gm"),
            pn.cross("jan", "jñ"),
            pn.cross("khan", "khn"),
            pn.cross("ghas", "kṣ"),
            pn.cross("han", "ghn"),
        )
        self.zero_grade_a_drop_vowel = pn.cdrewrite(
            _a_drop_roots + pn.cross(_any_weak, "+"),
            "",
            ALPHABET.vowels,
            sig
        )

        # Rule B.1: Pāṇini 6.4.64 āto lopa iṭi ca (ā drops before iṭ)
        # Roots ending in ā drop it before i/ī. e.g. tasthā+iṭ+tha -> tasthitha.
        # This applies across all roots.
        self.a_drop_before_i = pn.cdrewrite(
            pn.cross("ā+", "+"),
            "",
            pn.union("i", "ī"),
            sig
        )

        # Rule B.2: Unreduplicated perfect 'vid' does not take iṭ (Whitney §801).
        self.vid_perfect_i_drop = pn.cdrewrite(
            pn.cross("i", ""),
            pn.accep("[VID_UNRED]+") | pn.accep("[VID_UNRED]"),
            "",
            sig
        )
        self.vid_unred_to_perf_weak = pn.cdrewrite(
            pn.cross("[VID_UNRED]", "[PERF_WEAK]"),
            "", "", sig
        )
        
        # Rule B.2: Pāṇini 7.3.72 kasyāci ca (ksa drops a before ac)
        # sa-aorist (ksa) drops its final 'a' before vowel endings
        self.sa_aorist_a_drop = pn.cdrewrite(
            pn.cross("a", ""),
            "",
            "[SA_AORIST]+" + pn.union(*ALPHABET.vowels_list),
            sig
        )

        # Rule C: han becomes ja before dhi (imperative 2sg) (Pāṇini 6.4.36)
        # Class 2 uses 'dhi', so we must also change 'dhi' to 'hi' in the same stroke.
        self.zero_grade_han_hi = pn.cdrewrite(
            pn.cross("han", "ja") + pn.cross(_any_weak, "+") + pn.cross("dhi", "hi"),
            "", "",
            sig
        )

        # Rule C.1: han drops 'n' before STOP consonants (t, th, s, etc.) but retains it before nasals.
        _stops = pn.union("t", "th", "d", "dh", "k", "kh", "g", "gh",
                          "p", "ph", "b", "bh", "c", "j", "s", "ś", "ṣ")
        self.zero_grade_han_cons = pn.cdrewrite(
            pn.cross("han", "ha") + pn.cross(_any_weak, "+"),
            "",
            _stops,
            sig
        )
        
        # Rule D: han retains 'n' before NASALS.
        _nasals = pn.union("m", "n", "ṇ", "ṅ")
        self.zero_grade_han_nasal = pn.cdrewrite(
            pn.cross("han", "han") + pn.cross(_any_weak, "+"),
            "",
            _nasals,
            sig
        )
        
        # Rule E: śās -> śā before dhi (P. 6.4.35)
        self.zero_grade_sas_dhi = pn.cdrewrite(
            pn.cross("śās", "śā") + pn.cross(_any_weak, "+"),
            "",
            pn.accep("dhi"),
            sig
        )

        # Rule F: śās -> śiṣ before weak endings starting with consonants (except dhi and y) OR before 'an' (P. 6.4.34).
        # Whitney §639: śās becomes śiṣ before weak consonant-endings (except y). Alternative forms with śās are attested.
        sas_context = pn.difference(ALPHABET.consonants, pn.union(pn.accep("dh"), pn.accep("y"))) | pn.accep("an")
        self.zero_grade_sas_cons = pn.cdrewrite(
            pn.union(pn.cross("śās", "śiṣ"), pn.cross("śās", "śās")) + pn.cross(_any_weak, "+"),
            "",
            sas_context,
            sig
        )

        # ── 7.1. Intensive Imperative 2sg [HI_DHI] Resolution ─────────────────
        # Whitney §1011: The 2d sing. act. takes dhi after a consonant, and hi after a vowel.
        opt_tags = pn.closure(pn.union(*ALPHABET.tags_list), 0)
        self.intensive_hi = pn.cdrewrite(
            pn.cross("[HI_DHI]", "hi"),
            pn.union(*ALPHABET.vowels_list) + opt_tags + pn.accep("+"),
            "",
            sig
        )
        self.intensive_dhi = pn.cdrewrite(
            pn.cross("[HI_DHI]", "dhi"),
            pn.union(*ALPHABET.consonants_list) + opt_tags + pn.accep("+"),
            "",
            sig
        )

        # ── 7.5 Sandhi context tags (tag-gated phonology; see sandhi.py) ─────────
        # Whitney §213–219 (dental+palatal, ś+t); §231 (gemination); §249 (sibilant
        # clusters); visarga before stops (internal).
        self.sd_insert_ssr = pn.cdrewrite(
            pn.string_map([
                ("ś+t", "ś[SD_SSR]+t"), ("ś+th", "ś[SD_SSR]+th"),
            ]),
            "", "", sig,
        )
        self.sd_insert_dcp = pn.cdrewrite(
            pn.string_map([
                ("t+c", "t[SD_DCP]+c"), ("t+ch", "t[SD_DCP]+ch"),
                ("d+c", "d[SD_DCP]+c"), ("d+ch", "d[SD_DCP]+ch"),
                ("dh+c", "dh[SD_DCP]+c"), ("dh+ch", "dh[SD_DCP]+ch"),
            ]),
            "", "", sig,
        )
        self.sd_insert_gem = pn.cdrewrite(
            pn.string_map([
                ("t+t", "t[SD_GEM]+t"), ("d+d", "d[SD_GEM]+d"),
                ("p+p", "p[SD_GEM]+p"), ("b+b", "b[SD_GEM]+b"),
                ("k+k", "k[SD_GEM]+k"), ("g+g", "g[SD_GEM]+g"),
                ("ṭ+ṭ", "ṭ[SD_GEM]+ṭ"), ("ḍ+ḍ", "ḍ[SD_GEM]+ḍ"),
                ("c+c", "c[SD_GEM]+c"), ("j+j", "j[SD_GEM]+j"),
                ("l+l", "l[SD_GEM]+l"), ("r+r", "r[SD_GEM]+r"),
                ("y+y", "y[SD_GEM]+y"), ("v+v", "v[SD_GEM]+v"),
            ]),
            "", "", sig,
        )
        self.sd_insert_sib = pn.cdrewrite(
            pn.string_map([
                ("ṣ+s", "ṣ[SD_SIB]+s"), ("ś+s", "ś[SD_SIB]+s"),
                ("s+ṣ", "s[SD_SIB]+ṣ"), ("ṣ+ś", "ṣ[SD_SIB]+ś"),
            ]),
            "", "", sig,
        )
        self.sd_insert_lar = pn.cdrewrite(
            pn.string_map([
                ("ḥ+k", "ḥ[SD_LAR]+k"), ("ḥ+kh", "ḥ[SD_LAR]+kh"),
                ("ḥ+g", "ḥ[SD_LAR]+g"), ("ḥ+gh", "ḥ[SD_LAR]+gh"),
                ("ḥ+c", "ḥ[SD_LAR]+c"), ("ḥ+ch", "ḥ[SD_LAR]+ch"),
                ("ḥ+t", "ḥ[SD_LAR]+t"), ("ḥ+th", "ḥ[SD_LAR]+th"),
                ("ḥ+p", "ḥ[SD_LAR]+p"), ("ḥ+ph", "ḥ[SD_LAR]+ph"),
            ]),
            "", "", sig,
        )
        self.sd_boundary_tagging = (
            self.sd_insert_ssr
            @ self.sd_insert_dcp
            @ self.sd_insert_gem
            @ self.sd_insert_sib
            @ self.sd_insert_lar
        ).optimize()

        all_tags = pn.union(
            "[PASSIVE]", "[CLASS4]", "[CLASS8]", "[CAUS_PASS]",
            "[STRONG]",  "[WEAK]",   "[VRIDDHI]", "[CLASS2_WEAK]",
            "[ROOT_AORIST]", "[AORIST]", "[AORIST_PASS_3SG]", "[SA_AORIST]", "[INTENSIVE_ACTIVE]",
            "[SAMP]", "[AUG]", "[NASAL]", "[HI_DHI]",
            # Note: [NO_RUKI], [RUH_H], [PERF_WEAK], and [MRJ] MUST NOT be stripped here,
            # as they are needed by SandhiEngine. They are stripped in sandhi.py.
        )
        self.clean_tags = pn.cdrewrite(pn.cross(all_tags, ""), "", "", sig)

    def apply_all(self, fst: pn.Fst, debug: bool = False) -> pn.Fst:
        """Apply all morphological adjustments in order."""
        if debug:
            rules = [
                ("samprasarana",             self.samprasarana),
                ("augment_vriddhi",          self.augment_vriddhi),
                ("augment_erase",            self.augment_erase),
                ("nasal_m_insertion",        self.nasal_m_insertion),
                ("nasal_n_insertion",        self.nasal_n_insertion),
                ("nasal_retroflex_insertion", self.nasal_retroflex_insertion),
                ("nasal_velar_insertion",    self.nasal_velar_insertion),
                ("nasal_palatal_insertion",  self.nasal_palatal_insertion),
                ("nasal_vowel_fallback",     self.nasal_vowel_fallback),
                ("passive_vowels",           self.passive_vowels),
                ("class4_lengthening",       self.class4_lengthening),
                ("caus_pass_erase_with_a",   self.caus_pass_erase_with_a),
                ("caus_pass_erase",          self.caus_pass_erase),
                ("class1_suppletion",        self.class1_suppletion),
                ("class1_irr_erase",         self.class1_irr_erase),
                ("class5_suppletion",        self.class5_suppletion),
                ("class8_suppletion",        self.class8_suppletion),
                ("class8_u_drop",            self.class8_u_drop),
                ("class5_8_u_drop_opt",      self.class5_8_u_drop_opt),
                ("root_aorist_bhuv",         self.root_aorist_bhuv),
                ("aorist_pass_vriddhi_final",     self.aorist_pass_vriddhi_final),
                ("aorist_pass_vriddhi_medial_a",  self.aorist_pass_vriddhi_medial_a),
                ("aorist_pass_guna_medial",  self.aorist_pass_guna_medial),
                ("aorist_pass_yuk",          self.aorist_pass_yuk),
                ("intensive_active_erase",   self.intensive_active_erase),
                ("zero_grade_as",            self.zero_grade_as),
                ("zero_grade_a_drop_vowel",  self.zero_grade_a_drop_vowel),
                ("a_drop_before_i",          self.a_drop_before_i),
                ("vid_perfect_i_drop",       self.vid_perfect_i_drop),
                ("vid_unred_to_perf_weak",   self.vid_unred_to_perf_weak),
                ("sa_aorist_a_drop",         self.sa_aorist_a_drop),
                ("zero_grade_han_hi",        self.zero_grade_han_hi),
                ("zero_grade_han_cons",      self.zero_grade_han_cons),
                ("zero_grade_han_nasal",     self.zero_grade_han_nasal),
                ("zero_grade_sas_dhi",       self.zero_grade_sas_dhi),
                ("zero_grade_sas_cons",      self.zero_grade_sas_cons),
                ("intensive_hi",             self.intensive_hi),
                ("intensive_dhi",            self.intensive_dhi),
                ("clean_tags",               self.clean_tags),
                ("sd_boundary_tagging",      self.sd_boundary_tagging),
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
            @ self.samprasarana
            @ self.augment_vriddhi
            @ self.augment_erase
            @ self.nasal_m_insertion
            @ self.nasal_n_insertion
            @ self.nasal_retroflex_insertion
            @ self.nasal_velar_insertion
            @ self.nasal_palatal_insertion
            @ self.nasal_vowel_fallback
            @ self.passive_vowels
            @ self.class4_lengthening
            @ self.caus_pass_erase_with_a
            @ self.caus_pass_erase
            @ self.class1_suppletion
            @ self.class1_irr_erase
            @ self.class5_suppletion
            @ self.class8_suppletion
            @ self.class8_u_drop
            @ self.class5_8_u_drop_opt
            @ self.root_aorist_bhuv
            @ self.aorist_pass_vriddhi_final
            @ self.aorist_pass_vriddhi_medial_a
            @ self.aorist_pass_guna_medial
            @ self.aorist_pass_yuk
            @ self.intensive_active_erase
            @ self.zero_grade_as
            @ self.zero_grade_a_drop_vowel
            @ self.a_drop_before_i
            @ self.vid_perfect_i_drop
            @ self.vid_unred_to_perf_weak
            @ self.sa_aorist_a_drop
            @ self.zero_grade_han_hi
            @ self.zero_grade_han_cons
            @ self.zero_grade_han_nasal
            @ self.zero_grade_sas_dhi
            @ self.zero_grade_sas_cons
            @ self.intensive_hi
            @ self.intensive_dhi
            @ self.clean_tags
            @ self.sd_boundary_tagging
        )