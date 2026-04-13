import pynini as pn
from alphabet import ALPHABET

class GunaEngine:
    """Handles Guna (strengthening) and Vriddhi (protraction) rules."""

    def __init__(self):
        # Mapping for Guna: i -> e, u -> o, ṛ -> ar
        self.guna_map = pn.string_map([
            ("i", "e"), ("ī", "e"),
            ("u", "o"), ("ū", "o"),
            ("ṛ", "ar")
        ])
        
        # Rule: Apply Guna only if [STRONG] exists later in the string
        self.apply_guna = pn.cdrewrite(
            self.guna_map, 
            "", 
            ALPHABET.sigma_star + "[STRONG]", 
            ALPHABET.sigma_star
        )

    def get_transducer(self):
        return self.apply_guna