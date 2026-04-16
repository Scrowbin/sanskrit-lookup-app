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
        self.savarna = pn.cdrewrite(
            pn.string_map([
                # a-family
                ("aa", "ā"), ("aā", "ā"), ("āa", "ā"), ("āā", "ā"),
                # i-family
                ("ii", "ī"), ("iī", "ī"), ("īi", "ī"), ("īī", "ī"),
                # u-family
                ("uu", "ū"), ("uū", "ū"), ("ūu", "ū"), ("ūū", "ū"),
                # ṛ-family
                ("ṛṛ", "ṝ"), ("ṛṝ", "ṝ"), ("ṝṛ", "ṝ"), ("ṝṝ", "ṝ")
            ]),
            "", 
            "", 
            self.sig
        )

        # B. Ayadi Sandhi: e/o before ANY vowel becomes ay/av (131)
        # Fixes: bho + iṣyati -> bhaviṣyati
        self.ayadi = pn.cdrewrite(
            pn.string_map([("e", "ay"), ("o", "av"),("ai", "āy"),("au", "āv")]), 
            "", 
            pn.union(ALPHABET.vowels), 
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
                ("ī", "y"),
                ("u", "v"),
                ("ū", "v"),
                ("ṛ", "r")
            ]),
            "",
            pn.union(ALPHABET.vowels),
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
            pn.string_map([
                ("d", "t"), ("dh", "t"), 
                ("g", "k"), ("gh", "k"),
                ("b", "p"), ("bh", "p"),
                ("ḍ", "ṭ"), ("ḍh", "ṭ")]),
                "",
                pn.union("t", "th", "s"),
                self.sig
        )
        # Aspiration Throwback
        throwback_map = pn.string_map([("b", "bh"), ("d", "dh"), ("g", "gh")])
        root_vowels = ALPHABET.vowels
        final_aspirates = pn.union("gh", "dh", "bh", "h")
        throwback_triggers = pn.union("s", "t", "th", "[EOS]")
        
        self.grassmann_throwback = pn.cdrewrite(
            throwback_map,
            "", # Targets the initial b/d/g
            root_vowels + final_aspirates + throwback_triggers, # Looks ahead
            self.sig
        )
        
        # H-Sandhi: 'h' hardens to 'k' before 's' (Needed for roots like duh/guh)
        self.h_to_k = pn.cdrewrite(
            pn.cross("h", "k"), 
            pn.union(ALPHABET.vowels, "r", "l", "y", "v"), 
            "s", 
            self.sig
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
        triggers = pn.union("r", "ṛ", "ṣ", "ṝ")
        others = pn.union("y", "v", "h", "ṃ")
        
        # Using the clean global groups from ALPHABET
        allowed_interveners = pn.union(
            ALPHABET.vowels, 
            ALPHABET.gutturals, 
            ALPHABET.labials, 
            ALPHABET.retroflexes, 
            others
        ).star.optimize()
        
        right_context = pn.union(ALPHABET.vowels, "n", "m", "y", "v")

        self.nati = pn.cdrewrite(
            pn.cross("n", "ṇ"), 
            triggers + allowed_interveners, 
            right_context, 
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
            self.class9_special @
            self.yan_sandhi @
            self.savarna @
            
            # --- CONSONANT SANDHI ---
            self.grassmann_throwback @    # 1. Throwback first! (bodhsya -> bhodhsya)
            self.h_to_k @                 # 2. Harden H (dhohsya -> dhoksya)
            self.palatal_sandhi @         # 3. Revert Palatals 
            self.devoicing @              # 4. Devoice (bhodhsya -> bhotsya)
            self.nasal_assimilation @ 
            self.velar_nasal @
            # ------------------------
            
            self.drop_a @ 
            self.optative_cleanup @
            self.ruki @                   # 5. Ruki catches the new K! (dhoksya -> dhokṣya)
            self.nati @ 
            self.visarga              
        )