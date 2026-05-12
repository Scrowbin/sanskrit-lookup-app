"""Lexical hints mined from INRIA-derived corpora (adverbs.csv, parts.csv).

Used when there is **no** Dhātupāṭha row for the root (``DhatupathaAnalyzer``
falls back to bare IAST). Short SLP1 entries without ``\\`` are still treated as
authoritative and are **not** overridden from adverbs alone.
"""

from __future__ import annotations

import csv
import os
import re
from collections import Counter

# Primary gerund only (no causative / desiderative / etc.)
_GERUND_POS = "gerund"


def normalize_corpus_root(root_iast: str) -> str:
    """Strip INRIA homonym suffix (#1, #2) for dictionary keys."""
    if not root_iast:
        return root_iast
    return re.sub(r"#\d+$", "", root_iast.strip())


def classify_primary_gerund_connecting_i(form_iast: str) -> bool | None:
    """Infer whether the absolutive used connecting *i* (seṭ-style) before *tvā*.

    Returns:
        True  — form ends in ...itvā (iṭ before ktvā / tvā allomorph)
        False — ...ktvā or ...tvā without that *i* (aniṭ tendency)
        None  — non-primary pattern (causative -yitvā, desiderative, etc.)
    """
    if not form_iast:
        return None
    f = form_iast.strip()
    if not f.endswith("tvā"):
        return None
    # Desiderative gerund: ...iṣitvā / ...ṣitvā (skip — derivative)
    if "iṣitvā" in f or re.search(r"[iī]ṣitvā$", f):
        return None
    # Causative: ...ayitvā / ...yitvā (derivative)
    if re.search(r"[aā]yitvā$", f) or f.endswith("yitvā"):
        return None
    if f.endswith("itvā"):
        return True
    if f.endswith("ktvā"):
        return False
    # e.g. gatvā, uktvā, śrutvā — no iṭ vowel before tvā
    return False


def load_adverb_primary_gerund_set_hints(
    csv_path: str | None = None,
) -> dict[str, bool]:
    """Build root → True (seṭ) / False (aniṭ) from adverbs.csv primary gerunds.

    When multiple rows disagree, majority wins; ties prefer True (seṭ), the
    statistically safer default for Sanskrit primary gerunds.
    """
    if csv_path is None:
        csv_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "adverbs.csv"
        )
    votes: dict[str, list[bool]] = {}
    try:
        with open(csv_path, "r", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                if (row.get("pos") or "").strip() != _GERUND_POS:
                    continue
                if (row.get("modification") or "").strip():
                    continue
                form = (row.get("form_IAST") or "").strip()
                root_key = normalize_corpus_root(row.get("root_IAST") or "")
                if not root_key or not form:
                    continue
                hint = classify_primary_gerund_connecting_i(form)
                if hint is None:
                    continue
                votes.setdefault(root_key, []).append(hint)
    except OSError:
        return {}

    out: dict[str, bool] = {}
    for root_key, lst in votes.items():
        c = Counter(lst)
        true_n, false_n = c.get(True, 0), c.get(False, 0)
        if true_n > false_n:
            out[root_key] = True
        elif false_n > true_n:
            out[root_key] = False
        else:
            out[root_key] = True
    return out


def load_parts_past_stems_by_root(
    csv_path: str | None = None,
) -> dict[tuple[str, str, str], list[str]]:
    """Index parts.csv past participles for validation.

    Key: (normalized_root_IAST, class_str, voice) where voice is 'pass' | 'active'.
    Value: list of attested stem_IAST strings (may include duplicates).
    """
    if csv_path is None:
        csv_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "parts.csv"
        )
    index: dict[tuple[str, str, str], list[str]] = {}
    try:
        with open(csv_path, "r", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                if (row.get("mode") or "").strip() != "past":
                    continue
                voice = (row.get("voice") or "").strip()
                if voice not in ("pass", "active"):
                    continue
                mod = (row.get("modification") or "").strip()
                if mod:
                    continue
                root_key = normalize_corpus_root(row.get("root_IAST") or "")
                cls = (row.get("class") or "").strip()
                stem = (row.get("stem_IAST") or "").strip()
                if not root_key or not stem:
                    continue
                key = (root_key, cls, voice)
                index.setdefault(key, []).append(stem)
    except OSError:
        return {}
    return index


def extract_ppp_masc_from_krdanta_block(block: str) -> str | None:
    """Parse first masculine PPP surface from KrdantaEngine.generate_block output."""
    lines = block.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "Past Passive Participle" and i + 1 < len(lines):
            nxt = lines[i + 1].strip()
            # "dyūta m. n. dyūtā f." or "gata m. n. gatā f."
            if " m. n. " in nxt:
                return nxt.split(" m. n. ")[0].strip()
            return nxt.split()[0].strip() if nxt else None
    return None


def extract_pp_act_masc_from_krdanta_block(block: str) -> str | None:
    """Parse first masculine past-active participle stem from krdanta block."""
    lines = block.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "Past Active Participle" and i + 1 < len(lines):
            nxt = lines[i + 1].strip()
            if " m. n. " in nxt:
                return nxt.split(" m. n. ")[0].strip()
            return nxt.split()[0].strip() if nxt else None
    return None
