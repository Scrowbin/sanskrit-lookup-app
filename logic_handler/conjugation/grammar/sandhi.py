import pynini as pn
from alphabet import ALPHABET

class SandhiEngine:
    """The internal sandhi engine for phonetic resolution."""

    def __init__(self):
        sig = ALPHABET.sigma_star
        
        # 1. Internal Vowel Sandhi
        vowel_to_cons = pn.string_map([("e", "ay"), ("o", "av")])
        self.resolve_stem_joint = pn.cdrewrite(vowel_to_cons, "", "a", sig)

        # --- THE FIX ---
        # 2. 1st Person Lengthening
        # Look specifically for the 1st person endings, not just any 'm' or 'v'
        first_person_suffixes = pn.union("mi", "vaḥ", "maḥ")
        self.lengthen_1st = pn.cdrewrite(pn.cross("a", "ā"), "", first_person_suffixes, sig)

        # 3. Ruki Rule
        ruki_triggers = pn.union("ṛ", "r", "u", "ū", "k", "i", "ī", "e", "ai", "o", "au")
        self.ruki = pn.cdrewrite(pn.cross("s", "ṣ"), ruki_triggers, "", sig)

    def apply_all(self, fst):
        return fst @ self.resolve_stem_joint @ self.lengthen_1st @ self.ruki