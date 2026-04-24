import pynini as pn
from irregulars import (
    class_1_irregulars,
    causative_stem_irregulars,
    perfect_weak_guna_roots, perfect_stem_overrides,
    aorist_overrides, nasal_roots, desiderative_stem_overrides
)
from dhatupatha_analyzer import DHATUPATHA_ANALYZER
from alphabet import ALPHABET
from reduplication import ReduplicationEngine

# Pure short/long monophthongs — diphthongs (e, o, ai, au) are intentionally
# excluded so that diphthong-final guna forms count as "consonant-ending" for
# the Seṭ/Aniṭ decision (they become consonants via ayadi before -iṣya-).
_PURE_VOWELS = {"a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "ḷ", "ḹ"}

# Ayadi resolution table: diphthong → semivowel form (before a following vowel)
_AYADI_MAP = {"au": "āv", "ai": "āy", "o": "av", "e": "ay"}


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
        self.sigma        = ALPHABET.sigma_star
        self.sig          = self.sigma

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
            fst = builder(root_str, class_num, strength, tense, person=person, number=number) @ self.guna @ self.vriddhi

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
        """Future (Lṛṭ and Luṭ) and Conditional (Lṛṅ)."""
        is_anit = DHATUPATHA_ANALYZER.is_anit(root_str, class_num)
        
        # Exceptions to Seṭ/Aniṭ baseline in Future
        if root_str in ("gam", "kṛ"):
            is_anit = False # gam and kṛ are Seṭ in simple future
        if root_str == "krī":
            is_anit = True  # krī is Aniṭ in future (kreṣyati)

        if class_num == 10:
            base = self._build_causative_base(root_str)
            return base + pn.accep("ayiṣya")

        stem = self._apply_guna(root_str, "[STRONG]")
        suffix = "+sya" if is_anit else "+iṣya"
        return stem + pn.accep(suffix)

    def _build_periphrastic_future_system(self, root_str, class_num, strength, tense, **kwargs):
        """Periphrastic Future (Luṭ) stem = Guna root + (i) + tā/tār/tās endings."""
        is_anit = DHATUPATHA_ANALYZER.is_anit(root_str, class_num)
        
        # Exceptions to Seṭ/Aniṭ baseline in Future
        if root_str == "gam":
            is_anit = False
        if root_str == "krī":
            is_anit = True
        
        if class_num == 10:
            base = self._build_causative_base(root_str)
            return base + pn.accep("ayi")

        stem = self._apply_guna(root_str, "[STRONG]")
        # kṛ is Seṭ for simple future (kariṣyati) but Aniṭ for periphrastic future (kartā)
        if root_str == "kṛ":
            suffix = ""
        else:
            suffix = "" if is_anit else "+i"
        return stem + pn.accep(suffix)

    def _build_aorist_system(self, root_str, class_num, strength, tense, **kwargs):
        """Aorist stem (used by Aorist and Injunctive)."""
        if root_str in aorist_overrides:
            info = aorist_overrides[root_str]
            # Use explicit override if provided (e.g. ad -> ghasa)
            if strength == "[STRONG]" and "active" in info:
                return pn.accep(info["active"])
            if strength == "[WEAK]" and "middle" in info:
                return pn.accep(info["middle"])
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
            if strength == "[STRONG]":
                fst = self._apply_guna(root_str, "[STRONG]")
            else:
                fst = pn.accep(root_str)
            
            if is_anit:
                return fst + pn.accep("+s")
            return fst + pn.accep("+iṣ")
                    
        elif a_type == "root":
            return pn.accep(root_str + "[ROOT_AORIST]")

        return pn.accep(root_str + "[AORIST]")

    def _build_perfect_system(self, root_str, class_num, strength, tense, **kwargs):
        """Perfect stem = reduplication prefix + (guna | shortened) root."""
        prefix = self.reduplicator.generate_prefix(root_str)
        person = kwargs.get("person")
        number = kwargs.get("number")
        
        if strength == "[STRONG]":
            # Strong: guna or vriddhi grade
            if root_str in perfect_stem_overrides:
                stem_str = perfect_stem_overrides[root_str]["strong"]
                return pn.accep(stem_str)
            
            # Pāṇini 7.2.115: Vriddhi of final vowel in perfect active 1/3sg.
            # (Note: 1sg is optionally Guna, but Vriddhi is standard).
            if (person in ("1", "3") and number == "sg"):
                # Use Vriddhi if it ends in a vowel, else Guna
                if root_str[-1] in ALPHABET.vowels_list:
                    root_fst = self._apply_vriddhi(root_str)
                else:
                    root_fst = self._apply_guna(root_str, "[STRONG]")
            else:
                # 2sg active or other strong forms take Guna
                root_fst = self._apply_guna(root_str, "[STRONG]")
        else:
            # Weak: priority table
            if root_str in perfect_stem_overrides:
                # Suppletive: full stem already encoded — no prefix
                stem_str = perfect_stem_overrides[root_str]["weak"]
                return pn.accep(stem_str)
            if root_str in perfect_weak_guna_roots:
                root_fst = self._apply_guna(root_str, "[STRONG]")
            else:
                _SHORTEN = {"ī": "i", "ū": "u", "ṝ": "ṛ", "ā": "a"}
                if root_str and root_str[-1] in _SHORTEN:
                    short_root = root_str[:-1] + _SHORTEN[root_str[-1]]
                else:
                    short_root = root_str
                root_fst = pn.accep(short_root)
        return pn.accep(prefix + "+") + root_fst

    def _build_desiderative(self, root_str, strength):
        """Build the desiderative (Sanādi) stem.
        Uses overrides from irregulars.py for the complex benchmark roots."""
        if root_str in desiderative_stem_overrides:
            bases = desiderative_stem_overrides[root_str]
            # Use union for roots with multiple valid bases (e.g. gam -> jigāṃsa/jigamiṣa)
            return pn.union(*[pn.accep(b) for b in bases])
        
        # Algorithmic fallback
        prefix = self.reduplicator.generate_desiderative_prefix(root_str)
        is_anit = DHATUPATHA_ANALYZER.is_anit(root_str, 1)
        suffix = "sa" if is_anit else "iṣa"
        return pn.accep(prefix) + pn.accep(root_str) + pn.accep(suffix)

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
    def _build_desiderative_passive(self, root_str, strength):
        """Build the desiderative passive stem (e.g. bubhūṣya)."""
        base = self._build_desiderative(root_str, strength)
        # Remove the 'a' of bubhūṣa before adding 'ya'
        return (base + pn.accep("+")) @ pn.cdrewrite(pn.cross("a+", ""), "", "", self.sig) + pn.accep("ya")

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
        prefix = self.reduplicator.generate_intensive_prefix(root_str)
        if voice == "middle":
            return pn.accep(prefix) + pn.accep(root_str) + pn.accep("+ya")
        else:
            # Active takes Guna in strong grade.
            # In weak grade, it also takes Guna if ending in a vowel.
            if strength == "[STRONG]" or root_str[-1] in ALPHABET.vowels_list:
                stem = pn.accep(prefix) + self._apply_guna(root_str, "[STRONG]")
            else:
                stem = pn.accep(prefix) + pn.accep(root_str)
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