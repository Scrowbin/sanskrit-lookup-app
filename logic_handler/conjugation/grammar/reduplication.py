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
            
        # Pāṇini 7.4.67: dyutisvāpyoḥ samprasāraṇam
        if root_str == "svap":
            return "su"
        if root_str == "dyut":
            return "di"
        # vy-initial: samprasāraṇa vi- (vivyathitha), not va-.
        if root_str.startswith("vy"):
            return "vi"

        if root_str and root_str[0] in ALPHABET.vowels_list:
            phonemes = ALPHABET.parse_phonemes(root_str)
            if root_str[0] == "a" and len(phonemes) > 2 and phonemes[1] not in ALPHABET.vowels_list and phonemes[2] not in ALPHABET.vowels_list:
                # Pāṇini 7.4.71 (nuṭ) + 7.4.70 (ādeḥ): ān- before a-initial heavy root (ānakṣa).
                return "ān"
            elif root_str[0] == "a":
                # For non-heavy a-initial roots (like aś), the prefix is ā (P. 7.4.70 ata ādeḥ) or an depending on the root.
                return "ā"
            elif root_str[0] in ("i", "ī"):
                return "i"
            elif root_str[0] in ("u", "ū"):
                return "u"
            elif root_str[0] in ("ṛ", "ṝ"):
                # Monosyllabic ṛ-roots (ṛj): ar- reduplicant (arjitha), not ā-.
                if len(phonemes) == 2:
                    return "ar"
                return "ā"
            
            import warnings
            warnings.warn(
                f"ReduplicationEngine: generating prefix for vowel-initial root '{root_str}'. "
                f"This root likely requires the periphrastic perfect instead.",
                stacklevel=2
            )

        syllable = self._extract_initial_syllable(root_str)
        prefix = self._reduce_via_fst(syllable)

        # Pāṇini 6.1.17: In the perfect, the reduplicating syllable of samprasāraṇa roots gets samprasāraṇa.
        # Note: samprasāraṇa (6.1.17) applies BEFORE halādiḥ śeṣaḥ (7.4.60).
        # Thus, 'vya' -> 'vi', NOT 'va' -> 'u'.
        from dhatupatha_analyzer import DHATUPATHA_ANALYZER
        root_obj = DHATUPATHA_ANALYZER.get(root_str, 1)
        if root_obj.takes_samprasarana:
            if root_str.startswith("vya"):
                prefix = "vi"
            elif root_str.startswith("śvi"):
                prefix = "śu"
            elif prefix.startswith("ya"):
                prefix = "i" + prefix[2:]
            elif prefix.startswith("va"):
                prefix = "u" + prefix[2:]
            elif prefix.startswith("ra"):
                prefix = "ṛ" + prefix[2:]

        return prefix

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
        
        # Add [NO_RUKI] tag (Whitney §184d: prefix 's' does not trigger RUKI on root 's')
        # The tag breaks the RUKI rule context.
        # Exception (Pāṇini 8.3.61): stu and ṇī DO undergo RUKI in desiderative.
        prefix = self._reduce_via_fst(new_syllable)
        if root_str not in ("stu", "nī", "ṇī"):
            prefix += "[NO_RUKI]"
        return prefix

    def generate_intensive_prefix(self, root_str: str) -> str:
        """Return the reduplication prefix for Intensive (Whitney §1002).
        Handles three subtypes:
        1. ṛ/ṝ roots get 'arī' (e.g. kṛ -> carīkṛ, nṛt -> narīnṛt)
        2. Nasal roots (am/an) get 'aṃ' (e.g. gam -> jaṅgam, kram -> caṅkram)
        3. Others get strong vowel (a -> ā, i/ī -> e, u/ū -> o)
        """
        syllable = self._extract_initial_syllable(root_str)
        vowels = set(ALPHABET.vowels_list)
        consonants = ""
        root_vowel = ""
        for ch in syllable:
            if ch in vowels:
                root_vowel = ch
                break
            consonants += ch
        
        phonemes = ALPHABET.parse_phonemes(root_str)
        
        # Subtype 2: Nasal final (Whitney §1002d)
        if phonemes and phonemes[-1] in ('m', 'n') and root_vowel == 'a':
            # Use homorganic nasal matching the root's first consonant
            # (INRIA convention: ṅ before velars, ñ before palatals, etc.)
            first_cons = phonemes[0] if phonemes else ''
            velar = {'k', 'kh', 'g', 'gh'}
            palatal = {'c', 'ch', 'j', 'jh'}
            retroflex = {'ṭ', 'ṭh', 'ḍ', 'ḍh'}
            dental = {'t', 'th', 'd', 'dh'}
            if first_cons in velar:
                nasal = "ṅ"
            elif first_cons in palatal:
                nasal = "ñ"
            elif first_cons in retroflex:
                nasal = "ṇ"
            elif first_cons in dental:
                nasal = "n"
            else:
                nasal = "ṃ"  # fallback
            target_vowel = "a" + nasal
        # Subtype 1: ṛ/ṝ root (Whitney §1002c)
        elif 'ṛ' in phonemes or 'ṝ' in phonemes:
            target_vowel = "arī"
        # Subtype 3: Standard strong vowel (Whitney §1002a)
        else:
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
        
        phonemes = ALPHABET.parse_phonemes(root_str)
        for ph in phonemes:
            if ph in vowels:
                root_vowel = ph
                found_vowel = True
            elif found_vowel:
                post_vowel_cons += ph
                
        # pre_vowel_cons must come from the REDUPLICATED syllable!
        pre_vowel_cons = ""
        for ph in ALPHABET.parse_phonemes(syllable):
            if ph in vowels:
                break
            pre_vowel_cons += ph
                
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
            @ self.deaspirate
            @ self.palatalize
            # Aorist reduplication preserves the long vowel if lengthened!
            @ self.r_to_a
        ).optimize()
        return list(res.paths().ostrings())[0]