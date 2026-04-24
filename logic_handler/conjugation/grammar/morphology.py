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
        # "div[CLASS4]+ya" → "dīv+ya"
        self.class4_lengthening = pn.cdrewrite(
            pn.cross("i[CLASS4]", "ī"),
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
            "+u",    # only fires before the class-8 weak affix
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
            ALPHABET.consonants.closure() + tag_or_boundary.star + "[AORIST_PASS_3SG]",
            sig
        )

        # Intensive Active: optional ī before consonants (except y)
        self.intensive_i_it = pn.cdrewrite(
            pn.union("", pn.cross("", "ī")),
            pn.accep("[INTENSIVE_ACTIVE]") + pn.accep("+"),
            ALPHABET.consonants - pn.accep("y"),
            sig
        )

        all_tags = pn.union(
            "[PASSIVE]", "[CLASS4]", "[CLASS8]", "[CAUS_PASS]",
            "[STRONG]",  "[WEAK]",   "[VRIDDHI]",
            "[ROOT_AORIST]", "[AORIST]", "[AORIST_PASS_3SG]", "[INTENSIVE_ACTIVE]"
        )
        self.clean_tags = pn.cdrewrite(pn.cross(all_tags, ""), "", "", sig)

    def apply_all(self, fst):
        """Apply all morphological adjustments in order."""
        return (
            fst
            @ self.passive_vowels
            @ self.class4_lengthening
            @ self.caus_pass_erase_with_a   # Case B: erase +a[CAUS_PASS]
            @ self.caus_pass_erase          # Case A: erase bare [CAUS_PASS]
            @ self.class8_suppletion
            @ self.class8_u_drop
            @ self.root_aorist_bhuv
            @ self.aorist_pass_vriddhi
            @ self.intensive_i_it
            @ self.clean_tags
        )