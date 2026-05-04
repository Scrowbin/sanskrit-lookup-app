"""conjugate.py — Sanskrit conjugation pipeline orchestrator.

This module is intentionally kept as a *dumb pipe*: it receives raw arguments,
delegates all morphological decision-making to ``MorphologicalFeatureResolver``,
assembles FSTs in the canonical order, and returns the final IAST string.

Pipeline
--------
    root string
        │
        ▼ MorphologicalFeatureResolver.resolve() → ResolvedFeatures
        │
        ▼ StemBuilder.build()       – class/tense-specific stem FST
        │
        ▼ augment prefix (a+)       – imperfect / conditional / aorist
        │
        ▼ Suffix.to_fst()           – endings table lookup; FST carries tags
        │
        ▼ MorphologyEngine.apply_all() – passive lengthening, class-4/8 etc.
        │
        ▼ SandhiEngine.apply_all()  – vowel → consonant → long-distance → clean
        │
        ▼ optimised IAST string
"""
from __future__ import annotations

import pynini as pn
from functools import lru_cache

from alphabet import ALPHABET
from vowel_strength import VowelStrengthEngine
from sandhi import SandhiEngine
from stem_rules import StemBuilder
from endings import SuffixProvider, Suffix
from morphology import MorphologyEngine
from feature_resolver import MorphologicalFeatureResolver
from inria_lookup import INRIA_LOOKUP


class SanskritConjugator:
    """Orchestrates the conjugation pipeline from root to inflected form.

    Caching
    -------
    Stem FSTs are expensive to build.  ``_stem_cache`` stores them keyed on
    ``(root_str, class_num, strength, tense, derivative, person, number)``
    so repeated calls reuse the compiled FST.

    ``conjugate()`` is additionally wrapped with ``lru_cache`` so the final
    IAST string is returned immediately for warm calls without any FST work.
    """

    def __init__(self):
        self.strength_engine = VowelStrengthEngine()
        self.sandhi     = SandhiEngine()
        self.morphology = MorphologyEngine()
        self.stems      = StemBuilder(self.strength_engine)
        self.resolver   = MorphologicalFeatureResolver()

        # FST stem cache: (root, class, strength, tense, derivative, person, number) → FST
        self._stem_cache: dict = {}

        # ── Ending provider dispatch ──────────────────────────────────────────
        self._ending_dispatch: dict = {
            ("present",    "active"):  SuffixProvider.get_present_active,
            ("present",    "middle"):  SuffixProvider.get_present_middle,
            ("imperfect",  "active"):  SuffixProvider.get_secondary_active,
            ("imperfect",  "middle"):  SuffixProvider.get_secondary_middle,
            ("imperative", "active"):  SuffixProvider.get_imperative_active,
            ("imperative", "middle"):  SuffixProvider.get_imperative_middle,
            ("optative",   "active"):  SuffixProvider.get_optative_active,
            ("optative",   "middle"):  SuffixProvider.get_optative_middle,
            # Future / Conditional reuse present / secondary paradigms
            ("future",     "active"):  SuffixProvider.get_present_active,
            ("future",     "middle"):  SuffixProvider.get_present_middle,
            ("conditional","active"):  SuffixProvider.get_secondary_active,
            ("conditional","middle"):  SuffixProvider.get_secondary_middle,
            ("perfect",    "active"):  SuffixProvider.get_perfect_active,
            ("perfect",    "middle"):  SuffixProvider.get_perfect_middle,
            ("periphrastic_future", "active"): SuffixProvider.get_periphrastic_future_active,
            ("periphrastic_future", "middle"): SuffixProvider.get_periphrastic_future_middle,
            ("aorist",     "active"):  SuffixProvider.get_aorist_active,
            ("aorist",     "middle"):  SuffixProvider.get_aorist_middle,
            ("aorist",     "passive"): SuffixProvider.get_aorist_passive,
            ("injunctive", "active"):  SuffixProvider.get_aorist_active,
            ("injunctive", "middle"):  SuffixProvider.get_aorist_middle,
            ("injunctive", "passive"): SuffixProvider.get_aorist_passive,
            ("benedictive","active"):  SuffixProvider.get_benedictive_active,
            ("benedictive","middle"):  SuffixProvider.get_benedictive_middle,
            ("subjunctive","active"):  SuffixProvider.get_subjunctive_active,
            ("subjunctive","middle"):  SuffixProvider.get_subjunctive_middle,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _get_stem(
        self,
        root_str: str,
        class_num: int,
        strength: str,
        tense: str,
        derivative: str | None,
        person: str | None = None,
        number: str | None = None,
    ) -> pn.Fst:
        key = (root_str, class_num, strength, tense, derivative, person, number)
        if key not in self._stem_cache:
            self._stem_cache[key] = self.stems.build(
                root_str, class_num, strength,
                tense=tense, derivative=derivative,
                person=person, number=number,
            )
        return self._stem_cache[key]

    def _fetch_endings(
        self,
        class_num: int,
        voice: str,
        tense: str,
        root_str: str | None = None,
    ) -> dict[str, Suffix]:
        if voice == "passive":
            if tense in ("aorist", "injunctive"):
                return SuffixProvider.get_aorist_passive(
                    class_num=class_num, root_str=root_str
                )
            return SuffixProvider.get_passive_endings(tense)

        key = (tense, voice)
        provider = self._ending_dispatch.get(key)
        if provider is None:
            raise ValueError(f"No ending table for tense='{tense}' voice='{voice}'.")
        return provider(class_num=class_num, root_str=root_str, tense=tense)

    # ──────────────────────────────────────────────────────────────────────────
    # Main entry point
    # ──────────────────────────────────────────────────────────────────────────

    @lru_cache(maxsize=4096)
    def conjugate(
        self,
        root_str: str,
        class_num: int,
        person: str,
        number: str,
        voice: str = "active",
        tense: str = "present",
        derivative: str | None = None,
        use_db: bool = True,
    ) -> str:
        """Conjugate a Sanskrit root.

        Args:
            root_str:   IAST string (e.g. "bhū")
            class_num:  Gaṇa 1-10
            person:     "1", "2", "3"
            number:     "sg", "du", "pl"
            voice:      "active" | "middle" | "passive"
            tense:      "present" | "imperfect" | "imperative" | "optative" |
                        "future" | "conditional" | "perfect" |
            derivative: None | "causative" | "desiderative" | "intensive" | "denominative"

        Returns:
            IAST form, or multiple forms joined with " OR ".
        """
        if tense == "krdantas":
            return self.get_krdantas_block(root_str, class_num, use_db=use_db)
        # Block morphologically impossible combinations early
        if voice == "passive" and tense in (
            "perfect", "future", "periphrastic_future", "conditional", "benedictive"
        ):
            raise ValueError(
                f"Impossible combination: voice='{voice}' tense='{tense}'. "
                "These tenses have no distinct passive morphological paradigm."
            )

        # ── 0. Parse Preverbs (Upasargas) ────────────────────────────────────
        preverb_str = ""
        if "+" in root_str:
            parts = root_str.rsplit("+", 1)
            preverb_str = parts[0] + "+"
            root_str = parts[1]

        # ── 1. Resolve morphological features ────────────────────────────────
        f = self.resolver.resolve(
            root_str, class_num, person, number, voice, tense, derivative
        )

        if f.is_periphrastic:
            return self._conjugate_periphrastic_perfect(
                root_str, class_num, voice, person, number, derivative, preverb_str
            )

        # ── 2. Build / fetch stem FST ─────────────────────────────────────────
        stem = self._get_stem(
            root_str, f.effective_class, f.strength, tense,
            f.effective_derivative, person, number,
        )

        # ── 3. Augmentation (a- prefix for past tenses) ───────────────────────
        if f.augment:
            stem = pn.accep("a+") + stem

        # ── 4. Fetch ending and combine ───────────────────────────────────────
        endings = self._fetch_endings(f.effective_class, voice, tense, root_str=root_str)
        tag = f"[{person}{number}]"
        if tag not in endings:
            raise ValueError(f"No ending for {tag} in {tense} {voice}.")

        suffix: Suffix = endings[tag]
        if suffix.is_empty:
            combined = stem
        else:
            combined = stem + pn.accep("+") + suffix.to_fst()

        if preverb_str:
            combined = pn.accep(preverb_str) + combined

        # ── 5. Post-processing ────────────────────────────────────────────────
        morph_fst  = self.morphology.apply_all(combined)
        sandhi_fst = self.sandhi.apply_all(morph_fst)
        result     = sandhi_fst.optimize()

        try:
            forms = set(result.paths().ostrings())
        except Exception as e:
            try:
                forms = {pn.shortestpath(result).string()}
            except Exception:
                forms = set()

        if use_db:
            db_forms = INRIA_LOOKUP.lookup(root_str, tense, voice, person, number, derivative)
            forms.update(db_forms)

        if not forms:
            return "CRASHED: No valid path"
            
        return " OR ".join(sorted(forms))

    # ──────────────────────────────────────────────────────────────────────────
    # Periphrastic perfect
    # ──────────────────────────────────────────────────────────────────────────

    def _conjugate_periphrastic_perfect(
        self,
        root_str: str,
        class_num: int,
        voice: str,
        person: str,
        number: str,
        derivative: str | None = None,
        preverb_str: str = "",
    ) -> str:
        """Periphrastic perfect: base-stem + ām + auxiliary (kṛ/bhū/as)."""
        base_fst = self.stems._build_periphrastic_base(root_str, class_num, derivative)
        base_fst = (base_fst @ self.morphology.clean_tags).optimize()

        aux_str = self.conjugate("kṛ", 8, person, number, voice, "perfect")
        results = []
        for aux in aux_str.split(" OR "):
            combined = base_fst + pn.accep("+") + pn.accep(aux)
            if preverb_str:
                combined = pn.accep(preverb_str) + combined
            for form in self.sandhi.apply_all(combined).optimize().paths().ostrings():
                results.append(form)
        return " OR ".join(sorted(set(results))) if results else "CRASHED: No periphrastic forms"

    def get_krdantas_block(self, root_str: str, class_num: int, use_db: bool = False) -> str:
        preverb_str = ""
        if "+" in root_str:
            parts = root_str.rsplit("+", 1)
            preverb_str = parts[0] + "+"
            root_str = parts[1]
            
        from krdantas import KrdantaEngine
        engine = KrdantaEngine(self)
        return engine.generate_block(root_str, class_num, preverb_str)

    # ──────────────────────────────────────────────────────────────────────────
    # Debug helper — per-rule trace through entire pipeline
    # ──────────────────────────────────────────────────────────────────────────

    def debug_conjugate(
        self,
        root_str: str,
        class_num: int,
        person: str,
        number: str,
        voice: str = "active",
        tense: str = "present",
        derivative: str | None = None,
    ) -> None:
        """Step-by-step pipeline trace with per-rule sandhi/morphology breakdown.

        Uses ``debug=True`` on MorphologyEngine and SandhiEngine so every
        individual rule prints its output (or flags the exact rule that kills
        the FST).
        """
        print(f"\n{'='*60}")
        print(f"DEBUG: {root_str} cl{class_num} {person}{number} {voice} {tense}"
              + (f" [{derivative}]" if derivative else ""))
        print(f"{'='*60}")

        f = self.resolver.resolve(
            root_str, class_num, person, number, voice, tense, derivative
        )
        print(f"  ResolvedFeatures: strength={f.strength}  "
              f"class={f.effective_class}  derivative={f.effective_derivative}  "
              f"augment={f.augment}  periphrastic={f.is_periphrastic}")

        # Step 1 – stem
        stem = self._get_stem(
            root_str, f.effective_class, f.strength, tense,
            f.effective_derivative, person, number,
        )
        try:
            print(f"  1. stem: '{stem.optimize().string()}'")
        except Exception:
            print(f"  1. stem: ambiguous / empty")

        # Step 2 – augment
        if f.augment:
            stem = pn.accep("a+") + stem
            try:
                print(f"  2. augmented stem: '{stem.optimize().string()}'")
            except Exception:
                print(f"  2. augmented stem: ambiguous / empty")

        # Step 3 – ending
        endings = self._fetch_endings(f.effective_class, voice, tense, root_str=root_str)
        tag = f"[{person}{number}]"
        suffix: Suffix = endings.get(tag, Suffix(""))
        print(f"  3. ending surface='{suffix.surface}' tags={suffix.tags}")

        combined = stem + pn.accep("+") + suffix.to_fst()
        try:
            print(f"  4. stem+ending: '{combined.optimize().string()}'")
        except Exception:
            print(f"  4. stem+ending: ambiguous / empty")

        # Step 5 – morphology (per-rule)
        morph = self.morphology.apply_all(combined, debug=True)

        # Step 6 – sandhi (per-rule, all three phases)
        self.sandhi.apply_all(morph, debug=True)