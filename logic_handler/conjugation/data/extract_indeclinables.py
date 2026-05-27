"""
Extract particles, gerunds, and indeclinable forms from SL_morph.xml.

Categories extracted (per dnt.txt DTD):
  <uf>  — indeclinable form wrapper, contains:
    ind    – adverb/indeclinable
    interj – interjection
    parti  – particle
    prep   – preposition/preverb used independently
    conj   – conjunction
    tasil  – adverbs of manner in -tas
  <avya> – right component of avyayībhāva compound
  <vu>   — undeclinable verbal form, contains <cj> + <iv>:
    <iv> contains:
      abs  – absolutive / gerund (-ya, -tvā, -ṇamul)
      inf  – infinitive (-tum)
      per  – periphrastic perfect (verbal indeclinable)

Output: indeclinables.csv  (UTF-8, with BOM for Excel)
Columns:
  form_slp1, form_iast, category, subtype, conjugation, stem_slp1, stem_iast
"""

import re
import csv
import sys
import os

# ---------------------------------------------------------------------------
# SLP1 → IAST  (Heritage/INRIA scheme used by Gérard Huet's Sanskrit Library)
# Source: logic_handler/conjugation/data/transliterate.py
# ---------------------------------------------------------------------------
SLP1_TO_IAST = {
    # vowels
    "a": "a",  "A": "ā",  "i": "i",  "I": "ī",
    "u": "u",  "U": "ū",  "f": "ṛ",  "F": "ṝ",
    "x": "ḷ",  "X": "ḹ",
    "e": "e",  "E": "ai",
    "o": "o",  "O": "au",
    # consonants – velar
    "k": "k",  "K": "kh", "g": "g",  "G": "gh", "N": "ṅ",
    # palatal
    "c": "c",  "C": "ch", "j": "j",  "J": "jh", "Y": "ñ",
    # retroflex
    "w": "ṭ",  "W": "ṭh", "q": "ḍ",  "Q": "ḍh", "R": "ṇ",
    # dental
    "t": "t",  "T": "th", "d": "d",  "D": "dh", "n": "n",
    # labial
    "p": "p",  "P": "ph", "b": "b",  "B": "bh", "m": "m",
    # semivowels
    "y": "y",  "r": "r",  "l": "l",  "v": "v",
    # sibilants + aspirate
    "S": "ś",  "z": "ṣ",  "s": "s",  "h": "h",
    # special
    "M": "ṃ",  "H": "ḥ",  "~": "̃",
    # Heritage-specific: F used for ñ in DTD consonant listing
    # (Y is standard SLP1 for ñ; keep F→ṝ as long vowel above is correct;
    #  if a word shows F in consonantal position it maps ñ via explicit check)
}

# The DTD consonant row lists 'F' in the palatal series position for ñ,
# but the project's transliterate.py uses 'Y'=ñ and 'F'=ṝ (long ṛ vowel).
# We keep the project mapping as authoritative.

def slp1_to_iast(text: str) -> str:
    """Transliterate a SLP1 string to IAST Unicode."""
    out = []
    for ch in text:
        out.append(SLP1_TO_IAST.get(ch, ch))
    return "".join(out)


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------
FORM_RE    = re.compile(r'<f form="([^"]+)">')
STEM_RE    = re.compile(r'<s stem="([^"]+)"/>')
UF_RE      = re.compile(r'<uf>(.+?)</uf>')
VU_RE      = re.compile(r'<vu>(.+?)</vu>')
CJ_RE      = re.compile(r'<cj><(prim|ca|int|des)/></cj>')

UF_SUBTYPES = {
    "ind":    "indeclinable (adverb)",
    "interj": "interjection",
    "parti":  "particle",
    "prep":   "preposition",
    "conj":   "conjunction",
    "tasil":  "adverb-in-tas",
}
VU_SUBTYPES = {
    "abs": "absolutive/gerund",
    "inf": "infinitive",
    "per": "periphrastic-perfect",
}
CJ_LABELS = {
    "prim": "primary",
    "ca":   "causative",
    "int":  "intensive",
    "des":  "desiderative",
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def extract(xml_path: str, out_path: str) -> None:
    total = 0
    uf_count  = 0
    vu_count  = 0
    avya_count = 0

    rows = []

    print(f"Reading {xml_path} …", flush=True)

    with open(xml_path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if lineno % 200_000 == 0:
                print(f"  … {lineno:,} lines processed ({len(rows):,} records so far)",
                      flush=True)

            # Every data line starts with <f form=
            if "<f form=" not in line:
                continue

            form_m = FORM_RE.search(line)
            stem_m = STEM_RE.search(line)
            if not form_m:
                continue

            form_slp1 = form_m.group(1)
            stem_slp1 = stem_m.group(1) if stem_m else ""

            # Strip homonymy index from stem (#n suffix)
            stem_clean = re.sub(r"#\d+$", "", stem_slp1)

            form_iast  = slp1_to_iast(form_slp1)
            stem_iast  = slp1_to_iast(stem_clean)

            # ---- <uf> indeclinable forms ------------------------------------
            uf_m = UF_RE.search(line)
            if uf_m:
                inner = uf_m.group(1)
                for tag, label in UF_SUBTYPES.items():
                    if f"<{tag}/>" in inner:
                        rows.append({
                            "form_slp1":   form_slp1,
                            "form_iast":   form_iast,
                            "category":    "indeclinable",
                            "subtype":     label,
                            "conjugation": "",
                            "stem_slp1":   stem_clean,
                            "stem_iast":   stem_iast,
                        })
                        uf_count += 1
                        break

            # ---- <avya> right-component of avyayībhāva ---------------------
            # avya can appear inside <f> or as standalone child
            if "<avya/>" in line and "<uf>" not in line:
                rows.append({
                    "form_slp1":   form_slp1,
                    "form_iast":   form_iast,
                    "category":    "avyayibhava",
                    "subtype":     "avyayibhava-component",
                    "conjugation": "",
                    "stem_slp1":   stem_clean,
                    "stem_iast":   stem_iast,
                })
                avya_count += 1

            # ---- <vu> undeclinable verbal forms (abs / inf / per) ----------
            vu_m = VU_RE.search(line)
            if vu_m:
                inner = vu_m.group(1)
                cj_m  = CJ_RE.search(inner)
                cj    = CJ_LABELS.get(cj_m.group(1), "primary") if cj_m else "primary"

                for tag, label in VU_SUBTYPES.items():
                    if f"<{tag}/>" in inner:
                        rows.append({
                            "form_slp1":   form_slp1,
                            "form_iast":   form_iast,
                            "category":    "verbal-indeclinable",
                            "subtype":     label,
                            "conjugation": cj,
                            "stem_slp1":   stem_clean,
                            "stem_iast":   stem_iast,
                        })
                        vu_count += 1
                        break

    print(f"\nExtracted:")
    print(f"  <uf>  indeclinables : {uf_count:>8,}")
    print(f"  <avya> components   : {avya_count:>8,}")
    print(f"  <vu>  verbal forms  : {vu_count:>8,}")
    print(f"  TOTAL               : {len(rows):>8,}")

    # Write CSV (UTF-8 with BOM so Excel opens it correctly)
    fieldnames = ["form_slp1", "form_iast", "category", "subtype",
                  "conjugation", "stem_slp1", "stem_iast"]

    with open(out_path, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved → {out_path}")


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    xml  = os.path.join(base, "SL_morph.xml")
    out  = os.path.join(base, "indeclinables.csv")
    extract(xml, out)
