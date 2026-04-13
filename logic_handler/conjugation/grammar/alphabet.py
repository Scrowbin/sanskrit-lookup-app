import pynini as pn

class SanskritAlphabet:
    """Defines the IAST characters and metadata tags for the FST universe."""
    def __init__(self):
        # We use lists so Python doesn't split our multi-character strings
        vowels = ["a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "ḷ", "ḹ", "e", "ai", "o", "au"]
        consonants = [
            "k", "kh", "g", "gh", "ṅ", "c", "ch", "j", "jh", "ñ", 
            "ṭ", "ṭh", "ḍ", "ḍh", "ṇ", "t", "th", "d", "dh", "n", 
            "p", "ph", "b", "bh", "m", "y", "r", "l", "v", "ś", "ṣ", "s", "h"
        ]
        others = ["ḥ", "ṃ"]
        tags = ["[STRONG]", "[WEAK]", "[3s]", "[1s]", "[1d]", "[1p]", "[2s]", "[2d]", "[2p]", "[3d]", "[3p]"]

        # Native utf8 union. Pynini treats "[STRONG]" as an 8-character sequence automatically.
        self.alpha = pn.union(*(vowels + consonants + others + tags))
        self.sigma_star = self.alpha.closure()

ALPHABET = SanskritAlphabet()