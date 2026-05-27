"""engine.py — DeclensionEngine: unified Sanskrit nominal declension via pynini FSTs.

All paradigm transducers from the stem-rules modules are compiled once into a
single contextualised master FST.  ``declense()`` annotates the input stem with
morph-syntactic tags, applies the master FST, and runs a post-processing
phonological pipeline (neuter-nasal insertion, nati, RUKI, permitted-finals
devoicing, visarga) to yield surface IAST strings.

Root cause of previous empty-results bug
-----------------------------------------
The paradigm FSTs accept only the *suffix* portion of the input string
(e.g. ``"a[A_STEM][Masc][Nom][Sg]"``).  A plain ``pn.accep(full_stem) @
master`` composition would therefore always be empty.  The fix is to
prepend a sigma-star *identity* transducer (over IAST stem characters) so
that any stem prefix is passed through unchanged before the paradigm FST
consumes the tag/suffix portion.

Usage::

    from engine import DeclensionEngine
    engine = DeclensionEngine()
    forms  = engine.declense("rāma", gender="m")
    # → {("Nom","Sg"): ["rāmaḥ"], ("Acc","Sg"): ["rāmam"], …}
"""

from __future__ import annotations

import os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pynini as pn
from grammar.grammar import SanskritPhonology

# ── Paradigm imports ──────────────────────────────────────────────────────────
from a_stem_rules import (
    masc_a_stem_paradigm,
    fem_a_stem_paradigm,
    neut_a_stem_paradigm,
)
from i_stem_rules import all_i_stems_paradigm
from u_stem_rules import all_u_stems_paradigm
from r_stems_rules import agt_paradigm, kin_paradigm, neut_r_paradigm
from an_in_stem_rules import nasal_stems_paradigm
from ant_mant_vant_stem_adj import ant_stem_paradigm
from as_us_is_stem_rules import t_stem_paradigm, s_stem_paradigm
from s_rules import sh_stem_master_paradigm
from dip_thong_rules import diphthong_stems_paradigm
from general_term_rules import cons_stem_paradigm
from van_stems_perfect_principles import vas_stem_paradigm
from t_stems import all_t_stems_paradigm as retroflex_t_paradigm
from special_cases import all_irregular_nouns_paradigm

# ── Constants ─────────────────────────────────────────────────────────────────

_GENDER_TAG: dict[str, str] = {
    "m": "[Masc]",
    "masc": "[Masc]",
    "f": "[Fem]",
    "fem": "[Fem]",
    "n": "[Neut]",
    "neut": "[Neut]",
}

CASES = ("Nom", "Acc", "Ins", "Dat", "Abl", "Gen", "Loc", "Voc")
NUMBERS = ("Sg", "Du", "Pl")

# IAST characters that appear in nominal stems (NOT tag brackets / uppercase).
# The identity transducer is built over this set so it passes stem prefixes
# through while stopping before the first tag character ('[').
_STEM_CHARS: frozenset[str] = frozenset(
    "abcdefghijklmnopqrstuvwxyz"
    "āīūṛṝḷḹ"  # macron / subscript-dot vowels
    "ṃḥṅñṇśṣ"  # anusvāra, visarga, nasals, sibilants
    "ṭḍ"  # retroflex stops (needed for ṭ-final stems)
)

# Stop consonants (single IAST char) that trigger neuter plural nasal insertion.
_NOM_STOPS = frozenset("tdkgpbcjṭḍ")

STEM_TYPE_AUTO = "auto"


# ── Engine ────────────────────────────────────────────────────────────────────


class DeclensionEngine:
    """Compile all declension paradigm FSTs and expose a ``declense()`` method.

    The constructor eagerly compiles the master contextual transducer
    (typically a few seconds on first run; subsequent calls are fast).

    Example
    -------
    >>> engine = DeclensionEngine()
    >>> engine.declense("deva", "m")[("Nom", "Sg")]
    ['devaḥ']
    >>> engine.declense("vāc", "f")[("Nom", "Sg")]
    ['vāk']
    >>> engine.declense("jagat", "n")[("Nom", "Pl")]
    ['jaganti']
    """

    def __init__(self) -> None:
        self._phono = SanskritPhonology()
        self._master = self._compile_master()

    # ── Compilation ────────────────────────────────────────────────────────────

    @staticmethod
    def _compile_master() -> pn.Fst:
        """Build a contextual master FST: (IAST-id)* + union(all paradigms).

        The left factor is a sigma-star identity transducer over IAST stem
        characters; it passes any stem prefix through unchanged.  The right
        factor is the union of all paradigm FSTs, which consume the
        morpho-syntactic tag suffix and output the inflectional ending.
        """
        # Identity transducer: each IAST stem char maps to itself.
        id_char = pn.union(*[pn.cross(c, c) for c in sorted(_STEM_CHARS)])
        id_star = pn.closure(id_char)  # Kleene star → any stem prefix

        raw = pn.union(
            masc_a_stem_paradigm,
            fem_a_stem_paradigm,
            neut_a_stem_paradigm,
            all_i_stems_paradigm,
            all_u_stems_paradigm,
            agt_paradigm,
            kin_paradigm,
            neut_r_paradigm,
            nasal_stems_paradigm,
            ant_stem_paradigm,
            t_stem_paradigm,       # dental-t consonant stems (as_us_is_stem_rules)
            s_stem_paradigm,       # as/is/us/yas stems
            sh_stem_master_paradigm,  # ś-final stems (e.g. etādṛś, diś)
            diphthong_stems_paradigm,
            cons_stem_paradigm,
            vas_stem_paradigm,
            retroflex_t_paradigm,  # ṭ-final stems (t_stems.py)
            all_irregular_nouns_paradigm,
        )
        return (id_star + raw).optimize()

    # ── Stem-type detection ────────────────────────────────────────────────────

    def _detect_stem_tag(self, stem: str, gender_tag: str) -> str:
        """Infer the FST stem-type tag from the stem's final phoneme(s)."""
        if gender_tag == "[Fem]" and stem.endswith("ā"):
            return "[Ā_STEM]"
        if stem.endswith("ī"):
            return "[I_bar_STEM]"
        if stem.endswith("ū"):
            return "[Ū_STEM]"
        if stem.endswith("vāṅs"):
            return "[VAS_STEM]"
        if stem.endswith("vant") or stem.endswith("vat"):
            return "[VANT_STEM]"
        if stem.endswith("mant") or stem.endswith("mat"):
            return "[MANT_STEM]"
        if stem.endswith("ant") or stem.endswith("at"):
            return "[ANT_STEM]"
        if stem.endswith("in"):
            return "[IN_STEM]"
        if stem.endswith("an"):
            return "[AN_STEM]"
        # YAS comparatives before generic AS check (e.g. śreyas, not pravayas)
        if stem.endswith("yas") and not stem.endswith("ayas"):
            return "[YAS_STEM]"
        if stem.endswith("as"):
            return "[AS_STEM]"
        if stem.endswith("is"):
            return "[IS_STEM]"
        if stem.endswith("us"):
            return "[US_STEM]"
        if stem.endswith("au"):
            return "[AU_STEM]"
        if stem.endswith("ai"):
            return "[AI_STEM]"
        if stem.endswith("e"):
            return "[E_STEM]"
        if stem.endswith("o"):
            return "[O_STEM]"
        if stem.endswith("ś"):
            return "[SH_STEM]"
        if stem.endswith("i"):
            return "[I_STEM]"
        if stem.endswith("u"):
            return "[U_STEM]"
        if stem.endswith("t"):
            return "[DENTAL_T_STEM]"
        if stem.endswith("ṭ"):
            return "[T_STEM]"  # retroflex-ṭ final stems
        if stem.endswith("ṛ") or stem.endswith("ṝ"):
            return "[R_STEM]"
        if stem.endswith("a") and gender_tag in ("[Masc]", "[Neut]"):
            return "[A_STEM]"
        return "[CONS_STEM]"

    # ── Post-processing ────────────────────────────────────────────────────────

    # ── Junction sandhi maps (internal stem-suffix assimilation at '#') ────────
    # Whitney §157–159: at internal (pada) junctions, the stem-final consonant
    # assimilates to the class of the following suffix-initial consonant.
    # Keyed longest-first so multi-char digraphs are tried before single chars.

    _JUNC_VOICE: dict[str, str] = {  # before voiced sounds (bh/b/g/d…)
        "kh": "g",
        "k": "g",
        "ch": "g",
        "c": "g",
        "jh": "g",
        "j": "g",  # palatals → velar g
        "ṭh": "ḍ",
        "ṭ": "ḍ",
        "ḍh": "ḍ",
        "th": "d",
        "t": "d",
        "dh": "d",
        "ph": "b",
        "p": "b",
        "bh": "b",
        "ś": "j",
        "h": "gh",
    }
    _JUNC_DEVOICE: dict[str, str] = {  # before voiceless sounds (s/k/t/p)
        "gh": "k",
        "g": "k",
        "jh": "k",
        "j": "k",
        "ch": "k",
        "c": "k",  # palatals → velar k
        "ḍh": "ṭ",
        "ḍ": "ṭ",
        "ṭh": "ṭ",
        "dh": "t",
        "d": "t",
        "th": "t",
        "bh": "p",
        "b": "p",
        "ph": "p",
        "ś": "k",
        "ṣ": "ṭ",
        "h": "k",
    }

    def _junction_sandhi(self, form: str) -> str:
        """Apply Whitney §157–159 consonant assimilation at every '#' junction.

        '#' is the pada (word-internal boundary) marker inserted by the
        consonant-stem paradigm FSTs.  Before voiced suffix-initials (``bh``
        etc.) the stem-final stop is voiced; before voiceless (``s`` etc.)
        it is devoiced so that RUKI can subsequently fire (k+s → kṣ).
        """
        while "#" in form:
            idx = form.index("#")
            before = form[:idx]
            after = form[idx + 1 :]  # suffix starting immediately after #

            if after.startswith("bh"):
                table = self._JUNC_VOICE
            elif (
                after[:1] in ("s", "ś", "ṣ")
                or after.startswith("k")
                or after.startswith("t")
            ):
                table = self._JUNC_DEVOICE
            else:
                # No specific assimilation rule; just remove the marker
                form = before + after
                continue

            # Try digraphs before single chars (longest-match)
            matched = False
            for src in sorted(table, key=len, reverse=True):
                if before.endswith(src):
                    before = before[: -len(src)] + table[src]
                    matched = True
                    break

            form = before + after  # # is removed implicitly (not re-inserted)

        return form

    # Permitted finals map — try longest suffix first (key order matters).

    _PERMITTED: dict[str, str] = {
        "gh": "k",
        "kh": "k",
        "g": "k",
        "jh": "k",
        "ch": "k",
        "j": "k",
        "c": "k",  # palatals → velar
        "ḍh": "ṭ",
        "ṭh": "ṭ",
        "ḍ": "ṭ",
        "dh": "t",
        "th": "t",
        "d": "t",
        "bh": "p",
        "ph": "p",
        "b": "p",
        "ś": "ṭ",
        "ṣ": "ṭ",
        "h": "k",
    }

    def _check_sigma(self, form: str, step: str) -> None:
        """Print characters not covered by sigma alphabet."""
        try:
            sigma_chars = set()

            for state in self._phono.sigma.states():
                for arc in self._phono.sigma.arcs(state):
                    if arc.ilabel != 0:
                        sigma_chars.add(
                            self._phono.sigma.input_symbols().find(arc.ilabel)
                        )

        except Exception:
            return

        missing = {c for c in form if c not in sigma_chars}

        if missing:
            print(
                f"[{step}] missing from sigma: "
                f"{[f'{c!r} U+{ord(c):04X}' for c in missing]}"
            )
            print(f"  form was: {form!r}")

    def _postprocess(
        self,
        raw: str,
        case: str,
        number: str,
        gender_tag: str,
    ) -> str:
        """Apply phonological post-processing to one raw output form.

        Pipeline (order is linguistically significant)
        -----------------------------------------------
        1. Strip ``#`` boundary markers (consonant-stem pada marker).
        2. Neuter plural nasal insertion (Whitney §207).
        3. S-stem oblique sandhi (as→o / is-us→r before bh).
        4. Nati (n → ṇ, long-distance retroflexion).
        5. Visarga FIRST — word-final s/r → ḥ  (must precede RUKI so that
           the word-final s is consumed before RUKI can turn it into ṣ).
        6. RUKI — internal s → ṣ after i/u/r/k/e/o.
        7. Permitted finals devoicing — word-final voiced/aspirated stops
           → voiceless unaspirated; palatals → velars (Whitney §141–150).
        """
        # 0. Internal junction sandhi at '#' (Whitney §157–159)
        #    Must precede step 1 so assimilation fires before the marker is lost.
        form = self._junction_sandhi(raw)

        # 1. Strip any remaining '#' pada boundary markers
        form = form.replace("#", "")

        # 2. Neuter plural nasal insertion (consonant stems):
        #    vowel + stop + 'i' → vowel + n + stop + 'i'  (e.g. jagati → jaganti)
        if (
            gender_tag == "[Neut]"
            and number == "Pl"
            and case in ("Nom", "Acc", "Voc")
            and len(form) >= 2
            and form.endswith("i")
        ):
            pre = form[:-1]
            if pre and pre[-1] in _NOM_STOPS:
                # Guard: skip if a nasal was already pre-inserted by the FST
                # (ṭ-stem neuter plural: pn.cross("ṭ[T_STEM]","nṭi") already has 'n')
                already_has_nasal = len(pre) >= 2 and pre[-2] in "mnṃṅñṇ"
                if not already_has_nasal:
                    form = pre[:-1] + "n" + pre[-1] + "i"

        # 3. S-stem oblique sandhi (FST is safe here — no [WORD_END] needed)
        try:
            form = (pn.accep(form) @ self._phono.apply_s_stem_sandhi).string()
        except Exception:
            pass

        # 4. Nati

        self._check_sigma(form, "pre-nati")
        form = self._phono.apply_nati(form)

        # 5. Visarga BEFORE RUKI — word-final s/r → ḥ
        if form.endswith(("s", "r")):
            form = form[:-1] + "ḥ"

        # 6. RUKI — internal s → ṣ (word-final s already gone via step 5)

        self._check_sigma(form, "pre-ruki")
        form = self._phono.apply_ruki(form)

        # 7. Permitted finals devoicing (Python string, longest-match first)
        if form.endswith("ḥ"):
            pass  # visarga is already the correct final
        else:
            for surd, target in self._PERMITTED.items():
                if form.endswith(surd):
                    form = form[: -len(surd)] + target
                    break

        return form

    # ── Core query ─────────────────────────────────────────────────────────────

    def _query(
        self,
        annotated: str,
        case: str,
        number: str,
        gender_tag: str,
        extra_annotated: str | None = None,
    ) -> list[str]:
        """Compose *annotated* (and optionally *extra_annotated*) through the master FST.

        *extra_annotated* is the tag-less form ``stem+gender+case+num`` used by
        ``special_cases.all_irregular_nouns_paradigm`` whose FSTs embed the
        full stem string directly rather than using a stem-type tag.
        """
        raw_forms: list[str] = []
        for ann in filter(None, [annotated, extra_annotated]):
            try:
                result_fst = (pn.accep(ann) @ self._master).optimize()
                raw_forms.extend(result_fst.paths().ostrings())
            except Exception:
                pass

        out: list[str] = []
        for raw in raw_forms:
            if raw is not None:
                surface = self._postprocess(raw, case, number, gender_tag)
                if surface:
                    out.append(surface)
        return sorted(set(out))

    # ── Public API ─────────────────────────────────────────────────────────────

    def declense(
        self,
        stem: str,
        gender: str,
        stem_type: str = STEM_TYPE_AUTO,
        r_subtype: str = "agt",
    ) -> dict[tuple[str, str], list[str]]:
        """Decline *stem* across all 24 case-number combinations.

        Parameters
        ----------
        stem : str
            IAST nominal stem (e.g. ``"rāma"``, ``"agni"``, ``"vāc"``).
        gender : str
            ``'m'``/``'masc'`` | ``'f'``/``'fem'`` | ``'n'``/``'neut'``.
        stem_type : str
            Explicit FST tag override (e.g. ``"[A_STEM]"``).  Pass
            ``STEM_TYPE_AUTO`` (default) to auto-detect from final phoneme(s).
        r_subtype : str
            For ṛ/ṝ-final stems only: ``'agt'`` (dātṛ), ``'kin'`` (pitṛ),
            or ``'neut'``.

        Returns
        -------
        dict
            ``(case, number) → list[str]`` of surface IAST forms.
            Empty lists mean no valid form was generated for that cell.

        Raises
        ------
        ValueError
            If *gender* is not a recognised specifier.
        """
        gender_tag = _GENDER_TAG.get(gender.lower(), "")
        if not gender_tag:
            raise ValueError(
                f"Unknown gender {gender!r}. Use 'm'/'f'/'n' (or 'masc'/'fem'/'neut')."
            )

        if stem_type in (STEM_TYPE_AUTO, None, ""):
            tag = self._detect_stem_tag(stem, gender_tag)
        else:
            tag = stem_type if stem_type.startswith("[") else f"[{stem_type}]"

        queries = []
        if stem.endswith("a") and gender_tag == "[Fem]" and stem_type in (STEM_TYPE_AUTO, None, ""):
            # Query both feminine ā-stem and feminine ī-stem
            queries.append((stem[:-1] + "ā", "[Ā_STEM]"))
            queries.append((stem[:-1] + "ī", "[I_bar_STEM]"))
        else:
            queries.append((stem, tag))

        results: dict[tuple[str, str], list[str]] = {}
        for case in CASES:
            for number in NUMBERS:
                results[(case, number)] = []

        for curr_stem, curr_tag in queries:
            # Normalize weak -mat/-vat/-at stems to strong -mant/-vant/-ant for the FST
            if curr_tag == "[VANT_STEM]" and curr_stem.endswith("vat"):
                curr_stem = curr_stem[:-3] + "vant"
            elif curr_tag == "[MANT_STEM]" and curr_stem.endswith("mat"):
                curr_stem = curr_stem[:-3] + "mant"
            elif curr_tag == "[ANT_STEM]" and curr_stem.endswith("at"):
                curr_stem = curr_stem[:-2] + "ant"

            curr_gender_tag = gender_tag
            # ṛ-stems use subtype pseudo-gender tags instead of Masc/Fem/Neut
            if curr_tag == "[R_STEM]":
                curr_gender_tag = {"agt": "[Agt]", "kin": "[Kin]", "neut": "[Neut]"}.get(
                    r_subtype, "[Agt]"
                )

            for case in CASES:
                for number in NUMBERS:
                    annotated = f"{curr_stem}{curr_tag}{curr_gender_tag}[{case}][{number}]"
                    # Tag-less form for special_cases paradigms (no stem-type tag)
                    special_ann = f"{curr_stem}{curr_gender_tag}[{case}][{number}]"
                    res = self._query(
                        annotated,
                        case,
                        number,
                        curr_gender_tag,
                        extra_annotated=special_ann,
                    )
                    results[(case, number)].extend(res)

        # De-duplicate and sort
        for key in results:
            results[key] = sorted(set(results[key]))

        return results
