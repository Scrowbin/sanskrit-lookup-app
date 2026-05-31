import pynini as pn
from irregulars import (
    class_1_irregulars,
    class_2_irregulars,
    class_3_irregulars,
    class_5_irregulars,
    passive_stem_overrides,
    causative_stem_irregulars,
    perfect_weak_guna_roots,
    perfect_stem_overrides,
    aorist_overrides,
    desiderative_stem_overrides,
    intensive_stem_overrides,
)
from dhatupatha_analyzer import DHATUPATHA_ANALYZER
from alphabet import ALPHABET
from reduplication import ReduplicationEngine

# Pure short/long monophthongs
_PURE_VOWELS = {"a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "ḷ", "ḹ"}

# Ayadi resolution table
_AYADI_MAP = {"au": "āv", "ai": "āy", "o": "av", "e": "ay"}

# Perfect weak vowel-shortening table (module-level constant)
# Whitney §786: ī and ū do NOT shorten in the weak perfect.
_PERFECT_SHORTEN = {"ṝ": "ṛ", "ā": "a"}


def _ends_in_consonant(s: str) -> bool:
    """True for consonant-final OR diphthong-final strings.

    Diphthong-final guna forms (bho, kre…) need -iṣya- because the diphthong
    resolves via ayadi before the following 'i': bho+iṣya → bhaviṣya.
    """
    return bool(s) and s[-1] not in _PURE_VOWELS


class StemBuilder:
    """Builds the verbal stem for each class / tense / voice combination.

    Tag placement
    -------------
    [STRONG] / [WEAK] must appear *directly* after the root consonants so the
    guna FST's right-context lookahead fires correctly.  Tags are erased
    immediately after guna is applied — never carried forward.

    Sandhi context tags ``[SD_DCP]``, ``[SD_GEM]``, ``[SD_SSR]``, ``[SD_SIB]``,
    ``[SD_LAR]`` are **not** emitted here by default: ``MorphologyEngine`` inserts
    them on morpheme ``+`` patterns immediately before ``clean_tags`` so that
    ``SandhiEngine`` can apply cluster rules in a **tag-gated** way (see
    ``alphabet.SanskritAlphabet.tags_list`` and ``morphology.py`` ``sd_insert_*``).
    For exceptional surfaces, stems may emit these tags explicitly (same as tests
    in ``grammar/test_phonology.py``).

    Seṭ / Aniṭ (future)
    --------------------
    The decision is made on the **guna-grade** surface string, not the raw root.
    Diphthong-final guna also counts as consonant-ending (→ Seṭ).
    Explicit Aniṭ overrides live in ``irregulars.aset_roots``.
    """

    def __init__(self, strength_engine):
        self.guna = strength_engine.get_guna()
        self.vriddhi = strength_engine.get_vriddhi()
        self.reduplicator = ReduplicationEngine()
        self.sig = ALPHABET.sigma_star

        # Ayadi resolver for derived bases (e.g. bhau → bhāv)
        self.ayadi = pn.cdrewrite(
            pn.string_map(_AYADI_MAP),
            "",
            pn.union(ALPHABET.vowels, "[WEAK]", "[STRONG]", "[VRIDDHI]", "+"),
            self.sig,
        )

        self.tense_dispatch = {
            "present": self._build_present_system,
            "imperfect": self._build_present_system,
            "imperative": self._build_present_system,
            "optative": self._build_present_system,
            "subjunctive": self._build_present_system,
            "future": self._build_future_system,
            "conditional": self._build_future_system,
            "periphrastic_future": self._build_periphrastic_future_system,
            "aorist": self._build_aorist_system,
            "injunctive": self._build_aorist_system,
            "perfect": self._build_perfect_system,
            "pluperfect": self._build_perfect_system,
            "benedictive": self._build_benedictive_system,
        }

        self.class_handlers = {
            1: self._build_class_1,
            2: self._build_class_2,
            3: self._build_class_3,
            4: self._build_class_4,
            5: self._build_class_5,
            6: self._build_class_6,
            7: self._build_class_7,
            8: self._build_class_8,
            9: self._build_class_9,
            10: self._build_class_10,
        }

    # ─── Public entry point ──────────────────────────────────────────────────

    def build(
        self,
        root_str,
        class_num,
        strength,
        tense="present",
        derivative=None,
        person=None,
        number=None,
        voice="active",
        **kwargs
    ):
        root_str = root_str.strip()
        
        # Pāṇini 6.4.24: Drop penultimate nasal in weak/present system forms
        # (not in causative: añj → añjayati, not *ājayati).
        if (
            derivative not in ("causative", "causative_passive")
            and (
                tense in ("present", "imperfect", "imperative", "optative")
                or derivative == "passive"
            )
        ):
            nasal_drop_map = {
                "rañj": "raj", "sañj": "saj", "bhañj": "bhaj",
                "añj": "aj", "bandh": "badh", "stambh": "stabh",
            }
            if root_str in nasal_drop_map:
                root_str = nasal_drop_map[root_str]
                
        root_obj = DHATUPATHA_ANALYZER.get(root_str, class_num)
        fst = pn.accep(root_str)

        # Pāṇini 7.1.58: Id-it roots always get a nasal (Num-āgama)
        if root_obj.is_idit:
            fst = pn.accep("[NASAL]") + fst

        # Let the FST handle Samprasāraṇa dynamically!
        apply_samp = (
            strength == "[WEAK]"
            and root_obj.takes_samprasarana
            and tense not in ("present", "imperative", "optative")
        )

        if apply_samp or derivative == "passive":
            fst = pn.accep("[SAMP]") + pn.accep(root_str)
        # SPECIAL CASE: Causative futures/conditionals (class-10 with future tenses)
        # Pāṇini 6.4.51 + 7.2.3: Causative base + aya + iṣya/sya
        # Must be handled before the normal class-10 handler to avoid hardcoded +aya
        if tense in ("future", "conditional"):
            if derivative in ("causative", "causative_passive"):
                use_vriddhi = self._class10_use_vriddhi(
                    root_str, derivative, tense
                )
                base = self._build_causative_base(
                    root_str, derivative=derivative, use_vriddhi=use_vriddhi
                )
                fst = base + pn.accep("ay+iṣya")
                return (fst @ self._clean()).optimize()
            if class_num == 10 and derivative is None:
                # Primary gaṇa-10 (agada / denom in class slot): …ay+iṣya-, not curādi āpayiṣya-
                fst = self._class10_primary_future_fst(root_str)
                return (fst @ self._clean()).optimize()

        if derivative == "desiderative":
            # Desiderative is a present-system stem in -a (…-ṣa/…-iṣa).
            # For the perfect, the desiderative stem itself takes a perfect formation
            # (i.e., it is reduplicated again), as reflected in INRIA forms like
            # bububhūṣ-iva (perfect of bubhūṣa-).
            if tense == "perfect":
                fst = self._build_desiderative_perfect(root_str, strength)
            else:
                fst = self._build_desiderative(root_str, strength)
            if tense in ("future", "conditional", "periphrastic_future"):
                # Desiderative future/conditional takes -iṣya- after dropping final -a:
                # bubhūṣiṣyati, pipāsiṣyati.
                suffix = "i" if tense == "periphrastic_future" else "iṣya"
                fst = (fst + pn.accep("+")) @ pn.cdrewrite(
                    pn.cross("a+", ""), "", "", self.sig
                ) + pn.accep(suffix)
        elif derivative == "desiderative_passive":
            fst = self._build_desiderative_passive(root_str, strength)
        elif derivative == "causative_passive":
            # Causative passive stem: causative base + ya
            # (e.g. bhāv+ya -> bhāvye, lambh+ya -> lambhye).
            base = self._build_causative_base(
                root_str, derivative="causative_passive", use_vriddhi=True
            )
            fst = base + pn.accep("ya")
        elif derivative == "passive":
            fst = self._build_passive(root_str, class_num, tense=tense)
        elif derivative == "aorist_passive_3sg":
            fst = self._build_aorist_passive_3sg(root_str)
        elif derivative == "intensive_middle":
            fst = self._build_intensive(root_str, strength, voice="middle")
        elif derivative == "intensive_active_luganta":
            fst = self._build_intensive(root_str, strength, voice="active_luganta")
        elif derivative == "intensive_active_anta":
            fst = self._build_intensive(root_str, strength, voice="active_anta")
        elif derivative and derivative.startswith("denominative"):
            fst = self._build_denominative(root_str, derivative)
            if tense in (
                "present",
                "imperfect",
                "imperative",
                "optative",
                "subjunctive",
            ):
                fst = fst + pn.accep("+a")
            elif tense in ("future", "conditional"):
                fst = fst + pn.accep("+iṣya")
            elif tense == "periphrastic_future":
                fst = fst + pn.accep("+itā")
            elif tense in ("aorist", "injunctive"):
                fst = fst + pn.accep("+is")
            elif tense == "perfect":
                fst = fst + pn.accep("+ām")
        else:
            builder = self.tense_dispatch.get(tense)
            if builder is None:
                raise ValueError(f"Tense '{tense}' not supported.")
            fst = builder(
                root_str,
                class_num,
                strength,
                tense,
                derivative=derivative,
                person=person,
                number=number,
                voice=voice,
                **kwargs,
            )

        # Pāṇini 8.2.31 ho ḍhaḥ (h -> ḍh) & 8.2.32 dāder dhātor ghaḥ (d...h -> gh).
        # We inject [RUH_H] for h-final roots that take ḍh, avoiding the ones that take gh (d-initial) or dh (nah).
        if ALPHABET.parse_phonemes(root_str)[-1] == "h":
            if root_str == "nah":
                pass
            elif root_str.startswith("d") and root_str not in {"druh"}:
                pass
            else:
                # Replace 'h' with 'h[RUH_H]' when followed by '+' or at the end of the stem or before a tag like [WEAK]
                _abstract_tags = pn.union(*ALPHABET.tags_list)
                fst = fst @ pn.cdrewrite(pn.cross("h", "h[RUH_H]"), "", pn.union("+", "[EOS]", _abstract_tags), self.sig)

        # Pāṇini 8.2.36 (vraśca-bhrasja-sṛja-mṛja-yaja-rāja-bhrāja-cchaśāṃ ṣaḥ)
        # Tag roots that change final j/ś/ch → ṣ before dentals/jhal.
        if DHATUPATHA_ANALYZER.get(root_str, class_num).is_mrj_class:
            _abstract_tags = pn.union(*ALPHABET.tags_list)
            fst = fst @ pn.cdrewrite(pn.cross("", "[MRJ]"), pn.union(*ALPHABET.consonants_list), pn.union("+", "[EOS]", _abstract_tags), self.sig)

        return (fst @ self._clean()).optimize()

    # ─── Low-level FST helpers ───────────────────────────────────────────────

    def _clean(self, tags=None):
        """cdrewrite that erases strength tags by default."""
        if tags is None:
            # Erase [STRONG] and [VRIDDHI] tags, but let [WEAK] pass through 
            # to MorphologyEngine for systematic zero-grade application.
            tags = pn.union("[STRONG]", "[VRIDDHI]")
        elif isinstance(tags, str):
            tags = pn.accep(tags)
        return pn.cdrewrite(pn.cross(tags, ""), "", "", self.sig)

    def _apply_guna(self, root_str, strength):
        # Pāṇini 7.2.114 (mṛjer vṛddhiḥ): mṛj takes Vṛddhi in place of Guṇa everywhere.
        if root_str == "mṛj" and strength == "[STRONG]":
            return self._apply_vriddhi(root_str)
            
        tagged = pn.accep(root_str + strength)
        if strength == "[STRONG]":
            return tagged @ self.guna @ self._clean()
        return tagged @ self._clean()

    def _apply_vriddhi(self, root_str):
        return (
            pn.accep(root_str + "[VRIDDHI]") @ self.vriddhi @ self._clean("[VRIDDHI]")
        )

    def _apply_ruh_strong(self, root_str: str):
        """Class-1 guh/ruh/duh strong: penultimate u → ū (agūhat), not guṇa o or vr̥ddhi au."""
        phonemes = ALPHABET.parse_phonemes(root_str)
        if len(phonemes) >= 2 and phonemes[-2] == "u":
            return pn.accep(root_str[:-2] + "ū" + phonemes[-1])
        return self._apply_vriddhi(root_str)

    # Pāṇini 7.2.114 (mṛjer vṛddhiḥ): mṛj takes Vṛddhi in causative,
    # overriding the general Guṇa rule for short penultimate ṛ.
    _CAUSATIVE_VRIDDHI_OVERRIDE = frozenset({"mṛj"})

    def _takes_guna_in_causative(self, root_str: str) -> bool:
        """Pāṇinian algorithmic rule for Causative (ṇic) stem strength.

        General rule (P. 7.3.86): consonant-final roots with short penultimate
        vowel (i, u, ṛ, ḷ) take Guṇa. All others take Vṛddhi.

        Exception (P. 7.2.114): mṛj takes Vṛddhi despite short penultimate ṛ.
        """
        if root_str in self._CAUSATIVE_VRIDDHI_OVERRIDE:
            return False  # Force Vṛddhi path
        if root_str in self._CAUSATIVE_KEEP_R_PENULT:
            return False  # Keep ṛ, no guṇa/vṛddhi
        phonemes = ALPHABET.parse_phonemes(root_str)
        if not phonemes:
            return False
        if phonemes[-1] in ALPHABET.vowels_list:
            return False
        if len(phonemes) >= 2 and phonemes[-2] in ("i", "u", "ṛ", "ḷ"):
            return True
        return False

    # Roots whose ā-final causative uses -y- extension instead of -p-
    # (Whitney §1042: pā-class). pā → pāyayati (not pāpayati).
    _CAUSATIVE_AY_ROOTS = frozenset(
        {"pā", "nī", "pyā", "sā", "bhī", "śī", "si", "hū", "śū"}
    )

    # Roots that insert a nasal in the causative (Pāṇini 7.3.36 / Whitney §1042b).
    # labh → lambhayati, rabh → rambhayati.
    _CAUSATIVE_NASAL = {"labh": "lambh", "rabh": "rambh"}

    # Vowel-final roots (i/ī/u/ū) whose causative drops the final vowel and appends -āp-.
    # Whitney §1042: krī → krāpayati, ji → jāpayati.
    # We use an explicit set for safety.
    _CAUSATIVE_AP_ROOTS = frozenset({"krī", "jī", "ji", "ci"})

    # Roots with medial 'a' that explicitly do NOT take vṛddhi in the causative
    # (Pāṇini 7.3.34 mitāṃ hrasvaḥ / Whitney §1042d). 
    # e.g., gam -> gamaya (not *gāmaya), jan -> janaya.
    _CAUSATIVE_SHORT_A_ROOTS = frozenset({
        "gam", "jan", "svan", "kṣam", "vyath", "prath", "mrac", "mrad", "ghat", "vyat",
        "śrath", "snath", "klam", "trap", "tvar", "chur", "gad", "dam", "rac", "rah",
        "stan", "sthag", "val", "svar", "kvaṇ", "paṇ", "raṇ", "mah", "dhvan", "ślath",
        "smi",
    })
    # Lexical causative stems (before +aya); Whitney / INRIA class-10 causatives.
    _CAUSATIVE_STEM_OVERRIDES = {
        "praś": "pracch",
        "krīḍ": "krīḍāp",
        "dham": "dhmāp",
        "śrā": "śrap",
        "dhū": "dhūn",
        "prī": "prīṇ",
        "jāgṛ": "jāgar",
        "druh": "drār",
        "drāgh": "dhrāg",
        "bṛh": "bṛṃh",
        "radh": "randh",
        "sañj": "sajj",
        "hrī": "hrep",
        "luṇch": "loṭh",
        "sidh": "sādh",
        "kṣī": "kṣap",
        "i": "āpy",
    }
    # ṛ-initial perfect: nuṭ reduplicant ān- + guṇa weak/strong grades (Whitney / INRIA).
    _RIC_PERFECT_NUT_ROOTS = frozenset({"ṛc", "ṛṣ"})
    _AR_PERFECT_ROOTS = frozenset({"ṛj"})
    # Class-3 Caṅ: perfect-style reduplicant (ca-, not lengthened ci-/tī-).
    _CAANG_PERFECT_REDUP_PREFIX = frozenset({"kamp", "budh", "tan"})
    # Caṅ only: lengthen ci- → cī- for light i-roots (kath, kṛṣ); not all ci- prefixes.
    _CAANG_LONG_CI_PREFIX_ROOTS = frozenset({"kath", "kṛṣ", "car", "klp"})
    # Causative imperfect keeps upadhā-vṛddhi (Whitney / INRIA: atānayam, not *atanayam).
    _CAUSATIVE_KEEP_VRIDDHI_IMPERFECT = frozenset({"tan", "man", "van", "śvan", "stan"})
    _LUNG_TENSES = frozenset(
        {"imperfect", "conditional", "pluperfect", "injunctive"}
    )

    # Class-1 ū/ī-final roots that keep length in middle (knūya-), not guṇa (bhav-).
    _CLASS1_MIDDLE_LONG_VOWEL_ROOTS = frozenset({"knū"})

    # Class-1 roots with Pāṇini 7.3.78 suppletion (gam→gacch, …).
    _CLASS1_SUPPLETIVE = frozenset({"gam", "sthā", "pā", "sad", "scand", "vyā"})
    # Lexically conditioned a-aorist bases that follow stable historical alternation.
    _A_AORIST_BASES = {
        "vac": "voc",
        "dṛś": "darś",
        "śru": "śrav",
        "hu": "ho",  # class-4 active: ahoṣat (not *ahvat)
    }
    # Divādi (class 4) middle a-aorist weak stems (samprasāraṇa / grade alternation).
    _DIVADI_AORIST_WEAK_MIDDLE = {
        "tyaj": "tyak",
        "bhaj": "bhak",
        "bandh": "banddh",
        "chid": "chitt",
        "tud": "tutt",
        "dah": "dagdh",
        "labh": "labd",
        "pac": "pak",
        "rudh": "ruddh",
        "sidh": "siddh",
        "vyadh": "viddh",
        "svap": "supt",
        "gāh": "gāḍh",
        "dā": "it",
        "spṛś": "spṛṣ",
        "stu": "stut",
        "khan": "khans",
        "nakṣ": "nakṣ",
        "ram": "rams",
    }

    def _is_causative_derivative(self, derivative) -> bool:
        return derivative in ("causative", "causative_passive")

    def _class10_use_vriddhi(self, root_str: str, derivative, tense: str) -> bool:
        """Upadhā-vṛddhi on class-10 bases.

        Causatives: vṛddhi in all lakāras including luṅ (INRIA: akāṇayat).
        Guṇa-only bases (gam, short-a, u-penult) are handled inside
        ``_build_causative_base`` regardless of this flag.
        Primary gaṇa-10 in luṅ: only lexical keepers (tan, man, …).
        """
        if self._is_causative_derivative(derivative):
            return True
        if tense in self._LUNG_TENSES:
            return root_str in self._CAUSATIVE_KEEP_VRIDDHI_IMPERFECT
        return False

    def _is_class10_a_primary(self, root_str: str, derivative, class_num) -> bool:
        """Nominal / ā-dhātu in -a (agada): future in -yiṣya-, not curādi -ayiṣya-."""
        if class_num != 10 or self._is_causative_derivative(derivative):
            return False
        phonemes = ALPHABET.parse_phonemes(root_str)
        return bool(phonemes and phonemes[-1] == "a")

    def _class10_a_primary_base(self, root_str: str):
        return pn.accep(root_str[:-1] + "+")

    # Class-10 nominal/denominative futures (no Dhātupāṭha curādi row; INRIA -īyiṣya-, etc.)
    _CLASS10_DENOM_PRIMARY_FUTURE: dict[str, str] = {
        "agada": "yiṣya",
        "aśva": "yiṣya",
        "gadgada": "yiṣya",
        "putrakāma": "yiṣya",
        "rathakāma": "yiṣya",
        "asūya": "yiṣya",
        "mitra": "īyiṣya",
        "citra": "īyiṣya",
        "udaka": "īyiṣya",
        "māṃsa": "īyiṣya",
        "paryaṅka": "īyiṣya",
        "prāsāda": "īyiṣya",
        "prāvāra": "īyiṣya",
        "rājagava": "īyiṣya",
        "sajja": "īyiṣya",
        "taviṣa": "īyiṣya",
        "śāṇa": "īyiṣya",
        "kṣīra": "syiṣya",
        "vatsala": "syiṣya",
        "bhūsvarga": "āyiṣya",
        "mahī": "yiṣya_keep",
        "mī": "eṣya",
        "ri": "eṣya",
        "putra": "putra",
        "vṛṣa": "vṛṣa",
        "śṛṅga": "śṛṅga",
    }

    def _class10_primary_future_fst(self, root_str: str):
        """Primary gaṇa-10 future: curādi …ay+iṣya- or nominal denominative patterns."""
        denom = self._CLASS10_DENOM_PRIMARY_FUTURE.get(root_str)
        if denom is not None:
            return self._class10_denominator_future_fst(root_str, denom)
        phonemes = ALPHABET.parse_phonemes(root_str)
        if phonemes and phonemes[-1] == "a":
            return pn.accep(root_str[:-1] + "+") + pn.accep("āyiṣya")
        return pn.accep(root_str + "+") + pn.accep("ay+iṣya")

    def _class10_denominator_future_fst(self, root_str: str, pattern: str) -> pn.Fst:
        if pattern == "yiṣya":
            return pn.accep(root_str[:-1] + "+") + pn.accep("yiṣya")
        if pattern == "yiṣya_keep":
            return pn.accep(root_str + "+") + pn.accep("yiṣya")
        if pattern in ("īyiṣya", "syiṣya", "āyiṣya"):
            return pn.accep(root_str[:-1] + "+") + pn.accep(pattern)
        if pattern == "eṣya":
            return pn.accep(root_str[:-1] + "e+") + pn.accep("iṣya")
        if pattern == "putra":
            b = root_str[:-1]
            return pn.union(
                pn.accep(b + "s+") + pn.accep("yiṣya"),
                pn.accep(b + "i+") + pn.accep("yiṣya"),
                pn.accep(b + "ī+") + pn.accep("yiṣya"),
            )
        if pattern == "vṛṣa":
            b = root_str[:-1]
            return pn.union(
                pn.accep(b + "s+") + pn.accep("yiṣya"),
                pn.accep(b + "ī+") + pn.accep("yiṣya"),
            )
        if pattern == "śṛṅga":
            return pn.accep("śrṅgā+") + pn.accep("yiṣya")
        phonemes = ALPHABET.parse_phonemes(root_str)
        base = root_str[:-1] if phonemes and phonemes[-1] == "a" else root_str
        return pn.accep(base + "+") + pn.accep("ay+iṣya")

    def _class10_primary_peri_fst(self, root_str: str):
        if root_str in self._CLASS10_DENOM_PRIMARY_FUTURE:
            pattern = self._CLASS10_DENOM_PRIMARY_FUTURE[root_str]
            if pattern == "yiṣya":
                return pn.accep(root_str[:-1] + "+") + pn.accep("y+i")
            if pattern in ("īyiṣya", "syiṣya", "āyiṣya"):
                return pn.accep(root_str[:-1] + "+") + pn.accep(
                    {"īyiṣya": "īy+i", "syiṣya": "sy+i", "āyiṣya": "āy+i"}[pattern]
                )
        phonemes = ALPHABET.parse_phonemes(root_str)
        if phonemes and phonemes[-1] == "a":
            return pn.accep(root_str[:-1] + "+") + pn.accep("āy+i")
        return pn.accep(root_str + "+") + pn.accep("ay+i")

    def _class10_a_primary_future_fst(self, root_str: str):
        return self._class10_primary_future_fst(root_str)

    def _class10_a_primary_peri_fst(self, root_str: str):
        return self._class10_primary_peri_fst(root_str)

    # Causative of ṛ-penultimate roots that keep ṛ (kṛp → kṛpayati, not *karpayati).
    _CAUSATIVE_KEEP_R_PENULT = frozenset({"kṛp"})

    # Lexical causative bases before +aya (Whitney / INRIA).
    _CAUSATIVE_BASE_OVERRIDES = {
        "guh": "gūh",
        "knū": "knop",
        "ṛ": "arp",
        "arth": "arthāp",  # p-increment (Whitney §1048), not plain ā+yaya-
    }

    # ī/ṝ stems with āy-extension before causative -aya- (klāmay-, jāray-).
    _CAUSATIVE_ĀY_STEMS = frozenset({"klam", "jṝ"})

    def _build_nominal_class1_future(self, root_str: str):
        """INRIA nominal stems (class 1): future in -yiṣya- / -āyiṣya-."""
        if root_str == "am":
            return pn.union(
                pn.accep("am+") + pn.accep("īṣya"),
                pn.accep("am+") + pn.accep("iṣya"),
            )
        if root_str == "i":
            return pn.accep("e+") + pn.accep("iṣya")
        if root_str.endswith("as"):
            if root_str == "as":
                return pn.accep("as+") + pn.accep("iṣya")
            if len(root_str) >= 6:
                return pn.accep(root_str[:-2] + "ā+") + pn.accep("yiṣya")
            return pn.accep(root_str + "y+") + pn.accep("iṣya")
        if root_str.endswith("i"):
            return pn.accep(root_str[:-1] + "y+") + pn.accep("iṣya")
        return None

    def _build_nominal_class1_periphrastic(self, root_str: str):
        """INRIA nominal stems (class 1): periphrastic future in -yitā- / -āyitā-."""
        if root_str == "i":
            return pn.accep("e+") + pn.accep("i")
        if root_str.endswith("as"):
            if len(root_str) >= 6:
                return pn.accep(root_str[:-2] + "ā+") + pn.accep("yi")
            return pn.accep(root_str + "y+") + pn.accep("i")
        if root_str.endswith("i"):
            return pn.accep(root_str[:-1] + "y+") + pn.accep("i")
        return None

    def _build_causative_base(
        self,
        root_str: str,
        class_num: int = 1,
        derivative: str = None,
        *,
        use_vriddhi: bool = True,
    ):
        """Return the FST for the causative base (Vṛddhi/Guna + ayadi).

        Priority:
        1. Remaining true irregulars (han→ghāt, krī→krāp handled below).
        2. Nasal-insertion roots (labh→lambh — Pāṇini 7.3.36).
        3. ā-final roots with -y- extension (pā → pāy — Whitney §1042).
        4. ā-final roots with -p- extension (dā, sthā, … — Pāṇini 6.4.55).
        5. ī/ū-final roots with -p- extension (krī → krāp — Whitney §1042).
        6. a-vowel consonant-final roots — no strengthening (gamaya, caray).
        7. Long high-vowel penultimate — no strengthening (pūjaya).
        8. guna-eligible short i/u/ṛ penultimate — Guna + base.
        9. Default — Vṛddhi.
        """
        # Layer 0: lexical causative bases (guh→gūh, knū→knop, ṛ→arp, …)
        if root_str in self._CAUSATIVE_BASE_OVERRIDES:
            return pn.accep(self._CAUSATIVE_BASE_OVERRIDES[root_str] + "+")

        if root_str in self._CAUSATIVE_STEM_OVERRIDES:
            return pn.accep(self._CAUSATIVE_STEM_OVERRIDES[root_str] + "+")

        # Denominative bases (Class 10) ending in 'a' drop their final 'a'
        # before taking the causative/denominative sign (Whitney §1054).
        # Only for primary curādi/class-10 denominatives — not causative derivative.
        phonemes = ALPHABET.parse_phonemes(root_str)
        if (
            phonemes
            and phonemes[-1] == "a"
            and derivative not in ("causative", "causative_passive")
        ):
            root_str = root_str[:-1]
            return pn.accep(root_str + "+")

        # Layer 0b: ā-extension stems (arthāpay-, klāmay-, kṣāyay-)
        if root_str in self._CAUSATIVE_ĀY_STEMS:
            if root_str == "klam":
                return pn.accep("klām+")
            if root_str == "jṝ":
                return pn.accep("jār+")
            if root_str.endswith("ī"):
                return pn.accep(root_str[:-1] + "āy+")
            return pn.accep(root_str + "āy+")

        # Layer 1: true irregular override (han→ghāt only after removing dā/sthā/pā/krī/labh)
        if root_str in causative_stem_irregulars:
            override = causative_stem_irregulars[root_str]
            if isinstance(override, list):
                return pn.union(*[pn.accep(s) for s in override])
            return pn.accep(override)

        phonemes = ALPHABET.parse_phonemes(root_str)
        vowels = set(ALPHABET.vowels_list)
        vowel_positions = [i for i, ph in enumerate(phonemes) if ph in vowels]

        # Layer 2: Nasal-insertion causative (Pāṇini 7.3.36 / Whitney §1042b)
        # labh → lambhayati, rabh → rambhayati
        if root_str in self._CAUSATIVE_NASAL:
            return pn.accep(self._CAUSATIVE_NASAL[root_str] + "+")

        # Layer 3: Roots with -y- extension in causative (Whitney §1042)
        # ā-final: pā → pāyayati (just append y).
        # ī/ū-final: nī → nāyayati (replace final vowel with ā, then append y).
        if root_str in self._CAUSATIVE_AY_ROOTS:
            if root_str.endswith("ā"):
                return pn.accep(root_str + "y+")
            else:
                # Replace final vowel with ā
                cons_base = root_str[:-1]
                return pn.accep(cons_base + "āy+")

        # Layer 4: ā-final roots with -p- extension (dā→dāp, sthā→sthāp — Pāṇini 6.4.55)
        if root_str.endswith("ā"):
            return pn.accep(root_str + "p+")

        # Layer 5: ī/ū-final vowel roots — drop vowel, use āp (krī→krāp, mī→māp, kṣī→kṣāp).
        if phonemes and phonemes[-1] in ("ī", "ū"):
            return pn.accep(root_str[:-1] + "āp+")

        if root_str in self._CAUSATIVE_AP_ROOTS:
            cons_base = root_str[:-1]
            return pn.accep(cons_base + "āp+")

        # u-penultimate: INRIA causatives use guṇa (kuc→kocaya, budh→bodhaya), not ū-lengthening.
        # (Former ū-lengthen rule covered duṣ→dūṣ but broke most u-roots in verbs_clean.)

        # EXCEPT for specific mit roots (Pāṇini 7.3.34) which do not take vriddhi (e.g., gam -> gamaya).
        if (
            phonemes
            and phonemes[-1] not in vowels
            and len(vowel_positions) == 1
            and phonemes[vowel_positions[0]] == "a"
        ):
            if root_str in self._CAUSATIVE_SHORT_A_ROOTS:
                return pn.accep(root_str + "+")
            # Otherwise, it falls through to Layer 9 (Default - Vṛddhi) which correctly applies Upadhā Vriddhi!

        # Layer 7: consonant-final with long penultimate vowel (ī/ū/ṝ) — no strengthening.
        # Whitney §1042: roots with already-long medial vowels stay as-is (pūjayati, not *paujayati).
        if (
            phonemes
            and phonemes[-1] not in vowels
            and len(phonemes) >= 2
            and phonemes[-2] in {"ī", "ū", "ṝ"}
        ):
            return pn.accep(root_str + "+")

        # Layer 8: Heavy syllables ending in a consonant cluster — no strengthening.
        # Pāṇini's rules for Guṇa/Vṛddhi only apply to final vowels or penultimate vowels (upadhā).
        # In a root like 'kuñc', the vowel 'u' is antepenultimate, so it remains unchanged.
        if (
            phonemes
            and vowel_positions
            and len(phonemes) - 1 - vowel_positions[-1] >= 2
        ):
            return pn.accep(root_str + "+")

        if root_str in self._CAUSATIVE_KEEP_R_PENULT:
            return pn.accep(root_str + "+")

        if not use_vriddhi:
            # Luṅ/Lṛṅ/luṭ-lṛṭ of causatives: no upadhā-vṛddhi on the base (Whitney §1043).
            # e.g. kathayati → akathayat, not *akāthayat.
            if (
                phonemes
                and phonemes[-1] not in vowels
                and len(vowel_positions) == 1
                and phonemes[vowel_positions[0]] == "a"
            ):
                return pn.accep(root_str + "+")
            if self._takes_guna_in_causative(root_str):
                return self._apply_guna(root_str, "[STRONG]") + pn.accep("+")

        if self._takes_guna_in_causative(root_str):
            # For short-ṛ penultimate consonant-final roots, class-10 also
            # takes guṇa (ṛ -> ar): kṛś -> karśaya, kṛt -> kartaya.
            base = self._apply_guna(root_str, "[STRONG]")
        else:
            base = self._apply_vriddhi(root_str)

        return base + pn.accep("+")

    # ─── Tense-system builders ────────────────────────────────────────────────

    def _build_present_system(
        self, root_str, class_num, strength, tense, derivative=None, **kwargs
    ):
        # Specific override for dā/dhā imperative 2sg active (Pāṇini 6.4.119: dehi, dhehi)
        person = kwargs.get("person")
        number = kwargs.get("number")
        voice = kwargs.get("voice")
        if tense == "imperative" and person == "2" and number == "sg" and voice == "active" and class_num == 3:
            if root_str == "dā":
                return pn.accep("de")
            elif root_str == "dhā":
                return pn.accep("dhe")

        handler = self.class_handlers.get(class_num)
        if handler is None:
            raise ValueError(f"Class {class_num} not supported.")
        return handler(
            root_str,
            strength,
            tense=tense,
            derivative=derivative,
            class_num=class_num,
            **kwargs,
        )

    def _build_future_system(self, root_str, class_num, strength, tense, **kwargs):
        """Future (Lṛṭ) and Conditional (Lṛṅ)."""
        if class_num == 1 and kwargs.get("derivative") is None:
            nominal = self._build_nominal_class1_future(root_str)
            if nominal is not None:
                return nominal

        root_obj = DHATUPATHA_ANALYZER.get(root_str, class_num)

        stem = self._apply_guna(root_str, "[STRONG]")
        is_anit = root_obj.is_anit
        is_vet = root_obj.is_vet

        # Pāṇini 6.1.58: sṛj and dṛś take 'am' augment (sraj, draś) before jhal affixes.
        if root_str in {"sṛj", "dṛś"}:
            stem = pn.accep(root_str.replace("ṛ", "ra"))

        # Div lengthens in future
        if root_str == "div":
            stem = pn.accep("dīv")
            is_anit = False

        # Gam and Han are Seṭ in future (Pāṇini 7.2.58 etc.)
        if root_str in {"gam", "han"}:
            is_anit = False

        # Kṛ and other ṛ-ending roots are Seṭ in future (Pāṇini 7.2.70 ṛddhanoḥ sye)
        if root_str.endswith("ṛ") or root_str.endswith("ṝ"):
            is_anit = False

        if root_str == "vṛ":
            # Pāṇini 7.2.38 (vṛto vā): vṛ takes optionally long īṭ in future systems
            return pn.union(stem + pn.accep("+iṣya"), stem + pn.accep("+īṣya"))

        if root_obj.takes_optional_future_i:
            ro = DHATUPATHA_ANALYZER.get(root_str, class_num)
            if ro.is_vet:
                return pn.union(stem + pn.accep("+sya"), stem + pn.accep("+iṣya"))
            return stem + pn.accep("+iṣya")

        suffix = "+sya" if is_anit else "+iṣya"
        return stem + pn.accep(suffix)

    def _build_periphrastic_future_system(
        self, root_str, class_num, strength, tense, **kwargs
    ):
        """Periphrastic Future (Luṭ): stem + (i) + tā/tār/tās endings."""
        derivative = kwargs.get("derivative")
        if class_num == 1 and derivative is None:
            nominal = self._build_nominal_class1_periphrastic(root_str)
            if nominal is not None:
                return nominal
        if derivative in ("causative", "causative_passive"):
            use_vriddhi = self._class10_use_vriddhi(root_str, derivative, tense)
            base = self._build_causative_base(root_str, use_vriddhi=use_vriddhi)
            return base + pn.accep("ayi")
        if class_num == 10 and derivative is None:
            return self._class10_primary_peri_fst(root_str)
        if derivative == "desiderative":
            base = self._build_desiderative(root_str, "[STRONG]")
            # Desiderative bases take 'i' augment in periphrastic forms
            return (base + pn.accep("[WORD_END]")) @ pn.cdrewrite(pn.cross("a[WORD_END]", ""), "", "", self.sig) @ pn.cdrewrite(pn.cross("[WORD_END]", ""), "", "", self.sig) + pn.accep("i")

        root_obj = DHATUPATHA_ANALYZER.get(root_str, class_num)
        stem = self._apply_guna(root_str, "[STRONG]")
        is_anit = root_obj.is_anit

        # Pāṇini 6.1.58: sṛj and dṛś take 'am' augment (sraj, draś) before jhal affixes.
        if root_str in {"sṛj", "dṛś"}:
            stem = pn.accep(root_str.replace("ṛ", "ra"))

        # div -> dīv (Seṭ)
        if root_str == "div":
            stem = pn.accep("dīv")
            is_anit = False

        # Special: class-6 and class-7 roots are generally Aniṭ for periphrastic
        # (This heuristic has been removed in favor of the unified RootObject.is_anit property)

        if root_str == "vṛ":
            return pn.union(stem + pn.accep("+i"), stem + pn.accep("+ī"))

        if root_obj.takes_optional_future_i:
            if root_str == "am":
                return pn.accep("am+") + pn.accep("ī")
            if root_str == "as":
                return pn.accep("as+") + pn.accep("i")
            ro = DHATUPATHA_ANALYZER.get(root_str, class_num)
            if ro.is_vet:
                return pn.union(stem, stem + pn.accep("+i"))
            return stem + pn.accep("+i")

        suffix = "" if is_anit else "+i"
        return stem + pn.accep(suffix)

    def _build_aorist_system(self, root_str, class_num, strength, tense, **kwargs):
        """Aorist stem (used by Aorist and Injunctive).

        Supports a 'middle_type' key in aorist_overrides for roots where the
        active and middle use different aorist types (e.g. pā active=root, middle=iṣ).
        """
        voice = kwargs.get("voice", "active")
        derivative = kwargs.get("derivative", "primary")
        forced_aorist_type = kwargs.get("aorist_type_override")
        valid_aorist_types = {"s", "is", "sa", "sis", "root", "a", "reduplicated", "s_or_is", "s_or_a"}
        root_obj = DHATUPATHA_ANALYZER.get(root_str, class_num)

        if root_str == "nī" and class_num == 4 and voice == "active":
            return pn.accep("na")

        # Paninian-first default: use analyzer-derived type unless an override
        # carries explicit lexical behavior that cannot be inferred.
        a_type = DHATUPATHA_ANALYZER.get_aorist_type(root_str, class_num, voice=voice)

        if forced_aorist_type:
            a_type = forced_aorist_type
        elif derivative == "causative":
            a_type = "reduplicated"
        elif voice == "middle" and root_obj.aorist_middle_type:
            a_type = root_obj.aorist_middle_type
        elif root_str in aorist_overrides:
            info = aorist_overrides[root_str]
            # Check for middle-specific type override (Whitney §879)
            if voice == "middle" and "middle_type" in info:
                middle_val = info["middle_type"]
                if middle_val in valid_aorist_types:
                    a_type = middle_val
                elif middle_val == "is_stem": # fallback if we meant literal stem?
                    pass 
                else:
                    return pn.accep(middle_val)
            else:
                voice_key = "active" if strength == "[STRONG]" else "middle"
                if voice_key in info and isinstance(info[voice_key], str) and info[voice_key] not in valid_aorist_types:
                    return pn.accep(info[voice_key])
                # Use override type only when this entry carries lexical stem
                # behavior or a forced dual-type declaration.
                if (
                    "active" in info
                    or "middle" in info
                    or ("type" in info and "_or_" in str(info["type"]))
                ):
                    a_type = info["type"]

        # print(f"DEBUG: a_type={a_type}, voice={voice}, derivative={derivative}")

        # Algorithmic derivation based on type
        phonemes = ALPHABET.parse_phonemes(root_str)
        ends_in_vowel = phonemes and phonemes[-1] in ALPHABET.vowels_list
        is_anit = root_obj.is_anit
        is_vet = root_obj.is_vet

        def build_s():
            if root_str in {"sṛj", "dṛś"}:
                # Pāṇini 6.1.58: am augment before jhal affix (s is jhal). 
                # Strong: vṛddhi -> srāj. Weak: guṇa -> sraj (but s-aorist middle takes no guna for consonant roots, wait).
                # Wait, s-aorist middle doesn't take guna for consonant roots? 
                # sṛj aorist middle: asṛkṣi (no augment!). Wait!
                # Whitney §832: The middle of s-aorist takes no strengthening, so it's asṛkṣi!
                # ONLY the active takes vṛddhi + am-augment -> asrākṣīt.
                if strength == "[STRONG]":
                    fst = pn.accep(root_str.replace("ṛ", "rā"))
                else:
                    fst = pn.accep(root_str)
            else:
                if strength == "[STRONG]":
                    fst = self._apply_vriddhi(root_str)
                else:
                    if voice == "middle" and root_obj.aorist_middle_stem:
                        fst = pn.accep(root_obj.aorist_middle_stem)
                    elif root_str in aorist_overrides and voice == "middle" and "middle" in aorist_overrides[root_str]:
                        fst = pn.accep(aorist_overrides[root_str]["middle"])
                    else:
                        fst = (
                            self._apply_guna(root_str, "[STRONG]")
                            if ends_in_vowel
                            else pn.accep(root_str)
                        )
            return fst + pn.accep("+s")

        def build_is():
            if voice == "active" and root_obj.aorist_active_stem:
                return pn.accep(root_obj.aorist_active_stem)
            if voice == "middle" and root_obj.aorist_middle_stem:
                return pn.accep(root_obj.aorist_middle_stem)
            if strength == "[STRONG]":
                if ends_in_vowel:
                    fst = self._apply_vriddhi(root_str)
                else:
                    fst = self._apply_guna(root_str, "[STRONG]")
            else:
                # Whitney §903: The root-vowel, if capable of it, takes guṇa-strengthening 
                # in the middle (is-aorist), as well as in the active.
                fst = self._apply_guna(root_str, "[STRONG]")
            return fst

        if a_type == "s_or_is" or (a_type in ("s", "is") and is_vet):
            return pn.union(build_s(), build_is())

        if a_type == "s":
            return build_s()
        
        elif a_type == "is":
            return build_is()
        elif a_type == "sa":
            base = self._A_AORIST_BASES.get(root_str, root_str)
            return pn.accep(base) + pn.accep("+sa[SA_AORIST]")

        elif a_type == "sis":
            return pn.accep(root_str)

        elif a_type == "reduplicated":
            # Whitney §1046: causative aorist shortens the root vowel (Pāṇini 7.4.59).
            # Whitney §1048: p-increment roots use the p.
            base_str = root_str
            if derivative == "causative" or class_num == 10:
                if root_str in self._CAUSATIVE_AP_ROOTS:
                    base_str = root_str[:-1] + "ap"
                elif root_str.endswith("ā"):
                    base_str = root_str + "p"
                # Shorten the root vowel!
                phonemes = ALPHABET.parse_phonemes(base_str)
                vowels = set(ALPHABET.vowels_list)
                short_map = {"ā": "a", "ī": "i", "ū": "u", "ṝ": "ṛ", "e": "i", "ai": "i", "o": "u", "au": "u"}
                for i, ph in enumerate(phonemes):
                    if ph in vowels:
                        phonemes[i] = short_map.get(ph, ph)
                base_str = "".join(phonemes)
                
            if root_str == "sthā" and (derivative == "causative" or class_num == 10):
                prefix = "ti"
                base_str = "sthip"
            elif derivative == "causative" or class_num == 10:
                prefix = self.reduplicator.generate_aorist_prefix(base_str)
            else:
                root_obj = DHATUPATHA_ANALYZER.get(root_str, class_num)
                phonemes = ALPHABET.parse_phonemes(base_str)
                if root_str in self._CAANG_PERFECT_REDUP_PREFIX:
                    prefix = self.reduplicator.generate_prefix(base_str)
                else:
                    prefix = self.reduplicator.generate_aorist_prefix(base_str)
                    # Light-root lengthening (cī/tī/dū) is optional; INRIA often has short ci/ti/du.
                    if prefix.endswith("ī"):
                        prefix = prefix[:-1] + "i"
                    elif prefix.endswith("ū"):
                        prefix = prefix[:-1] + "u"
                    if (
                        prefix == "ci"
                        and root_str in self._CAANG_LONG_CI_PREFIX_ROOTS
                    ):
                        prefix = "cī"
                if root_obj.takes_samprasarana:
                    pass  # yaj, vac, … — aorist prefix already correct
                elif phonemes and phonemes[-1] == "i" and not root_obj.takes_samprasarana:
                    # i-final: epenthetic y (śri → śriy-).
                    base_str = base_str + "y"
            return pn.accep(prefix) + pn.accep(base_str) + pn.accep("+a")

        elif a_type == "a":
            if voice == "active" and root_obj.aorist_active_stem:
                return pn.accep(root_obj.aorist_active_stem)
            if voice == "middle" and root_obj.aorist_middle_stem:
                return pn.accep(root_obj.aorist_middle_stem)
            base = self._A_AORIST_BASES.get(root_str, root_str)
            if voice == "middle" and class_num == 4:
                base = self._DIVADI_AORIST_WEAK_MIDDLE.get(root_str, base)
                # Divādi middle: weak stem + secondary -ta (atyakta), no thematic aorist -a-.
                return pn.accep(base)
            return pn.accep(base) + pn.accep("+a")

        elif a_type == "is":
            # The iṣ/is is embedded in the endings (iṣam, iṣṭām, etc.)
            # so the stem is just the guna/bare root with no extra suffix.
            return build_is()

        elif a_type == "root":
            if voice == "active" and root_obj.aorist_active_stem:
                return pn.accep(root_obj.aorist_active_stem + "[ROOT_AORIST]")
            if voice == "active" and (root_str.endswith("ṛ") or root_str.endswith("ṝ")):
                return self._apply_guna(root_str, "[STRONG]") + pn.accep("[ROOT_AORIST]")
            return pn.accep(root_str + "[ROOT_AORIST]")

        return pn.accep(root_str + "[AORIST]")

    def _build_benedictive_system(self, root_str, class_num, strength, tense, **kwargs):
        """Benedictive stem: root with specific phonological mutations before active suffix.

        Whitney §921a: the active benedictive (precative) of samprasāraṇa roots
        uses the samprasāraṇa (weak/passive-style) form of the root, not the full root.
        e.g. yaj (active bened.) → ij+yāsām (not yaj+yāsām).
        """
        root_obj = DHATUPATHA_ANALYZER.get(root_str, class_num)
        voice = kwargs.get("voice", "active")

        if voice == "active":
            # Samprasāraṇa roots (Whitney §921a): Inject tag for Morphology
            if root_obj.takes_samprasarana:
                return pn.accep("[SAMP]" + root_str)

            if root_str.endswith("ā"):
                # Whitney §922a: ā-final roots change ā to e (e.g. dā→de, sthā→sthe).
                e_form = pn.accep(root_str[:-1] + "e")
                if root_str == "jñā":
                    return pn.union(pn.accep(root_str), e_form)
                return e_form
            elif root_str.endswith("i"):
                # Whitney §922: i-final roots lengthen
                return pn.accep(root_str[:-1] + "ī")
            elif root_str.endswith("u"):
                # Whitney §922: u-final roots lengthen
                return pn.accep(root_str[:-1] + "ū")
            elif root_str.endswith("ṛ") or root_str.endswith("ṝ"):
                # Macdonell §438: ṛ becomes ri; ṝ becomes īr (ūr after labials).
                # Exceptions: smṛ, jṛ etc. take guna (ar).
                if root_str in ("smṛ", "jṛ", "stṛ"):
                    return pn.accep(root_str[:-1] + "ar")
                elif root_str.endswith("ṝ"):
                    if len(root_str) > 1 and root_str[-2] in ("p", "ph", "b", "bh", "m", "v"):
                        return pn.accep(root_str[:-1] + "ūr")
                    return pn.accep(root_str[:-1] + "īr")
                else:
                    return pn.accep(root_str[:-1] + "ri")
            elif root_str == "div":
                # Pāṇini 8.2.77: div lengthens to dīv before consonants
                return pn.accep("dīv")
            elif root_str == "śās":
                # śās becomes śiṣ in benedictive active (since it's a kit affix, unlike the ṅit optative active where it remains śās)
                return pn.accep("śiṣ")
            # All other roots: use root as-is, NO strength tag
            # (strength/[WEAK] would trigger zero-grade, corrupting long vowels like dīv→div)
            return pn.accep(root_str)

        # Middle voice (Ātmanepada)
        is_anit = root_obj.is_anit
        # Whitney §912: roots in u and ū (except stu and su) take iṭ and guna.
        phonemes = ALPHABET.parse_phonemes(root_str)
        if not is_anit and phonemes and phonemes[-1] in ("u", "ū") and root_str not in ("stu", "su"):
            stem = self._apply_guna(root_str, "[STRONG]") + pn.accep("+i")
        elif not is_anit:
            # Other seṭ roots also take iṭ in benedictive middle (P. 7.2.79)
            stem = pn.accep(root_str) + pn.accep("+i")
        else:
            stem = pn.accep(root_str)
            
        return stem

    def _build_perfect_system(self, root_str, class_num, strength, tense, **kwargs):
        """Perfect stem = reduplication prefix + (guna | shortened) root.

        Whitney §805-807: Strong forms (1sg, 2sg, 3sg active) use GUNA.
        Whitney §789: 3sg active takes Vriddhi (long-ā) for a-vowel roots.
        Whitney §800: ā-final roots: strong=prefix+ā, weak=prefix+consonant.
        Whitney §783c: Samprasāraṇa roots form perfect via samprasāraṇa vowel.
        Pāṇini 7.3.84: Class-6 (Tudādi) roots take NO guna in the perfect.
        Whitney §794: Roots ending in a before voiced aspirate use e-grade weak.
        """
        if root_str == "vid" and class_num == 2:
            # Whitney §801: vid has an unreduplicated perfect (veda, vidva) that acts as a present (active only),
            # alongside the regular reduplicated perfect (viveda, vividiva).
            reg_prefix = self.reduplicator.generate_prefix(root_str)
            voice = kwargs.get("voice", "active")
            if strength == "[STRONG]":
                reg_strong = pn.accep(reg_prefix + "+") + pn.accep("ved")
                unred_strong = pn.accep("ved[VID_UNRED]")
                # Both are valid in active.
                return pn.union(reg_strong, unred_strong) if voice == "active" else reg_strong
            else:
                reg_weak = pn.accep(reg_prefix + "+") + pn.accep("vid[PERF_WEAK]")
                unred_weak = pn.accep("vid[VID_UNRED]")
                return pn.union(reg_weak, unred_weak) if voice == "active" else reg_weak

        prefix = self.reduplicator.generate_prefix(root_str)

        # Whitney 794 weak e-grade roots (a → e before bh/gh/dh/ḍh in weak perfect)
        _E_GRADE_WEAK_ROOTS = {"labh", "rabh", "nabh", "grabh"}

        person = kwargs.get("person")
        number = kwargs.get("number")
        phonemes = ALPHABET.parse_phonemes(root_str)
        vowels = set(ALPHABET.vowels_list)

        # ṛc/ṛṣ: ān- reduplicant + guṇa in strong, full ṛ-root in weak (ānarca / ānṛca).
        if root_str in self._RIC_PERFECT_NUT_ROOTS:
            prefix = "ān"
            if strength == "[STRONG]":
                guna_stem = "ar" + "".join(phonemes[1:])
                return pn.accep(prefix) + pn.accep(guna_stem)
            return pn.accep(prefix) + pn.accep(root_str)

        # ṛj: ar- reduplicant + bare root (arjitha).
        if root_str in self._AR_PERFECT_ROOTS:
            prefix = "ar"
            if strength == "[STRONG]":
                return pn.accep(prefix) + pn.accep(root_str[1:])
            return pn.accep(prefix) + pn.accep(root_str[1:])

        # √i, √ah: vowel-initial reduplicated perfect (iyāya, āttha).
        if root_str == "i":
            if strength == "[STRONG]":
                if person == "3" and number == "sg":
                    return pn.accep("iyāy")  # +active 3sg -a → iyāya
                return pn.accep("ī") + pn.accep("ya")
            return pn.accep("ī") + pn.accep("i")
        if root_str == "ah":
            if strength == "[STRONG]":
                if person == "2" and number == "sg":
                    return pn.accep("āt")  # +tha → āttha
                return pn.accep("ā") + pn.accep("th")
            return pn.accep("ā") + pn.accep("h")

        # ── Rule A: ā-final root perfect (Whitney §800) ───────────────────────
        # pā→papā/pap, dā→dadā/dad, sthā→tasthā/tasth, mā→mamā/mam, hā→jahā/jah
        # Strong: prefix + ā-root (keeps ā).
        # Weak:   prefix + root-minus-ā (zero grade = bare consonant cluster).
        if phonemes and phonemes[-1] == "ā":
            if strength == "[STRONG]":
                return pn.accep(prefix + "+") + pn.accep(root_str)  # prefix+dā
            else:
                return pn.accep(prefix + "+") + pn.accep(root_str[:-1])  # prefix+d



        if strength == "[STRONG]":
            # Check for explicit 3sg override before algorithmic vṛddhi
            if person == "3" and number == "sg" and root_str in perfect_stem_overrides:
                if "strong_3sg" in perfect_stem_overrides[root_str]:
                    return pn.accep(perfect_stem_overrides[root_str]["strong_3sg"])

            # Whitney §787 & §789: vowel-final roots and medial a-vowel roots
            # use Vriddhi in 3sg active perfect, REGARDLESS of overrides.
            # Exception: bhū is completely anomalous and takes neither vriddhi nor guna (Whitney §793).
            if person == "3" and number == "sg" and root_str != "bhū":
                if phonemes:
                    # Condition 1: Vowel-final root (short or long)
                    if phonemes[-1] in vowels:
                        vr_root_fst = self._apply_vriddhi(root_str)
                        return pn.accep(prefix + "+") + vr_root_fst
                    # Condition 2: Medial 'a' (e.g. tan, gam) that is penultimate (ata upadhāyāḥ)
                    root_vowel_idx = next(
                        (i for i, p in enumerate(phonemes) if p in vowels), None
                    )
                    if root_vowel_idx is not None and phonemes[root_vowel_idx] == "a":
                        # Only apply if it's followed by exactly one consonant (penultimate)
                        if root_vowel_idx == len(phonemes) - 2:
                            vr_phonemes = list(phonemes)
                            vr_phonemes[root_vowel_idx] = "ā"
                            vr_root = "".join(vr_phonemes)
                            return pn.accep(prefix + "+") + pn.accep(vr_root)

            # Override check: non-3sg strong, or roots with explicit strong_3sg
            # that aren't a-vowel (e.g. hu→juhāv, su→suṣāv, div→didev).
            if root_str in perfect_stem_overrides:
                info = perfect_stem_overrides[root_str]
                # If we made it here, it means we are either 3sg and needed the vṛddhi,
                # or we are not 3sg. In any case, return the strong stem.
                if person == "3" and number == "sg" and "strong_3sg" in info:
                    return pn.accep(info["strong_3sg"])
                # Wait, if we are 3sg and "strong_3sg" is missing, we must NOT return
                # just info["strong"] if we haven't applied vṛddhi!
                # Wait! If it's in perfect_stem_overrides, it's totally irregular. 
                # Let's just return info["strong"]! 
                return pn.accep(info["strong"])

            # Whitney §805: strong forms use Guna for most roots
            root_fst = self._apply_guna(root_str, "[STRONG]")
        else:
            if root_str in perfect_stem_overrides:
                info = perfect_stem_overrides[root_str]
                if "weak2" in info:
                    return pn.union(pn.accep(info["weak"] + "[PERF_WEAK]"), pn.accep(info["weak2"] + "[PERF_WEAK]"))
                return pn.accep(info["weak"] + "[PERF_WEAK]")

            if root_str in _E_GRADE_WEAK_ROOTS:
                # Whitney §794: e-grade weak stem (a→e, e.g. labh→lebh).
                e_stem = "".join("e" if ph == "a" else ph for ph in phonemes)
                return pn.accep(prefix + "+") + pn.accep(e_stem + "[PERF_WEAK]")
            # Penultimate a → e in weak perfect (cat→cet, dram→drem; tan uses override).
            root_vowel_idx = next(
                (i for i, p in enumerate(phonemes) if p in vowels), None
            )
            if (
                root_vowel_idx is not None
                and phonemes[root_vowel_idx] == "a"
                and root_vowel_idx == len(phonemes) - 2
                and root_str not in perfect_stem_overrides
            ):
                weak_ph = list(phonemes)
                weak_ph[root_vowel_idx] = "e"
                return pn.accep(prefix + "+") + pn.accep(
                    "".join(weak_ph) + "[PERF_WEAK]"
                )
            elif root_str in perfect_weak_guna_roots:
                root_fst = self._apply_guna(root_str, "[STRONG]")
            else:
                # Whitney §783: shorten long vowels in the weak perfect.
                if root_str and root_str[-1] in _PERFECT_SHORTEN:
                    short_root = root_str[:-1] + _PERFECT_SHORTEN[root_str[-1]]
                else:
                    short_root = root_str
                
                root_obj = DHATUPATHA_ANALYZER.get(root_str, class_num)
                if root_obj.takes_samprasarana:
                    # The root takes samprasarana in the weak perfect.
                    # We add [SAMP] so morphology.py can resolve consonant-initial samprasarana
                    # like svap->sup, vyadh->vidh, prach->pṛch.
                    # For vowel-initial ones (yaj, vac), this will yield ij, uc, etc.
                    # Wait, if we prepend [SAMP], it's handled perfectly by the rules!
                    short_root = "[SAMP]" + short_root

                # Tag with [PERF_WEAK] so sandhi.py can apply specific yan rules (e.g., ninyiva, suṣuviva).
                root_fst = pn.accep(short_root + "[PERF_WEAK]")
        return pn.accep(prefix + "+") + root_fst

    def _build_perfect_krdanta_base(self, root_str, class_num, voice):
        """Build the base for perfect participles (kvasu/kāna)."""
        prefix = self.reduplicator.generate_prefix(root_str)
        if root_str in perfect_stem_overrides:
            info = perfect_stem_overrides[root_str]
            return pn.accep(info["weak"])

        if root_str in perfect_weak_guna_roots:
            root_fst = self._apply_guna(root_str, "[STRONG]")
        else:
            if root_str and root_str[-1] in _PERFECT_SHORTEN:
                short_root = root_str[:-1] + _PERFECT_SHORTEN[root_str[-1]]
            else:
                short_root = root_str
            root_fst = pn.accep(short_root)
        return pn.accep(prefix + "+") + root_fst

    def _desiderative_root_base(self, root_str: str) -> str:
        """Vowel grades on the root before desiderative -ṣa (Whitney §1028 / INRIA)."""
        phonemes = ALPHABET.parse_phonemes(root_str)
        if not phonemes:
            return root_str
        last = phonemes[-1]
        if last == "ā":
            return "".join(phonemes[:-1]) + "ī"
        if last == "i":
            return "".join(phonemes[:-1]) + "ī"
        if last == "u":
            return "".join(phonemes[:-1]) + "ū"
        if last == "ṛ":
            return "".join(phonemes[:-1]) + "īr"
        if last == "ṝ":
            return "".join(phonemes[:-1]) + "ar"
        out: list[str] = []
        for i, p in enumerate(phonemes):
            if p in ("ṛ", "ṝ") and i < len(phonemes) - 1:
                out.append("ar")
            else:
                out.append(p)
        return "".join(out)

    def _build_desiderative(self, root_str, strength):
        """Build the desiderative (Sanadi) stem."""
        if root_str in desiderative_stem_overrides:
            bases = desiderative_stem_overrides[root_str]
            return pn.union(*[pn.accep(b) for b in bases])
        prefix = self.reduplicator.generate_desiderative_prefix(root_str)
        is_anit = DHATUPATHA_ANALYZER.get(root_str, 1).is_anit  # P.7.2.10
        suffix = "+sa" if is_anit else "+iṣa"
        base_str = self._desiderative_root_base(root_str)

        # Block yan-sandhi (ū+ → v+) before seṭ desiderative -ṣa so tuṣṭūṣa stays intact.
        if suffix == "+iṣa" and base_str.endswith("ū"):
            return pn.accep(prefix) + pn.accep(base_str) + pn.accep("[DESID_Ū]+iṣa")
        return pn.accep(prefix) + pn.accep(base_str) + pn.accep(suffix)

    def _build_desiderative_perfect(self, root_str: str, strength: str) -> pn.Fst:
        """Perfect stem of a desiderative base.

        Builds desiderative present-stem, strips final -a (…-ṣa), then applies the
        regular perfect stem formation to that resulting base.

        NOTE: For these derived bases, INRIA attests perfects that keep the base
        vowel (e.g. bubhūṣ- → bububhūṣ-), rather than applying guṇa (…hoṣ-).
        """
        # Expand overrides (may be multiple bases).
        if root_str in desiderative_stem_overrides:
            bases = desiderative_stem_overrides[root_str]
        else:
            prefix = self.reduplicator.generate_desiderative_prefix(root_str)
            is_anit = DHATUPATHA_ANALYZER.get(root_str, 1).is_anit  # P.7.2.10
            suffix = "+sa" if is_anit else "+iṣa"
            base_str = self._desiderative_root_base(root_str)
            bases = [prefix + base_str + suffix]

        # Strip trailing 'a' (thematic vowel of the desiderative present stem).
        bases = [b[:-1] if b.endswith("a") else b for b in bases]

        # Derived-base perfect: reduplicate the (a-stripped) base and keep it
        # unchanged (no guṇa on ū → o), matching INRIA benchmark forms.
        stems = []
        for b in bases:
            pfx = self.reduplicator.generate_prefix(b)
            st = pfx + "+" + b
            if root_str == "sṛj":
                st = st.replace("sṛj", "ṣṛj") # INRIA expects double ruki: siṣiṣṛkṣa
            stems.append(pn.accep(st))
        return pn.union(*stems)

    def _build_desiderative_passive(self, root_str, strength):
        """Build the desiderative passive stem (e.g. bubhūṣya)."""
        base = self._build_desiderative(root_str, strength)
        return (base + pn.accep("+")) @ pn.cdrewrite(
            pn.cross("a+", ""), "", "", self.sig
        ) + pn.accep("ya")

    def _compute_samprasarana_passive(self, root_str: str):
        """Algorithmically derive Samprasāraṇa-based passive stem.

        Pāṇini 6.1.13-15, Whitney §252:
        Roots whose initial consonant cluster ends in a semivowel (y/v/r)
        replace that semivowel with its corresponding vowel in weak stems:
            y → i   (yaj → ij)
            v → u   (vac → uc, vap → up, vah → uh)
            r → ṛ   (grah → gṛh — but initial 'gr' reverses to 'gṛh')
        The resulting vowel also causes lengthening before voiced endings.

        Returns the samprasāraṇa passive base (without +ya) if applicable,
        else returns None (= not a samprasāraṇa root).
        """
        phonemes = ALPHABET.parse_phonemes(root_str)
        if not phonemes:
            return None

        # Semivowel → vowel map (Samprasāraṇa proper)
        sv_map = {"y": "i", "v": "u", "r": "ṛ"}

        # Scan the root for an initial consonant cluster containing a semivowel
        # Pattern: (one or more stop consonants) + semivowel + vowel + (rest)
        # e.g. vac: v(semivowel) a c  → semivowel at position 0
        #      yaj: y(semivowel) a j  → semivowel at position 0
        #      grah: g r(semivowel) a h → semivowel at position 1
        consonants_set = set(ALPHABET.consonants_list)
        semivowels_set = {"y", "v", "r"}
        vowels_set = set(ALPHABET.vowels_list)

        # Find where the first vowel is
        vowel_idx = next((i for i, p in enumerate(phonemes) if p in vowels_set), None)
        if vowel_idx is None or vowel_idx == 0:
            return None  # Root starts with a vowel — no samprasāraṇa

        pre_vowel = phonemes[:vowel_idx]  # consonants before the root vowel
        # The last consonant before the vowel must be a semivowel
        if pre_vowel[-1] not in semivowels_set:
            return None

        sv = pre_vowel[-1]
        sv_vowel = sv_map[sv]

        # Build new root: consonants before sv + sv_vowel + consonants after old vowel
        # The root vowel is dropped (samprasāraṇa replaces both the semivowel and the vowel).
        # e.g. vac: pre=[v], vowel=a, rest=[c]  → u + c = uc
        # e.g. yaj: pre=[y], vowel=a, rest=[j]  → i + j = ij
        # e.g. grah: pre=[g,r], vowel=a, rest=[h] → g + ṛ + h = gṛh
        before_sv = pre_vowel[:-1]  # consonants before the semivowel
        rest = phonemes[vowel_idx + 1 :]  # consonants after root vowel

        new_phonemes = before_sv + [sv_vowel] + rest
        return "".join(new_phonemes)

    def _build_passive(self, root_str: str, class_num=None, tense: str = "present", **kwargs):
        """Passive stem with correct long-vowel and Samprasarana handling.

        Priority order:
        1. Explicit overrides (passive_stem_overrides).
        2. Long-vowel substitution (Panini 6.4.66, Whitney 997):
           a-final roots: a -> i before passive ya  (pa->pi, da->di, stha->sthi).
        3. Special case: sru passive = sru+ya with long u (Whitney 997).
        4. Algorithmic Samprasarana (whitelist only, Panini 6.1.13-15).
        5. Generic [PASSIVE] tag.
        """
        root_obj = DHATUPATHA_ANALYZER.get(root_str, class_num)
        if class_num == 10:
            # Curādi primary passive: same base as active (kathaya → kathyata), no upadhā-vṛddhi.
            use_vriddhi = self._class10_use_vriddhi(root_str, None, tense)
            base = self._build_causative_base(root_str, class_num=10, use_vriddhi=use_vriddhi)
            return base + pn.accep("ya")

        # Layer 1: Explicit override
        if root_str in passive_stem_overrides:
            override = passive_stem_overrides[root_str]
            if isinstance(override, list):
                return pn.union(*[pn.accep(s) for s in override]) + pn.accep("+ya")
            return pn.accep(override) + pn.accep("+ya")

        # Layer 2: aa-final root passive: aa -> ii (Panini 6.4.66, Whitney 997)
        # pa->pi, da->di, stha->sthi, ma->mi, ha->hi, jna->jni
        phonemes = ALPHABET.parse_phonemes(root_str)
        if phonemes and phonemes[-1] == "ā":
            stem = root_str[:-1] + "ī"
            return pn.accep(stem) + pn.accep("+ya")

        # Special śru case
        if root_str == "śru":
            return pn.accep("śrū+ya")

        tag = "[PASSIVE]"
        if class_num == 4:
            tag = "[CLASS4]"

        # Pāṇini 6.4.48 (ato lopaḥ): final short 'a' drops before 'yak' (passive 'ya')
        # This primarily affects denominative roots like 'yantra', 'dola'.
        stem_str = root_str
        # Class-4 verbal roots keep final -a for [CLASS4] vr̥ddhi (jan → jānya-).
        # Final -a drop is for denominative stems only (yantra → yantrya-).
        if phonemes and phonemes[-1] == "a" and class_num != 4:
            stem_str = root_str[:-1]

        fst = pn.accep(stem_str + tag)
        if root_obj.takes_samprasarana:
            fst = pn.accep("[SAMP]") + fst

        return fst + pn.accep("+ya")

    def _build_aorist_passive_3sg(self, root_str):
        return pn.accep(root_str + "[AORIST_PASS_3SG]")

    # ─── Class builders ───────────────────────────────────────────────────────

    def _build_class_1(self, root_str, strength, **kwargs):
        # Class 1 affix (śap): active takes guṇa + thematic -a-; middle uses guṇa stem only.
        voice = kwargs.get("voice", "active")
        class_num = kwargs.get("class_num", 1)
        root_obj = DHATUPATHA_ANALYZER.get(root_str, class_num)
        if strength == "[STRONG]":
            if root_obj.is_ruh_class:
                stem = self._apply_ruh_strong(root_str)
            else:
                stem = self._apply_guna(root_str, "[STRONG]")
            return stem + pn.accep("[CLASS1_IRR]+a")
        if voice == "middle":
            if (
                root_str.endswith(("ū", "ī"))
                and root_str in self._CLASS1_MIDDLE_LONG_VOWEL_ROOTS
            ):
                # knū etc.: middle thematic on long vowel (knūya-).
                return pn.accep(root_str + strength) + pn.accep("+ya")
            if root_str in self._CLASS1_SUPPLETIVE:
                # Suppletion + śap (gacche, gacchase, tiṣṭhate, …).
                return pn.accep(root_str + strength + "[CLASS1_IRR]+a")
            # ṛ/ṝ in the root: ātmanepada present-system keeps zero-grade ṛ (akṛpata).
            phonemes = ALPHABET.parse_phonemes(root_str)
            if "ṛ" in phonemes or "ṝ" in phonemes:
                return pn.accep(root_str) + pn.accep("+a")
            if root_obj.is_ruh_class:
                return self._apply_ruh_strong(root_str) + pn.accep("+a")
            # bhū, nī, …: guṇa + śap (bhave, bhavase, …).
            return self._apply_guna(root_str, "[STRONG]") + pn.accep("+a")
        stem = pn.accep(root_str + strength)
        return stem + pn.accep("[CLASS1_IRR]+a")

    def _build_class_2(self, root_str, strength, **kwargs):
        """Adādi (class 2) — athematic, strong/weak alternation.

        Whitney §212-213 / Pāṇini 7.3.86:
        - Strong: Guna for most roots; Vriddhi for ṛ-vowel roots (mṛj → mārj).
        - Weak: Bare root with [WEAK] tag for systematic zero-grade in morphology.
        """
        if root_str == "vac":
            if strength == "[STRONG]":
                return self._apply_guna(root_str, strength)
            else:
                # Whitney §219a: vac makes as middle 2d pl. vagdhve or vaḍḍhve.
                # We can union a special tag or stem if needed, but let's just let it be vac[WEAK]
                return pn.accep(root_str + "[WEAK]")

        # Whitney §212: ṛ-vowel class-2 roots take Vriddhi in strong forms.
        # e.g. mṛj → mārj (Vriddhi of ṛ = ār), not *merj (Guna = er).
        if strength == "[STRONG]":
            phonemes = ALPHABET.parse_phonemes(root_str)
            vowels = set(ALPHABET.vowels_list)
            if any(ph == "ṛ" for ph in phonemes if ph in vowels):
                return self._apply_vriddhi(root_str)
                
            # Whitney §626 / Pāṇini 7.3.89: u-final roots take Vriddhi (optionally Guna).
            # e.g., stu → staumi (vriddhi) / stomi (guna).
            if phonemes[-1] == "u":
                # vriddhi and ī augment are applied in morphology.py before consonants
                return self._apply_guna(root_str, strength) + pn.accep("[CLASS2_U]")

        if strength == "[WEAK]":
            phonemes = ALPHABET.parse_phonemes(root_str)
            if phonemes and phonemes[-1] in ("u", "ū"):
                # Pāṇini 6.4.77: u/ū ending roots take uv before vowels.
                # Tagging with [PERF_WEAK] forces sandhi.py to apply perfect_yan_simple
                # which converts u/ū -> uv (e.g. stu -> stuvanti).
                return pn.accep(root_str + "[PERF_WEAK]")

        return self._apply_guna(root_str, strength)

    def _build_class_3(self, root_str, strength, **kwargs):
        """Juhotyādi (class 3) reduplication stem.

        Whitney §671 / Pāṇini 3.1.5:
        - Strong (sg act): prefix + full root (guna if applicable).
        - Weak (all others): prefix + zero-grade root.
          For ā-final roots (dā, dhā): zero-grade = root minus ā (d, dh).
        """
        if root_str in class_3_irregulars:
            irr = class_3_irregulars[root_str]
            return pn.accep(irr["strong"] if strength == "[STRONG]" else irr["weak"])

        prefix = self.reduplicator.generate_prefix(root_str)
        
        # Pāṇini 7.4.75 (nijāṃ trayāṇāṃ guṇaḥ ślau): nij, vij, viṣ take guṇa in class 3 reduplication.
        if root_str in {"nij", "vij", "viṣ"}:
            prefix = prefix.replace("i", "e")

        # Whitney §671: ā-final roots (dā, dhā, …) — weak stem drops the ā.
        # generate_prefix already gives the shortened prefix (ā→a, ī→i, ū→u).
        # e.g. dā → prefix='da', strong='da+dā', weak='da+d'
        phonemes = ALPHABET.parse_phonemes(root_str)
        if phonemes and phonemes[-1] == "ā":
            if strength == "[STRONG]":
                return pn.accep(prefix) + pn.accep(root_str)  # dadā
            else:
                return pn.accep(prefix) + pn.accep(root_str[:-1])  # dad (drop ā)

        return pn.accep(prefix) + self._apply_guna(root_str, strength)

    def _build_class_4(self, root_str, strength, **kwargs):
        # Whitney §761: jan class-4 → jāya- (final nasal drops, vowel lengthens)
        if root_str == "jan":
            return pn.accep("jā") + pn.accep("+ya")
        if root_str == "klam":
            return pn.accep("kl" + "a[CLASS4_VRIDDHI]" + "m[CLASS4]+ya")
        # [CLASS4] triggers i→ī lengthening in MorphologyEngine before +ya
        return pn.accep(root_str + "[CLASS4]") + pn.accep("+ya")

    def _build_class_5(self, root_str, strength, **kwargs):
        """Svādi (class 5) — affix nu/no."""
        affix = "no" if strength == "[STRONG]" else "nu"
        return pn.accep(root_str + "+" + affix)

    def _build_class_6(self, root_str, strength, **kwargs):
        """Class 6 (Tudādi) - Nasal infix for ḷ-it roots (P. 7.1.59).

        Roots marked with ḷ-it (x~ suffix in the Dhātupāṭha) insert a nasal
        after the root vowel in the class-6 present stem:
        muc → muñcati, vid → vindati, lip → limpati, sic → siñcati.
        """
        root_obj = DHATUPATHA_ANALYZER.get(root_str, 6)
        # ṝ-final roots weaken to ir in the class-6 present stem (kṝ → kir-).
        if root_str.endswith("ṝ"):
            root_str = root_str[:-1] + "ir"
        # ū-final roots take -uv- before thematic a (kū → kuv-).
        elif root_str.endswith("ū"):
            root_str = root_str[:-1] + "uv"
        # iṭ/ḷṭ roots (I~, x~) insert nasal after the root vowel (kṛt → kṛṇt-).
        elif root_obj.is_idit or root_obj.is_lrit:
            vowels = set(ALPHABET.vowels_list)
            insert_idx = -1
            for i, ch in enumerate(root_str):
                if ch in vowels:
                    insert_idx = i + 1
                    break
            if insert_idx != -1:
                root_str = root_str[:insert_idx] + "n" + "+" + root_str[insert_idx:]
        return pn.accep(root_str) + pn.accep("+a")

    def _build_class_7(self, root_str, strength, present_system: bool = True, **kwargs):
        """Rudhādi (class 7) — nasal infix inserted after the root vowel.

        Whitney §683–696 / Pāṇini 3.1.78:
        - **Present system** (present, imperfect, imperative, optative):
            Strong (sg act): root unchanged + 'na' infix.
            Weak (all others): root unchanged + 'n'  infix.
            e.g. yuj → yu+na+j (3sg act) / yu+n+j (3pl act / all mid).
        - **Non-present systems** (perfect, aorist):
            Strong: guṇa on root vowel + 'na' infix.
            e.g. bhid perfect strong → bhe+na+d.

        Whitney §686 is explicit: in the present system the root vowel is NOT
        strengthened — only the nasal infix alternates (ná vs n).
        A '+' after the infix lets nasal_assimilation fire (n→ñ/m/ṇ).
        """
        _GUNA = {
            "i": "e", "ī": "e",
            "u": "o", "ū": "o",
            "ṛ": "ar", "ṝ": "ār",
            "a": "a", "ā": "ā",
            "e": "e", "o": "o",
        }
        vowels = set(ALPHABET.vowels_list)
        phonemes = ALPHABET.parse_phonemes(root_str)
        if not phonemes:
            raise ValueError(f"Class-7 root '{root_str}' has no phonemes.")

        vowel_idx = next((i for i, ph in enumerate(phonemes) if ph in vowels), -1)
        if vowel_idx == -1:
            raise ValueError(f"Class-7 root '{root_str}' has no vowel.")

        pre  = "".join(phonemes[:vowel_idx + 1])
        post = "".join(phonemes[vowel_idx + 1:])

        if strength == "[STRONG]" and not present_system:
            # Perfect/aorist strong: guṇa the vowel, then insert 'na'
            root_vowel   = phonemes[vowel_idx]
            graded_vowel = _GUNA.get(root_vowel, root_vowel)
            pre = "".join(phonemes[:vowel_idx]) + graded_vowel
            infixed = pre + "na+" + post
        elif strength == "[STRONG]":
            # Present strong: root vowel unchanged, insert 'na'
            infixed = pre + "na+" + post
        else:
            # Weak (all systems): root vowel unchanged, insert 'n'
            infixed = pre + "n+" + post

        return pn.accep(infixed)

    def _build_class_8(self, root_str, strength, **kwargs):

        """Tanadi - root + -o- (strong) or -u- (weak).

        MorphologyEngine's class8_suppletion converts kr -> kur before +u.
        class8_u_drop then removes the +u before consonant-initial endings.
        """
        stem = self._apply_guna(root_str, strength)
        affix = "+o" if strength == "[STRONG]" else "+u"
        return stem + pn.accep(affix)

    def _build_class_9(self, root_str, strength, **kwargs):
        stem = root_str
        tense = kwargs.get("tense", "present")
        root_obj = DHATUPATHA_ANALYZER.get(root_str, 9)
        if (
            strength == "[WEAK]"
            and root_obj.takes_samprasarana
            and tense not in ("present", "imperative", "optative")
        ):
            stem = "[SAMP]" + root_str
        affix = "+nā" if strength == "[STRONG]" else "+nī[CLASS9]"
        return pn.accep(stem) + pn.accep(affix)

    def _build_intensive(self, root_str, strength, voice="middle"):
        """Intensive (yaṅ) stem."""
        if root_str in intensive_stem_overrides:
            override = intensive_stem_overrides[root_str]
            if isinstance(override, dict):
                stem_base = override.get("middle") if voice == "middle" else (override.get("strong") if strength == "[STRONG]" else override.get("weak"))
                if not stem_base: # fallback
                    stem_base = override.get("strong", list(override.values())[0])
            else:
                stem_base = override
        else:
            prefix = self.reduplicator.generate_intensive_prefix(root_str)
            stem_base = prefix + root_str if voice in ("middle", "active_anta") else None
            if voice not in ("middle", "active_anta"):
                prefix = self.reduplicator.generate_intensive_prefix(root_str)
                stem_base = prefix  # will be used below

        if voice in ("middle", "active_anta"):
            if root_str in intensive_stem_overrides:
                if isinstance(stem_base, list):
                    return pn.union(*[pn.accep(s) for s in stem_base]) + pn.accep("[PASSIVE]+ya")
                return pn.accep(stem_base) + pn.accep("[PASSIVE]+ya")
            prefix = self.reduplicator.generate_intensive_prefix(root_str)
            return pn.accep(prefix) + pn.accep(root_str) + pn.accep("[PASSIVE]+ya")
        else:
            # Active luganta: Guna grade + [INTENSIVE_ACTIVE] tag.
            # Morphology erases [INTENSIVE_ACTIVE]+ → +, then sandhi's ayadi fires:
            if root_str in intensive_stem_overrides:
                if isinstance(stem_base, list):
                    return pn.union(*[pn.accep(s) for s in stem_base]) + pn.accep("[INTENSIVE_ACTIVE]")
                return pn.accep(stem_base) + pn.accep("[INTENSIVE_ACTIVE]")
            
            prefix = self.reduplicator.generate_intensive_prefix(root_str)
            # Apply strength to root
            if root_str == "hu":
                if strength == "[STRONG]":
                    base_stem = pn.accep(prefix) + pn.accep("ho")
                else:
                    base_stem = pn.accep(prefix) + pn.accep("hav")
            elif root_str == "bhū":
                if strength == "[STRONG]":
                    base_stem = pn.accep(prefix) + pn.accep("bho")
                else:
                    base_stem = pn.accep(prefix) + pn.union(pn.accep("bho"), pn.accep("bhav"))
            else:
                base_stem = pn.accep(prefix) + self._apply_guna(root_str, strength)
                
            return base_stem + pn.accep("[INTENSIVE_ACTIVE]")

    def _build_class_10(self, root_str, strength, **kwargs):
        """Curādi / Causative."""
        tense = kwargs.get("tense", "present")
        derivative = kwargs.get("derivative")
        voice = kwargs.get("voice", "active")
        # Mitāṃ-hrasva / no-vṛddhi roots: compose -aya literally (churaya, not *chauraya).
        if root_str in self._CAUSATIVE_SHORT_A_ROOTS:
            return pn.accep(root_str + "aya")
        if root_str == "i" and voice == "middle":
            return pn.accep("āpya")
        use_vriddhi = self._class10_use_vriddhi(root_str, derivative, tense)
        base = self._build_causative_base(
            root_str,
            class_num=10,
            derivative=derivative,
            use_vriddhi=use_vriddhi,
        )
        return base + pn.accep("aya")

    def _build_periphrastic_base(self, root_str, class_num, derivative=None):
        """Build the periphrastic perfect base (e.g. coray + ām)."""
        if derivative == "causative" or class_num == 10:
            use_vriddhi = self._class10_use_vriddhi(
                root_str, derivative, "perfect"
            )
            base = self._build_causative_base(
                root_str, derivative=derivative, use_vriddhi=use_vriddhi
            )
            return base + pn.accep("ayām")
        if derivative == "desiderative":
            base = self._build_desiderative(root_str, "[STRONG]")
            # Strip final 'a' and add 'ām'
            return (base + pn.accep("[WORD_END]")) @ pn.cdrewrite(pn.cross("a[WORD_END]", ""), "", "", self.sig) @ pn.cdrewrite(pn.cross("[WORD_END]", ""), "", "", self.sig) + pn.accep("ām")
        if derivative == "intensive":
            # Intensive periphrastic is rare but uses the intensive stem + ām
            # For simplicity, using intensive_middle (thematic) as base
            base = self._build_intensive(root_str, "[WEAK]", voice="middle")
            return (base + pn.accep("+")) @ pn.cdrewrite(
                pn.cross("a+", ""), "", "", self.sig
            ) + pn.accep("ām")
        if derivative == "denominative":
            base = self._build_denominative(root_str)
            # base ends in 'y' (putrīy), add 'ām' -> putrīyām
            return base + pn.accep("ām")

        # Primary roots (starting with long vowel etc.)
        # Default: guna grade + ām
        return self._apply_guna(root_str, "[STRONG]") + pn.accep("ām")

    def _build_denominative(self, base_str: str, variant: str = "denominative"):
        """Build denominative verbal base from a nominal stem.

        Whitney §1058-1068 / Pāṇini 3.1.8 (nāmadhātu):

        - a/ā-stems and many consonant-final stems form an īy-base
          (e.g. putra -> putrīya-, mālā -> mālīya-).
        - i/ī -> īya- (Whitney §1058b)
        - u/ū -> ūya- (Whitney §1058c)
        - ṛ/ṝ -> rīya- (Whitney §1058d)
        - -as stems commonly form direct -sya- (e.g. namas -> namasya-).
        """
        phonemes = ALPHABET.parse_phonemes(base_str)
        if not phonemes:
            return pn.accep(base_str + "+īy")

        final = phonemes[-1]
        vowels = {"a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "e", "o", "ai", "au"}

        # Explicit sya-type extension for non-as-stems (namasya-type generalization)
        if variant == "denominative_sya":
            return pn.accep(base_str + "+s+y")

        # -as stems: namas -> namasya-
        if base_str.endswith("as"):
            return pn.accep(base_str + "+y")

        if final in ("i", "ī"):
            stem = base_str[: -len(final)] + "ī"
            return pn.accep(stem + "+y")

        if final in ("u", "ū"):
            stem = base_str[: -len(final)] + "ū"
            return pn.accep(stem + "+y")

        if final in ("ṛ", "ṝ"):
            stem = base_str[: -len(final)] + "rī"
            return pn.accep(stem + "+y")

        # a/ā-final stems: primary denominative is -īya (Whitney §1058, kāmyac affix).
        # The -āya variant (Whitney §1066) is a distinct formation; only generated
        # when explicitly requested via denominative_aya.
        if final in ("a", "ā"):
            base = base_str[: -len(final)]
            if variant == "denominative_aya":
                return pn.accep(base + "ā+y")
            # Both -īya (Whitney §1058) and -āya (Whitney §1066) are attested
            # for different a-final stems. Generate both, and also -aya.
            variants = [pn.accep(base + "ī+y"), pn.accep(base + "ā+y"), pn.accep(base_str + "+y")]
            if base.endswith(("n", "ṇ")) and variant == "denominative":
                variants.append(pn.accep(base_str + "+s+y"))
            return pn.union(*variants)

        # Consonant-final (Whitney §1059)
        if final not in vowels:
            variants = []
            if variant in ("denominative", "denominative_ya"):
                variants.append(pn.accep(base_str + "+y"))
            if variant in ("denominative", "denominative_aya"):
                variants.append(pn.accep(base_str + "ā+y"))
            return pn.union(*variants) if variants else pn.accep(base_str + "+y")

        # Fallback for any unclassified vocalic ending.
        return pn.accep(base_str + "+īy")
