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
    Stem FSTs are expensive (``StemBuilder.build().optimize()``).  They are
    memoized without person/number for most tenses; perfect and cl.3 impv.
    ``dā``/``dhā`` keep a paradigm slot.

  ``_finalize_forms_cached`` memoizes morph → sandhi → surface extraction for
    a cell.  That helps benchmarks (many cells share stems) and production
    ``/api/conjugate/full`` (one stem, twelve endings).

    ``conjugate()`` is wrapped with ``lru_cache`` for exact repeat queries
    (common in UI re-renders).  A single cold ``/api/conjugate`` call still
    pays full FST cost once; stem/finalize caches matter less there.
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

    @staticmethod
    def _stem_cache_needs_paradigm_slot(
        tense: str, class_num: int, root_str: str
    ) -> bool:
        """True when stem FST varies by person/number (perfect, impv. 2sg cl.3)."""
        if tense == "perfect":
            return True
        if (
            tense == "imperative"
            and class_num == 3
            and root_str in ("dā", "dhā")
        ):
            return True
        return False

    @lru_cache(maxsize=32768)
    def _get_stem_cached(
        self,
        root_str: str,
        class_num: int,
        strength: str,
        tense: str,
        derivative: str | None,
        aorist_type_override: str | None,
        voice: str,
    ) -> pn.Fst:
        """Memoized stem FST for paradigms where only endings vary by person/number."""
        return self.stems.build(
            root_str,
            class_num,
            strength,
            tense=tense,
            derivative=derivative,
            voice=voice,
            aorist_type_override=aorist_type_override,
        )

    @lru_cache(maxsize=8192)
    def _get_stem_cached_paradigm(
        self,
        root_str: str,
        class_num: int,
        strength: str,
        tense: str,
        derivative: str | None,
        aorist_type_override: str | None,
        voice: str,
        person: str | None,
        number: str | None,
    ) -> pn.Fst:
        """Memoized stem when person/number change the stem (perfect, dehi/dhehi)."""
        return self.stems.build(
            root_str,
            class_num,
            strength,
            tense=tense,
            derivative=derivative,
            person=person,
            number=number,
            voice=voice,
            aorist_type_override=aorist_type_override,
        )

    def _get_stem(
        self,
        root_str: str,
        class_num: int,
        strength: str,
        tense: str,
        derivative: str | None,
        aorist_type_override: str | None = None,
        voice: str = "active",
        person: str | None = None,
        number: str | None = None,
    ) -> pn.Fst:
        if self._stem_cache_needs_paradigm_slot(tense, class_num, root_str):
            return self._get_stem_cached_paradigm(
                root_str,
                class_num,
                strength,
                tense,
                derivative,
                aorist_type_override,
                voice,
                person,
                number,
            )
        return self._get_stem_cached(
            root_str,
            class_num,
            strength,
            tense,
            derivative,
            aorist_type_override,
            voice,
        )

    def _fetch_endings(
        self,
        class_num: int,
        voice: str,
        tense: str,
        root_str: str | None = None,
        derivative: str | None = None,
        aorist_type_override: str | None = None,
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
        return provider(
            class_num=class_num,
            root_str=root_str,
            tense=tense,
            derivative=derivative,
            aorist_type_override=aorist_type_override,
        )

    @lru_cache(maxsize=8192)
    def _fetch_endings_cached(
        self,
        class_num: int,
        voice: str,
        tense: str,
        root_str: str | None,
        derivative: str | None,
        aorist_type_override: str | None = None,
    ) -> dict[str, Suffix]:
        """Memoized ending-table fetch for repeated lookup workloads."""
        return self._fetch_endings(
            class_num=class_num,
            voice=voice,
            tense=tense,
            root_str=root_str,
            derivative=derivative,
            aorist_type_override=aorist_type_override,
        )

    @staticmethod
    def _extract_forms_fast(fst: pn.Fst) -> set[str]:
        """Extract output forms; prefer O(1) ``string()`` when the FST is single-path."""
        optimized = fst.optimize()
        try:
            out_acc = pn.project(optimized, "output").optimize()
        except Exception:
            return set(optimized.paths().ostrings())
        try:
            s = out_acc.string()
            if s:
                return {s}
        except Exception:
            pass
        try:
            probe = pn.shortestpath(out_acc, nshortest=2, unique=True).optimize()
            probe_forms = list(probe.paths().ostrings())
            if len(probe_forms) == 1:
                return {probe_forms[0]}
        except Exception:
            pass
        return set(optimized.paths().ostrings())

    @staticmethod
    def _combine_stem_suffix(
        stem: pn.Fst,
        suffix: Suffix,
        root_str: str,
        class_num: int,
        voice: str,
        tense: str,
    ) -> pn.Fst:
        """Join stem and ending FSTs (aorist ``is``/``sis`` attach without ``+``)."""
        if suffix.is_empty:
            return stem
        aor_type = (
            DHATUPATHA_ANALYZER.get_aorist_type(root_str, class_num, voice=voice)
            if tense in ("aorist", "injunctive")
            else ""
        )
        if aor_type in ("is", "sis") and suffix.surface.startswith(("iṣ", "siṣ")):
            return stem + suffix.to_fst()
        return stem + pn.accep("+") + suffix.to_fst()

    @lru_cache(maxsize=131072)
    def _finalize_forms_cached(
        self,
        root_str: str,
        effective_class: int,
        strength: str,
        tense: str,
        derivative_key: str,
        voice: str,
        person: str,
        number: str,
        preverb_str: str,
        augment: bool,
        suffix_surface: str,
        suffix_tags: tuple[str, ...],
        aorist_type_override: str,
    ) -> tuple[str, ...]:
        """Morph + sandhi + surface extraction for one paradigm cell."""
        derivative = derivative_key or None
        stem = self._get_stem(
            root_str,
            effective_class,
            strength,
            tense,
            derivative,
            aorist_type_override=aorist_type_override or None,
            voice=voice,
            person=person,
            number=number,
        )
        if augment:
            stem = pn.accep("[AUG]a+") + stem
        suffix = Suffix(suffix_surface, frozenset(suffix_tags))
        combined = self._combine_stem_suffix(
            stem, suffix, root_str, effective_class, voice, tense
        )
        if preverb_str:
            combined = pn.accep(preverb_str) + combined
        morph_fst = self.morphology.apply_all(combined)
        sandhi_fst = self.sandhi.apply_all(morph_fst)
        forms = self._extract_forms_fast(sandhi_fst)
        return tuple(sorted(forms))

    # ──────────────────────────────────────────────────────────────────────────
    # Main entry point
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _split_preverbs(root_str: str) -> tuple[str, str]:
        """Return ``(preverb_prefix, bare_root)``; prefix ends with ``+`` when non-empty."""
        if "+" not in root_str:
            return "", root_str
        parts = root_str.rsplit("+", 1)
        preverbs = parts[0].split("+")
        if "ā" in preverbs and len(preverbs) > 1:
            preverbs.remove("ā")
            preverbs.append("ā")
        return "+".join(preverbs) + "+", parts[1]

    @staticmethod
    def _voice_for_tense(voice: str, tense: str) -> str:
        """Whitney §530: passive aliases to middle where no passive paradigm exists."""
        if voice == "passive" and tense in {
            "perfect",
            "future",
            "conditional",
            "benedictive",
        }:
            return "middle"
        if voice == "passive" and tense == "periphrastic_future":
            raise ValueError(
                "Impossible combination: voice='passive' tense='periphrastic_future'. "
                "The periphrastic future has no passive or middle paradigm."
            )
        return voice

    @staticmethod
    def _normalize_class_num(
        root_str: str,
        class_num: int | str | None,
        derivative: str | None,
    ) -> int:
        if class_num in (None, "", 0, "0"):
            clean_root = root_str.rsplit("+", 1)[-1] if "+" in root_str else root_str
            if (
                clean_root.endswith("a")
                or derivative == "causative"
                or derivative == "denominative"
            ):
                return 10
            return 1
        if isinstance(class_num, str):
            if class_num.isdigit():
                return int(class_num)
            if class_num == "denom":
                return 10
        return int(class_num)

    @lru_cache(maxsize=65536)
    def conjugate(
        self,
        root_str: str,
        class_num: int | str | None = None,
        person: str = "3",
        number: str = "sg",
        voice: str = "active",
        tense: str = "present",
        derivative: str | None = None,
        use_db: bool = True,
        auxiliary: str = "kṛ",
    ) -> list[str] | str:
        """Conjugate a Sanskrit root.

        Args:
            root_str:   IAST string (e.g. "bhū")
            class_num:  Gaṇa 1-10 or None (engine will guess if None)
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
        class_num = self._normalize_class_num(root_str, class_num, derivative)

        if tense == "krdantas":
            return self.get_krdantas_block(root_str, class_num, derivative=derivative, use_db=use_db)
            
        if derivative == "intensive":
            if voice == "active":
                # Whitney §1002-1012: The active intensive uses the yaṅluganta
                # (reduplication without -ya-), conjugated athematically (cl3).
                # The yaṅanta (-ya- infix) is strictly the middle/passive paradigm.
                # Do NOT union anta forms into active — they produce spurious stems
                # like bobhūya- which only belong in the middle column.
                return self._conjugate_internal(root_str, class_num, person, number, voice, tense, "intensive_luganta", use_db, auxiliary)
            else:
                # Middle (and passive, which aliases to middle for intensives)
                # uses the yaṅanta stem (reduplicated + -ya-).
                return self._conjugate_internal(root_str, class_num, person, number, voice, tense, "intensive_anta", use_db, auxiliary)

                
        return self._conjugate_internal(root_str, class_num, person, number, voice, tense, derivative, use_db, auxiliary)

    def conjugate_paradigm(
        self,
        root_str: str,
        class_num: int | str | None = None,
        voice: str = "active",
        tense: str = "present",
        derivative: str | None = None,
        use_db: bool = True,
        auxiliary: str = "kṛ",
    ) -> dict[str, list[str]]:
        """All twelve person/number cells with shared setup (production full paradigm)."""
        class_num = self._normalize_class_num(root_str, class_num, derivative)

        if tense == "krdantas":
            block = self.get_krdantas_block(
                root_str, class_num, derivative=derivative, use_db=use_db
            )
            return {"krdantas": [block]}

        if derivative == "intensive":
            deriv = "intensive_luganta" if voice == "active" else "intensive_anta"
            return self._conjugate_paradigm_loop(
                root_str, class_num, voice, tense, deriv, use_db, auxiliary
            )

        return self._conjugate_paradigm_loop(
            root_str, class_num, voice, tense, derivative, use_db, auxiliary
        )

    def _conjugate_paradigm_loop(
        self,
        root_str: str,
        class_num: int,
        voice: str,
        tense: str,
        derivative: str | None,
        use_db: bool,
        auxiliary: str,
    ) -> dict[str, list[str]]:
        preverb_str, root_str = self._split_preverbs(root_str)
        clean_root = root_str
        voice = self._voice_for_tense(voice, tense)

        allowed = DHATUPATHA_ANALYZER.get_permitted_voices(
            clean_root, class_num, tense, derivative
        )
        if voice not in allowed:
            raise ValueError(
                f"Grammar error: Root '{clean_root}' class {class_num} "
                f"({tense}, {derivative or 'primary'}) does not permit "
                f"'{voice}' voice. Allowed: {'/'.join(sorted(allowed))}."
            )

        dual_aorist = False
        if tense in ("aorist", "injunctive"):
            from irregulars import aorist_overrides

            info = aorist_overrides.get(root_str)
            dual_aorist = bool(
                info and info.get("type") and "_or_" in info.get("type", "")
            )

        paradigm: dict[str, list[str]] = {}
        for person in ("1", "2", "3"):
            for number in ("sg", "du", "pl"):
                key = f"{person}{number}"
                try:
                    if dual_aorist:
                        forms = self._conjugate_aorist_dual(
                            root_str,
                            class_num,
                            person,
                            number,
                            voice,
                            tense,
                            derivative,
                            preverb_str,
                        )
                    else:
                        f = self.resolver.resolve(
                            root_str,
                            class_num,
                            person,
                            number,
                            voice,
                            tense,
                            derivative,
                        )
                        if f.is_periphrastic:
                            forms = self._conjugate_periphrastic_perfect(
                                root_str,
                                class_num,
                                voice,
                                person,
                                number,
                                derivative,
                                preverb_str,
                                auxiliary,
                            )
                        else:
                            endings = self._fetch_endings_cached(
                                f.effective_class,
                                voice,
                                tense,
                                root_str,
                                f.effective_derivative,
                            )
                            tag = f"[{person}{number}]"
                            if tag not in endings:
                                raise ValueError(
                                    f"No ending for {tag} in {tense} {voice}."
                                )
                            suffix = endings[tag]
                            forms = list(
                                self._finalize_forms_cached(
                                    root_str,
                                    f.effective_class,
                                    f.strength,
                                    tense,
                                    f.effective_derivative or "",
                                    voice,
                                    person,
                                    number,
                                    preverb_str,
                                    f.augment,
                                    suffix.surface,
                                    tuple(sorted(suffix.tags)),
                                    "",
                                )
                            )
                            if use_db:
                                db_forms = INRIA_LOOKUP.lookup(
                                    root_str,
                                    tense,
                                    voice,
                                    person,
                                    number,
                                    derivative,
                                )
                                if db_forms:
                                    pass
                    paradigm[key] = forms
                except Exception as exc:
                    paradigm[key] = [f"Error: {exc}"]
        return paradigm

    def _conjugate_internal(
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
        
        preverb_str, root_str = self._split_preverbs(root_str)
        clean_root_str = root_str
        voice = self._voice_for_tense(voice, tense)

        # ── 0.5 Voice (Pada) Validation Gatekeeper ───────────────────────────
        # Lakāra-specific sets from verbs_clean.csv (e.g. budh: present active+passive,
        # future active+middle — not middle in every tense).
        allowed = DHATUPATHA_ANALYZER.get_permitted_voices(
            clean_root_str, class_num, tense, derivative
        )
        if voice not in allowed:
            raise ValueError(
                f"Grammar error: Root '{clean_root_str}' class {class_num} "
                f"({tense}, {derivative or 'primary'}) does not permit "
                f"'{voice}' voice. Allowed: {'/'.join(sorted(allowed))}."
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

        endings = self._fetch_endings_cached(
            f.effective_class, voice, tense, root_str, f.effective_derivative
        )
        tag = f"[{person}{number}]"
        if tag not in endings:
            raise ValueError(f"No ending for {tag} in {tense} {voice}.")

        suffix: Suffix = endings[tag]
        forms = self._finalize_forms_cached(
            root_str,
            f.effective_class,
            f.strength,
            tense,
            f.effective_derivative or "",
            voice,
            person,
            number,
            preverb_str,
            f.augment,
            suffix.surface,
            tuple(sorted(suffix.tags)),
            "",
        )

        if use_db:
            db_forms = INRIA_LOOKUP.lookup(
                root_str, tense, voice, person, number, derivative
            )
            if db_forms:
                pass

        return list(forms)

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
        forced_types = info.get("type", "").split("_or_")
        all_forms: set[str] = set()

        for forced_type in forced_types:
            try:
                f = self.resolver.resolve(
                    root_str, class_num, person, number, voice, tense, derivative
                )
                endings = self._fetch_endings_cached(
                    f.effective_class,
                    voice,
                    tense,
                    root_str,
                    f.effective_derivative,
                    forced_type,
                )
                tag = f"[{person}{number}]"
                if tag not in endings:
                    continue
                suffix: Suffix = endings[tag]
                all_forms.update(
                    self._finalize_forms_cached(
                        root_str,
                        f.effective_class,
                        f.strength,
                        tense,
                        f.effective_derivative or "",
                        voice,
                        person,
                        number,
                        preverb_str,
                        f.augment,
                        suffix.surface,
                        tuple(sorted(suffix.tags)),
                        forced_type,
                    )
                )
            except Exception:
                pass  # skip if one subtype fails

        return sorted(all_forms)

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

        # 3. Generate the auxiliary (reduplicated liṭ; √kṛ is never periphrastic itself)
        aux_out = self.conjugate(
            root_str=auxiliary,
            class_num=aux_class,
            person=person,
            number=number,
            voice=aux_voice,
            tense="perfect",
            use_db=False,
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
            results.extend(self._extract_forms_fast(self.sandhi.apply_all(combined)))
                
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