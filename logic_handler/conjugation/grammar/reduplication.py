import pynini as pn
from alphabet import ALPHABET


class ReduplicationEngine:
    """Applies Abhyāsa (Reduplication) phonetic reductions to a verbal prefix.

    Architecture note
    -----------------
    The four Pāṇinian reduction rules (aspiration loss, velar→palatal,
    vowel shortening, ṛ→a) are each encoded as a ``pn.cdrewrite`` FST so that
    the reduction pipeline is fully transducer-based.  ``generate_prefix``
    composes these FSTs on a per-syllable acceptor and realises the result as a
    string — the string is used as a ``pn.accep(prefix)`` in the caller.

    Special-case overrides (e.g. √bhū → prefix "ba") are stored in
    ``irregulars.perfect_redupe_overrides`` so the FST rules remain generic.
    """

    def __init__(self):
        sig = ALPHABET.sigma_star

        # ── Rule 1: Aspiration loss ───────────────────────────────────────────
        self.deaspirate = pn.cdrewrite(
            pn.string_map([
                ("kh", "k"), ("gh", "g"),
                ("ch", "c"), ("jh", "j"),
                ("ṭh", "ṭ"), ("ḍh", "ḍ"),
                ("th", "t"), ("dh", "d"),
                ("ph", "p"), ("bh", "b"),
            ]),
            "", "", sig
        )

        # ── Rule 2: Velars & h → palatals ────────────────────────────────────
        self.palatalize = pn.cdrewrite(
            pn.string_map([("k", "c"), ("g", "j"), ("h", "j")]),
            "", "", sig
        )

        # ── Rule 3: Long vowel → short ────────────────────────────────────────
        self.shorten = pn.cdrewrite(
            pn.string_map([("ā", "a"), ("ī", "i"), ("ū", "u")]),
            "", "", sig
        )

        # ── Rule 4: Vocalic ṛ → a in the prefix ──────────────────────────────
        self.r_to_a = pn.cdrewrite(
            pn.cross("ṛ", "a"), "", "", sig
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _extract_initial_syllable(self, root_str: str) -> str:
        """Return the FIRST consonant + first vowel of *root_str* for reduplication.

        Whitney §590 / Pāṇini 7.4.60: when a root begins with a consonant cluster,
        only the FIRST consonant of the cluster is reduplicated.
        Pāṇini 7.4.61 (śarpūrvāḥ khayaḥ): if a sibilant (ś, ṣ, s) is followed by
        a voiceless stop (khay), the stop is reduplicated, not the sibilant.
        """
        vowels = set(ALPHABET.vowels_list)
        sibilants = {"ś", "ṣ", "s"}
        voiceless_stops = {"k", "kh", "c", "ch", "ṭ", "ṭh", "t", "th", "p", "ph"}
        
        phonemes = ALPHABET.parse_phonemes(root_str)
        if len(phonemes) >= 2 and phonemes[0] in sibilants and phonemes[1] in voiceless_stops:
            chosen_cons = phonemes[1]
        else:
            chosen_cons = None

        syllable = ""
        saw_consonant = False
        for ph in phonemes:
            if ph in vowels:
                syllable += ph
                break
            else:
                if not saw_consonant:
                    syllable += chosen_cons if chosen_cons else ph
                    saw_consonant = True
        return syllable

    def _reduce_via_fst(self, syllable: str) -> str:
        """Apply the four reduction FSTs to *syllable* and return the string."""
        fst = pn.accep(syllable)
        fst = (fst @ self.deaspirate
                    @ self.palatalize
                    @ self.shorten
                    @ self.r_to_a).optimize()
        return fst.string()

    # ── Public API ────────────────────────────────────────────────────────────

    def generate_prefix(self, root_str: str) -> str:
        """Return the reduplication prefix for *root_str* (Perfect/Class-3)."""
        # Pāṇini 7.4.73: bhavater aḥ (bhū takes a)
        if root_str == "bhū":
            return "ba"

        syllable = self._extract_initial_syllable(root_str)
        return self._reduce_via_fst(syllable)

    def generate_desiderative_prefix(self, root_str: str) -> str:
        """Return the reduplication prefix for Desiderative.
        Rule: prefix vowel is 'u' if root has 'u/ū', else 'i'."""
        syllable = self._extract_initial_syllable(root_str)
        
        # Vowel mapping for Desiderative
        vowels = set(ALPHABET.vowels_list)
        consonants = ""
        root_vowel = ""
        for ch in syllable:
            if ch in vowels:
                root_vowel = ch
                break
            consonants += ch
        
        target_vowel = "u" if root_vowel in ("u", "ū") else "i"
        new_syllable = consonants + target_vowel
        
        return self._reduce_via_fst(new_syllable)

    def generate_intensive_prefix(self, root_str: str) -> str:
        """Return the reduplication prefix for Intensive.
        Rule: prefix vowel is the guna of the root vowel (or lengthened 'a')."""
        syllable = self._extract_initial_syllable(root_str)
        vowels = set(ALPHABET.vowels_list)
        consonants = ""
        root_vowel = ""
        for ch in syllable:
            if ch in vowels:
                root_vowel = ch
                break
            consonants += ch
        
        # Intensive prefix vowels are strong:
        # a -> ā, i/ī -> e, u/ū -> o, ṛ -> ar
        guna_map = {"a": "ā", "ā": "ā", "i": "e", "ī": "e", "u": "o", "ū": "o", "ṛ": "ar", "ṝ": "ar"}
        target_vowel = guna_map.get(root_vowel, root_vowel)
        
        return self._reduce_via_fst(consonants + target_vowel)

    def generate_aorist_prefix(self, root_str: str) -> str:
        """Type 3 (Reduplicated / Caṅ) Aorist prefix.
        Used mostly for causatives.
        Reduplicating vowel is i/ī or u/ū.
        It is lengthened if the root is 'light' (short vowel + at most one consonant).
        """
        syllable = self._extract_initial_syllable(root_str)
        vowels = {"a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "ḷ", "e", "ai", "o", "au"}
        long_vowels = {"ā", "ī", "ū", "ṝ", "e", "ai", "o", "au"}
        
        # Determine root vowel and post-vowel consonants
        root_vowel = ""
        post_vowel_cons = ""
        pre_vowel_cons = ""
        found_vowel = False
        
        for ch in root_str:
            if ch in vowels:
                root_vowel = ch
                found_vowel = True
            elif found_vowel:
                post_vowel_cons += ch
            else:
                pre_vowel_cons += ch
                
        # Determine weight
        is_heavy = (root_vowel in long_vowels) or (len(post_vowel_cons) > 1)
        
        # Determine base reduplicating vowel
        if root_vowel in ("u", "ū", "o", "au"):
            base_v = "u"
        else:
            base_v = "i"
            
        # Lengthen if light
        if not is_heavy:
            if base_v == "i": base_v = "ī"
            elif base_v == "u": base_v = "ū"
            
        # Standard consonant reduction
        fst = pn.accep(pre_vowel_cons + base_v)
        res = (
            fst
            @ self.palatalize
            @ self.deaspirate
            # Aorist reduplication preserves the long vowel if lengthened!
            @ self.r_to_a
        ).optimize()
        return list(res.paths().ostrings())[0]