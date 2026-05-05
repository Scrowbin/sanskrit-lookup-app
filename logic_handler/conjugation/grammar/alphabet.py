import pynini as pn

class SanskritAlphabet:
    """Defines IAST characters, phonetic groups, and abstract morphophonological
    tags for the FST universe.

    Tags that appear *inside* FST strings (and must therefore be in sigma_star):
        [STRONG]  – triggers Guna in the vowel-strength FST
        [WEAK]    – no strengthening; consumed by clean_tags
        [VRIDDHI] – triggers Vriddhi (unused in present system, reserved)
        [CLASS4]  – triggers Class-4 internal vowel lengthening
        [CLASS8]  – triggers kṛ → kur / kar suppletion
        [PASSIVE] – triggers passive vowel lengthening
    """

    def __init__(self):
        # ── Vowels ────────────────────────────────────────────────────────────
        self.vowels_list = [
            "a", "ā", "i", "ī", "u", "ū",
            "ṛ", "ṝ", "ḷ", "ḹ",
            "e", "ai", "o", "au"
        ]

        # ── Consonant classes ─────────────────────────────────────────────────
        self.gutturals_list  = ["k", "kh", "g", "gh", "ṅ"]
        self.palatals_list   = ["c", "ch", "j", "jh", "ñ"]
        self.retroflexes_list= ["ṭ", "ṭh", "ḍ", "ḍh", "ṇ"]
        self.dentals_list    = ["t", "th", "d", "dh", "n"]
        self.labials_list    = ["p", "ph", "b", "bh", "m"]
        self.semivowels_list = ["y", "r", "l", "v"]
        self.sibilants_list  = ["ś", "ṣ", "s"]

        self.consonants_list = (
            self.gutturals_list  + self.palatals_list  +
            self.retroflexes_list+ self.dentals_list   +
            self.labials_list    + self.semivowels_list +
            self.sibilants_list  + ["h"]
        )

        # ── Modifiers / suprasegmentals ───────────────────────────────────────
        self.modifiers_list = ["ḥ", "ṃ"]

        # ── Abstract morphophonological tags that live inside FST strings ──────
        # IMPORTANT: keep this list in sync with every tag emitted by stem_rules.py
        # and consumed (erased) by morphology.py.
        self.tags_list = [
            "[STRONG]", "[WEAK]", "[VRIDDHI]",
            "[CLASS4]", "[CLASS8]", "[PASSIVE]", "[CAUS_PASS]",
            "[ROOT_AORIST]", "[AORIST]", "[AORIST_PASS_3SG]", "[INTENSIVE_ACTIVE]",
            "[CLASS2_WEAK]", "[SAMP]", "[AUG]", "[NASAL]"
        ]
        # ── Pynini FST atoms ─────────────────────────────────────────────────
        self.vowels      = pn.union(*self.vowels_list)
        self.gutturals   = pn.union(*self.gutturals_list)
        self.palatals    = pn.union(*self.palatals_list)
        self.retroflexes = pn.union(*self.retroflexes_list)
        self.dentals     = pn.union(*self.dentals_list)
        self.labials     = pn.union(*self.labials_list)
        self.semivowels  = pn.union(*self.semivowels_list)
        self.sibilants   = pn.union(*self.sibilants_list)
        self.consonants  = pn.union(*self.consonants_list)

        # ── Master universe (sigma*) ──────────────────────────────────────────
        all_chars = (
            self.vowels_list   +
            self.consonants_list +
            self.modifiers_list +
            self.tags_list      +
            ["+"]               # morpheme boundary
        )
        self.alpha      = pn.union(*all_chars)
        self.sigma_star = pn.closure(self.alpha)

    def parse_phonemes(self, s: str) -> list:
        """Tokenize an IAST string into Sanskrit phonemes."""
        valid_phonemes = set(self.vowels_list + self.consonants_list + self.modifiers_list)
        result = []
        i = 0
        while i < len(s):
            # Check 2-character phonemes first (like 'kh', 'ai')
            if i < len(s) - 1 and s[i:i+2] in valid_phonemes:
                result.append(s[i:i+2])
                i += 2
            elif s[i] in valid_phonemes:
                result.append(s[i])
                i += 1
            else:
                # Keep abstract tags or unknown characters as-is
                # Since tags are formatted like [STRONG], we can let them be
                # or we can handle them manually if needed.
                # For basic stem_rules usage on clean roots, simple iteration works.
                result.append(s[i])
                i += 1
        return result

ALPHABET = SanskritAlphabet()