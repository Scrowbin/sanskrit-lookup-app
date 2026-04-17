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
    def get_present_active(class_num=1):
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
    def get_present_middle(class_num=1):
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
    def get_secondary_active(class_num=1):
        if is_thematic(class_num):
            return {
                "[3sg]": "t",  "[3du]": "tām",  "[3pl]": "n",
                "[2sg]": "s",  "[2du]": "tam",  "[2pl]": "ta",
                "[1sg]": "m",  "[1du]": "āva",  "[1pl]": "āma"
            }
        # Athematic: 3pl = "uḥ" for cl3 (ajuhavuḥ), "an" otherwise
        third_pl = "uḥ" if class_num == 3 else "an"
        return {
            "[3sg]": "t",   "[3du]": "tām", "[3pl]": third_pl,
            "[2sg]": "s",   "[2du]": "tam", "[2pl]": "ta",
            "[1sg]": "am",  "[1du]": "va",  "[1pl]": "ma"
        }

    @staticmethod
    def get_secondary_middle(class_num=1):
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
    def get_imperative_active(class_num=1):
        if is_thematic(class_num):
            return {
                "[3sg]": "tu",   "[3du]": "tām",  "[3pl]": "ntu",
                "[2sg]": "",     "[2du]": "tam",  "[2pl]": "ta",
                "[1sg]": "āni",  "[1du]": "āva",  "[1pl]": "āma"
            }
        # Athematic: 3pl = "atu" for cl3 (juhavatu), "antu" otherwise
        third_pl = "atu" if class_num == 3 else "antu"
        return {
            "[3sg]": "tu",   "[3du]": "tām",  "[3pl]": third_pl,
            "[2sg]": "hi",   "[2du]": "tam",  "[2pl]": "ta",
            "[1sg]": "āni",  "[1du]": "āva",  "[1pl]": "āma"
        }

    @staticmethod
    def get_imperative_middle(class_num=1):
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
    def get_optative_active(class_num=1):
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
    def get_optative_middle(class_num=1):
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
    def get_perfect_active():
        # Default 2sg ending is -itha (with connecting vowel i).
        # Roots that take bare -tha are handled as overrides in conjugate.py.
        return {
            "[3sg]": "a",     "[3du]": "atuḥ",  "[3pl]": "uḥ",
            "[2sg]": "itha",  "[2du]": "athuḥ", "[2pl]": "a",
            "[1sg]": "a",     "[1du]": "iva",   "[1pl]": "ima"
        }

    @staticmethod
    def get_perfect_middle():
        return {
            "[3sg]": "e",    "[3du]": "āte",   "[3pl]": "ire",
            "[2sg]": "iṣe",  "[2du]": "āthe",  "[2pl]": "idhve",
            "[1sg]": "e",    "[1du]": "ivahe", "[1pl]": "imahe"
        }


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