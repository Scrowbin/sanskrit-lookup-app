#!/usr/bin/env python3
"""
extract_slp1_to_csv.py
----------------------
Parse SL_morph.xml (Gérard Huet / INRIA Heritage, SLP1 encoding) and emit a
CSV file with one row per nominal inflection:

  stem_iast, gender, case, number, form_iast

Only <na> (nominal/adjective) entries are extracted; verbal, participial, and
indeclinable entries are skipped.

Usage:
    python3 extract_slp1_to_csv.py            # uses default paths
    python3 extract_slp1_to_csv.py <xml> <csv>
"""

import csv
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from indic_transliteration import sanscript

# Valid IAST codepoints — used to filter out unmapped passthrough
_VALID_IAST: frozenset[str] = frozenset(
    "aāiīuūṛṝḷḹeoṃḥ"
    "kgcjṭḍṇtdpbmnyrlvśṣshṅñḻ "
)

def _is_clean_iast(text: str) -> bool:
    return all(ch in _VALID_IAST for ch in text)


def slp1_to_iast(text: str) -> str:
    """Convert an SLP1-encoded Sanskrit string to IAST using indic-transliteration."""
    if not text:
        return text
    # Underlying word-final s / r → visarga ḥ
    if text.endswith("s") or text.endswith("r"):
        text = text[:-1] + "H"   # H is visarga in SLP1
    return sanscript.transliterate(text, sanscript.SLP1, sanscript.IAST)


# ── Tag mappings ──────────────────────────────────────────────────────────────
_GENDER_MAP = {"mas": "m", "neu": "n", "fem": "f", "dei": "dei"}
_CASE_MAP   = {
    "nom": "Nom", "acc": "Acc", "ins": "Ins",
    "dat": "Dat", "abl": "Abl", "gen": "Gen",
    "loc": "Loc", "voc": "Voc",
}
_NUMBER_MAP = {"sg": "Sg", "du": "Du", "pl": "Pl"}


# ── Main ──────────────────────────────────────────────────────────────────────
def extract(xml_path: Path, csv_path: Path) -> None:
    print(f"Parsing {xml_path}  ({xml_path.stat().st_size / 1_000_000:.1f} MB)…")
    t0 = time.perf_counter()

    tree = ET.parse(xml_path)
    root = tree.getroot()

    print(f"  XML parsed in {time.perf_counter() - t0:.1f}s — writing CSV…")

    rows_written = 0
    skipped_no_na = 0

    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["stem_iast", "gender", "case", "number", "form_iast"])

        for f_tag in root.findall("f"):
            form_slp1 = f_tag.get("form", "")
            form_iast = slp1_to_iast(form_slp1)

            s_tag = f_tag.find("s")
            if s_tag is None:
                continue

            stem_slp1 = s_tag.get("stem", "")
            # Strip homonymy index (#1, #2, …)
            stem_slp1_clean = re.sub(r"#\d+$", "", stem_slp1)
            stem_iast = slp1_to_iast(stem_slp1_clean)
            # Skip if unmapped chars slipped through (Vedic forms, etc.)
            if not _is_clean_iast(form_iast) or not _is_clean_iast(stem_iast):
                skipped_no_na += 1
                continue
            # Stems are dictionary forms — undo accidental visarga on stems
            if stem_iast.endswith("ḥ"):
                stem_iast = stem_iast[:-1] + "s"

            na_tags = f_tag.findall("na")
            if not na_tags:
                skipped_no_na += 1
                continue

            for na_tag in na_tags:
                case = number = gender = None
                for child in na_tag:
                    t = child.tag
                    if   t in _CASE_MAP:    case   = _CASE_MAP[t]
                    elif t in _NUMBER_MAP:  number = _NUMBER_MAP[t]
                    elif t in _GENDER_MAP:  gender = _GENDER_MAP[t]

                if not all([case, number, gender]):
                    continue

                writer.writerow([stem_iast, gender, case, number, form_iast])
                rows_written += 1

    elapsed = time.perf_counter() - t0
    print(f"  Done in {elapsed:.1f}s")
    print(f"  Rows written : {rows_written:,}")
    print(f"  Non-nominal  : {skipped_no_na:,}  (skipped — verbal/indeclinable/etc.)")
    print(f"  Output       : {csv_path}")


if __name__ == "__main__":
    data_dir = Path(__file__).parent

    xml_path = Path(sys.argv[1]) if len(sys.argv) > 1 else data_dir / "SL_morph.xml"
    csv_path = Path(sys.argv[2]) if len(sys.argv) > 2 else data_dir / "nominal_forms_iast.csv"

    if not xml_path.exists():
        print(f"ERROR: XML not found: {xml_path}", file=sys.stderr)
        sys.exit(1)

    extract(xml_path, csv_path)
