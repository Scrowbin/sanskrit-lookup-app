import pynini as pn
from alphabet import ALPHABET

class SandhiEngine:
    """Modular FST engine for Sanskrit Phonology."""
    
    def __init__(self):
        self.sig = ALPHABET.sigma_star

        # Initialize Rule Blocks
        self._setup_vowel_rules()
        self._setup_consonant_rules()
        self._setup_morphology_rules()
        self._setup_long_distance_rules()

    def _setup_vowel_rules(self):
        """Rules handling vowel contact and mergers."""
        
        # A. Savarna Dirgha (Homogeneous Merger): a+a -> ā, i+i -> ī, etc.
        # Fixes: a + ad -> ād | krīṇā + āni -> krīṇāni
        self.savarna = pn.cdrewrite(
            pn.string_map([("aa", "ā"), ("aā", "ā"), ("āa", "ā"), ("āā", "ā")]),
            "", 
            "", 
            self.sig
        )

        self.vowel_cleanup = pn.cdrewrite(
            pn.union(
                pn.cross("āā", "ā"),
                pn.cross("īī", "ī"),
                pn.cross("ūū", "ū")
            ),
            "",
            "",
            self.sig
        )

        # B. Ayadi Sandhi: e/o before ANY vowel becomes ay/av
        # Fixes: bho + iṣyati -> bhaviṣyati
        self.ayadi = pn.cdrewrite(
            pn.string_map([("e", "ay"), ("o", "av")]), 
            "", 
            pn.union(*ALPHABET.vowels), 
            self.sig
        )

        # C. Thematic Merger: a + e -> e
        # Fixes: bhava + et -> bhavet
        self.thematic_merger = pn.cdrewrite(
            pn.cross("a", ""),
            "",
            "e",
            self.sig
        )

        # D. Yan Sandhi: i/u/ṛ -> y/v/r before a vowel
        # Fixes: sunu + anti -> sunvanti
        self.yan_sandhi = pn.cdrewrite(
            pn.string_map([
                ("i", "y"),
                ("u", "v"),
                ("ū", "v"),
                ("ṛ", "r")
            ]),
            "",
            pn.union(*ALPHABET.vowels),
            self.sig
        )

        # Class 9 special: ī disappears before 'a' or 'ā' (krīṇī + anti -> krīṇanti)
        self.class9_special = pn.cdrewrite(
            pn.cross("ī", ""),
            "",
            pn.union("a", "ā"),
            self.sig
        )

    def _setup_consonant_rules(self):
        # A. Palatal Reversion & Devoicing (j/d -> k/t before unvoiced)
        self.palatal_sandhi = pn.cdrewrite(
            pn.string_map([("j", "k"), ("c", "k")]), "", pn.union("t", "th", "s"), self.sig
        )
        self.devoicing = pn.cdrewrite(
            pn.string_map([("d", "t")]), "", pn.union("t", "th", "s"), self.sig
        )
        # B. Nasal Assimilation (n -> ñ/ṅ)
        self.nasal_assimilation = pn.cdrewrite(
            pn.string_map([("n", "ñ")]), "", pn.union("j", "c"), self.sig
        )
        self.velar_nasal = pn.cdrewrite(
            pn.string_map([("n", "ṅ")]), "", pn.union("k", "g", "kh", "gh"), self.sig
        )

    def _setup_morphology_rules(self):
        # Anchor the suffixes to [EOS] so they don't misfire on internal syllables
        self.drop_a = pn.cdrewrite(pn.cross("a", ""), "ā", "nti", self.sig)
        self.optative_cleanup = pn.cdrewrite(pn.cross("yā", ""), "", "yuḥ", self.sig)

    def _setup_long_distance_rules(self):
        """Late-firing rules for Ruki and Nati."""

        # A. Ruki: s -> ṣ
        ruki_triggers = pn.union("ṛ", "r", "u", "ū", "k", "i", "ī", "e", "ai", "o", "au")
        self.ruki = pn.cdrewrite(pn.cross("s", "ṣ"), ruki_triggers, "", self.sig)

        # B. Nati: n -> ṇ
        # Trigger: r, ṛ, ṣ
        # Interveners: Vowels, Gutturals, Labials, y, v, h, AND retroflexes (like ṇ)
        triggers = pn.union("r", "ṛ", "ṣ")
        allowed = pn.union(
            *ALPHABET.vowels, 
            pn.union("k", "kh", "g", "gh", "ṅ", "h"), 
            pn.union("p", "ph", "b", "bh", "m", "v", "y"),
            pn.union("ṭ", "ṭh", "ḍ", "ḍh", "ṇ") # Added retroflexes to allowed list
        ).optimize()
        
        self.nati = pn.cdrewrite(
            pn.cross("n", "ṇ"), 
            triggers + allowed.star, 
            pn.union(*ALPHABET.vowels, "n", "m", "y", "v"), 
            self.sig
        )

        self.visarga = pn.cdrewrite(
            pn.string_map([("s", "ḥ"), ("r", "ḥ"), ("ṣ", "ḥ")]),
            "",
            "[EOS]",
            self.sig
        )

    def apply_all(self, fst):
        return (fst @ 
            self.thematic_merger @ 
            self.ayadi @ 
            self.yan_sandhi @
            self.class9_special @
            self.savarna @
            self.vowel_cleanup @
            self.palatal_sandhi @ 
            self.devoicing @ 
            self.nasal_assimilation @ 
            self.velar_nasal @
            self.drop_a @ 
            self.ruki @ 
            self.nati @ 
            self.visarga              
        )