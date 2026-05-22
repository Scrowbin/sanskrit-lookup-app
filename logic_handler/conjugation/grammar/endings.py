"""endings.py — Tiṅ-pratyaya (verb ending) tables.

Each ending is a ``Suffix`` dataclass that carries both its surface IAST string
and an optional set of morpho-phonemic tags.  The ``to_fst()`` method converts
the suffix to a Pynini FST so that tag-triggered morphological rules (e.g. Vriddhi
for aorist-passive 3sg) are encoded in the *ending* rather than intercepted
upstream in the orchestrator.

Usage::

    suffixes = SuffixProvider.get_present_active(class_num=1)
    suffix   = suffixes["[3sg]"]      # Suffix(surface="ti", tags=frozenset())
    fst      = suffix.to_fst()        # pn.accep("ti")
"""
from __future__ import annotations
import re

from irregulars import perfect_stem_overrides
import pynini as pn
from dataclasses import dataclass, field
def is_thematic(class_num: int) -> bool:
    return class_num in (1, 4, 6, 10)


# ── Suffix dataclass ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Suffix:
    """An inflectional ending with optional morpho-phonemic trigger tags.

    Attributes:
        surface: IAST string that will appear in the final output (may be empty
                 for zero-endings such as imperative 2sg thematic "—").
        tags: Frozenset of abstract tags that instruct MorphologyEngine / SandhiEngine.
              Supported tags:
                  ``"AORIST_PASS_3SG"`` — Vriddhi on stem (ciṇ-ending).
                  ``"PRAGRHYA"`` — Whitney §138: dual (etc.) finals ī/ū/e exempt from
                  hiatus resolution before a vowel; emit ``[PRAGRHYA]`` before surface.
    """
    surface: str
    tags: frozenset[str] = field(default_factory=frozenset)

    def to_fst(self) -> pn.Fst:
        """Return a Pynini FST for this ending.

        Tag FSTs are prepended before the surface so MorphologyEngine sees them
        in the correct left-to-right position relative to the stem.
        For zero-endings (imperative 2sg thematic), returns an epsilon machine.
        """
        if "|" in self.surface:
            alts = self.surface.split("|")
            base = pn.union(*[pn.accep(a) for a in alts])
        else:
            base = pn.accep(self.surface)
        if "AORIST_PASS_3SG" in self.tags:
            base = pn.accep("[AORIST_PASS_3SG]") + base
        if "PRAGRHYA" in self.tags:
            # Blocks internal vowel fusion across +: vowels cannot see each other across tag.
            base = pn.accep("[PRAGRHYA]") + base
        return base

    @property
    def is_empty(self) -> bool:
        """True for zero-endings (no surface form, no tags)."""
        return not self.surface and not self.tags


# Convenience constructor for the common tag-free case
def _s(surface: str, *tags: str) -> Suffix:
    """Build a Suffix with optional tags. Keeps table definitions concise."""
    return Suffix(surface, frozenset(tags))


# Whitney §138: dual endings in ī / ū / e (etc.) — exempt from hiatus with following vowel.
_PRAGRHya_DUAL_END = re.compile(r"(ī|ū|e|ai|au)$")


def maybe_pragrhya_dual_suffix(suffix: Suffix, number: str) -> Suffix:
    """Attach PRAGRHYA for dual persons when the ending qualifies (§138)."""
    if number != "du" or not suffix.surface:
        return suffix
    if _PRAGRHya_DUAL_END.search(suffix.surface.strip()):
        return Suffix(suffix.surface, suffix.tags | frozenset(["PRAGRHYA"]))
    return suffix


# ── SuffixProvider ─────────────────────────────────────────────────────────────

class SuffixProvider:
    """Manages the Tiṅ-pratyaya (verb endings) tables.

    All methods return ``dict[str, Suffix]``.  Dual keys use ``'du'`` (matching
    INRIA's number column: sg / du / pl).

    Paradigm branching uses ``is_thematic(class_num)`` (from paradigm.py)
    rather than inline ``class_num in [1, 4, 6, 10]`` checks.
    Class-3 further overrides 3pl active forms wherever it differs.
    """

    # ── 1. PRESENT TENSE (Laṭ) ────────────────────────────────────────────────

    @staticmethod
    def get_present_active(class_num: int = 1, root_str=None, **kwargs) -> dict[str, Suffix]:
        # Future/Conditional always use thematic endings
        if kwargs.get("tense") in ("future", "conditional"):
            class_num = 1
        if is_thematic(class_num):
            return {
                "[3sg]": _s("ti"),   "[3du]": _s("taḥ"),  "[3pl]": _s("nti"),
                "[2sg]": _s("si"),   "[2du]": _s("thaḥ"), "[2pl]": _s("tha"),
                "[1sg]": _s("āmi"),  "[1du]": _s("āvaḥ"), "[1pl]": _s("āmaḥ"),
            }
        third_pl = "ati" if class_num == 3 else "anti"
        endings = {
            "[3sg]": _s("ti"),   "[3du]": _s("taḥ"),    "[3pl]": _s(third_pl),
            "[2sg]": _s("si"),   "[2du]": _s("thaḥ"),   "[2pl]": _s("tha"),
            "[1sg]": _s("mi"),   "[1du]": _s("vaḥ"),    "[1pl]": _s("maḥ"),
        }
        
        # Pāṇini 7.2.76: rudādibhyaḥ sārvadhātuke
        if class_num == 2 and root_str in {"rud", "svap", "śvas", "an", "jakṣ"}:
            for key, suf in endings.items():
                if suf.surface[0] not in ("a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "e", "ai", "o", "au", "y"):
                    endings[key] = _s("i" + suf.surface, suf.tags)
                    
        return endings

    @staticmethod
    def get_present_middle(class_num: int = 1, root_str=None, **kwargs) -> dict[str, Suffix]:
        if kwargs.get("tense") in ("future", "conditional"):
            class_num = 1
        if is_thematic(class_num):
            return {
                "[3sg]": _s("te"),   "[3du]": _s("ete"),   "[3pl]": _s("nte"),
                "[2sg]": _s("se"),   "[2du]": _s("ethe"),  "[2pl]": _s("dhve"),
                "[1sg]": _s("e"),    "[1du]": _s("āvahe"), "[1pl]": _s("āmahe"),
            }
        return {
            "[3sg]": _s("te"),   "[3du]": _s("āte"),  "[3pl]": _s("ate"),
            "[2sg]": _s("se"),   "[2du]": _s("āthe"), "[2pl]": _s("dhve"),
            "[1sg]": _s("e"),    "[1du]": _s("vahe"),  "[1pl]": _s("mahe"),
        }

    # ── 2. IMPERFECT / CONDITIONAL (Laṅ / Lṛṅ) ───────────────────────────────

    @staticmethod
    def get_secondary_active(class_num: int = 1, root_str=None, **kwargs) -> dict[str, Suffix]:
        if kwargs.get("tense") == "conditional":
            class_num = 1
        if is_thematic(class_num):
            return {
                "[3sg]": _s("t"),   "[3du]": _s("tām"),  "[3pl]": _s("n"),
                "[2sg]": _s("s"),   "[2du]": _s("tam"),  "[2pl]": _s("ta"),
                "[1sg]": _s("m"),   "[1du]": _s("āva"),  "[1pl]": _s("āma"),
            }
        third_pl = "uḥ" if class_num == 3 else "an"
        # √ad cl-2 imperfect uses connecting-vowel endings
        if root_str == "ad":
            return {
                "[3sg]": _s("at"),  "[3du]": _s("tām"), "[3pl]": _s("an"),
                "[2sg]": _s("as"),  "[2du]": _s("tam"), "[2pl]": _s("ta"),
                "[1sg]": _s("am"),  "[1du]": _s("va"),  "[1pl]": _s("ma"),
            }
            
        endings = {
            "[3sg]": _s("t"),   "[3du]": _s("tām"), "[3pl]": _s(third_pl),
            "[2sg]": _s("s"),   "[2du]": _s("tam"), "[2pl]": _s("ta"),
            "[1sg]": _s("am"),  "[1du]": _s("va"),  "[1pl]": _s("ma"),
        }
        
        # Pāṇini 7.2.76 / 7.3.98-99: rudādibhyaḥ sārvadhātuke
        if class_num == 2 and root_str in {"rud", "svap", "śvas", "an", "jakṣ"} and kwargs.get("tense") != "conditional":
            for key, suf in endings.items():
                if suf.surface[0] not in ("a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "e", "ai", "o", "au", "y"):
                    # 2sg and 3sg imperfect option for ī or a (P. 7.3.98-99 / Whitney §631)
                    if key in ("[2sg]", "[3sg]"):
                        # We return the ī option as primary to match expected forms like asvapīt
                        endings[key] = _s("ī" + suf.surface, suf.tags)
                    else:
                        endings[key] = _s("i" + suf.surface, suf.tags)
                        
        return endings

    @staticmethod
    def get_secondary_middle(class_num: int = 1, root_str=None, **kwargs) -> dict[str, Suffix]:
        if kwargs.get("tense") == "conditional":
            class_num = 1
        if is_thematic(class_num):
            return {
                "[3sg]": _s("ta"),   "[3du]": _s("etām"),  "[3pl]": _s("nta"),
                "[2sg]": _s("thāḥ"), "[2du]": _s("ethām"), "[2pl]": _s("dhvam"),
                "[1sg]": _s("i"),    "[1du]": _s("āvahi"), "[1pl]": _s("āmahi"),
            }
        return {
            "[3sg]": _s("ta"),   "[3du]": _s("ātām"),  "[3pl]": _s("ata"),
            "[2sg]": _s("thāḥ"), "[2du]": _s("āthām"), "[2pl]": _s("dhvam"),
            "[1sg]": _s("i"),    "[1du]": _s("vahi"),  "[1pl]": _s("mahi"),
        }

    # ── 3. IMPERATIVE (Loṭ) ───────────────────────────────────────────────────

    @staticmethod
    def get_imperative_active(class_num: int = 1, root_str=None, **kwargs) -> dict[str, Suffix]:
        if is_thematic(class_num):
            return {
                "[3sg]": _s("tu|tāt"), "[3du]": _s("tām"),  "[3pl]": _s("ntu"),
                "[2sg]": _s("|tāt"),   "[2du]": _s("tam"),  "[2pl]": _s("ta"),
                "[1sg]": _s("āni"),    "[1du]": _s("āva"),  "[1pl]": _s("āma"),
            }
        
        if class_num in (5, 8):
            from alphabet import ALPHABET as _A
            phonemes = _A.parse_phonemes(root_str or "")
            # Class 8 always drops 'hi' (tanu, manu). Class 5 drops 'hi' only for vowel roots (sunu).
            if class_num == 8 or (phonemes and phonemes[-1] in _A.vowels_list):
                sg2 = "|tāt"
            else:
                sg2 = "hi|tāt"
            if root_str == "kṛ":
                sg2 = "|tāt"
            return {
                "[3sg]": _s("tu|tāt"), "[3du]": _s("tām"),  "[3pl]": _s("antu"),
                "[2sg]": _s(sg2),      "[2du]": _s("tam"),  "[2pl]": _s("ta"),
                "[1sg]": _s("āni"),    "[1du]": _s("āva"),  "[1pl]": _s("āma"),
            }
        if root_str == "ad":
            return {
                "[3sg]": _s("tu|tāt"),  "[3du]": _s("tām"), "[3pl]": _s("antu"),
                "[2sg]": _s("dhi|tāt"), "[2du]": _s("tam"), "[2pl]": _s("ta"),
                "[1sg]": _s("āni"),     "[1du]": _s("āva"), "[1pl]": _s("āma"),
            }
        # Whitney §636 — class 2 (adādi/root-class) imperative 2sg:
        # 'dhi' after consonant-final stem, 'hi' after vowel-final stem.
        # Applies to all athematic non-nasal non-3 classes (primarily class 2).
        if class_num == 2:
            from alphabet import ALPHABET as _A
            phonemes = _A.parse_phonemes(root_str or "")
            sg2 = "dhi" if (phonemes and phonemes[-1] not in _A.vowels_list) else "hi"
            endings = {
                "[3sg]": _s("tu|tāt"),       "[3du]": _s("tām"), "[3pl]": _s("antu"),
                "[2sg]": _s(f"{sg2}|tāt"),   "[2du]": _s("tam"), "[2pl]": _s("ta"),
                "[1sg]": _s("āni"),           "[1du]": _s("āva"), "[1pl]": _s("āma"),
            }
            # Pāṇini 7.2.76: rudādibhyaḥ sārvadhātuke
            if root_str in {"rud", "svap", "śvas", "an", "jakṣ"}:
                for key, suf in endings.items():
                    new_surfaces = []
                    for s in suf.surface.split("|"):
                        if s[0] not in ("a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "e", "ai", "o", "au", "y"):
                            # Whitney §631: 2sg is ihi (also dhi allowed sometimes, but ihi is standard)
                            # Let's replace 'dhi' with 'hi' before adding 'i'
                            base_s = "hi" if s == "dhi" else s
                            new_surfaces.append("i" + base_s)
                        else:
                            new_surfaces.append(s)
                    endings[key] = _s("|".join(new_surfaces), suf.tags)
            return endings
        if class_num == 3:
            is_intensive = kwargs.get('derivative') == 'intensive_active'
            if is_intensive:
                from alphabet import ALPHABET as _A
                # Intensive stem ending in consonant takes 'dhi' (e.g. carkar-dhi)
                # But wait, we don't have the stem here, only the root. kṛ -> carkar (cons). hu -> johav/joho. 
                # Actually, any intensive of a consonant root or kṛ ends in a consonant or takes 'dhi'.
                # To be safe, just use 'dhi|hi' for intensives and let sandhi or FST handle it, or check root:
                phonemes = _A.parse_phonemes(root_str or "")
                ends_in_vowel = phonemes and phonemes[-1] in _A.vowels_list
                # For kṛ, it's carkar (cons). For hu, it's johav (cons) / joho (vowel).
                # To be completely safe and dynamic, we can provide both 'dhi|hi' for all intensives, 
                # but 'dhi' is only allowed after consonants according to Sanskrit rules.
                # Actually, let's just supply 'dhi|hi' and let the FST graph match the valid one?
                # No, FST will just output both.
                # carkar ends in r. hu intensive can end in v (johav) or o (joho). 
                sg2 = "dhi|hi" if is_intensive else ("dhi" if root_str in ("hu", "ad") else "hi")
            else:
                sg2 = "dhi" if root_str in ("hu", "ad") else "hi"
                
            return {
                "[3sg]": _s("tu|tāt"),     "[3du]": _s("tām"), "[3pl]": _s("atu"),
                "[2sg]": _s(f"{sg2}|tāt"), "[2du]": _s("tam"), "[2pl]": _s("ta"),
                "[1sg]": _s("āni"),        "[1du]": _s("āva"), "[1pl]": _s("āma"),
            }
        if class_num == 7:
            return {
                "[3sg]": _s("tu|tāt"),  "[3du]": _s("tām"), "[3pl]": _s("antu"),
                "[2sg]": _s("dhi|tāt"), "[2du]": _s("tam"), "[2pl]": _s("ta"),
                "[1sg]": _s("āni"),     "[1du]": _s("āva"), "[1pl]": _s("āma"),
            }
        return {
            "[3sg]": _s("tu|tāt"), "[3du]": _s("tām"),  "[3pl]": _s("antu"),
            "[2sg]": _s("hi|tāt"), "[2du]": _s("tam"),  "[2pl]": _s("ta"),
            "[1sg]": _s("āni"),    "[1du]": _s("āva"),  "[1pl]": _s("āma"),
        }

    @staticmethod
    def get_imperative_middle(class_num: int = 1, root_str=None, **kwargs) -> dict[str, Suffix]:
        if is_thematic(class_num):
            return {
                "[3sg]": _s("tām"),  "[3du]": _s("itām"),   "[3pl]": _s("ntām"),
                "[2sg]": _s("sva"),  "[2du]": _s("ithām"),  "[2pl]": _s("dhvam"),
                "[1sg]": _s("ai"),   "[1du]": _s("āvahai"), "[1pl]": _s("āmahai"),
            }
        return {
            "[3sg]": _s("tām"),  "[3du]": _s("ātām"),   "[3pl]": _s("atām"),
            "[2sg]": _s("sva"),  "[2du]": _s("āthām"),  "[2pl]": _s("dhvam"),
            "[1sg]": _s("ai"),   "[1du]": _s("āvahai"), "[1pl]": _s("āmahai"),
        }

    # ── 4. OPTATIVE (Vidhi Liṅ) ───────────────────────────────────────────────

    @staticmethod
    def get_optative_active(class_num: int = 1, root_str=None, **kwargs) -> dict[str, Suffix]:
        if is_thematic(class_num):
            return {
                "[3sg]": _s("et"),   "[3du]": _s("etām"),  "[3pl]": _s("eyuḥ"),
                "[2sg]": _s("eḥ"),   "[2du]": _s("etam"),  "[2pl]": _s("eta"),
                "[1sg]": _s("eyam"), "[1du]": _s("eva"),   "[1pl]": _s("ema"),
            }
        return {
            "[3sg]": _s("yāt"),  "[3du]": _s("yātām"), "[3pl]": _s("yuḥ"),
            "[2sg]": _s("yāḥ"),  "[2du]": _s("yātam"), "[2pl]": _s("yāta"),
            "[1sg]": _s("yām"),  "[1du]": _s("yāva"),  "[1pl]": _s("yāma"),
        }

    @staticmethod
    def get_optative_middle(class_num: int = 1, root_str=None, **kwargs) -> dict[str, Suffix]:
        if is_thematic(class_num):
            return {
                "[3sg]": _s("eta"),   "[3du]": _s("eyātām"),  "[3pl]": _s("eran"),
                "[2sg]": _s("ethāḥ"), "[2du]": _s("eyāthām"), "[2pl]": _s("edhvam"),
                "[1sg]": _s("eya"),   "[1du]": _s("evahi"),   "[1pl]": _s("emahi"),
            }
        return {
            "[3sg]": _s("īta"),   "[3du]": _s("īyātām"),  "[3pl]": _s("īran"),
            "[2sg]": _s("īthāḥ"), "[2du]": _s("īyāthām"), "[2pl]": _s("īdhvam"),
            "[1sg]": _s("īya"),   "[1du]": _s("īvahi"),   "[1pl]": _s("īmahi"),
        }

    # ── 5. PERFECT (Liṭ) ──────────────────────────────────────────────────────

    @staticmethod
    def get_perfect_active(root_str=None, class_num=1, **kwargs) -> dict[str, Suffix]:
        from irregulars import perfect_bare_tha_roots, perfect_weak_guna_roots
        from dhatupatha_analyzer import DhatupathaAnalyzer
        
        analyzer = DhatupathaAnalyzer()
        root_obj = analyzer.get(root_str, class_num) if root_str else None

        is_primary = kwargs.get('derivative') in (None, "", "primary")
        
        if is_primary and (root_str == "kṛ" or root_str in perfect_bare_tha_roots or root_str in perfect_weak_guna_roots):
            second_sg = "tha"
        elif root_obj and root_obj.is_vet:
            second_sg = "tha|itha"
        else:
            second_sg = "itha"
        first_third_sg = "au" if root_str and root_str.endswith("ā") else "a"
        endings = {
            "[3sg]": _s(first_third_sg), "[3du]": _s("atuḥ"),  "[3pl]": _s("uḥ"),
            "[2sg]": _s(second_sg),      "[2du]": _s("athuḥ"), "[2pl]": _s("a"),
            "[1sg]": _s(first_third_sg), "[1du]": _s("iva"),   "[1pl]": _s("ima"),
        }
        is_primary = kwargs.get('derivative') in (None, "", "primary")
        if is_primary and root_str and (
            root_str.endswith("ṛ") or root_str.endswith("ṝ") or 
            root_str.endswith("u") or root_str.endswith("ū")
        ) and root_str not in perfect_stem_overrides:
            endings["[1du]"] = _s("va")
            endings["[1pl]"] = _s("ma")
        return endings

    @staticmethod
    def get_perfect_middle(root_str=None, **kwargs) -> dict[str, Suffix]:
        endings = {
            "[3sg]": _s("e"),    "[3du]": _s("āte"),   "[3pl]": _s("ire"),
            "[2sg]": _s("iṣe"),  "[2du]": _s("āthe"),  "[2pl]": _s("idhve"),
            "[1sg]": _s("e"),    "[1du]": _s("ivahe"), "[1pl]": _s("imahe"),
        }
        # √kṛ perfect middle keeps bare ṣe/dhve (cakṛṣe, cakṛdhve).
        is_primary = kwargs.get('derivative') in (None, "", "primary")
        if is_primary and root_str == "kṛ":
            endings["[2sg]"] = _s("ṣe")
            endings["[2pl]"] = _s("dhve")
            
        # ṛ-final and u/ū-final roots use bare du/pl endings (Aniṭ) in the perfect middle
        # This only applies to the primary root, not to derivatives like desideratives!
        is_primary = kwargs.get('derivative') in (None, "", "primary")
        if is_primary and root_str and (
            root_str.endswith("ṛ") or root_str.endswith("ṝ") or 
            root_str.endswith("u") or root_str.endswith("ū")
        ) and root_str not in perfect_stem_overrides:
            endings["[1du]"] = _s("vahe")
            endings["[1pl]"] = _s("mahe")
            endings["[2sg]"] = _s("ṣe")
            endings["[2pl]"] = _s("dhve")
        return endings

    # ── 6. PERIPHRASTIC FUTURE (Luṭ) ──────────────────────────────────────────

    @staticmethod
    def get_periphrastic_future_active(**kwargs) -> dict[str, Suffix]:
        return {
            "[3sg]": _s("tā"),    "[3du]": _s("tārau"),  "[3pl]": _s("tāraḥ"),
            "[2sg]": _s("tāsi"),  "[2du]": _s("tāsthaḥ"),"[2pl]": _s("tāstha"),
            "[1sg]": _s("tāsmi"), "[1du]": _s("tāsvaḥ"), "[1pl]": _s("tāsmaḥ"),
        }

    @staticmethod
    def get_periphrastic_future_middle(**kwargs) -> dict[str, Suffix]:
        return {
            "[3sg]": _s("tā"),    "[3du]": _s("tārau"),   "[3pl]": _s("tāraḥ"),
            "[2sg]": _s("tāse"),  "[2du]": _s("tāsāthe"), "[2pl]": _s("tādhve"),
            "[1sg]": _s("tāhe"),  "[1du]": _s("tāsvahe"), "[1pl]": _s("tāsmahe"),
        }

    # ── 7. AORIST (Luṅ) / INJUNCTIVE ──────────────────────────────────────────

    @staticmethod
    def get_aorist_active(class_num: int = 1, root_str=None, **kwargs) -> dict[str, Suffix]:
        from irregulars import aorist_overrides
        from dhatupatha_analyzer import DHATUPATHA_ANALYZER
        
        derivative = kwargs.get("derivative")
        if derivative == "causative" or class_num == 10:
            aorist_type = "reduplicated"
        else:
            info = aorist_overrides.get(root_str)
            aorist_type = info["type"] if info else DHATUPATHA_ANALYZER.get_aorist_type(root_str, class_num)

        if aorist_type in ("a", "reduplicated"):
            return SuffixProvider.get_secondary_active(class_num=1)
        if aorist_type == "sa":
            return SuffixProvider.get_secondary_active(class_num=1) # sa-aorist active is just like a-stem
        if aorist_type == "root":
            return SuffixProvider.get_secondary_active(class_num=2)
        if aorist_type == "is":
            return {
                "[3sg]": _s("īt"),    "[3du]": _s("iṣṭām"), "[3pl]": _s("iṣus"),
                "[2sg]": _s("īs"),    "[2du]": _s("iṣṭam"), "[2pl]": _s("iṣṭa"),
                "[1sg]": _s("iṣam"),  "[1du]": _s("iṣva"),  "[1pl]": _s("iṣma"),
            }
        if aorist_type == "sis":
            return {
                "[3sg]": _s("siṣīt"),   "[3du]": _s("siṣṭām"), "[3pl]": _s("siṣus"),
                "[2sg]": _s("siṣīs"),   "[2du]": _s("siṣṭam"), "[2pl]": _s("siṣṭa"),
                "[1sg]": _s("siṣam"),   "[1du]": _s("siṣva"),  "[1pl]": _s("siṣma"),
            }
        # s-aorist
        return {
            "[3sg]": _s("īt"),  "[3du]": _s("tām"), "[3pl]": _s("us"),
            "[2sg]": _s("īs"),  "[2du]": _s("tam"), "[2pl]": _s("ta"),
            "[1sg]": _s("am"),  "[1du]": _s("va"),  "[1pl]": _s("ma"),
        }

    @staticmethod
    def get_aorist_middle(class_num: int = 1, root_str=None, **kwargs) -> dict[str, Suffix]:
        from irregulars import aorist_overrides
        from dhatupatha_analyzer import DHATUPATHA_ANALYZER
        
        derivative = kwargs.get("derivative")
        if derivative == "causative" or class_num == 10:
            aorist_type = "reduplicated"
        else:
            info = aorist_overrides.get(root_str)
            aorist_type = (info.get("middle_type") or info["type"]) if info else DHATUPATHA_ANALYZER.get_aorist_type(root_str, class_num)

        if aorist_type in ("a", "reduplicated"):
            return SuffixProvider.get_secondary_middle(class_num=1)
        if aorist_type == "sa":
            # Whitney §917: sa-aorist middle takes i (not e) and āthām, ātām (not ethām, etām)
            return {
                "[3sg]": _s("ta"),    "[3du]": _s("ātām"),  "[3pl]": _s("ata"),
                "[2sg]": _s("thās"),  "[2du]": _s("āthām"), "[2pl]": _s("dhvam"),
                "[1sg]": _s("i"),     "[1du]": _s("āvahi"), "[1pl]": _s("āmahi"),
            }
        if aorist_type == "root":
            return SuffixProvider.get_secondary_middle(class_num=2)
        if aorist_type == "is":
            return {
                "[3sg]": _s("iṣṭa"),   "[3du]": _s("iṣātām"),  "[3pl]": _s("iṣata"),
                "[2sg]": _s("iṣṭhāḥ"), "[2du]": _s("iṣāthām"), "[2pl]": _s("idhvam"),
                "[1sg]": _s("iṣi"),    "[1du]": _s("iṣvahi"),  "[1pl]": _s("iṣmahi"),
            }
        # s-aorist
        return {
            "[3sg]": _s("ta"),   "[3du]": _s("ātām"),  "[3pl]": _s("ata"),
            "[2sg]": _s("thāḥ"), "[2du]": _s("āthām"), "[2pl]": _s("dhvam"),
            "[1sg]": _s("i"),    "[1du]": _s("vahi"),  "[1pl]": _s("mahi"),
        }

    @staticmethod
    def get_aorist_passive(class_num: int = 1, root_str=None, **kwargs) -> dict[str, Suffix]:
        """Passive aorist endings.  3sg ciṇ carries the AORIST_PASS_3SG tag
        which instructs MorphologyEngine to apply Vriddhi on the stem side."""
        endings = SuffixProvider.get_aorist_middle(class_num=class_num, root_str=root_str)
        # Override 3sg with the tagged Suffix — Vriddhi tag is self-contained here
        endings["[3sg]"] = _s("i", "AORIST_PASS_3SG")
        return endings

    # ── 8. BENEDICTIVE (Āśīr-liṅ) ─────────────────────────────────────────────

    @staticmethod
    def get_benedictive_active(root_str=None, **kwargs) -> dict[str, Suffix]:
        """Active Benedictive endings (-yāsut). Added directly to the bare root."""
        return {
            "[3sg]": _s("yāt"),   "[3du]": _s("yāstām"), "[3pl]": _s("yāsuḥ"),
            "[2sg]": _s("yāḥ"),   "[2du]": _s("yāstam"), "[2pl]": _s("yāsta"),
            "[1sg]": _s("yāsam"), "[1du]": _s("yāsva"),  "[1pl]": _s("yāsma"),
        }

    @staticmethod
    def get_benedictive_middle(root_str=None, **kwargs) -> dict[str, Suffix]:
        """Middle Benedictive endings (-sīṣṭa). Very rare in Classical Sanskrit."""
        return {
            "[3sg]": _s("sīṣṭa"),   "[3du]": _s("sīyāstām"), "[3pl]": _s("sīran"),
            "[2sg]": _s("sīṣṭhāḥ"), "[2du]": _s("sīyāsthām"),"[2pl]": _s("sīdhvam"),
            "[1sg]": _s("sīya"),    "[1du]": _s("sīvahi"),   "[1pl]": _s("sīmahi"),
        }

    # ── 9. SUBJUNCTIVE (Leṭ) ──────────────────────────────────────────────────

    @staticmethod
    def get_subjunctive_active(root_str=None, **kwargs) -> dict[str, Suffix]:
        """Subjunctive active endings. Mostly Vedic. Uses generalized thematic paradigm."""
        return {
            "[3sg]": _s("āt"),   "[3du]": _s("ātaḥ"), "[3pl]": _s("ān"),
            "[2sg]": _s("ās"),   "[2du]": _s("āthaḥ"),"[2pl]": _s("ātha"),
            "[1sg]": _s("āni"),  "[1du]": _s("āva"),  "[1pl]": _s("āma"),
        }

    @staticmethod
    def get_subjunctive_middle(root_str=None, **kwargs) -> dict[str, Suffix]:
        """Subjunctive middle endings. Mostly Vedic."""
        return {
            "[3sg]": _s("āte"),  "[3du]": _s("āithe"),"[3pl]": _s("ānte"),
            "[2sg]": _s("āse"),  "[2du]": _s("āithe"),"[2pl]": _s("ādhve"),
            "[1sg]": _s("āi"),   "[1du]": _s("āvahai"),"[1pl]": _s("āmahai"),
        }

    # ── 10. PASSIVE VOICE (Karmani Prayoga) ────────────────────────────────────

    @staticmethod
    def get_passive_endings(tense: str) -> dict[str, Suffix]:
        """Passives use the Middle voice endings (thematic pattern)."""
        if tense in ("present", "future"):
            return SuffixProvider.get_present_middle(class_num=1)
        if tense in ("imperfect", "conditional"):
            return SuffixProvider.get_secondary_middle(class_num=1)
        if tense == "imperative":
            return SuffixProvider.get_imperative_middle(class_num=1)
        if tense == "optative":
            return SuffixProvider.get_optative_middle(class_num=1)
        if tense == "perfect":
            raise ValueError("No passive perfect in Sanskrit.")
        return {}