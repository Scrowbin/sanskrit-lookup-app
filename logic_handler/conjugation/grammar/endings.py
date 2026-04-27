import pynini as pn
from paradigm import is_thematic


class SuffixProvider:
    """Manages the Tiṅ-pratyaya (verb endings) tables.

    Dual keys use 'du' (matching INRIA's number column: sg / du / pl).

    Paradigm branching uses ``is_thematic(class_num)`` (from paradigm.py)
    rather than inline ``class_num in [1, 4, 6, 10]`` checks.
    Class-3 further overrides 3pl active forms wherever it differs.
    """

    # ── 1. PRESENT TENSE (Laṭ) ───────────────────────────────────────────────

    @staticmethod
    def get_present_active(class_num=1, root_str=None, **kwargs):
        # Future/Conditional always use thematic endings
        if kwargs.get("tense") in ("future", "conditional"):
            class_num = 1
        if is_thematic(class_num):
            return {
                "[3sg]": "ti",  "[3du]": "taḥ",  "[3pl]": "nti",
                "[2sg]": "si",  "[2du]": "thaḥ", "[2pl]": "tha",
                "[1sg]": "āmi", "[1du]": "āvaḥ", "[1pl]": "āmaḥ"
            }
        # Athematic: 3pl = "ati" for cl3 (juhv+ati), "anti" otherwise
        third_pl = "ati" if class_num == 3 else "anti"
        return {
            "[3sg]": "ti",  "[3du]": "taḥ",  "[3pl]": third_pl,
            "[2sg]": "si",  "[2du]": "thaḥ", "[2pl]": "tha",
            "[1sg]": "mi",  "[1du]": "vaḥ",  "[1pl]": "maḥ"
        }

    @staticmethod
    def get_present_middle(class_num=1, root_str=None, **kwargs):
        if kwargs.get("tense") in ("future", "conditional"):
            class_num = 1
        if is_thematic(class_num):
            return {
                "[3sg]": "te",  "[3du]": "ete",   "[3pl]": "nte",
                "[2sg]": "se",  "[2du]": "ethe",  "[2pl]": "dhve",
                "[1sg]": "e",   "[1du]": "āvahe", "[1pl]": "āmahe"
            }
        return {
            "[3sg]": "te",  "[3du]": "āte",  "[3pl]": "ate",
            "[2sg]": "ṣe",  "[2du]": "āthe", "[2pl]": "dhve",
            "[1sg]": "e",   "[1du]": "vahe", "[1pl]": "mahe"
        }


    # ── 2. IMPERFECT / CONDITIONAL (Laṅ / Lṛṅ) ──────────────────────────────

    @staticmethod
    def get_secondary_active(class_num=1, root_str=None, **kwargs):
        if kwargs.get("tense") == "conditional":
            class_num = 1
        if is_thematic(class_num):
            return {
                "[3sg]": "t",  "[3du]": "tām",  "[3pl]": "n",
                "[2sg]": "s",  "[2du]": "tam",  "[2pl]": "ta",
                "[1sg]": "m",  "[1du]": "āva",  "[1pl]": "āma"
            }
        # Athematic: 3pl = "uḥ" for cl3 (ajuhavuḥ), "an" otherwise
        third_pl = "uḥ" if class_num == 3 else "an"
        
        # √ad cl-2 imperfect/aorist/injunctive active uses connecting-vowel endings
        if root_str == "ad":
            return {
                "[3sg]": "at",  "[3du]": "tām",  "[3pl]": "an",
                "[2sg]": "as",  "[2du]": "tam",  "[2pl]": "ta",
                "[1sg]": "am",  "[1du]": "va",   "[1pl]": "ma"
            }

        return {
            "[3sg]": "t",   "[3du]": "tām", "[3pl]": third_pl,
            "[2sg]": "s",   "[2du]": "tam", "[2pl]": "ta",
            "[1sg]": "am",  "[1du]": "va",  "[1pl]": "ma"
        }

    @staticmethod
    def get_secondary_middle(class_num=1, root_str=None, **kwargs):
        if kwargs.get("tense") == "conditional":
            class_num = 1
        if is_thematic(class_num):
            return {
                "[3sg]": "ta",   "[3du]": "etām",  "[3pl]": "nta",
                "[2sg]": "thāḥ", "[2du]": "ethām", "[2pl]": "dhvam",
                "[1sg]": "i",    "[1du]": "āvahi", "[1pl]": "āmahi"
            }
        return {
            "[3sg]": "ta",   "[3du]": "ātām",  "[3pl]": "ata",
            "[2sg]": "thāḥ", "[2du]": "āthām", "[2pl]": "dhvam",
            "[1sg]": "i",    "[1du]": "vahi",  "[1pl]": "mahi"
        }


    # ── 3. IMPERATIVE TENSE (Loṭ) ────────────────────────────────────────────

    @staticmethod
    def get_imperative_active(class_num=1, root_str=None, **kwargs):
        if is_thematic(class_num):
            return {
                "[3sg]": "tu",   "[3du]": "tām",  "[3pl]": "ntu",
                "[2sg]": "",     "[2du]": "tam",  "[2pl]": "ta",
                "[1sg]": "āni",  "[1du]": "āva",  "[1pl]": "āma"
            }
        if class_num == 3:
            # Panini 6.4.101: dhi after hu/ad; hi elsewhere for athematic cl3
            return {
                "[3sg]": "tu",  "[3du]": "tām", "[3pl]": "atu",
                "[2sg]": "dhi" if root_str in ("hu", "ad") else "hi",
                "[2du]": "tam", "[2pl]": "ta",
                "[1sg]": "āni", "[1du]": "āva", "[1pl]": "āma"
            }
        # Generic athematic
        return {
            "[3sg]": "tu",   "[3du]": "tām",  "[3pl]": "antu",
            "[2sg]": "hi",   "[2du]": "tam",  "[2pl]": "ta",
            "[1sg]": "āni",  "[1du]": "āva",  "[1pl]": "āma"
        }

    @staticmethod
    def get_imperative_middle(class_num=1, root_str=None, **kwargs):
        if is_thematic(class_num):
            return {
                "[3sg]": "tām",  "[3du]": "itām",  "[3pl]": "ntām",
                "[2sg]": "sva",  "[2du]": "ithām", "[2pl]": "dhvam",
                # "ai" ending: sandhi a+ai→ai handled in sandhi.thematic_merger
                "[1sg]": "ai",   "[1du]": "āvahai", "[1pl]": "āmahai"
            }
        return {
            "[3sg]": "tām",  "[3du]": "ātām",   "[3pl]": "atām",
            "[2sg]": "ṣva",  "[2du]": "āthām",  "[2pl]": "dhvam",
            "[1sg]": "ai",   "[1du]": "āvahai", "[1pl]": "āmahai"
        }


    # ── 4. OPTATIVE TENSE (Vidhi Liṅ) ────────────────────────────────────────

    @staticmethod
    def get_optative_active(class_num=1, root_str=None, **kwargs):
        if is_thematic(class_num):
            return {
                "[3sg]": "et",   "[3du]": "etām",  "[3pl]": "eyuḥ",
                "[2sg]": "eḥ",   "[2du]": "etam",  "[2pl]": "eta",
                "[1sg]": "eyam", "[1du]": "eva",   "[1pl]": "ema"
            }
        return {
            "[3sg]": "yāt",  "[3du]": "yātām", "[3pl]": "yuḥ",
            "[2sg]": "yāḥ",  "[2du]": "yātam", "[2pl]": "yāta",
            "[1sg]": "yām",  "[1du]": "yāva",  "[1pl]": "yāma"
        }

    @staticmethod
    def get_optative_middle(class_num=1, root_str=None, **kwargs):
        if is_thematic(class_num):
            return {
                "[3sg]": "eta",   "[3du]": "eyātām",  "[3pl]": "eran",
                "[2sg]": "ethāḥ", "[2du]": "eyāthām", "[2pl]": "edhvam",
                "[1sg]": "eya",   "[1du]": "evahi",   "[1pl]": "emahi"
            }
        return {
            "[3sg]": "īta",   "[3du]": "īyātām",  "[3pl]": "īran",
            "[2sg]": "īthāḥ", "[2du]": "īyāthām", "[2pl]": "īdhvam",
            "[1sg]": "īya",   "[1du]": "īvahi",   "[1pl]": "īmahi"
        }


    # ── 5. PERFECT TENSE (Liṭ) ───────────────────────────────────────────────

    @staticmethod
    def get_perfect_active(root_str=None, **kwargs):
        # Default 2sg ending is -itha (with connecting vowel i).
        # Roots that take bare -tha are handled as overrides.
        from irregulars import perfect_bare_tha_roots, perfect_weak_guna_roots
        
        second_sg = "tha" if (root_str in perfect_bare_tha_roots or root_str in perfect_weak_guna_roots) else "itha"
        
        endings = {
            "[3sg]": "a",     "[3du]": "atuḥ",  "[3pl]": "uḥ",
            "[2sg]": second_sg, "[2du]": "athuḥ", "[2pl]": "a",
            "[1sg]": "a",     "[1du]": "iva",   "[1pl]": "ima"
        }

        # ṛ-final roots in the perfect take bare 'va/vahe/ma/mahe' du/pl endings
        if root_str and root_str.endswith("ṛ"):
            endings["[1du]"] = "va"
            endings["[1pl]"] = "ma"
            endings["[2du]"] = "vathuḥ"
            
        return endings

    @staticmethod
    def get_perfect_middle(root_str=None, **kwargs):
        endings = {
            "[3sg]": "e",    "[3du]": "āte",   "[3pl]": "ire",
            "[2sg]": "iṣe",  "[2du]": "āthe",  "[2pl]": "idhve",
            "[1sg]": "e",    "[1du]": "ivahe", "[1pl]": "imahe"
        }
        
        # ṛ-final roots in the perfect take bare 'vahe/mahe' du/pl endings
        if root_str and root_str.endswith("ṛ"):
            endings["[1du]"] = "vahe"
            endings["[1pl]"] = "mahe"
            
        return endings

    # ── 6. PERIPHRASTIC FUTURE (Luṭ) ─────────────────────────────────────────

    @staticmethod
    def get_periphrastic_future_active(**kwargs):
        return {
            "[3sg]": "tā",    "[3du]": "tārau",  "[3pl]": "tāraḥ",
            "[2sg]": "tāsi",  "[2du]": "tāsthaḥ", "[2pl]": "tāstha",
            "[1sg]": "tāsmi", "[1du]": "tāsvaḥ",  "[1pl]": "tāsmaḥ"
        }

    @staticmethod
    def get_periphrastic_future_middle(**kwargs):
        return {
            "[3sg]": "tā",    "[3du]": "tārau",   "[3pl]": "tāraḥ",
            "[2sg]": "tāse",  "[2du]": "tāsāthe", "[2pl]": "tādhve",
            "[1sg]": "tāhe",  "[1du]": "tāsvahe", "[1pl]": "tāsmahe"
        }

    # ── 7. AORIST (Luṅ) / INJUNCTIVE ─────────────────────────────────────────

    @staticmethod
    def get_aorist_active(class_num=1, root_str=None, **kwargs):
        from irregulars import aorist_overrides
        info = aorist_overrides.get(root_str)
        aorist_type = info["type"] if info else "s"
        
        if aorist_type in ("a", "reduplicated", "sa"):
            return SuffixProvider.get_secondary_active(class_num=1)
        if aorist_type == "root":
            # Root aorist uses standard athematic secondary endings
            return SuffixProvider.get_secondary_active(class_num=2)
            
        if aorist_type == "is":
            return {
                "[3sg]": "īt",     "[3du]": "iṣṭām", "[3pl]": "iṣus",
                "[2sg]": "īs",     "[2du]": "iṣṭam", "[2pl]": "iṣṭa",
                "[1sg]": "iṣam",   "[1du]": "iṣva",  "[1pl]": "iṣma"
            }
        
        # s, sis aorists use special endings:
        return {
            "[3sg]": "īt",  "[3du]": "tām", "[3pl]": "us",
            "[2sg]": "īs",  "[2du]": "tam", "[2pl]": "ta",
            "[1sg]": "am",  "[1du]": "va",  "[1pl]": "ma"
        }

    @staticmethod
    def get_aorist_middle(class_num=1, root_str=None, **kwargs):
        from irregulars import aorist_overrides
        info = aorist_overrides.get(root_str)
        aorist_type = (info.get("middle_type") or info["type"]) if info else "s"
        
        if aorist_type in ("a", "reduplicated", "sa"):
            return SuffixProvider.get_secondary_middle(class_num=1)
        if aorist_type == "root":
            return SuffixProvider.get_secondary_middle(class_num=2)
            
        if aorist_type == "is":
            return {
                "[3sg]": "iṣṭa",   "[3du]": "iṣātām",  "[3pl]": "iṣata",
                "[2sg]": "iṣṭhāḥ", "[2du]": "iṣāthām", "[2pl]": "idhvam",
                "[1sg]": "iṣi",    "[1du]": "iṣvahi",  "[1pl]": "iṣmahi"
            }
            
        # s, sis aorists
        return {
            "[3sg]": "ta",   "[3du]": "ātām",  "[3pl]": "ata",
            "[2sg]": "thāḥ", "[2du]": "āthām", "[2pl]": "dhvam",
            "[1sg]": "i",    "[1du]": "vahi",  "[1pl]": "mahi"
        }
    @staticmethod
    def get_aorist_passive(class_num=1, root_str=None, **kwargs):
        """Passive aorist endings. 3sg ciṇ uses bare -i (Vriddhi on the stem side)."""
        endings = SuffixProvider.get_aorist_middle(class_num=class_num, root_str=root_str)
        endings["[3sg]"] = "i"   # ciṇ ending; stem carries [AORIST_PASS_3SG] for Vriddhi
        return endings


    # ── 6. PASSIVE VOICE (Karmani Prayoga) ───────────────────────────────────

    @staticmethod
    def get_passive_endings(tense):
        """Passives use the Middle voice endings (thematic pattern)."""
        if tense in ("present", "future"):
            return SuffixProvider.get_present_middle(class_num=1)
        if tense in ("imperfect", "conditional"):
            return SuffixProvider.get_secondary_middle(class_num=1)
        if tense == "imperative":
            return SuffixProvider.get_imperative_middle(class_num=1)
        if tense == "optative":
            return SuffixProvider.get_optative_middle(class_num=1)
        if tense == "perfect":
            raise ValueError("No passive perfect in Sanskrit.")
        return {}