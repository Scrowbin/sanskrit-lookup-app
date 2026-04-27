import pynini as pn
from irregulars import (
    class_1_irregulars,
    causative_stem_irregulars,
    perfect_weak_guna_roots, perfect_stem_overrides,
    aorist_overrides, nasal_roots, desiderative_stem_overrides,
    future_stem_overrides, periphrastic_stem_overrides,
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
_PERFECT_SHORTEN = {"ī": "i", "ū": "u", "ṝ": "ṛ", "ā": "a"}


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

    Seṭ / Aniṭ (future)
    --------------------
    The decision is made on the **guna-grade** surface string, not the raw root.
    Diphthong-final guna also counts as consonant-ending (→ Seṭ).
    Explicit Aniṭ overrides live in ``irregulars.aset_roots``.
    """

    def __init__(self, strength_engine):
        self.guna         = strength_engine.get_guna()
        self.vriddhi      = strength_engine.get_vriddhi()
        self.reduplicator = ReduplicationEngine()
        self.sig          = ALPHABET.sigma_star

        # Ayadi resolver for derived bases (e.g. bhau → bhāv)
        self.ayadi = pn.cdrewrite(
            pn.string_map(_AYADI_MAP),
            "", pn.union(ALPHABET.vowels, "[WEAK]", "[STRONG]", "[VRIDDHI]", "+"), 
            self.sig
        )

        self.tense_dispatch = {
            "present":     self._build_present_system,
            "imperfect":   self._build_present_system,
            "imperative":  self._build_present_system,
            "optative":    self._build_present_system,
            "future":      self._build_future_system,
            "conditional": self._build_future_system,
            "perfect":     self._build_perfect_system,
            "periphrastic_future": self._build_periphrastic_future_system,
            "aorist":      self._build_aorist_system,
            "injunctive":  self._build_aorist_system,
        }

        self.class_handlers = {
            1:  self._build_class_1,
            2:  self._build_class_2,
            3:  self._build_class_3,
            4:  self._build_class_4,
            5:  self._build_class_5,
            6:  self._build_class_6,
            7:  self._build_class_7,
            8:  self._build_class_8,
            9:  self._build_class_9,
            10: self._build_class_10,
        }

    # ─── Public entry point ──────────────────────────────────────────────────

    def build(self, root_str, class_num, strength, tense="present", derivative=None, person=None, number=None):
        if derivative == "desiderative":
            fst = self._build_desiderative(root_str, strength)
            if tense in ("future", "conditional", "periphrastic_future"):
                # Derived thematic stems (desid/caus) take -iṣya- (or -i- for periph) after dropping final 'a'
                suffix = "i" if tense == "periphrastic_future" else "iṣya"
                fst = (fst + pn.accep("+")) @ pn.cdrewrite(pn.cross("a+", ""), "", "", self.sig) + pn.accep(suffix)
        elif derivative == "desiderative_passive":
            fst = self._build_desiderative_passive(root_str, strength)
        elif derivative == "passive":
            fst = self._build_passive(root_str, class_num)
        elif derivative == "aorist_passive_3sg":
            fst = self._build_aorist_passive_3sg(root_str)
        elif derivative == "intensive_middle":
            fst = self._build_intensive(root_str, strength, voice="middle")
        elif derivative == "intensive_active":
            fst = self._build_intensive(root_str, strength, voice="active")
        else:
            builder = self.tense_dispatch.get(tense)
            if builder is None:
                raise ValueError(f"Tense '{tense}' not supported.")
            fst = builder(root_str, class_num, strength, tense, person=person, number=number)

        return (fst @ self._clean()).optimize()

    # ─── Low-level FST helpers ───────────────────────────────────────────────

    def _clean(self, tags=None):
        """cdrewrite that erases strength tags by default."""
        if tags is None:
            # ONLY erase strength tags; structural tags like [PASSIVE], [ROOT_AORIST]
            # must reach MorphologyEngine.
            tags = pn.union("[STRONG]", "[WEAK]", "[VRIDDHI]")
        elif isinstance(tags, str):
            tags = pn.accep(tags)
        return pn.cdrewrite(pn.cross(tags, ""), "", "", self.sig)

    def _apply_guna(self, root_str, strength):
        tagged = pn.accep(root_str + strength)
        if strength == "[STRONG]":
            return tagged @ self.guna @ self._clean()
        return tagged @ self._clean()

    def _apply_vriddhi(self, root_str):
        return (pn.accep(root_str + "[VRIDDHI]")
                @ self.vriddhi
                @ self._clean("[VRIDDHI]"))

    def _takes_guna_in_causative(self, root_str: str) -> bool:
        """Paninian algorithmic rule for Causative (ṇic) stem strength.
        If a root ends in a consonant and has a short penultimate vowel
        (i, u, ṛ, ḷ), it takes Guna. Otherwise, it takes Vṛddhi."""
        phonemes = ALPHABET.parse_phonemes(root_str)
        if not phonemes: return False
        if phonemes[-1] in ALPHABET.vowels_list: return False
        if len(phonemes) >= 2 and phonemes[-2] in ("i", "u", "ṛ", "ḷ"):
            return True
        return False

    def _build_causative_base(self, root_str: str):
        """Return the FST for the causative base (Vṛddhi/Guna + ayadi)."""
        if root_str in causative_stem_irregulars:
            return pn.accep(causative_stem_irregulars[root_str])

        if self._takes_guna_in_causative(root_str):
            base = self._apply_guna(root_str, "[STRONG]")
        else:
            base = self._apply_vriddhi(root_str)
        
        return base + pn.accep("+")

    # ─── Tense-system builders ────────────────────────────────────────────────

    def _build_present_system(self, root_str, class_num, strength, tense, **kwargs):
        handler = self.class_handlers.get(class_num)
        if handler is None:
            raise ValueError(f"Class {class_num} not supported.")
        return handler(root_str, strength)

    def _build_future_system(self, root_str, class_num, strength, tense, **kwargs):
        """Future (Lṛṭ) and Conditional (Lṛṅ)."""
        if class_num == 10:
            base = self._build_causative_base(root_str)
            return base + pn.accep("ayiṣya")

        # Root-specific future stem override (e.g. div uses dīv+iṣya, not guna)
        if root_str in future_stem_overrides:
            info = future_stem_overrides[root_str]
            stem = pn.accep(info["stem"])
            is_anit = info.get("anit", False)
            suffix = "+sya" if is_anit else "+iṣya"
            return stem + pn.accep(suffix)

        is_anit = DHATUPATHA_ANALYZER.is_anit(root_str, class_num)
        if root_str in ("gam", "kṛ"):
            is_anit = False
        if root_str == "krī":
            is_anit = True

        stem = self._apply_guna(root_str, "[STRONG]")
        suffix = "+sya" if is_anit else "+iṣya"
        return stem + pn.accep(suffix)


    def _build_periphrastic_future_system(self, root_str, class_num, strength, tense, **kwargs):
        """Periphrastic Future (Luṭ): stem + (i) + tā/tār/tās endings."""
        if class_num == 10:
            base = self._build_causative_base(root_str)
            return base + pn.accep("ayi")

        # Root-specific override: returns the bare stem (gant, dīv, etc.)
        if root_str in periphrastic_stem_overrides:
            bare = periphrastic_stem_overrides[root_str]
            # gam → gant (aniṭ, no connecting i): gantā
            # div → dīv (seṭ, needs +i):           dīvitā
            is_anit = root_str in ("gam",)
            suffix = "" if is_anit else "+i"
            return pn.accep(bare) + pn.accep(suffix)

        is_anit = DHATUPATHA_ANALYZER.is_anit(root_str, class_num)
        if root_str == "krī":
            is_anit = True

        stem = self._apply_guna(root_str, "[STRONG]")
        # kṛ: Aniṭ periphrastic (kartā) despite Seṭ simple future
        if root_str == "kṛ":
            return stem
        suffix = "" if is_anit else "+i"
        return stem + pn.accep(suffix)

    def _build_aorist_system(self, root_str, class_num, strength, tense, **kwargs):
        """Aorist stem (used by Aorist and Injunctive)."""
        if root_str in aorist_overrides:
            info = aorist_overrides[root_str]
            # Explicit active/middle stems are complete bases — return as-is, no suffix
            voice_key = "active" if strength == "[STRONG]" else "middle"
            if voice_key in info:
                return pn.accep(info[voice_key])
            a_type = info["type"]
        else:
            a_type = DHATUPATHA_ANALYZER.get_aorist_type(root_str, class_num)
            
        # Algorithmic derivation based on type
        phonemes = ALPHABET.parse_phonemes(root_str)
        ends_in_vowel = phonemes and phonemes[-1] in ALPHABET.vowels_list
        is_anit = DHATUPATHA_ANALYZER.is_anit(root_str, class_num)

        if a_type == "s":
            if strength == "[STRONG]":
                fst = self._apply_vriddhi(root_str)
            else:
                fst = self._apply_guna(root_str, "[STRONG]") if ends_in_vowel else pn.accep(root_str)

            if is_anit:
                return fst + pn.accep("+s")
            return fst + pn.accep("+is")
                
        elif a_type == "sa":
            return pn.accep(root_str) + pn.accep("+sa")
                
        elif a_type == "a":
            return pn.accep(root_str) + pn.accep("+a")
                
        elif a_type == "is":
            # The iṣ/is is embedded in the endings (iṣam, iṣṭām, etc.)
            # so the stem is just the guna/bare root with no extra suffix.
            if strength == "[STRONG]":
                return self._apply_guna(root_str, "[STRONG]")
            return pn.accep(root_str)
                    
        elif a_type == "root":
            return pn.accep(root_str + "[ROOT_AORIST]")

        return pn.accep(root_str + "[AORIST]")

    def _build_perfect_system(self, root_str, class_num, strength, tense, **kwargs):
        """Perfect stem = reduplication prefix + (guna | shortened) root."""
        prefix = self.reduplicator.generate_prefix(root_str)
        
        if strength == "[STRONG]":
            person = kwargs.get("person")
            number = kwargs.get("number")
            # For 3sg active: use override strong stem (Vriddhi) if available
            if person == "3" and number == "sg" and root_str in perfect_stem_overrides:
                stem_str = perfect_stem_overrides[root_str]["strong"]
                return pn.accep(stem_str)
            # For non-3sg (1sg Guna, 2sg Guna): use algorithmic Guna
            if root_str in perfect_stem_overrides and person not in ("3",):
                # Use Guna (drop the Vriddhi override; let _apply_guna handle it)
                pass
            elif root_str in perfect_stem_overrides:
                stem_str = perfect_stem_overrides[root_str]["strong"]
                return pn.accep(stem_str)
            root_fst = self._apply_guna(root_str, "[STRONG]")
        else:
            # Weak: priority table
            if root_str in perfect_stem_overrides:
                # Suppletive: full stem already encoded — no prefix.
                # hu/su have two weak alternants: guna+ayadi form (before vowels)
                # and zero-grade (before consonants). Encode as union so sandhi
                # selects the phonotactically correct one.
                info = perfect_stem_overrides[root_str]
                if "weak2" in info:
                    return pn.union(pn.accep(info["weak"]), pn.accep(info["weak2"]))
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

    def _build_desiderative(self, root_str, strength):
        """Build the desiderative (Sanadi) stem."""
        if root_str in desiderative_stem_overrides:
            bases = desiderative_stem_overrides[root_str]
            return pn.union(*[pn.accep(b) for b in bases])
        prefix = self.reduplicator.generate_desiderative_prefix(root_str)
        is_anit = DHATUPATHA_ANALYZER.is_anit(root_str, 1)
        suffix = "sa" if is_anit else "iṣa"
        return pn.accep(prefix) + pn.accep(root_str) + pn.accep(suffix)

    def _build_desiderative_passive(self, root_str, strength):
        """Build the desiderative passive stem (e.g. bubhūṣya)."""
        base = self._build_desiderative(root_str, strength)
        return (base + pn.accep("+")) @ pn.cdrewrite(pn.cross("a+", ""), "", "", self.sig) + pn.accep("ya")

    def _build_passive(self, root_str, class_num=None):
        """Passive stem."""
        if class_num == 10:
            base = self._build_causative_base(root_str)
            return base + pn.accep("ya")
        return pn.accep(root_str + "[PASSIVE]") + pn.accep("+ya")

    def _build_aorist_passive_3sg(self, root_str):
        return pn.accep(root_str + "[AORIST_PASS_3SG]")


    # ─── Class builders ───────────────────────────────────────────────────────

    def _build_class_1(self, root_str, strength):
        if root_str in class_1_irregulars:
            return pn.accep(class_1_irregulars[root_str] + "+a")
        return self._apply_guna(root_str, strength) + pn.accep("+a")

    def _build_class_2(self, root_str, strength):
        return self._apply_guna(root_str, strength)

    def _build_class_3(self, root_str, strength):
        prefix = self.reduplicator.generate_prefix(root_str)
        return pn.accep(prefix) + self._apply_guna(root_str, strength)

    def _build_class_4(self, root_str, strength):
        # [CLASS4] triggers i→ī lengthening in MorphologyEngine before +ya
        return pn.accep(root_str + "[CLASS4]") + pn.accep("+ya")

    def _build_class_5(self, root_str, strength):
        affix = "+no" if strength == "[STRONG]" else "+nu"
        return pn.accep(root_str) + pn.accep(affix)

    def _build_class_6(self, root_str, strength):
        if root_str in nasal_roots:
            return pn.accep(nasal_roots[root_str] + "+a")
        return pn.accep(root_str) + pn.accep("+a")

    def _build_class_7(self, root_str, strength):
        """Rudhadi - nasal infix inserted after the root vowel.

        A '+' is placed after the infix so nasal_assimilation (n -> n before
        the following palatal: yunj -> yunj) fires correctly.
        """
        vowels = set(ALPHABET.vowels_list)
        insert_idx = -1
        for i, ch in enumerate(root_str):
            if ch in vowels:
                insert_idx = i + 1
                break
        if insert_idx == -1:
            raise ValueError(f"Class-7 root '{root_str}' has no vowel.")
        infix   = "na" if strength == "[STRONG]" else "n"
        infixed = root_str[:insert_idx] + infix + "+" + root_str[insert_idx:]
        return pn.accep(infixed)

    def _build_class_8(self, root_str, strength):
        """Tanadi - root + -o- (strong) or -u- (weak).

        MorphologyEngine's class8_suppletion converts kr -> kur before +u.
        class8_u_drop then removes the +u before consonant-initial endings.
        """
        stem  = self._apply_guna(root_str, strength)
        affix = "+o" if strength == "[STRONG]" else "+u"
        return stem + pn.accep(affix)

    def _build_class_9(self, root_str, strength):
        affix = "+nā" if strength == "[STRONG]" else "+nī"
        return pn.accep(root_str) + pn.accep(affix)

    def _build_intensive(self, root_str, strength, voice="middle"):
        """Intensive (yaṅ) stem."""
        if root_str in intensive_stem_overrides:
            stem_base = intensive_stem_overrides[root_str]
        else:
            prefix = self.reduplicator.generate_intensive_prefix(root_str)
            stem_base = prefix + root_str if voice == "middle" else None
            if voice != "middle":
                prefix = self.reduplicator.generate_intensive_prefix(root_str)
                stem_base = prefix  # will be used below

        if voice == "middle":
            if root_str in intensive_stem_overrides:
                return pn.accep(stem_base) + pn.accep("+ya")
            prefix = self.reduplicator.generate_intensive_prefix(root_str)
            return pn.accep(prefix) + pn.accep(root_str) + pn.accep("+ya")
        else:
            # Active: Guna grade + [INTENSIVE_ACTIVE] tag.
            # Morphology erases [INTENSIVE_ACTIVE]+ → +, then sandhi's ayadi fires:
            # joho[INTENSIVE_ACTIVE]+vaḥ → joho+vaḥ → johavaḥ
            if root_str in intensive_stem_overrides:
                return pn.accep(stem_base) + pn.accep("[INTENSIVE_ACTIVE]")
            prefix = self.reduplicator.generate_intensive_prefix(root_str)
            stem = pn.accep(prefix) + self._apply_guna(root_str, "[STRONG]")
            return stem + pn.accep("[INTENSIVE_ACTIVE]")

    def _build_class_10(self, root_str, strength):
        """Curādi / Causative."""
        base = self._build_causative_base(root_str)
        return base + pn.accep("aya")

    def _build_periphrastic_base(self, root_str, class_num, derivative=None):
        """Build the periphrastic perfect base (e.g. coray + ām)."""
        if derivative == "causative" or class_num == 10:
            base = self._build_causative_base(root_str)
            return base + pn.accep("ayām")
        if derivative == "desiderative":
            base = self._build_desiderative(root_str, "[STRONG]")
            # Strip final 'a' and add 'ām'
            return (base + pn.accep("+")) @ pn.cdrewrite(pn.cross("a+", ""), "", "", self.sig) + pn.accep("ām")
        if derivative == "intensive":
            # Intensive periphrastic is rare but uses the intensive stem + ām
            # For simplicity, using intensive_middle (thematic) as base
            base = self._build_intensive(root_str, "[WEAK]", voice="middle")
            return (base + pn.accep("+")) @ pn.cdrewrite(pn.cross("a+", ""), "", "", self.sig) + pn.accep("ām")
        
        # Primary roots (starting with long vowel etc.)
        # Default: guna grade + ām
        return self._apply_guna(root_str, "[STRONG]") + pn.accep("ām")