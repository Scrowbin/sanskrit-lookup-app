import pynini as pn

class SanskritAlphabet:
    """Defines the IAST characters, phonetic groups, and metadata tags for the FST universe."""
    
    def __init__(self):
        # 1. Define raw Python lists, using standard IAST
        self.vowels_list = ["a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "ḷ", "ḹ", "e", "ai", "o", "au"]
        
        self.gutturals_list = ["k", "kh", "g", "gh", "ṅ"]
        self.palatals_list = ["c", "ch", "j", "jh", "ñ"]
        self.retroflexes_list = ["ṭ", "ṭh", "ḍ", "ḍh", "ṇ"]
        self.dentals_list = ["t", "th", "d", "dh", "n"]
        self.labials_list = ["p", "ph", "b", "bh", "m"]
        
        self.semivowels_list = ["y", "r", "l", "v"]
        self.sibilants_list = ["ś", "ṣ", "s"]
        
        # h is functionally a consonant, ḥ and ṃ are modifiers (Visarga/Anusvara)
        self.others_list = ["ḥ", "ṃ"] 

        # --- THE CONSONANT LIST ---
        self.consonants_list = (
            self.gutturals_list + self.palatals_list + 
            self.retroflexes_list + self.dentals_list + 
            self.labials_list + self.semivowels_list + 
            self.sibilants_list + ["h"]
        )
        
        self.tags_list = ["[STRONG]", "[WEAK]", "[VRIDDHI]" "[3sg]", "[1sg]", "[1d]", "[1pl]", "[2sg]", "[2d]", "[2pl]", "[3d]", "[3pl]"]

        # 2. Pre-compile Pynini Unions 
        self.vowels = pn.union(*self.vowels_list)
        self.gutturals = pn.union(*self.gutturals_list)
        self.palatals = pn.union(*self.palatals_list)
        self.retroflexes = pn.union(*self.retroflexes_list)
        self.dentals = pn.union(*self.dentals_list)
        self.labials = pn.union(*self.labials_list)
        self.semivowels = pn.union(*self.semivowels_list)
        self.sibilants = pn.union(*self.sibilants_list)
        
        # --- THE MISSING CONSONANT FST ---
        self.consonants = pn.union(*self.consonants_list)

        # 3. Master Universe
        all_chars = self.vowels_list + self.consonants_list + self.others_list + self.tags_list
        
        self.alpha = pn.union(*all_chars)
        self.sigma_star = self.alpha.closure()

ALPHABET = SanskritAlphabet()