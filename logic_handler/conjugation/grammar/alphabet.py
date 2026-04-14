import pynini as pn

class SanskritAlphabet:
    """Defines the IAST characters and metadata tags for the FST universe."""
    def __init__(self):
        # We use lists so Python doesn't split our multi-character strings
        self.vowels = ["a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "ḷ", "ḹ", "e", "ai", "o", "au"]
        self.consonants = [
            "k", "kh", "g", "gh", "ṅ", "c", "ch", "j", "jh", "ñ", 
            "ṭ", "ṭh", "ḍ", "ḍh", "ṇ", "t", "th", "d", "dh", "n", 
            "p", "ph", "b", "bh", "m", "y", "r", "l", "v", "ś", "ṣ", "s", "h"
        ]
        self.others = ["ḥ", "ṃ"]
        self.tags = ["[STRONG]", "[WEAK]", "[3sg]", "[1sg]", "[1d]", "[1pl]", "[2sg]", "[2d]", "[2pl]", "[3d]", "[3pl]"]

        # Native utf8 union. Pynini treats "[STRONG]" as an 8-character sequence automatically.
        self.alpha = pn.union(*(self.vowels + self.consonants + self.others + self.tags))
        self.sigma_star = self.alpha.closure()

ALPHABET = SanskritAlphabet()