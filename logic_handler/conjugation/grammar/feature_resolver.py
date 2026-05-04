"""feature_resolver.py — MorphologicalFeatureResolver

Separates all derivative/strength/class resolution from the conjugation pipeline.
conjugate() becomes a dumb pipe; all morphological decision-making lives here.
"""
from __future__ import annotations
from dataclasses import dataclass
from dhatupatha_analyzer import DHATUPATHA_ANALYZER

# Derivatives whose perfect is always periphrastic (uses kṛ auxiliary).
# NOTE: Desideratives and intensives regularly build non-periphrastic perfects
# (e.g. bububhūṣ-iva, bobhav-a), which INRIA expects; do not force periphrastic.
_PERIPHRASTIC_DERIVATIVES: frozenset[str] = frozenset({"causative", "denominative"})

# Tenses that require the augment "a+" prefix.
_AUGMENTED_TENSES: frozenset[str] = frozenset({"imperfect", "conditional", "aorist"})

# Priority-ordered (predicate, strength_tag) table.
# Each predicate: (class_num, person, number, voice, tense) → bool.
_STRENGTH_RULES: list[tuple] = [
    # Passives always use a weak root
    (lambda c, p, n, v, t: v == "passive",                                         "[WEAK]"),
    # Future / Conditional / Periphrastic Future always use Guna (strong)
    (lambda c, p, n, v, t: t in ("future", "conditional", "periphrastic_future"),  "[STRONG]"),
    # Aorist / Injunctive: active = strong, middle = weak
    (lambda c, p, n, v, t: t in ("aorist", "injunctive") and v == "active",        "[STRONG]"),
    (lambda c, p, n, v, t: t in ("aorist", "injunctive") and v == "middle",        "[WEAK]"),
    # Perfect: sg active = strong; everything else = weak
    (lambda c, p, n, v, t: t == "perfect" and v == "active" and n == "sg",         "[STRONG]"),
    (lambda c, p, n, v, t: t == "perfect",                                          "[WEAK]"),
    # Thematic classes: cl 1/10 always strong, cl 4/6 always weak
    (lambda c, p, n, v, t: c in (1, 10),                                           "[STRONG]"),
    (lambda c, p, n, v, t: c in (4, 6),                                            "[WEAK]"),
    # Imperative 1st person: strong regardless of voice
    (lambda c, p, n, v, t: t == "imperative" and p == "1",                         "[STRONG]"),
    # Optative / Benedictive: always weak
    (lambda c, p, n, v, t: t in ("optative", "benedictive"),                       "[WEAK]"),
    # Middle voice: weak (after imperative-1 check)
    (lambda c, p, n, v, t: v == "middle",                                          "[WEAK]"),
    # Remaining imperative 2sg: weak
    (lambda c, p, n, v, t: t == "imperative" and p == "2" and n == "sg",          "[WEAK]"),
    # Singular active: strong (main athematic rule)
    (lambda c, p, n, v, t: n == "sg",                                              "[STRONG]"),
    # cl3 imperfect 3pl is exceptionally strong (ajuhavuḥ)
    (lambda c, p, n, v, t: c == 3 and t == "imperfect" and p == "3" and n == "pl","[STRONG]"),
    # Default: weak
    (lambda c, p, n, v, t: True,                                                   "[WEAK]"),
]


def _evaluate_strength(class_num: int, person: str, number: str,
                        voice: str, tense: str) -> str:
    """Return '[STRONG]' or '[WEAK]' by scanning the priority rule table."""
    for predicate, tag in _STRENGTH_RULES:
        if predicate(class_num, person, number, voice, tense):
            return tag
    return "[WEAK]"  # unreachable; last rule always matches


@dataclass(frozen=True)
class ResolvedFeatures:
    """Standardised morphological parameters ready for the conjugation pipeline.

    Attributes:
        strength: '[STRONG]' or '[WEAK]' — controls guna/vriddhi grade
        effective_class: class used for endings lookup (may differ from root class
            for derivatives; e.g. desiderative always uses class-1 endings)
        effective_derivative: derivative tag forwarded to StemBuilder
        is_periphrastic: True → call _conjugate_periphrastic_perfect instead
        augment: True → prepend augment "a+" to stem (past tenses)
    """
    strength: str
    effective_class: int
    effective_derivative: str | None
    is_periphrastic: bool
    augment: bool


class MorphologicalFeatureResolver:
    """Resolves raw conjugation arguments into standardised ResolvedFeatures.

    All morphological decision-making (derivative expansions, periphrastic
    detection, augment logic) is centralised here so that conjugate() can
    remain a pure FST pipeline.
    """

    def resolve(
        self,
        root_str: str,
        class_num: int,
        person: str,
        number: str,
        voice: str,
        tense: str,
        derivative: str | None,
    ) -> ResolvedFeatures:
        """Return a ResolvedFeatures for the given parameters."""

        # ── Periphrastic perfect detection ────────────────────────────────────
        is_periphrastic = False
        if tense == "perfect":
            root_obj = DHATUPATHA_ANALYZER.get(root_str, class_num)
            is_periphrastic = (
                derivative in _PERIPHRASTIC_DERIVATIVES
                or class_num == 10
                or root_obj.takes_periphrastic_perfect
            )

        # ── Derivative / voice expansion ──────────────────────────────────────
        if derivative == "primary":
            derivative = None

        if derivative == "causative":
            strength = _evaluate_strength(10, person, number, voice, tense)
            effective_class = 10
            # Causative passive uses a dedicated stem in -ya (not -aya).
            effective_derivative = "causative_passive" if voice == "passive" else None

        elif derivative == "desiderative":
            strength = "[STRONG]"
            effective_class = 1
            effective_derivative = (
                "desiderative_passive" if voice == "passive" else "desiderative"
            )

        elif derivative == "intensive":
            if voice == "middle":
                strength = "[WEAK]"
                effective_class = 1
                effective_derivative = "intensive_middle"
            else:
                # Active intensive: athematic class-3 endings with strength
                # evaluated against class-2 rules (like any athematic)
                strength = _evaluate_strength(2, person, number, voice, tense)
                effective_class = 3
                effective_derivative = "intensive_active"

        elif derivative == "denominative":
            strength = "[WEAK]"
            effective_class = 1
            effective_derivative = "denominative"

        elif voice == "passive":
            strength = "[WEAK]"
            effective_class = class_num
            if tense in ("present", "imperfect", "imperative", "optative"):
                effective_derivative = "passive"
            else:
                # Aorist passive 3sg gets a special tag; all other passive
                # aorist cells use the middle paradigm.
                effective_derivative = "aorist_passive_3sg" if (
                    tense in ("aorist", "injunctive")
                    and person == "3" and number == "sg"
                ) else None

        else:
            strength = _evaluate_strength(class_num, person, number, voice, tense)
            effective_class = class_num
            effective_derivative = derivative

        augment = tense in _AUGMENTED_TENSES
        # INRIA’s roots.csv has a small number of “injunctive” cells stored
        # with augment (notably 1sg active for some roots like √bhū).
        if tense == "injunctive" and voice == "active" and person == "1" and number == "sg":
            augment = True

        return ResolvedFeatures(
            strength=strength,
            effective_class=effective_class,
            effective_derivative=effective_derivative,
            is_periphrastic=is_periphrastic,
            augment=augment,
        )
