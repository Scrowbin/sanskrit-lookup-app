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
from dhatupatha_analyzer import DHATUPATHA_ANALYZER

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
            ("pluperfect", "active"):  SuffixProvider.get_secondary_active,
            ("pluperfect", "middle"):  SuffixProvider.get_secondary_middle,
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

    @lru_cache(maxsize=2048)
    def _get_stem(
        self,
        root_str: str,
        class_num: int,
        strength: str,
        tense: str,
        derivative: str | None,
        voice: str = "active",
        person: str | None = None,
        number: str | None = None,
    ) -> pn.Fst:
        return self.stems.build(
            root_str, class_num, strength,
            tense=tense, derivative=derivative,
            person=person, number=number, voice=voice
        )

    def _fetch_endings(
        self,
        class_num: int,
        voice: str,
        tense: str,
        root_str: str | None = None,
        derivative: str | None = None,
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
        return provider(class_num=class_num, root_str=root_str, tense=tense, derivative=derivative)

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
        auxiliary: str = "kṛ",
    ) -> list[str] | str:
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
            For normal conjugation: sorted ``list[str]`` of distinct IAST surfaces.
            For ``tense="krdantas"``: a single ``str`` block from the kṛdanta engine.
            Periphrastic perfect returns ``list[str]`` like the main path.
        """
        if tense == "krdantas":
            return self.get_krdantas_block(root_str, class_num, derivative=derivative, use_db=use_db)
        
        # Whitney §530-531: Outside the present-system, the middle voice doubles as
        # passive. Auto-alias passive → middle for tenses with no distinct passive
        # paradigm, rather than raising an error. Periphrastic future is excluded
        # entirely (no passive or middle paradigm exists for it).
        _no_distinct_passive = {"perfect", "future", "conditional", "benedictive"}
        if voice == "passive" and tense in _no_distinct_passive:
            voice = "middle"  # silent alias per Whitney §530
        elif voice == "passive" and tense == "periphrastic_future":
            raise ValueError(
                "Impossible combination: voice='passive' tense='periphrastic_future'. "
                "The periphrastic future has no passive or middle paradigm."
            )

        # ── 0. Parse Preverbs (Upasargas) ────────────────────────────────────
        preverb_str = ""
        clean_root_str = root_str
        if "+" in root_str:
            parts = root_str.rsplit("+", 1)
            preverbs = parts[0].split("+")
            # 4.1 Upasarga validation
            from upasargas import is_valid_upasarga
            for p in preverbs:
                if not is_valid_upasarga(p):
                    # Warning or error, but let's just log or accept it for robustness
                    pass
            
            # 4.2 ā-never-first enforcement: if 'ā' is present and not the only prefix,
            # it should be immediately before the root. We move it to the end of the list.
            if "ā" in preverbs and len(preverbs) > 1:
                preverbs.remove("ā")
                preverbs.append("ā")
                
            preverb_str = "+".join(preverbs) + "+"
            root_str = parts[1]

        # ── 0.5 Voice (Pada) Validation Gatekeeper ───────────────────────────
        # We only strictly validate primary (non-derivative) active/middle requests.
        if voice != "passive" and derivative is None:
            root_obj = DHATUPATHA_ANALYZER.get(clean_root_str, class_num)
            if voice not in root_obj.permitted_voices:
                allowed = "/".join(root_obj.permitted_voices)
                raise ValueError(
                    f"Grammar error: Root '{clean_root_str}' class {class_num} "
                    f"does not permit '{voice}' voice. Allowed: {allowed}."
                )

        # ── 1. Resolve morphological features ────────────────────────────────
        # s_or_is dual-dispatch (Whitney §881a): roots like budh that take either
        # the s-aorist or iṣ-aorist need two separate stem+ending pairings.
        if tense in ("aorist", "injunctive"):
            from irregulars import aorist_overrides
            info = aorist_overrides.get(root_str)
            if info and info.get("type") and "_or_" in info.get("type"):
                return self._conjugate_aorist_dual(
                    root_str, class_num, person, number, voice, tense,
                    derivative, preverb_str,
                )

        f = self.resolver.resolve(
            root_str, class_num, person, number, voice, tense, derivative
        )

        if f.is_periphrastic:
            return self._conjugate_periphrastic_perfect(
                root_str, class_num, voice, person, number, derivative, preverb_str, auxiliary
            )

        # ── 2. Build / fetch stem FST ─────────────────────────────────────────
        stem = self._get_stem(
            root_str, f.effective_class, f.strength, tense,
            f.effective_derivative, voice=voice, person=person, number=number
        )

        # ── 3. Augmentation (a- prefix for past tenses) ──────────────────────────────
        if f.augment:
            # [AUG] tag allows MorphologyEngine to apply vriddhi coalescence
            # (a+i→ai, a+u→au) rather than guna (e, o) when the stem is
            # vowel-initial. Whitney §135 / Pāṇini 6.1.87-89.
            stem = pn.accep("[AUG]a+") + stem

        # ── 4. Fetch ending and combine ───────────────────────────────────────
        endings = self._fetch_endings(f.effective_class, voice, tense, root_str=root_str, derivative=f.effective_derivative)
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

        forms = set(result.paths().ostrings())

        if use_db:
            db_forms = INRIA_LOOKUP.lookup(root_str, tense, voice, person, number, derivative)
            if db_forms:
                # Add all valid variants from the DB to standardise what we return if we want to match
                pass
        
        # We now return a clean list of unique forms directly
        return sorted(list(forms))

    # ──────────────────────────────────────────────────────────────────────────
    # Dual-dispatch aorist (s_or_is)
    # ──────────────────────────────────────────────────────────────────────────

    def _conjugate_aorist_dual(
        self,
        root_str: str,
        class_num: int,
        person: str,
        number: str,
        voice: str,
        tense: str,
        derivative: str | None,
        preverb_str: str,
    ) -> list[str]:
        """Dual-dispatch for s_or_is aorist roots (Whitney §881a).

        Runs the full stem→ending→sandhi pipeline twice: once with the
        s-aorist type and once with the iṣ-aorist type, then unions the
        results.  This avoids stem/ending cross-contamination that occurs
        when ``pn.union(build_s, build_is)`` is paired with a single
        ending set.
        """
        from irregulars import aorist_overrides

        info = aorist_overrides[root_str]
        original_type = info.get("type", "")
        forced_types = original_type.split("_or_")
        all_forms: set[str] = set()

        for forced_type in forced_types:
            aorist_overrides[root_str] = {**info, "type": forced_type}
            try:
                f = self.resolver.resolve(
                    root_str, class_num, person, number, voice, tense, derivative
                )
                stem = self.stems.build(
                    root_str, f.effective_class, f.strength, tense=tense,
                    derivative=f.effective_derivative, person=person, number=number,
                )
                if f.augment:
                    stem = pn.accep("[AUG]a+") + stem
                endings = self._fetch_endings(
                    f.effective_class, voice, tense, root_str=root_str, derivative=f.effective_derivative,
                )
                tag = f"[{person}{number}]"
                if tag not in endings:
                    continue
                suffix: Suffix = endings[tag]
                combined = (
                    stem if suffix.is_empty
                    else stem + pn.accep("+") + suffix.to_fst()
                )
                if preverb_str:
                    combined = pn.accep(preverb_str) + combined
                morph_fst = self.morphology.apply_all(combined)
                sandhi_fst = self.sandhi.apply_all(morph_fst)
                result = sandhi_fst.optimize()
                all_forms.update(result.paths().ostrings())
            except Exception:
                pass  # skip if one sub-type fails
            finally:
                aorist_overrides[root_str]["type"] = original_type  # restore original

        return sorted(list(all_forms))

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
        auxiliary: str = "kṛ",
    ) -> list[str]:
        """Periphrastic perfect: base-stem + ām + auxiliary (kṛ/bhū/as)."""
        
        # 1. Validate auxiliary and map to its Dhatupatha class
        valid_aux = {"kṛ": 8, "bhū": 1, "as": 2}
        if auxiliary not in valid_aux:
            raise ValueError(
                f"Invalid periphrastic auxiliary '{auxiliary}'. "
                "Sanskrit only permits 'kṛ', 'bhū', or 'as'."
            )

        base_fst = self.stems._build_periphrastic_base(root_str, class_num, derivative)
        base_fst = (base_fst @ self.morphology.clean_tags).optimize()

        # 2. Enforce Pāṇinian voice rules for auxiliaries
        # 'bhū' and 'as' ONLY take active endings, regardless of the main verb's voice.
        aux_voice = "active" if auxiliary in ("bhū", "as") else voice
        aux_class = valid_aux[auxiliary]

        # 3. Generate the auxiliary (turn off DB to ensure pure generation)
        aux_out = self.conjugate(
            root_str=auxiliary, 
            class_num=aux_class, 
            person=person, 
            number=number, 
            voice=aux_voice, 
            tense="perfect", 
            use_db=False
        )
        aux_forms = (
            aux_out if isinstance(aux_out, list) else aux_out.split(" OR ")
        )

        results = []
        vowels = set("aāiīuūṛṝḷeaiou")
        for aux in aux_forms:
            # 4.3 `āṁ` anusvāra normalization: ām -> āṃ before consonants
            if aux and aux[0] not in vowels:
                # Replace the final 'm' of base_fst (which is 'ām') with 'ṃ'
                # base_fst ends with 'ām'. We can append it with sandhi override.
                combined = base_fst @ pn.cdrewrite(
                    pn.cross("m", "ṃ"), "ā", "[EOS]", self.sandhi.sig
                ) + pn.accep("+") + pn.accep(aux)
            else:
                combined = base_fst + pn.accep("+") + pn.accep(aux)

            if preverb_str:
                combined = pn.accep(preverb_str) + combined
            for form in self.sandhi.apply_all(combined).optimize().paths().ostrings():
                results.append(form)
                
        return sorted(list(set(results)))

    def get_krdantas_block(self, root_str: str, class_num: int, derivative: str | None = None, use_db: bool = False) -> str:
        preverb_str = ""
        if "+" in root_str:
            parts = root_str.rsplit("+", 1)
            preverb_str = parts[0] + "+"
            root_str = parts[1]
            
        from krdantas import KrdantaEngine
        engine = KrdantaEngine(self)
        return engine.generate_block(root_str, class_num, preverb_str, derivative=derivative)

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
            f.effective_derivative, voice=voice, person=person, number=number
        )
        try:
            print(f"  1. stem: '{stem.optimize().string()}'")
        except Exception:
            print(f"  1. stem: ambiguous / empty")

        # Step 2 – augment
        if f.augment:
            stem = pn.accep("[AUG]a+") + stem
            try:
                print(f"  2. augmented stem: '{stem.optimize().string()}'")
            except Exception:
                print(f"  2. augmented stem: ambiguous / empty")

        # Step 3 – ending
        endings = self._fetch_endings(f.effective_class, voice, tense, root_str=root_str, derivative=f.effective_derivative)
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