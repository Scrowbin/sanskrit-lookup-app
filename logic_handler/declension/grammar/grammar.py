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
        self.sigma = pn.union(*"abcdefghijklmnopqrstuvwxyzāīūṛṝḷḹeaiouḥṃṅñṇnṃśṣs")
        self.sigma = pn.union(self.sigma, "[EOS]")
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
        self._build_sandi()

    def _build_nati_rule(self):
        """Compiles the Nati (retroflexion) context-dependent rewrite rule."""
        triggers = pn.union("r", "ṛ", "ṝ", "ṣ")
        velars = pn.union("k", "kh", "g", "gh", "ṅ")
        others = pn.union("y", "v", "h", "ṃ")

        # Interveners allowed between the trigger and 'n'
        allowed_interveners = pn.union(
            self.vowels, velars, self.labial, others
        ).closure()

        right_context = pn.union(self.vowels, "m", "v", "y")

        # Context-dependent rewrite: cross 'n' to 'ṇ'
        # Notice we are passing self.sigma_star here, not self.sigma!
        self.apply_nati_fst = pn.cdrewrite(
            pn.cross("n", "ṇ"),
            triggers + allowed_interveners,
            right_context,
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
        tau = pn.cross("s", "ṣ")

        ruki_sounds = ["r", "ṛ", "ṝ", "u", "ū", "k", "i", "ī", "e", "o"]
        lambda_ctx = pn.union(*ruki_sounds).optimize()
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
            pn.cross(pn.union("s", "r"), "ḥ"), "", "[EOS]", self.sigma
        )
        return eos_conversion.optimize()

    def _build_neuter_nasal_insertion(self):
        """
        Inserts 'n' before the final consonant for Neuter Nom/Acc/Voc Plurals.
        e.g., jagat[Neut][Nom][Pl] -> jagannt[Neut][Nom][Pl]
        """
        # 1. Define what triggers the rule (Neuter Plural tags)
        n_pl_tags = pn.union("[Neut][Nom][Pl]", "[Neut][Acc][Pl]", "[Neut][Voc][Pl]")

        # 2. Define the final consonants that require 'n' (plosives/stops)
        final_stops = pn.union("t", "d", "k", "g", "p", "b", "c", "j", "ṭ", "ḍ")

        # 3. The rule: Insert "n" out of thin air ("" -> "n")
        # Left context: Any vowel
        # Right context: The final consonant + the specific Neuter Plural tags
        insert_n = pn.cdrewrite(
            pn.cross("", "n"),
            self.vowels,
            final_stops + n_pl_tags,
            self.sigma_star,
        )

        self.neuter_nasal_insertion = insert_n.optimize()

    def _build_sandhi(self):
        # Jhal-to-Jash
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
            "",  # left context
            "[EOS]",  # right context
            self.sigma_star,
        )
        as_to_o = pn.cdrewrite(
            pn.cross("as", "o"),
            "",  # Left context: Empty (handled by the 'a' in the target)
            "bh",  # Right context: 'bh' (matches bhyām, bhis, bhyas)
            self.sigma_star,
        )
        is_us_to_r = pn.cdrewrite(
            pn.cross("s", "r"),
            pn.union(
                "i", "u", "ī", "ū"
            ),  # Left context: i, u (and their long versions)
            "bh",  # Right context: 'bh'
            self.sigma_star,
        )
        self.apply_s_stem_sandhi = (as_to_o @ is_us_to_r).optimize()


phonology = SanskritPhonology()
