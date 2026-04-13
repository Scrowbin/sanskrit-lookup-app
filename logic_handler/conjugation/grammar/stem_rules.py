import pynini as pn

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

    def build(self, root_fst, class_num):
        """Logic for thematic stem formation."""
        vikarana_str = self.vikaranas.get(class_num, "")
        
        # --- FIX: Removed token_type=ALPHABET.alpha ---
        # Let Pynini parse "a", "ya", and "aya" natively.
        vikarana_fst = pn.accep(vikarana_str)
        
        if class_num in [1, 10]:
            # Apply Guna logic then add vikarana
            return (root_fst @ self.guna) + vikarana_fst
        elif class_num in [4, 6]:
            # Just add vikarana (No Guna)
            return root_fst + vikarana_fst
        else:
            # Athematic logic (Class 2, 3, etc.) - simple root for now
            return root_fst