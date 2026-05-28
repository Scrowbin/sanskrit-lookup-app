import pynini as pn

"""
TODO : ~~ruki rule~~
~~ check for visarga as well  ~~
~~ s to ṣ : go -> goṣu ~~
~~ verify ant_mant_vant_stems  ~~
~~ Hardcode kinship/agent words ~~
~~ewrite the codebase to accept anygenders, D.R.Y methodology.~~
~~ check out  Jhal-to-Jash rule ($t \to d$ before voiced $bh$) ~~
~~ In the $s$-stem oblique cases (like manas + ā), the output is manasā. However, in the cases like manas + bhyām, the $s$ usually becomes $o$ (for $as$-stems) or $r$ (for $is$-stems). ~~
Long ū-stem implementaton
~~ Re compile all the shit ~~ + add isolated edge cases.
"""


class SanskritPhonology:
    def __init__(self):
        # 1. DEFINE SIGMA AND SIGMA STAR
        self.sigma = pn.union(*("abcdefghijklmnopqrstuvwxyzāīūṛṝḷḹṃḥṅñṭḍṇśṣḻ"))
        self.sigma = pn.union(self.sigma, "[WORD_END]")
        self.sigma_star = self.sigma.closure()

        # 2. VOWELS
        self.short_vowels = pn.union(*"aiuṛḷ")
        self.long_vowels = pn.union("ā", "ī", "ū", "ṝ", "ḹ")
        self.diph_thongs = pn.union("e", "ai", "o", "au")
        self.vowels = pn.union(self.short_vowels, self.long_vowels, self.diph_thongs)

        self.vowel_endings = pn.union("a", "ā", "i", "ī", "u", "ū", "ṛ")
        self.consonant_endings = pn.union("t", "n", "s")

        # 3. CONSONANTS
        self.guttural = pn.union("k", "kh", "g", "gh", "ṅ")
        self.palatal = pn.union("c", "ch", "j", "jh", "ñ")
        self.retroflex = pn.union("ṭ", "ṭh", "ḍ", "ḍh", "ṇ")
        self.dental = pn.union("t", "th", "d", "dh", "n")
        self.labial = pn.union("p", "ph", "b", "bh", "m")

        self.semivowels = pn.union("y", "r", "l", "v")
        self.sibilants = pn.union("ś", "ṣ", "s")
        self.aspirate = pn.union("h")

        # 4. VOICED & UNVOICED CONSONANTS
        self.voiced_stops = pn.union(
            "g", "gh", "j", "jh", "ḍ", "ḍh", "d", "dh", "b", "bh"
        )
        self.nasals = pn.union("ṅ", "ñ", "ṇ", "n", "m")
        self.voiced_consonants = pn.union(
            self.voiced_stops, self.nasals, self.semivowels, self.aspirate
        )

        self.unvoiced_stops = pn.union(
            "k", "kh", "c", "ch", "ṭ", "ṭh", "t", "th", "p", "ph"
        )
        self.hard_consonants = pn.union(self.unvoiced_stops, self.sibilants)

        # 5. MASTER SETS
        self.voiced_sounds = pn.union(self.vowels, self.voiced_consonants)
        self.all_consonants = pn.union(
            self.guttural,
            self.palatal,
            self.retroflex,
            self.dental,
            self.labial,
            self.semivowels,
            self.sibilants,
            self.aspirate,
        )
        self.all_sounds = pn.union(self.vowels, self.all_consonants)

        self.any_gender = pn.union("[Masc]", "[Fem]", "[Neut]")

        # 6. INITIALIZE REWRITE RULES
        self._build_nati_rule()
        self._build_ruki_rule()
        self._build_neuter_nasal_insertion()
        self._build_sandhi()

    def _build_nati_rule(self):
        """
        Build the Sanskrit ṇati rule.

        Dental n -> retroflex ṇ after:
            r, ṛ, ṝ, ṣ

        Allowed interveners (vowels, gutturals, labials, y, v, h, ṃ):
            Pāṇini's allowed interveners: vowels, velars/gutturals (k-varga),
            labials (p-varga), y, v, h, and anusvāra (ṃ).
        """
        triggers = pn.union("r", "ṛ", "ṝ", "ṣ")

        allowed = pn.union(
            self.vowels,
            # gutturals / velars
            "k", "kh", "g", "gh", "ṅ",
            # labials
            "p", "ph", "b", "bh", "m",
            # semivowels / misc
            "y", "v", "h", "ṃ",
        ).closure()

        self.apply_nati_fst = pn.cdrewrite(
            pn.cross("n", "ṇ"),
            triggers + allowed,
            pn.union(self.vowels, "m", "y", "v", "n"),
            self.sigma_star,
        )

    def apply_nati(self, word: str) -> str:
        """
        Helper method to process a string through the Nati FST.
        Composes the string acceptor with the rule FST and projects to the output string.
        """
        try:
            return (pn.accep(word) @ self.apply_nati_fst).string()
        except pn.FstOpError:
            # If composition fails (e.g., character not in alphabet), return the original word
            print("nati transformation failure")
            return word

    def _build_ruki_rule(self):
        """
        RUKI rule: s -> ṣ after r/ṛ/u/k/i (and long variants/diphthongs)
        optionally followed by ḥ or ṃ.
        """
        tau = pn.cross("s", "ṣ")

        ruki_sounds = ["r", "ṛ", "ṝ", "u", "ū", "k", "i", "ī", "e", "o", "ai", "au"]
        lambda_ctx = (pn.union(*ruki_sounds) + pn.union("ḥ", "ṃ", "")).optimize()
        self.apply_ruki_rule_fst = pn.cdrewrite(
            tau, lambda_ctx, "", self.sigma_star
        ).optimize()


    def apply_ruki(self, word: str) -> str:
        try:
            return (pn.accep(word) @ self.apply_ruki_rule_fst).string()
        except pn.FstOpError:
            print("ruki transformation failure")
            return word

    def apply_visarga(self):
        eos_conversion = pn.cdrewrite(
            pn.cross(pn.union("s", "r"), "ḥ"), "", "[WORD_END]", self.sigma
        )
        return eos_conversion.optimize()

    def _build_neuter_nasal_insertion(self):
        """
        Inserts 'n' before the final consonant for Neuter Nom/Acc/Voc Plurals.
        e.g., jagat[Neut][Nom][Pl] -> jagannt[Neut][Nom][Pl]
        """
        # 1. Define what triggers the rule (Neuter Plural tags)
        n_pl_tags = pn.union("[Neut][Nom][Pl]", "[Neut][Acc][Pl]", "[Neut][Voc][Pl]")

        # 2. Homorganic nasal insertion rules based on target consonant classes
        insert_n_dental = pn.cdrewrite(
            pn.cross("", "n"),
            self.vowels,
            pn.union("t", "d") + n_pl_tags,
            self.sigma_star,
        )
        insert_n_palatal = pn.cdrewrite(
            pn.cross("", "ñ"),
            self.vowels,
            pn.union("c", "j") + n_pl_tags,
            self.sigma_star,
        )
        insert_n_retroflex = pn.cdrewrite(
            pn.cross("", "ṇ"),
            self.vowels,
            pn.union("ṭ", "ḍ") + n_pl_tags,
            self.sigma_star,
        )
        insert_n_guttural = pn.cdrewrite(
            pn.cross("", "ṅ"),
            self.vowels,
            pn.union("k", "g") + n_pl_tags,
            self.sigma_star,
        )
        insert_n_labial = pn.cdrewrite(
            pn.cross("", "m"),
            self.vowels,
            pn.union("p", "b") + n_pl_tags,
            self.sigma_star,
        )

        insert_n = (
            insert_n_dental
            @ insert_n_palatal
            @ insert_n_retroflex
            @ insert_n_guttural
            @ insert_n_labial
        )

        self.neuter_nasal_insertion = insert_n.optimize()

    def _build_sandhi(self):
        # ── Jhal-to-Jash (P. 8.2.39) ─────────────────────────────────────────
        # EXTERNAL SANDHI only: final stop/sibilant → voiced unaspirated before
        # a voiced-initial word.  NOT used for isolated word forms (use
        # apply_permitted_finals instead for those).
        jhal_to_jash = pn.string_map(
            [
                ("k", "g"),
                ("kh", "g"),
                ("g", "g"),
                ("gh", "g"),
                ("c", "j"),
                ("ch", "j"),
                ("j", "j"),
                ("jh", "j"),
                ("ṭ", "ḍ"),
                ("ṭh", "ḍ"),
                ("ḍ", "ḍ"),
                ("ḍh", "ḍ"),
                ("t", "d"),
                ("th", "d"),
                ("d", "d"),
                ("dh", "d"),
                ("p", "b"),
                ("ph", "b"),
                ("b", "b"),
                ("bh", "b"),
                ("ś", "j"),
                ("ṣ", "ḍ"),
                ("s", "d"),
                ("h", "gh"),
            ]
        )
        self.apply_jhal_to_jash = pn.cdrewrite(
            jhal_to_jash,
            "",
            "[WORD_END]",
            self.sigma_star,
        )

        # ── Permitted Finals (Whitney §141–150; Pāṇini 8.2.30–39) ────────────
        # At ABSOLUTE word-end (isolated form), only voiceless unaspirated stops
        # are permitted.  Voiced/aspirated stops deasperate and devoice; palatals
        # revert to velars; ś/ṣ → ṭ; s/r → ḥ (handled by apply_visarga).
        permitted = pn.string_map(
            [
                # Velars: voiced/aspirated → k
                ("gh", "k"),
                ("g", "k"),
                # Palatals revert to velar (Whitney §142)
                ("jh", "k"),
                ("j", "k"),
                ("ch", "k"),
                ("c", "k"),
                # Retroflexes: voiced/aspirated → ṭ
                ("ḍh", "ṭ"),
                ("ḍ", "ṭ"),
                # Dentals: voiced/aspirated → t
                ("dh", "t"),
                ("d", "t"),
                ("th", "t"),
                # Labials: voiced/aspirated → p
                ("bh", "p"),
                ("b", "p"),
                ("ph", "p"),
                # Sibilants → retroflex stop (Whitney §145)
                ("ś", "ṭ"),
                ("ṣ", "ṭ"),
                # h: treated as voiced aspirate → devoice to k (default; duh-class
                # handled separately in paradigm FSTs)
                ("h", "k"),
            ]
        )
        self.apply_permitted_finals = pn.cdrewrite(
            permitted,
            "",
            "[WORD_END]",
            self.sigma_star,
        ).optimize()

        # ── S-stem oblique sandhi ─────────────────────────────────────────────
        # as → o / is-us → r before bh-initial endings (Whitney §176–177).
        as_to_o = pn.cdrewrite(
            pn.cross("as", "o"),
            "",
            "bh",
            self.sigma_star,
        )
        is_us_to_r = pn.cdrewrite(
            pn.cross("s", "r"),
            pn.union("i", "u", "ī", "ū"),
            "bh",
            self.sigma_star,
        )
        self.apply_s_stem_sandhi = (as_to_o @ is_us_to_r).optimize()


phonology = SanskritPhonology()
