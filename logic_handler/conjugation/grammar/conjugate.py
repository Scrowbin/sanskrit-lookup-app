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

    def conjugate(self, root_str, class_num, person, number, voice="P", tense="present"):
        """
        Orchestrates the conversion from a root string to a fully inflected form.
        Fixes: Reference-before-assignment, logic overwrites, and tag propagation.
        """
        # Determine Strength
        if class_num in [1, 10]:
            strength = "[STRONG]"  # Thematic stem base is always strong
        elif tense == "future":
            strength = "[STRONG]"
        elif tense == "optative":
            strength = "[WEAK]"    # Athematic optative is weak
        elif class_num in [4, 6] or voice == "A":
            strength = "[WEAK]"
        else:
            # Athematic Classes (2, 3, 5, 7, 8, 9)
            strength = "[WEAK]"  # Default
            if voice == "P" and number == "sg":
                strength = "[STRONG]"
            
            # Special Exceptions
            if class_num == 3 and tense == "imperfect" and person == "3" and number == "pl":
                strength = "[STRONG]"  # Logic for 'ajuhavuḥ'
            if tense == "imperative" and person == "1":
                strength = "[STRONG]"  # Imperative 1st person is always strong
            if tense == "imperative" and person == "2" and number == "sg":
                strength = "[WEAK]"    # 'juhuhi' vs 'juhoti'

        # 2. Create the Root FST
        # We bake the strength tag in here so StemBuilder and SandhiEngine can "see" it.
        root_fst = pn.accep(root_str + strength)

        # 3. Build the Stem
        # Ensure 'tense' is passed so StemBuilder knows to use Future rules vs Gana rules.
        stem = self.stems.build(root_str, root_fst, class_num, strength, tense=tense)

        # 4. Apply the Imperfect Augment (a-)
        if tense == "imperfect":
            stem = pn.accep("a") + stem

        # 5. Route to the correct Endings Map
        if tense == "future":
            # Future uses Class 1 (thematic) present endings
            endings_map = SuffixProvider.get_present_active(class_num=1)
        elif tense == "present":
            endings_map = SuffixProvider.get_present_active(class_num=class_num)
        elif tense == "imperfect":
            endings_map = SuffixProvider.get_secondary_active(class_num=class_num)
        elif tense == "imperative":
            endings_map = SuffixProvider.get_imperative_active(class_num=class_num)
        elif tense == "optative":
            endings_map = SuffixProvider.get_optative_active(class_num=class_num)
        else:
             raise ValueError(f"Tense '{tense}' is not supported yet.")

        # 6. Combine: Stem + Person Tag
        tag = f"[{person}{number}]"
        suffix_fst = pn.accep(endings_map[tag])
        combined = stem + suffix_fst

        # 7. Metadata Cleanup
        # Remove tags after phonetics have fired so the final string is clean.
        cleanup_regex = pn.union("[STRONG]", "[WEAK]")
        cleanup = pn.cdrewrite(pn.cross(cleanup_regex, ""), "", "", self.sigma)

        # Now clean_string is purely phonetic (e.g., "bhav a āni")
        clean_string = combined @ cleanup 

        # 8. Apply Phonetic Rules on the naked string
        sandhi_applied = self.sandhi.apply_all(clean_string)
        
        return sandhi_applied.optimize().string()