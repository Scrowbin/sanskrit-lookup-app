"""paradigm.py — Thematic / Athematic class classification.

Sanskrit verbal classes divide into two paradigm types:

  Thematic  (sa-vikāra)  – classes 1, 4, 6, 10
    Root/stem carries a thematic -a- vowel before endings.
    Strong and weak root grades coincide; one ending table serves all.

  Athematic (nir-vikāra) – classes 2, 3, 5, 7, 8, 9
    Endings attach directly to the root/stem (no thematic vowel).
    Strong (sg-active) vs. weak (du/pl, middle) grades are distinct.
    Several endings differ from the thematic table.

Using an explicit predicate keeps the distinction out of numeric
comparisons scattered across multiple modules.
"""

THEMATIC  = frozenset({1, 4, 6, 10})
ATHEMATIC = frozenset({2, 3, 5, 7, 8, 9})


def is_thematic(class_num: int) -> bool:
    """Return True for thematic classes (1, 4, 6, 10)."""
    return class_num in THEMATIC


def paradigm_label(class_num: int) -> str:
    """Return a human-readable paradigm label (for diagnostics)."""
    return "thematic" if is_thematic(class_num) else "athematic"
