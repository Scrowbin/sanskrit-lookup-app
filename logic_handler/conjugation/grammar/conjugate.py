import pynini as pn
from alphabet import ALPHABET
from guna import GunaEngine
from sandhi import SandhiEngine
from stem_rules import StemBuilder
from endings import SuffixProvider

class SanskritConjugator:
    """The main engine orchestrating the conjugation pipeline."""

    def __init__(self):
        self.guna = GunaEngine()
        self.sandhi = SandhiEngine()
        self.stems = StemBuilder(self.guna.get_transducer())
        self.sigma = ALPHABET.sigma_star

    def conjugate(self, root_str, class_num, person, number, voice="P"):
        """Stage-by-Stage Pipeline execution."""
        
        strength = "[STRONG]" if (number == "s" and voice == "P") else "[WEAK]"
        tag = f"[{person}{number}]"
        
        # --- FIX: Removed token_type. Let Pynini use default UTF-8 ---
        root_fst = pn.accep(root_str + strength)
        
        # Build the Stem
        stem = self.stems.build(root_fst, class_num)
        
        # Ending Addition
        is_thematic = class_num in [1, 4, 6, 10]
        endings_map = SuffixProvider.get_present_active(thematic=is_thematic)
        
        # --- FIX: Removed token_type. ---
        suffix_fst = pn.accep(endings_map[tag])
        
        # Combine: Stem + Suffix
        combined = stem + suffix_fst
        
        # 1. Delete the metadata tags so the letters physically touch
        cleanup = pn.cdrewrite(pn.cross(pn.union("[STRONG]", "[WEAK]"), ""), "", "", self.sigma)
        cleaned_combined = combined @ cleanup
        
        # 2. Now that the string is 'bhoati', apply Sandhi
        final_fst = self.sandhi.apply_all(cleaned_combined)
        
        # 3. Optimize and Extract
        result_fst = final_fst.optimize()
        
        # Return the string representation
        return result_fst.string()

if __name__ == "__main__":
    api = SanskritConjugator()
    print(f"bhū (1) 3s: {api.conjugate('bhū', 1, '3', 's')}")
    print(f"bhū (1) 1s: {api.conjugate('bhū', 1, '1', 's')}")