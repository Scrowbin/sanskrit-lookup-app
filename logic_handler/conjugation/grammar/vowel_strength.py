import pynini as pn
from alphabet import ALPHABET

class VowelStrengthEngine:
    """Handles Guna (strengthening) and Vriddhi (protraction) rules."""

    def __init__(self):
        # Mapping for Guna: i -> e, u -> o, ṛ -> ar
        self.guna_map = pn.string_map([
            ("i", "e"), ("ī", "e"),
            ("u", "o"), ("ū", "o"),
            ("ṛ", "ar"), ("ṝ", "ar")
        ])
        
        # Rule: Apply Guna only if [STRONG] exists later in the string
        self.apply_guna = pn.cdrewrite(
            self.guna_map, 
            "", 
            ALPHABET.sigma_star + "[STRONG]", 
            ALPHABET.sigma_star
        )

        #vriddhi (Step 2 Strengthening))
        self.vriddhi_map = pn.string_map([
            ("a", "ā"),              # Crucial difference: 'a' actually changes here
            ("i", "ai"), ("ī", "ai"),
            ("u", "au"), ("ū", "au"),
            ("ṛ", "ār"), ("ṝ", "ār")
        ])

        self.apply_vriddhi = pn.cdrewrite(
            self.vriddhi_map, 
            "", 
            ALPHABET.sigma_star + "[VRIDDHI]", # Looks for the specific Vriddhi tag
            ALPHABET.sigma_star
        )

    def get_guna(self):
        return self.apply_guna
    
    def get_vriddhi(self):
        return self.apply_vriddhi