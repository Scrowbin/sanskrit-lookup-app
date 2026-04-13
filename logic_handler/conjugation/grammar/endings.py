import pynini as pn

class SuffixProvider:
    """Manages the Tiṅ-pratyaya (verb endings) tables."""

    @staticmethod
    def get_present_active(thematic=True):
        """Returns Present Indicative Parasmaipada [αε] endings."""
        if thematic:
            # Thematic stems already end in 'a'
            return {
                "[3s]": "ti",  "[3d]": "taḥ", "[3p]": "nti",
                "[2s]": "si",  "[2d]": "thaḥ", "[2p]": "tha",
                "[1s]": "mi",  "[1d]": "vaḥ",  "[1p]": "maḥ"
            }
        else:
            return {
                "[3s]": "ti",  "[3d]": "taḥ", "[3p]": "ati",
                "[2s]": "si",  "[2d]": "thaḥ", "[2p]": "tha",
                "[1s]": "mi",  "[1d]": "vaḥ",  "[1p]": "maḥ"
            }