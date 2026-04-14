import pynini as pn
from irregulars import * 
from alphabet import ALPHABET
class StemBuilder:
    """Builds the verbal stem based on the Present Class (Gaṇa)."""

    def __init__(self, guna_transducer):
        self.guna = guna_transducer
        self.vikaranas = {
            1: "a",   # Guna + a
            4: "ya",  # No Guna + ya
            6: "a",   # No Guna + a
            10: "aya" # Guna + aya
        }
        self.sigma = ALPHABET.sigma_star
        self.consonants = ALPHABET.consonants
        lengthen_map = pn.string_map([("i", "ī"), ("u", "ū")])
        self.tags = pn.union("[STRONG]", "[WEAK]")
        self.set_roots = set_roots
        self.class_4_lengthen = pn.cdrewrite(
            pn.cross("i", "ī"), 
            "", 
            "v" + self.tags, 
            self.sigma
        )

    def get_abhyasa(self, root_str):
        """
        Calculates the reduplicated prefix (Abhyāsa) for Class 3.
        Basic Rules:
        1. Initial aspirated consonants become non-aspirated (bh -> b).
        2. Velars become palatals (h -> j, k -> c).
        3. Vowels are usually shortened.
        """
        # Basic mapping for common Class 3 roots
        # For a full FST, this would be a pynini transducer
        redup_map = {
            "bhū": "ba",  # (Actually bhū is class 1, but if it were 3)
            "hu": "ju",   # h -> j (velar to palatal)
            "dhā": "da",  # dh -> d (aspirate to non-aspirate)
            "bhṛ": "bi",
            "hā": "ja"
        }
        return redup_map.get(root_str, root_str[0])
    
    def build(self, root_str, root_fst, class_num, strength, tense="present"):
        """Logic for stem formation."""
        # --- TENSE: FUTURE (Lṛṭ) ---
        if tense == "future":
            # 1. Future always takes Guṇa
            stem = root_fst @ self.guna
            # 2. Add 'i' augment if it's a 'set' root
            if root_str in self.set_roots:
                stem = stem + pn.accep("i")
            # 3. Add 'sya' infix (Sandhi will turn s->ṣ later)
            return stem + pn.accep("sya")

        # --- TENSE: PRESENT SYSTEM (Laṭ, Laṅ, Loṭ, Vidhi Liṅ) ---
        vikarana_str = self.vikaranas.get(class_num, "")
        vikarana_fst = pn.accep(vikarana_str)
        
        #Thematic logic
        if class_num in [1, 10]:
            if class_num == 1 and root_str in class_1_irregulars:
                irregular_stem = class_1_irregulars[root_str]
                return pn.accep(irregular_stem + strength) + vikarana_fst
            # Apply Guna logic then add vikarana
            return (root_fst @ self.guna) + vikarana_fst
        
        elif class_num == 4:
            # 1. Apply the lengthening rule to the root
            # 2. Add the 'ya' vikarana
            return (root_fst @ self.class_4_lengthen) + vikarana_fst
        
        elif class_num == 6:
            if root_str in nasal_roots:
                # If it's a nasal root, build a new FST from the irregular string
                return pn.accep(nasal_roots[root_str] + strength) + vikarana_fst
            return root_fst + vikarana_fst

        else:
            # Athematic logic (Class 2, 3, etc.)
            if class_num == 2:
                if root_str in class_2_irregulars:
                    # Build a new FST from the irregular string + add the strength tag
                    return pn.accep(class_2_irregulars[root_str] + strength)
                return (root_fst @ self.guna) if strength == "[STRONG]" else root_fst
            if class_num == 3:
                # Reduplication + Root(Guna/Weak)
                prefix = self.get_abhyasa(root_str)
                core = (root_fst @ self.guna) if strength == "[STRONG]" else root_fst
                return pn.accep(prefix) + core
            
            if class_num == 5:
                # Sign: -no- (Strong) / -nu- (Weak)
                vik = pn.accep("no") if strength == "[STRONG]" else pn.accep("nu")
                return root_fst + vik
            
            elif class_num == 7:
                # Determine which infix to insert
                infix = "na" if strength == "[STRONG]" else "n"
                
                # Define what the final consonant looks like
                consonant_fst = pn.union(*self.consonants)
                
                # The Rewrite Rule: 
                # Use pn.cross("", infix) to effectively "insert"
                insert_infix = pn.cdrewrite(
                    pn.cross("", infix), # <--- Fix is here
                    "", 
                    consonant_fst + self.tags, 
                    self.sigma
                )
                
                return root_fst @ insert_infix

            if class_num == 8:
                # Sign: -o- (Strong) / -u- (Weak)
                # Similar to Class 5, but usually only for roots ending in 'n'
                vik = pn.accep("o") if strength == "[STRONG]" else pn.accep("u")
                return root_fst + vik
            
            if class_num == 9:
                # Sign: -nā- (Strong) / -nī- (Weak)
                # Note: 'n' will become 'ṇ' later if the root has 'r' or 'ṛ'
                vik = pn.accep("nā") if strength == "[STRONG]" else pn.accep("nī")
                return root_fst + vik

            return root_fst