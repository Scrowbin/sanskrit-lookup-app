import pynini as pn
from alphabet import ALPHABET

class SandhiEngine:
    """Modular FST engine for Sanskrit internal phonology (stem-boundary sandhi).

    Pipeline order: vowel_phase → consonant_phase → long_distance_phase.
    Within each phase, rules are ordered by specificity (most specific first).
    """

    def __init__(self):
        self.sig = ALPHABET.sigma_star
        self._setup_vowel_rules()
        self._setup_consonant_rules()
        self._setup_long_distance_rules()
        # Erase morpheme boundaries at the very end
        self.clean_boundaries = pn.cdrewrite(pn.cross("+", ""), "", "", self.sig)

    # ──────────────────────────────────────────────────────────────────────────
    # A. Vowel phase
    # ──────────────────────────────────────────────────────────────────────────

    def _setup_vowel_rules(self):
        # 1. Thematic / Pararupa mergers: a/ā + {e,o,ai,au} → the diphthong wins.
        #    MUST run before Savarna so a+ai doesn't get split into ā+i.
        #    Bug 7 fix: added a+ai→ai and a+au→au pairs.
        self.thematic_merger = pn.cdrewrite(
            pn.string_map([
                ("a+e",  "e"),  ("ā+e",  "e"),
                ("a+o",  "o"),  ("ā+o",  "o"),
                ("a+ai", "ai"), ("ā+ai", "ai"),
                ("a+au", "au"), ("ā+au", "au"),
            ]),
            "", "", self.sig
        )

        # 2. Savarna (identical vowel coalescence): a+a→ā, ī+ī→ī, etc.
        # NOTE: i+i→ī is intentionally EXCLUDED here. In the perfect weak paradigm,
        # short i+i should be handled by yan (i+→y) giving 'iy' not 'ī'. Example:
        #   cikri+ivahe → yan: i+→y → cikriyivahe  ✓  (NOT cikrīvahe via savarna)
        # Long-vowel coalescences (ī+ī, ī+i, i+ī) are kept for class-9 optative etc.
        self.savarna = pn.cdrewrite(
            pn.string_map([
                ("a+a", "ā"), ("a+ā", "ā"), ("ā+a", "ā"), ("ā+ā", "ā"),
                ("i+ī", "ī"), ("ī+i", "ī"), ("ī+ī", "ī"),   # no i+i→ī
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

        # 4. Ayadi (diphthong before vowel or y): e+V → ay+V, o+V → av+V, etc.
        self.ayadi = pn.cdrewrite(
            pn.string_map([
                ("e+", "ay"), ("o+", "av"), ("ai+", "āy"), ("au+", "āv"),
            ]),
            "", pn.union(ALPHABET.vowels, "y"), self.sig
        )

        # 5. Uvan/Iyan (for monosyllabic roots like hu/su)
        self.uvan_iyan = pn.cdrewrite(
            pn.string_map([("i+", "iy"), ("ī+", "iy"), ("u+", "uv"), ("ū+", "uv")]),
            "", ALPHABET.vowels, self.sig
        )

        # 6. Yan sandhi (semi-vowelisation before vowel)
        self.yan_sandhi = pn.cdrewrite(
            pn.string_map([
                ("i+", "y"), ("ī+", "y"),
                ("u+", "v"), ("ū+", "v"),
                ("ṛ+", "r"),
            ]),
            "", ALPHABET.vowels, self.sig
        )

        # 6. Class-9 suffix vowel-drop: ī/ā erased before ANY vowel-initial ending
        # Sanskrit rule: the class-9 infix nā (strong) / nī (weak) loses its
        # final vowel before any vowel-initial ending:
        #   krī+nā+anti  → krī+n+anti  = krīṇanti (strong, 3pl)
        #   krī+nī+e     → krī+n+e     = krīṇe    (weak middle 1sg)
        #   krī+nī+īya   → krī+n+īya   = krīṇīya  (optative weak)
        # Fires before ALL vowels (previously only a/ā).
        self.class9_special = pn.cdrewrite(
            pn.cross("ī+", ""), "", ALPHABET.vowels, self.sig
        )

    # ──────────────────────────────────────────────────────────────────────────
    # B. Consonant phase
    # ──────────────────────────────────────────────────────────────────────────

    def _setup_consonant_rules(self):
        unvoiced_triggers = pn.union("+t", "+th", "+s", "+ṣ")

        # Bartholomae (aspirate assimilation): h+t → gdh, etc.
        # Must run before general devoicing.
        self.bartho_hth = pn.cdrewrite(pn.cross("h+th", "gdh"), "", "", self.sig)
        self.bartho_hdh = pn.cdrewrite(pn.cross("h+dh", "gdh"), "", "", self.sig)
        self.bartho_ht  = pn.cdrewrite(pn.cross("h+t",  "gdh"), "", "", self.sig)

        # Grassmann's Law (throwback deaspiuration)
        throwback_triggers = pn.union(
            "+s", "+ṣ", "+t", "+th", "+dhv", "[EOS]", "+[EOS]"
        )
        self.grassmann_throwback = pn.cdrewrite(
            pn.string_map([("b", "bh"), ("d", "dh"), ("g", "gh")]),
            "", ALPHABET.vowels + pn.union("gh", "dh", "bh", "h") + throwback_triggers,
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

        # General devoicing
        self.devoicing = pn.cdrewrite(
            pn.string_map([
                ("d",  "t"), ("dh", "t"), ("g",  "k"), ("gh", "k"),
                ("b",  "p"), ("bh", "p"), ("ḍ",  "ṭ"), ("ḍh", "ṭ"),
            ]),
            "", unvoiced_triggers, self.sig
        )

        # Nasal assimilation: n/ñ → ñ before +j/+c  (Bug 5 support)
        self.nasal_assimilation = pn.cdrewrite(
            pn.cross("n", "ñ"), "", pn.union("+j", "+c", "j", "c"), self.sig
        )

        # Retroflex assimilation (ṣ + t/th/dhv, and ṣ+s -> kṣ)
        # Written as separate rules to avoid string_map prefix ambiguity (ṣ+t vs ṣ+th)
        self.retro_th = pn.cdrewrite(pn.cross("ṣ+th", "ṣṭh"), "", "", self.sig)
        self.retro_t  = pn.cdrewrite(pn.cross("ṣ+t", "ṣṭ"), "", "", self.sig)
        self.retro_dhv = pn.cdrewrite(pn.cross("ṣ+dhv", "ḍhv"), "", "", self.sig)
        self.retro_s = pn.cdrewrite(pn.cross("ṣ+s", "kṣ"), "", "", self.sig)

        # Velar nasal: n/ñ → ṅ before velar stops.
        # Bug 6 fix: also converts ñ (which nasal_assimilation produced) → ṅ.
        # Must run AFTER palatal_sandhi so j→k is already done.
        self.velar_nasal = pn.cdrewrite(
            pn.string_map([("n", "ṅ"), ("ñ", "ṅ")]),
            "", pn.union("+k", "+g", "+kh", "+gh"), self.sig
        )

    # ──────────────────────────────────────────────────────────────────────────
    # C. Long-distance phase
    # ──────────────────────────────────────────────────────────────────────────

    def _setup_long_distance_rules(self):
        # RUKI: s → ṣ after r/ṛ/u/ū/k/i/ī/e/ai/o/au (across optional +)
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

        # Visarga: word-final s/ṣ → ḥ
        self.visarga = pn.cdrewrite(
            pn.string_map([("s", "ḥ"), ("ṣ", "ḥ")]),
            "", pn.union("[EOS]", "+[EOS]"), self.sig
        )

        # Word-final cluster reduction: ṣṭ → ṭ
        self.cluster_reduction = pn.cdrewrite(
            pn.cross("ṣṭ", "ṭ"),
            "", pn.union("[EOS]", "+[EOS]"), self.sig
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Phase entry points
    # ──────────────────────────────────────────────────────────────────────────

    def vowel_phase(self, fst):
        # ORDER IS CRITICAL:
        # 1. thematic_merger: a+ai→ai etc. must precede savarna (a+ai ≠ ā+i)
        # 2. class9_special: ī+→ε before a/ā (nī-dropping)
        # 3. ayadi FIRST: consume full diphthong au+/ai+/o+/e+ before vowel
        #    → MUST precede yan so the 'u' in 'au+' isn't stolen by yan (u+→v)
        # 4. savarna: identical vowels coalesce BEFORE yan fires on ī+ī → yī
        #    (e.g. nī+ī → nī, not nyī)
        # 5. yan: remaining i/ī/u/ū/ṛ before vowel → semivowel
        # 6. guna_sandhi: a+i→e, a+u→o (last, after other vowel changes)
        vowel_done = (fst @ self.thematic_merger @ self.class9_special)
        vowel_done = self.ayadi(vowel_done)
        vowel_done = self.savarna(vowel_done)
        vowel_done = self.uvan_iyan(vowel_done)
        vowel_done = self.yan_sandhi(vowel_done)
        vowel_done = self.guna_sandhi(vowel_done)
        return vowel_done

    def consonant_phase(self, fst):
        # Order matters: Bartholomae → Grassmann → h_to_k → palatal/devoicing
        # → nasal_assimilation → velar_nasal (sees k produced by palatal_sandhi)
        return (fst
                @ self.bartho_hth
                @ self.bartho_hdh
                @ self.bartho_ht
                @ self.grassmann_throwback
                @ self.h_to_k
                @ self.palatal_sandhi
                @ self.retro_th
                @ self.retro_t
                @ self.retro_dhv
                @ self.retro_s
                @ self.devoicing
                @ self.nasal_assimilation
                @ self.velar_nasal)

    def long_distance_phase(self, fst):
        return (fst @ self.ruki @ self.nati @ self.visarga @ self.cluster_reduction @ self.clean_boundaries)

    def apply_all(self, fst):
        return self.long_distance_phase(
            self.consonant_phase(
                self.vowel_phase(fst)
            )
        )