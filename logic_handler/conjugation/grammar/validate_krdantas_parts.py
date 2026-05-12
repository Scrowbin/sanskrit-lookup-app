#!/usr/bin/env python3
"""Validate krdantas.py PPP / past-active stems against parts.csv (mode=past).

Usage (from this directory)::

  python validate_krdantas_parts.py [--limit N] [--root gam]

Checks:

- ``parts.csv`` rows with ``mode=past``, empty ``modification``:
  - ``voice=pass`` — PPP stem (stem_IAST minus ``ta``) vs ``KrdantaEngine`` block
  - ``voice=active`` — past active stem (stem_IAST minus ``tavat``) vs block

Roots with ``RootObject.is_odit`` (P. 8.2.45, o-it: ``t`` not ``ṅ`` before kta in
the classical pattern) are tagged in output as ``[odit]`` when INRIA shows
forms like ``modita`` / ``codita``.

Exit code **1** means “at least one PPP or pp_act mismatch” (not a Python crash).
Use for CI only after the engine catches up; until then expect a non-zero exit.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conjugate import SanskritConjugator
from corpus_lexical_hints import (
    extract_pp_act_masc_from_krdanta_block,
    extract_ppp_masc_from_krdanta_block,
    normalize_corpus_root,
)
from dhatupatha_analyzer import DHATUPATHA_ANALYZER


def _engine_root(root_iast: str) -> str:
    return normalize_corpus_root(root_iast.split("#")[0])


def _infer_default_class(parts_path: str) -> dict[str, int]:
    """Map root_IAST (as in parts) -> int class from first pres/para row with class set."""
    out: dict[str, int] = {}
    with open(parts_path, "r", encoding="utf-8") as fp:
        for row in csv.DictReader(fp):
            if (row.get("mode") or "").strip() != "pres":
                continue
            if (row.get("voice") or "").strip() != "para":
                continue
            cls_s = (row.get("class") or "").strip()
            if not cls_s:
                continue
            root_iast = (row.get("root_IAST") or "").strip()
            if not root_iast or root_iast in out:
                continue
            try:
                out[root_iast] = int(cls_s)
            except ValueError:
                continue
    return out


def _build_ppp_expectations(parts_path: str) -> dict[tuple[str, int], set[str]]:
    """(engine_root, class_int) -> set of attested masculine PPP stems (full …ta)."""
    default_cls = _infer_default_class(parts_path)
    out: dict[tuple[str, int], set[str]] = {}
    with open(parts_path, "r", encoding="utf-8") as fp:
        for row in csv.DictReader(fp):
            if (row.get("mode") or "").strip() != "past":
                continue
            if (row.get("modification") or "").strip():
                continue
            if (row.get("voice") or "").strip() != "pass":
                continue
            stem = (row.get("stem_IAST") or "").strip()
            if not stem.endswith("ta"):
                continue
            cls_s = (row.get("class") or "").strip()
            root_iast = (row.get("root_IAST") or "").strip()
            if not root_iast:
                continue
            if cls_s:
                try:
                    class_num = int(cls_s)
                except ValueError:
                    continue
            else:
                class_num = default_cls.get(root_iast, 1)
            key = (_engine_root(root_iast), class_num)
            out.setdefault(key, set()).add(stem)
    return out


def _build_pp_act_expectations(parts_path: str) -> dict[tuple[str, int], set[str]]:
    """(engine_root, class_int) -> set of attested …tavat stems."""
    default_cls = _infer_default_class(parts_path)
    out: dict[tuple[str, int], set[str]] = {}
    with open(parts_path, "r", encoding="utf-8") as fp:
        for row in csv.DictReader(fp):
            if (row.get("mode") or "").strip() != "past":
                continue
            if (row.get("modification") or "").strip():
                continue
            if (row.get("voice") or "").strip() != "active":
                continue
            stem = (row.get("stem_IAST") or "").strip()
            if not stem.endswith("tavat"):
                continue
            cls_s = (row.get("class") or "").strip()
            root_iast = (row.get("root_IAST") or "").strip()
            if not root_iast:
                continue
            if cls_s:
                try:
                    class_num = int(cls_s)
                except ValueError:
                    continue
            else:
                class_num = default_cls.get(root_iast, 1)
            key = (_engine_root(root_iast), class_num)
            out.setdefault(key, set()).add(stem)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=0, help="Max unique (root,class) keys (0=all)")
    ap.add_argument("--root", type=str, default="", help="Filter: engine root must contain this substring")
    args = ap.parse_args()

    parts_path = os.path.join(os.path.dirname(__file__), "..", "data", "parts.csv")
    ppp_exp = _build_ppp_expectations(parts_path)
    pp_act_exp = _build_pp_act_expectations(parts_path)
    conj = SanskritConjugator()

    mismatches = 0
    keys = sorted(set(ppp_exp) | set(pp_act_exp))
    if args.root:
        keys = [k for k in keys if args.root in k[0]]
    if args.limit:
        keys = keys[: args.limit]

    for root_str, class_num in keys:
        block = conj.get_krdantas_block(root_str, class_num, use_db=False)
        got_ppp = extract_ppp_masc_from_krdanta_block(block)
        got_act = extract_pp_act_masc_from_krdanta_block(block)

        if (root_str, class_num) in ppp_exp:
            exp_set = ppp_exp[(root_str, class_num)]
            if got_ppp not in exp_set:
                ro = DHATUPATHA_ANALYZER.get(root_str, class_num)
                tag = " [odit]" if ro.is_odit else ""
                print(
                    f"PPP mismatch{tag}: {root_str!r} class {class_num}\n"
                    f"  parts: {sorted(exp_set)}\n"
                    f"  engine: {got_ppp!r}"
                )
                mismatches += 1

        if (root_str, class_num) in pp_act_exp:
            exp_set = pp_act_exp[(root_str, class_num)]
            if got_act not in exp_set:
                ro = DHATUPATHA_ANALYZER.get(root_str, class_num)
                tag = " [odit]" if ro.is_odit else ""
                print(
                    f"pp_act mismatch{tag}: {root_str!r} class {class_num}\n"
                    f"  parts: {sorted(exp_set)}\n"
                    f"  engine: {got_act!r}"
                )
                mismatches += 1

    print(f"\nUnique (root,class) keys checked: {len(keys)}; mismatches={mismatches}")
    return 0 if mismatches == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
