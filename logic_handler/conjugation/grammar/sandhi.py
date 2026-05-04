"""sandhi.py — FST-based Sanskrit internal phonology (stem-boundary sandhi).

Pipeline order: vowel_phase → consonant_phase → long_distance_phase.
Within each phase, rules are ordered by specificity (most specific first).

All three phase methods accept ``debug=True``.  When enabled, rules are
applied *one by one* via ``_apply_rules_with_trace()``, which prints the
intermediate string after every rule and stops immediately when a rule causes
the FST to go empty — identifying exactly which rule killed the valid path.
"""
import pynini as pn
from alphabet import ALPHABET


class SandhiEngine:
    """Modular FST engine for Sanskrit internal phonology."""

    def __init__(self):
        self.sig = ALPHABET.sigma_star
        self._setup_vowel_rules()
        self._setup_consonant_rules()
        self._setup_long_distance_rules()
        # Erase morpheme boundaries at the very end
        self.clean_boundaries = pn.cdrewrite(pn.cross("+", ""), "", "", self.sig)
        # Named rule lists — populated after all rules are built
        self._build_named_rule_lists()

    # ──────────────────────────────────────────────────────────────────────────
    # Rule setup
    # ──────────────────────────────────────────────────────────────────────────

    def _setup_vowel_rules(self):
        # 1. Thematic / Pararupa mergers: a/ā + {e,o,ai,au} → the diphthong wins.
        self.thematic_merger = pn.cdrewrite(
            pn.string_map([
                ("a+e",  "e"),  ("ā+e",  "e"),
                ("a+o",  "o"),  ("ā+o",  "o"),
                ("a+ai", "ai"), ("ā+ai", "ai"),
                ("a+au", "au"), ("ā+au", "au"),
            ]),
            "", "", self.sig
        )

        # 2. Savarna (identical vowel coalescence).
        # NOTE: i+i→ī intentionally excluded — perfect weak yan handles it.
        self.savarna = pn.cdrewrite(
            pn.string_map([
                ("a+a", "ā"), ("a+ā", "ā"), ("ā+a", "ā"), ("ā+ā", "ā"),
                ("i+ī", "ī"), ("ī+i", "ī"), ("ī+ī", "ī"),
                ("u+u", "ū"), ("u+ū", "ū"), ("ū+u", "ū"), ("ū+ū", "ū"),
                ("ṛ+ṛ", "ṝ"), ("ṛ+ṝ", "ṝ"), ("ṝ+ṛ", "ṝ"), ("ṝ+ṝ", "ṝ"),
            ]),
            "", "", self.sig
        )

        # 3. Guna sandhi: a/ā + i/u/ṛ → e/o/ar
        self.guna_sandhi = pn.cdrewrite(
            pn.string_map([
                ("a+i", "e"),  ("a+ī", "e"),  ("ā+i", "e"),  ("ā+ī", "e"),
                ("a+u", "o"),  ("a+ū", "o"),  ("ā+u", "o"),  ("ā+ū", "o"),
                ("a+ṛ", "ar"), ("a+ṝ", "ar"), ("ā+ṛ", "ar"), ("ā+ṝ", "ar"),
            ]),
            "", "", self.sig
        )

        # 4. Ayadi (diphthong before vowel): e+V → ay+V, o+V → av+V, etc.
        self.ayadi = pn.cdrewrite(
            pn.string_map([
                ("e+", "ay"), ("o+", "av"), ("ai+", "āy"), ("au+", "āv"),
            ]),
            "", pn.union(ALPHABET.vowels, "y"), self.sig
        )

        # 5. Yan sandhi (semi-vowelisation before vowel)
        self.yan_sandhi = pn.cdrewrite(
            pn.string_map([
                ("i+", "y"), ("ī+", "y"),
                ("u+", "v"), ("ū+", "v"),
                ("ṛ+", "r"),
            ]),
            "", ALPHABET.vowels, self.sig
        )

        # 6. Class-9 suffix vowel-drop: ī+ erased before any vowel-initial ending
        self.class9_special = pn.cdrewrite(
            pn.cross("ī+", ""), "", ALPHABET.vowels, self.sig
        )

    def _setup_consonant_rules(self):
        unvoiced_triggers = pn.union("+t", "+th", "+s", "+ṣ")

        # Homorganic stop+aspirate assimilation at morpheme boundary:
        # ad + dhi → addhi (cf. standard internal sandhi; needed for imperative 2sg).
        self.d_dh_gemination = pn.cdrewrite(pn.cross("d+dh", "ddh"), "", "", self.sig)

        # Bartholomae (aspirate assimilation): h+t → gdh, etc.
        # bh+t is handled separately as bdh (e.g. labh+ta -> labdha).
        self.bartho_bht = pn.cdrewrite(pn.cross("bh+t", "bdh"), "", "", self.sig)
        self.bartho_bhth = pn.cdrewrite(pn.cross("bh+th", "bdh"), "", "", self.sig)
        self.bartho_hth = pn.cdrewrite(pn.cross("h+th", "gdh"), "", "", self.sig)
        self.bartho_hdh = pn.cdrewrite(pn.cross("h+dh", "gdh"), "", "", self.sig)
        self.bartho_ht  = pn.cdrewrite(pn.cross("h+t",  "gdh"), "", "", self.sig)

        # Grassmann's Law (throwback deaspiuration)
        throwback_triggers = pn.union(
            "+s", "+ṣ", "+t", "+th", "+dhv", "[EOS]", "+[EOS]"
        )
        self.grassmann_throwback = pn.cdrewrite(
            pn.string_map([("b", "bh"), ("d", "dh"), ("g", "gh")]),
            "", ALPHABET.vowels + pn.union("gh", "dh", "bh", "h", "gdh") + throwback_triggers,
            self.sig
        )

        # h → k before +s/+ṣ (after a vowel or sonorant)
        self.h_to_k = pn.cdrewrite(
            pn.cross("h", "k"),
            pn.union(ALPHABET.vowels, "r", "l", "y", "v"),
            pn.union("+s", "+ṣ"),
            self.sig
        )

        # Palatal → velar before unvoiced dental/sibilant
        self.palatal_sandhi = pn.cdrewrite(
            pn.string_map([("j", "k"), ("c", "k")]),
            "", unvoiced_triggers, self.sig
        )
        # After r, palatal j before dental t/th surfaces as retroflex ṣṭ/ṣṭh
        # (e.g. mārj+ti -> mārṣṭi; Whitney §212-213).
        self.rj_retroflex = pn.cdrewrite(
            pn.string_map([("rj+t", "rṣṭ"), ("rj+th", "rṣṭh")]),
            "", "", self.sig
        )

        # General devoicing
        self.devoicing = pn.cdrewrite(
            pn.string_map([
                ("d",  "t"), ("dh", "t"), ("g",  "k"), ("gh", "k"),
                ("b",  "p"), ("bh", "p"), ("ḍ",  "ṭ"), ("ḍh", "ṭ"),
            ]),
            "", unvoiced_triggers, self.sig
        )

        # Nasal assimilation: n → ñ before +j/+c
        self.nasal_assimilation = pn.cdrewrite(
            pn.cross("n", "ñ"), "", pn.union("+j", "+c", "j", "c"), self.sig
        )
        # Class-7 yuj-type clusters: yuñj+dhv/hi -> yuṅgdhv/i.
        # This bridges nasal assimilation output (ñj) to attested velar+aspirate
        # sequences in middle/imperative paradigms (Whitney class-7 behavior).
        self.nj_cluster_hardening = pn.cdrewrite(
            pn.string_map([
                ("ñ+j+dhv", "ṅgdhv"),
                ("ñ+j+dh", "ṅgdh"),
                ("ñ+j+h", "ṅgdh"),
            ]),
            "", "", self.sig
        )

        # ── Anusvāra and Parasavarṇa (m + consonant) ──────────────────────────
        # m -> anusvāra before all consonants (this is optional before stops externally, but obligatory internally/preverbs)
        # Then anusvāra -> parasavarṇa (homorganic nasal) before stops.
        # We can implement this directly mapping m + stop -> homorganic nasal + stop
        self.parasavarna = pn.cdrewrite(
            pn.string_map([
                ("m+k", "ṅ+k"), ("m+kh", "ṅ+kh"), ("m+g", "ṅ+g"), ("m+gh", "ṅ+gh"),
                ("m+c", "ñ+c"), ("m+ch", "ñ+ch"), ("m+j", "ñ+j"), ("m+jh", "ñ+jh"),
                ("m+ṭ", "ṇ+ṭ"), ("m+ṭh", "ṇ+ṭh"), ("m+ḍ", "ṇ+ḍ"), ("m+ḍh", "ṇ+ḍh"),
                ("m+t", "n+t"), ("m+th", "n+th"), ("m+d", "n+d"), ("m+dh", "n+dh"), ("m+n", "n+n"),
                ("m+p", "m+p"), ("m+ph", "m+ph"), ("m+b", "m+b"), ("m+bh", "m+bh"), ("m+m", "m+m"),
            ]),
            "", "", self.sig
        )
        
        # m -> ṃ (anusvāra) before semivowels (y, r, l, v) and sibilants (ś, ṣ, s, h)
        self.anusvara = pn.cdrewrite(
            pn.cross("m+", "ṃ+"),
            "", pn.union("y", "r", "l", "v", "ś", "ṣ", "s", "h"), self.sig
        )
        # Internal root+suffix m+y (e.g. gam+ya) remains m, not anusvāra.
        # This prevents over-assimilation in forms like saṅgamya (Whitney §993).
        self.gamya_fix = pn.cdrewrite(
            pn.cross("gaṃ+y", "gam+y"), "", "", self.sig
        )

        # Retroflex assimilation (Panini 8.4.41)
        self.retro_th  = pn.cdrewrite(pn.cross("ṣ+th", "ṣṭh"), "", "", self.sig)
        self.retro_t   = pn.cdrewrite(pn.cross("ṣ+t",  "ṣṭ"),  "", "", self.sig)
        self.retro_dhv = pn.cdrewrite(pn.cross("ṣ+dhv", "ḍhv"), "", "", self.sig)
        # Sigmatic aorist clusters like -kṣ+t- surface as -kt- (yuj: ayokta),
        # not as retroflex -kṣṭ-.
        self.ksha_t_simplify = pn.cdrewrite(
            pn.string_map([("kṣ+t", "kt"), ("kṣ+th", "kth")]),
            "", "", self.sig
        )
        self.retro_s   = pn.cdrewrite(
            pn.string_map([("ṣ+s", "kṣ"), ("ś+s", "kṣ")]), 
            "", "", self.sig
        )

        # Velar nasal: n/ñ → ṅ before velar stops
        self.velar_nasal = pn.cdrewrite(
            pn.string_map([("n", "ṅ"), ("ñ", "ṅ")]),
            "", pn.union("+k", "+g", "+kh", "+gh"), self.sig
        )

    def _setup_long_distance_rules(self):
        # RUKI: s → ṣ after r/ṛ/u/ū/k/i/ī/e/ai/o/au
        ruki_triggers = pn.union(
            "ṛ", "r", "u", "ū", "k", "i", "ī", "e", "ai", "o", "au"
        )
        self.ruki = pn.cdrewrite(
            pn.cross("s", "ṣ"),
            ruki_triggers + pn.accep("+").star, "", self.sig
        )

        # Nati: n → ṇ after r/ṛ/ṣ across allowable interveners
        triggers = pn.union("r", "ṛ", "ṣ", "ṝ")
        allowed_interveners = pn.union(
            ALPHABET.vowels, ALPHABET.gutturals, ALPHABET.labials,
            "y", "v", "h", "ṃ", "+"
        ).star.optimize()
        self.nati = pn.cdrewrite(
            pn.cross("n", "ṇ"),
            triggers + allowed_interveners,
            pn.union(ALPHABET.vowels, "n", "m", "y", "v"),
            self.sig
        )

        # Post-RUKI retroflex assimilation
        self.retro_post_ruki_th  = pn.cdrewrite(pn.cross("ṣ+th",  "ṣṭh"), "", "", self.sig)
        self.retro_post_ruki_t   = pn.cdrewrite(pn.cross("ṣ+t",   "ṣṭ"),  "", "", self.sig)
        self.retro_post_ruki_dhv = pn.cdrewrite(pn.cross("ṣ+dhv", "ḍhv"), "", "", self.sig)
        # After RUKI, sigmatic aorist k+ṣ+t/th should still simplify to kt/kth.
        self.ksha_t_simplify_post_ruki = pn.cdrewrite(
            pn.string_map([("k+ṣ+t", "k+t"), ("k+ṣ+th", "k+th")]),
            "", "", self.sig
        )

        # Visarga: word-final s/ṣ → ḥ
        self.visarga = pn.cdrewrite(
            pn.string_map([("s", "ḥ"), ("ṣ", "ḥ")]),
            "", pn.union("[EOS]", "+[EOS]"), self.sig
        )

        # Word-final cluster reduction: ṣṭ → ṭ
        self.cluster_reduction = pn.cdrewrite(
            pn.string_map([
                ("ṣṭ", "ṭ"),
                # Whitney-style imperfects like ayunakt -> ayunak.
                ("k+t", "k"),
                # doh+t path after Bartholomae/throwback: a+dhogdh -> a+dhok.
                ("gdh", "k"),
            ]),
            "", pn.union("[EOS]", "+[EOS]"), self.sig
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Named rule lists (for per-rule debug tracing)
    # ──────────────────────────────────────────────────────────────────────────

    def _build_named_rule_lists(self):
        self._vowel_rules: list[tuple[str, pn.Fst]] = [
            ("thematic_merger",    self.thematic_merger),
            ("class9_special",     self.class9_special),
            ("ayadi",              self.ayadi),
            ("savarna",            self.savarna),
            ("yan_sandhi",         self.yan_sandhi),
            ("guna_sandhi",        self.guna_sandhi),
        ]
        self._consonant_rules: list[tuple[str, pn.Fst]] = [
            ("d_dh_gemination",   self.d_dh_gemination),
            ("bartho_bht",         self.bartho_bht),
            ("bartho_bhth",        self.bartho_bhth),
            ("bartho_hth",         self.bartho_hth),
            ("bartho_hdh",         self.bartho_hdh),
            ("bartho_ht",          self.bartho_ht),
            ("grassmann_throwback",self.grassmann_throwback),
            ("h_to_k",             self.h_to_k),
            ("rj_retroflex",       self.rj_retroflex),
            ("palatal_sandhi",     self.palatal_sandhi),
            ("ksha_t_simplify",    self.ksha_t_simplify),
            ("retro_th",           self.retro_th),
            ("retro_t",            self.retro_t),
            ("retro_dhv",          self.retro_dhv),
            ("retro_s",            self.retro_s),
            ("devoicing",          self.devoicing),
            ("nasal_assimilation", self.nasal_assimilation),
            ("nj_cluster_hardening", self.nj_cluster_hardening),
            ("anusvara",           self.anusvara),
            ("gamya_fix",          self.gamya_fix),
            ("parasavarna",        self.parasavarna),
            ("velar_nasal",        self.velar_nasal),
        ]
        self._long_distance_rules: list[tuple[str, pn.Fst]] = [
            ("ruki",                 self.ruki),
            ("ksha_t_simplify_post_ruki", self.ksha_t_simplify_post_ruki),
            ("retro_post_ruki_th",   self.retro_post_ruki_th),
            ("retro_post_ruki_t",    self.retro_post_ruki_t),
            ("retro_post_ruki_dhv",  self.retro_post_ruki_dhv),
            ("nati",                 self.nati),
            ("visarga",              self.visarga),
            ("cluster_reduction",    self.cluster_reduction),
            ("clean_boundaries",     self.clean_boundaries),
        ]

    # ──────────────────────────────────────────────────────────────────────────
    # Debug helper
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _apply_rules_with_trace(
        fst: pn.Fst,
        rules: list[tuple[str, pn.Fst]],
        phase: str,
    ) -> pn.Fst:
        """Apply rules one by one, printing each result.

        Stops immediately when a rule causes the FST to go empty, identifying
        exactly which rule killed the valid path.
        """
        print(f"  [{phase}]")
        for name, rule_fst in rules:
            fst = (fst @ rule_fst).optimize()
            if fst.num_states() == 0:
                print(f"    ❌ {name}: FST went EMPTY — this rule killed the path")
                return fst
            try:
                print(f"    ✅ {name}: '{fst.string()}'")
            except Exception:
                try:
                    sp = pn.shortestpath(fst).string()
                    print(f"    ⚠️  {name}: ambiguous, shortest='{sp}'")
                except Exception:
                    print(f"    ⚠️  {name}: ambiguous (no shortest path)")
        return fst

    # ──────────────────────────────────────────────────────────────────────────
    # Phase entry points
    # ──────────────────────────────────────────────────────────────────────────

    def vowel_phase(self, fst: pn.Fst, debug: bool = False) -> pn.Fst:
        """Apply vowel sandhi rules.

        Order is critical — see inline comments in _setup_vowel_rules.
        """
        if debug:
            return self._apply_rules_with_trace(fst, self._vowel_rules, "vowel_phase")
        return (fst
                @ self.thematic_merger
                @ self.class9_special
                @ self.ayadi
                @ self.savarna
                @ self.yan_sandhi
                @ self.guna_sandhi)

    def consonant_phase(self, fst: pn.Fst, debug: bool = False) -> pn.Fst:
        """Apply consonant cluster sandhi rules."""
        if debug:
            return self._apply_rules_with_trace(fst, self._consonant_rules, "consonant_phase")
        return (fst
                @ self.d_dh_gemination
                @ self.bartho_bht
                @ self.bartho_bhth
                @ self.bartho_hth
                @ self.bartho_hdh
                @ self.bartho_ht
                @ self.grassmann_throwback
                @ self.h_to_k
                @ self.rj_retroflex
                @ self.palatal_sandhi
                @ self.ksha_t_simplify
                @ self.retro_th
                @ self.retro_t
                @ self.retro_dhv
                @ self.retro_s
                @ self.devoicing
                @ self.nasal_assimilation
                @ self.nj_cluster_hardening
                @ self.anusvara
                @ self.gamya_fix
                @ self.parasavarna
                @ self.velar_nasal)

    def long_distance_phase(self, fst: pn.Fst, debug: bool = False) -> pn.Fst:
        """Apply long-distance rules (RUKI, Nati, Visarga, etc.)."""
        if debug:
            return self._apply_rules_with_trace(
                fst, self._long_distance_rules, "long_distance_phase"
            )
        return (fst
                @ self.ruki
                @ self.ksha_t_simplify_post_ruki
                @ self.retro_post_ruki_th
                @ self.retro_post_ruki_t
                @ self.retro_post_ruki_dhv
                @ self.nati
                @ self.visarga
                @ self.cluster_reduction
                @ self.clean_boundaries)

    def apply_all(self, fst: pn.Fst, debug: bool = False) -> pn.Fst:
        """Run all three sandhi phases in sequence."""
        return self.long_distance_phase(
            self.consonant_phase(
                self.vowel_phase(fst, debug), debug
            ), debug
        )