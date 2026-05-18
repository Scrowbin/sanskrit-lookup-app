import pynini as pn
from alphabet import ALPHABET

class VowelStrengthEngine:
    """Handles Guna (strengthening) and Vriddhi (protraction) rules.

    Design note
    -----------
    The FST works on strings of the form:

        <consonants*> <vowel> <consonants*> [STRONG]
        e.g.  "kṛ[STRONG]"   →  "kar[STRONG]"   (ṛ → ar via guna)
              "hu[STRONG]"   →  "ho[STRONG]"    (u → o)

    The rewrite fires on the last vowel before the [STRONG] tag so that
    polysyllabic roots (rare but present) are handled correctly.

    [STRONG] / [WEAK] / [CLASS8] tags are consumed later by MorphologyEngine,
    so they must remain in the string until that stage.
    """

    def __init__(self):
        sig = ALPHABET.sigma_star

        # ── Guna rules (Whitney §240) ─────────────────────────────────────────
        # 1. Final vowels (short or long) take guna.
        guna_map_final = pn.string_map([
            ("i", "e"), ("ī", "e"),
            ("u", "o"), ("ū", "o"),
            ("ṛ", "ar"), ("ṝ", "ar"),
            ("ḷ", "al"),
        ])
        
        # 2. Medial vowels take guna ONLY if short AND followed by exactly ONE consonant.
        # (Prosodically heavy syllables — long vowel or vowel before cluster — block guna).
        guna_map_medial = pn.string_map([
            ("i", "e"),
            ("u", "o"),
            ("ṛ", "ar"),
            ("ḷ", "al"),
        ])

        self.apply_guna = (
            pn.cdrewrite(guna_map_final, "", "[STRONG]", sig)
            @ pn.cdrewrite(guna_map_medial, "", ALPHABET.consonants + "[STRONG]", sig)
        ).optimize()

        # ── Vriddhi map ───────────────────────────────────────────────────────
        # Whitney §235–237; Pāṇini 1.1.1 (vṛddhi of each vowel).
        vriddhi_map = pn.string_map([
            ("a", "ā"),
            ("i", "ai"), ("ī", "ai"),
            ("u", "au"), ("ū", "au"),
            ("ṛ", "ār"), ("ṝ", "ār"),
            ("ḷ", "āl"),   # Whitney §237: ḷ's vṛddhi is āl (was missing)
        ])

        self.apply_vriddhi = pn.cdrewrite(
            vriddhi_map,
            "",
            pn.closure(ALPHABET.consonants) + "[VRIDDHI]",
            sig
        )

    def get_guna(self):
        return self.apply_guna

    def get_vriddhi(self):
        return self.apply_vriddhi