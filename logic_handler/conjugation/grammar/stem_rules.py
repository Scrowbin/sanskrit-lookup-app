import pynini as pn
from irregulars import (
    class_1_irregulars, aset_roots,
    guna_causative_roots, causative_stem_irregulars,
    perfect_weak_guna_roots, perfect_stem_overrides,
)
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

        self.tense_dispatch = {
            "present":     self._build_present_system,
            "imperfect":   self._build_present_system,
            "imperative":  self._build_present_system,
            "optative":    self._build_present_system,
            "future":      self._build_future_system,
            "conditional": self._build_future_system,
            "perfect":     self._build_perfect_system,
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

    def build(self, root_str, class_num, strength, tense="present", derivative=None):
        if derivative == "passive":
            return self._build_passive(root_str, class_num)
        builder = self.tense_dispatch.get(tense)
        if builder is None:
            raise ValueError(f"Tense '{tense}' not supported.")
        return builder(root_str, class_num, strength, tense)

    # ─── Low-level FST helpers ───────────────────────────────────────────────

    def _clean(self, tags=None):
        """cdrewrite that erases [STRONG]/[WEAK] (or the given tag)."""
        if tags is None:
            tags = pn.union("[STRONG]", "[WEAK]")
        elif isinstance(tags, str):
            tags = pn.accep(tags)
        return pn.cdrewrite(pn.cross(tags, ""), "", "", self.sigma)

    def _apply_guna(self, root_str, strength):
        tagged = pn.accep(root_str + strength)
        if strength == "[STRONG]":
            return tagged @ self.guna @ self._clean()
        return tagged @ self._clean()

    def _apply_vriddhi(self, root_str):
        return (pn.accep(root_str + "[VRIDDHI]")
                @ self.vriddhi
                @ self._clean("[VRIDDHI]"))

    # ─── String-realisation helpers (used for Python-level decisions) ────────

    def _guna_string(self, root_str: str) -> str:
        """Realise the guna form as a Python string (for Seṭ/Aniṭ check)."""
        fst = (pn.accep(root_str + "[STRONG]") @ self.guna @ self._clean()).optimize()
        try:
            return fst.string()
        except Exception:
            return root_str

    def _causative_base_string(self, root_str: str) -> str:
        """Return the surface causative base after Vṛddhi/Guna + ayadi.

        Used by _build_passive(cl10) so the correct stem (bhāv, sāv, yoj…)
        is directly encoded in the FST without relying on sandhi ordering.

        Priority mirrors _build_class_10:
          1. causative_stem_irregulars (krī → krāp)
          2. guna_causative_roots      (yuj → yoj, cur → cor)
          3. default                   (Vṛddhi: bhū → bhau → bhāv via ayadi)
        """
        if root_str in causative_stem_irregulars:
            return causative_stem_irregulars[root_str]

        if root_str in guna_causative_roots:
            fst = (pn.accep(root_str + "[STRONG]")
                   @ self.guna @ self._clean()).optimize()
        else:
            fst = (pn.accep(root_str + "[VRIDDHI]")
                   @ self.vriddhi @ self._clean("[VRIDDHI]")).optimize()

        try:
            base = fst.string()
        except Exception:
            base = root_str

        # Resolve trailing diphthong via ayadi (bhau → bhāv, etc.)
        for diph, semivowel in _AYADI_MAP.items():
            if base.endswith(diph):
                return base[: -len(diph)] + semivowel
        return base

    # ─── Tense-system builders ────────────────────────────────────────────────

    def _build_present_system(self, root_str, class_num, strength, tense):
        handler = self.class_handlers.get(class_num)
        if handler is None:
            raise ValueError(f"Class {class_num} not supported.")
        return handler(root_str, strength)

    def _build_future_system(self, root_str, class_num, strength, tense):
        """Future / Conditional stem.

        Causative (cl10)
        ----------------
        (Vṛddhi or Guna base) + +ayiṣya — no boundary between -aya- and
        -iṣya- to prevent spurious a+i→e guna_sandhi.

        Seṭ / Aniṭ (all other classes)
        --------------------------------
        Decision on the post-guna surface form; diphthong-final guna counts
        as consonant-ending (→ Seṭ, -iṣya-); see _ends_in_consonant.
        Roots in aset_roots always take bare -sya-.
        """
        if class_num == 10:
            if root_str in causative_stem_irregulars:
                base = pn.accep(causative_stem_irregulars[root_str])
            elif root_str in guna_causative_roots:
                base = self._apply_guna(root_str, "[STRONG]")
            else:
                base = self._apply_vriddhi(root_str)
            return base + pn.accep("+ayiṣya")

        stem    = self._apply_guna(root_str, "[STRONG]")
        gstr    = self._guna_string(root_str)
        suffix  = "+sya" if root_str in aset_roots or not _ends_in_consonant(gstr) else "+iṣya"
        return stem + pn.accep(suffix)

    def _build_perfect_system(self, root_str, class_num, strength, tense):
        """Perfect stem = reduplication prefix + (guna | shortened) root.

        Strong (sg active): guna grade.
        Weak  (all others): by priority:
          1. perfect_stem_overrides: fully suppletive stem (e.g. tan→ten)
          2. perfect_weak_guna_roots: guna grade (hu→ho, su→so), then ayadi
             resolves the diphthong before vowel-initial endings
             (juho+iva → ayadi → juhav+iva = juhaviva).
          3. Default: bare root with long vowel SHORTENED (ī→i, ū→u)
             so yan fires correctly before vowel-initial endings
             (cikri+ivahe → yan → cikriyivahe).
        A '+' boundary between prefix and root allows savarna (a+a→ā).
        """
        prefix = self.reduplicator.generate_prefix(root_str)
        if strength == "[STRONG]":
            # Strong: guna grade (or suppletive)
            if root_str in perfect_stem_overrides:
                # Suppletive: full stem already encoded — no prefix
                stem_str = perfect_stem_overrides[root_str]["strong"]
                return pn.accep(stem_str)
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

    def _build_passive(self, root_str, class_num=None):
        """Passive stem.

        Class-10 causative passive
        --------------------------
        base = _causative_base_string (Vṛddhi/Guna + ayadi applied in Python)
        stem = pn.accep(base) + pn.accep('+ya')

        Example: bhū → bhāv+ya = bhāvya  ✓
                 su  → sāv+ya  = sāvya   ✓
                 yuj → yoj+ya  = yojya   ✓
                 krī → krāp+ya = krāpya  ✓

        All other classes
        -----------------
        root + [PASSIVE] + +ya
        MorphologyEngine lengthens the root vowel before [PASSIVE].
        """
        if class_num == 10:
            base = self._causative_base_string(root_str)
            return pn.accep(base) + pn.accep("+ya")
        return pn.accep(root_str + "[PASSIVE]") + pn.accep("+ya")

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
        return pn.accep(root_str) + pn.accep("+a")

    def _build_class_7(self, root_str, strength):
        """Rudhādi — nasal infix inserted after the root vowel.

        A '+' is placed after the infix so nasal_assimilation (n → ñ before
        the following palatal: yunj → yuñj) fires correctly.
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
        """Tanādi — root + -o- (strong) or -u- (weak).

        MorphologyEngine's class8_suppletion converts kṛ → kur before +u.
        class8_u_drop then removes the +u before consonant-initial endings.
        """
        stem  = self._apply_guna(root_str, strength)
        affix = "+o" if strength == "[STRONG]" else "+u"
        return stem + pn.accep(affix)

    def _build_class_9(self, root_str, strength):
        affix = "+nā" if strength == "[STRONG]" else "+nī"
        return pn.accep(root_str) + pn.accep(affix)

    def _build_class_10(self, root_str, strength):
        """Curādi / Causative — (special | Guna | Vṛddhi of root) + -aya-.

        Priority:
          1. causative_stem_irregulars: hand-specified base (e.g. krī → krāp)
          2. guna_causative_roots:      Guna grade (e.g. yuj → yoj, cur → cor)
          3. default:                   Vṛddhi grade (e.g. bhū → bhāv)
        """
        if root_str in causative_stem_irregulars:
            base = causative_stem_irregulars[root_str]
            return pn.accep(base) + pn.accep("+aya")
        if root_str in guna_causative_roots:
            return self._apply_guna(root_str, "[STRONG]") + pn.accep("+aya")
        return self._apply_vriddhi(root_str) + pn.accep("+aya")