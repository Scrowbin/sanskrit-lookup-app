import pynini as pn

class SuffixProvider:
    """Manages the Tiṅ-pratyaya (verb endings) tables with Class 3 overrides."""

    @staticmethod
    def get_present_active(class_num=1):
        """1. Primary Endings: Used for Present (Laṭ)."""
        # Thematic classes (1, 4, 6, 10)
        if class_num in [1, 4, 6, 10]:
            return {
                "[3sg]": "ti",  "[3d]": "taḥ", "[3pl]": "nti",
                "[2sg]": "si",  "[2d]": "thaḥ", "[2pl]": "tha",
                "[1sg]": "āmi",  "[1d]": "āvaḥ",  "[1pl]": "āmaḥ" 
            }
        # Athematic classes (2, 3, 5, 7, 8, 9)
        else:
            # Special Case: Class 3 (and other reduplicated stems) 
            # drops the 'n' in 3pl (e.g., juhvati)
            third_pl = "ati" if class_num == 3 else "anti"
            
            return {
                "[3sg]": "ti",  "[3d]": "taḥ", "[3pl]": third_pl,
                "[2sg]": "si",  "[2d]": "thaḥ", "[2pl]": "tha",
                "[1sg]": "mi",  "[1d]": "vaḥ",  "[1pl]": "maḥ"
            }
        
    @staticmethod
    def get_secondary_active(class_num=1):
        """2. Secondary Endings: Used for Imperfect (Laṅ)."""
        if class_num in [1, 4, 6, 10]:
            return {
                "[3sg]": "t",   "[3d]": "tām",  "[3pl]": "n",
                "[2sg]": "s",   "[2d]": "tam",  "[2pl]": "ta",
                "[1sg]": "m",   "[1d]": "āva",   "[1pl]": "āma"   # <--- Added ā
            }
        else:
            # Special Case: Class 3 3pl Imperfect usually takes 'uḥ' (jus)
            # which triggers Guṇa in the root (e.g., ajuhavuḥ)
            third_pl = "uḥ" if class_num == 3 else "an"
            first_sg = "am"
            
            return {
                "[3sg]": "t",   "[3d]": "tām",  "[3pl]": third_pl,
                "[2sg]": "s",   "[2d]": "tam",  "[2pl]": "ta",
                "[1sg]": first_sg, "[1d]": "va", "[1pl]": "ma"
            }

    @staticmethod
    def get_imperative_active(class_num=1):
        """3. Imperative Endings: Used for Commands (Loṭ)."""
        if class_num in [1, 4, 6, 10]:
            return {
                "[3sg]": "tu",   "[3d]": "tām",  "[3pl]": "ntu",
                "[2sg]": "",     "[2d]": "tam",  "[2pl]": "ta",
                "[1sg]": "āni",  "[1d]": "āva",  "[1pl]": "āma"
            }
        else:
            # Special Case: Class 3 3pl drops 'n' -> 'atu'
            third_pl = "atu" if class_num == 3 else "antu"
            # Athematic 2sg usually takes 'hi' or 'dhi'
            second_sg = "hi"
            
            return {
                "[3sg]": "tu",   "[3d]": "tām",  "[3pl]": third_pl,
                "[2sg]": second_sg, "[2d]": "tam",  "[2pl]": "ta",
                "[1sg]": "āni",  "[1d]": "āva",  "[1pl]": "āma"
            }

    @staticmethod
    def get_perfect_active():
        """4. Perfect Endings: Used for Distant Past (Liṭ)."""
        return {
            "[3sg]": "a",    "[3d]": "atur",  "[3pl]": "uḥ",
            "[2sg]": "tha",  "[2d]": "athur", "[2pl]": "a",
            "[1sg]": "a",    "[1d]": "va",    "[1pl]": "ma"
        }
    
    @staticmethod
    def get_optative_active(class_num=1):
        """4. Optative Endings: Used for 'should/would' (Vidhi Liṅ)."""
        if class_num in [1, 4, 6, 10]:
            # Thematic: a + ī -> e
            return {
                "[3sg]": "et",   "[3d]": "etām",  "[3pl]": "eyuḥ",
                "[2sg]": "eḥ",   "[2d]": "etam",  "[2pl]": "eta",
                "[1sg]": "eyam", "[1d]": "eva",   "[1pl]": "ema"
            }
        else:
            # Athematic: stem + yā + endings
            return {
                "[3sg]": "yāt",  "[3d]": "yātām", "[3pl]": "yuḥ",
                "[2sg]": "yāḥ",  "[2d]": "yātam", "[2pl]": "yāta",
                "[1sg]": "yām",  "[1d]": "yāva",  "[1pl]": "yāma"
            }