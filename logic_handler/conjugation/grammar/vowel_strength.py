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

        # ── Guna map: short/long vowel → Guna equivalent ─────────────────────
        guna_map = pn.string_map([
            ("i", "e"), ("ī", "e"),
            ("u", "o"), ("ū", "o"),
            ("ṛ", "ar"), ("ṝ", "ar"),
            # 'a' and 'ā' are unchanged by Guna (they ARE Guna)
        ])

        # Apply guna to the vowel that immediately precedes [STRONG].
        # The lookahead is: zero or more consonants (no other vowels) then [STRONG].
        # This correctly handles CV roots like "kṛ[STRONG]" → "kar[STRONG]".
        self.apply_guna = pn.cdrewrite(
            guna_map,
            "",
            pn.closure(ALPHABET.consonants) + "[STRONG]",
            sig
        )

        # ── Vriddhi map ───────────────────────────────────────────────────────
        vriddhi_map = pn.string_map([
            ("a", "ā"),
            ("i", "ai"), ("ī", "ai"),
            ("u", "au"), ("ū", "au"),
            ("ṛ", "ār"), ("ṝ", "ār"),
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