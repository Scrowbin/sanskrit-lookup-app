"""
inria_parser.py — Parse INRIA Sanskrit Grammarian conjugation HTML pages.

The INRIA site uses Anubis JavaScript proof-of-work bot protection.
curl/urllib cannot pass it. Fetch pages in a browser instead:

  1. Open: https://sanskrit.inria.fr/cgi-bin/SKT/sktconjug.cgi?lex=SH&q=<velthuis_root>&t=VH&c=<class>&font=roma
  2. File → Save Page As… → <root>_<class>.html  (save to the grammar directory)
  3. Run:  python inria_parser.py <root>_<class>.html

Velthuis encoding:  ā→aa  ī→ii  ū→uu  ṛ→.r  ṅ→"n  ñ→~n  ṭ→.t  ḍ→.d  ṇ→.n
                    ś→sh  ṣ→.s  ḥ→.h  ṃ→.m

Examples:
  bhū cl.1  → q=bhuu&c=1
  gam cl.1  → q=gam&c=1
  kṛ  cl.8  → q=k.r&c=8
  nī  cl.1  → q=nii&c=1
  dā  cl.3  → q=daa&c=3
  vac cl.2  → q=vac&c=2
  yaj cl.1  → q=yaj&c=1

HTML structure:
  Top-level sections are separated by: <table class="cyan_cent">
    <span class="b2">Primary Conjugation</span>
    <span class="b2">Causative Conjugation</span>
    <span class="b2">Intensive Conjugation</span>
    <span class="b2">Desiderative Conjugation</span>

  Within each section:
    Finite tenses:  <span class="b2">Present|Imperfect|Optative|Imperative|
                                      Future|Future2|Perfect|Aorist|Injunctive</span>
    Participles:    <span class="b2">Participles</span>
                      <h3 class="b3">Past Passive Participle<br>
                        <span class="red">form</span> ...
    Indeclinables:  <span class="b2">Indeclinable forms</span>
                      <h3 class="b3">Infinitive<br><span class="red">form</span>
                      <h3 class="b3">Absolutive<br><span class="red">form</span>

  Within finite tense tables:
    Voice sub-tables: <span class="b3">Active|Middle|Passive</span>
    Person rows:      <span class="b3">First|Second|Third</span>
    Forms:            <span class="red">form</span>  (multiple = alternatives)
"""

import sys
import io
import re
import os
import json
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


# ══════════════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════════════

PERSON_MAP  = {"First": "1", "Second": "2", "Third": "3"}
NUMBER_MAP  = {0: "sg", 1: "du", 2: "pl"}

INRIA_TO_ENGINE_TENSE = {
    "Present":     "present",
    "Imperfect":   "imperfect",
    "Optative":    "optative",
    "Imperative":  "imperative",
    "Future":      "future",
    "Future2":     "periphrastic_future",
    "Perfect":     "perfect",
    "Aorist":      "aorist",
    "Injunctive":  "injunctive",
    "Conditional": "conditional",
}

INRIA_TO_ENGINE_VOICE = {
    "Active":  "active",
    "Middle":  "middle",
    "Passive": "passive",
}

# Participle type → label in INRIA h3 headers
PARTICIPLE_LABELS = {
    "Past Passive Participle":      "ppp",
    "Past Active Participle":       "pp_act",
    "Present Active Participle":    "prp_act",
    "Present Middle Participle":    "prp_mid",
    "Present Passive Participle":   "prp_pass",
    "Future Active Participle":     "futp_act",
    "Future Middle Participle":     "futp_mid",
    "Future Passive Participle":    "fpp",
    "Perfect Active Participle":    "perf_act",
    "Perfect Middle Participle":    "perf_mid",
}

INDECLINABLE_LABELS = {
    "Infinitive":           "inf",
    "Absolutive":           "abs",      # may appear twice (-tvā and -ya)
    "Periphrastic Perfect": "perf_peri",
}


# ══════════════════════════════════════════════════════════════════════════════
# HTML Utilities
# ══════════════════════════════════════════════════════════════════════════════

def _strip_tags(html: str) -> str:
    """Remove all HTML tags, decode basic entities."""
    html = re.sub(r'<[^>]+>', '', html)
    html = html.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&nbsp;', ' ')
    return html.strip()

def _red_spans(html: str) -> list[str]:
    """Extract all <span class="red">…</span> text from a chunk of HTML."""
    return [f.strip() for f in re.findall(r'<span class="red">([^<]+)</span>', html) if f.strip()]


# ══════════════════════════════════════════════════════════════════════════════
# Section Isolation
# ══════════════════════════════════════════════════════════════════════════════

def _isolate_section(html: str, section_name: str) -> str | None:
    """
    Return the HTML content of a named top-level section.
    Sections are delimited by <table class="cyan_cent"> headers.
    """
    # Split the full HTML at each cyan_cent table boundary
    parts = re.split(r'<table class="cyan_cent">', html)
    # parts[0] = page preamble (skip)
    # parts[1..] = each section, starting with its header content

    for part in parts[1:]:
        # Check if this chunk's b2 span matches our target section
        m = re.search(r'<span class="b2">([^<]+)</span>', part)
        if m and m.group(1).strip() == section_name:
            return part

    return None


# ══════════════════════════════════════════════════════════════════════════════
# Finite Conjugation Parser
# ══════════════════════════════════════════════════════════════════════════════

def parse_finite_tenses(section_html: str) -> dict:
    """
    Parse all finite tense/voice tables from a section chunk.

    Returns:
      { (tense_raw, voice_raw): { (person, number): [form, ...] } }
    """
    result = {}

    # Split on b2 spans to find each tense block
    tense_parts = re.split(r'<span class="b2">([^<]+)</span>', section_html)

    for i in range(1, len(tense_parts), 2):
        tense_raw   = tense_parts[i].strip()
        tense_chunk = tense_parts[i + 1]

        # Only process known finite tenses
        if tense_raw not in INRIA_TO_ENGINE_TENSE:
            continue

        # Split on voice headers (Active / Middle / Passive)
        voice_parts = re.split(r'<span class="b3">(Active|Middle|Passive)</span>', tense_chunk)

        for j in range(1, len(voice_parts), 2):
            voice_raw   = voice_parts[j].strip()
            voice_chunk = voice_parts[j + 1]

            key = (tense_raw, voice_raw)
            result[key] = {}

            # Split on person rows (First / Second / Third)
            person_parts = re.split(r'<span class="b3">(First|Second|Third)</span>', voice_chunk)

            for k in range(1, len(person_parts), 2):
                person_raw   = person_parts[k]
                cell_chunk   = person_parts[k + 1]
                person       = PERSON_MAP[person_raw]

                # Find the three <th>…</th> cells (Sg, Du, Pl)
                cells = re.findall(r'<th>(.*?)</th>', cell_chunk, re.DOTALL)

                for col_idx in range(min(3, len(cells))):
                    number = NUMBER_MAP[col_idx]
                    forms  = _red_spans(cells[col_idx])
                    if forms:
                        result[key][(person, number)] = forms

    return result


# ══════════════════════════════════════════════════════════════════════════════
# Participles Parser
# ══════════════════════════════════════════════════════════════════════════════

def parse_participles(section_html: str) -> dict:
    """
    Parse the Participles sub-section.

    Returns:
      { participle_type_label: [form_m, form_f, ...] }
      e.g. { "ppp": ["bhūta", "bhūtā"], "prp_act": ["bhavant", "bhavantī"], ... }
    """
    result = {}

    # Find the Participles b2 block
    m = re.search(r'<span class="b2">Participles</span>(.*?)(?=<span class="b2">|$)',
                  section_html, re.DOTALL)
    if not m:
        return result

    participles_chunk = m.group(1)

    # Each participle is in an <h3 class="b3">Name<br>…forms…</h3>
    for h3_match in re.finditer(r'<h3 class="b3">([^<]+)<br>\s*(.*?)</h3>', participles_chunk, re.DOTALL):
        label_text = h3_match.group(1).strip()
        forms_html = h3_match.group(2)

        type_key = PARTICIPLE_LABELS.get(label_text)
        if type_key is None:
            continue  # unrecognised label

        forms = _red_spans(forms_html)
        if forms:
            # If this label already exists (e.g. multiple FPP variants), append
            if type_key in result:
                result[type_key].extend(f for f in forms if f not in result[type_key])
            else:
                result[type_key] = forms

    return result


# ══════════════════════════════════════════════════════════════════════════════
# Indeclinable Forms Parser
# ══════════════════════════════════════════════════════════════════════════════

def parse_indeclinables(section_html: str) -> dict:
    """
    Parse the Indeclinable forms sub-section.

    Returns:
      { "inf": ["form"], "abs": ["form1", "form2"], "perf_peri": ["form"] }
    """
    result = {}

    m = re.search(r'<span class="b2">Indeclinable forms</span>(.*?)(?=<span class="b2">|$)',
                  section_html, re.DOTALL)
    if not m:
        return result

    chunk = m.group(1)
    abs_forms = []

    for h3_match in re.finditer(r'<h3 class="b3">([^<]+)<br>\s*(.*?)</h3>', chunk, re.DOTALL):
        label_text = h3_match.group(1).strip()
        forms_html = h3_match.group(2)
        forms = _red_spans(forms_html)

        if label_text == "Infinitive":
            result["inf"] = forms
        elif label_text == "Absolutive":
            abs_forms.extend(forms)  # collect both -tvā and -ya forms
        elif label_text == "Periphrastic Perfect":
            result["perf_peri"] = forms

    if abs_forms:
        result["abs"] = abs_forms

    return result


# ══════════════════════════════════════════════════════════════════════════════
# Master Parser
# ══════════════════════════════════════════════════════════════════════════════

def parse_inria_html(html: str, section: str = "Primary Conjugation") -> dict:
    """
    Parse an INRIA page and return all data for the requested section.

    Returns a dict with keys:
      "finite"       → { (tense_raw, voice_raw): { (person, number): [forms] } }
      "participles"  → { type_key: [forms] }
      "indeclinables"→ { type_key: [forms] }
    """
    section_html = _isolate_section(html, section)
    if section_html is None:
        print(f"  ⚠  Section '{section}' not found in HTML.")
        return {"finite": {}, "participles": {}, "indeclinables": {}}

    return {
        "finite":        parse_finite_tenses(section_html),
        "participles":   parse_participles(section_html),
        "indeclinables": parse_indeclinables(section_html),
    }


def extract_root_from_html(html: str) -> tuple[str, str]:
    """Extract root and class from the page title, e.g. bhū_1."""
    m = re.search(r'<i>([^_<]+)_(\d+)</i>', html)
    if m:
        return m.group(1), m.group(2)
    return "?", "?"


# ══════════════════════════════════════════════════════════════════════════════
# Engine Comparison
# ══════════════════════════════════════════════════════════════════════════════

def compare_with_engine(data: dict, root: str, cls: int, section: str = "Primary Conjugation"):
    """
    Compare all INRIA forms against the local engine and print a report.
    """
    try:
        from conjugate import SanskritConjugator
        engine = SanskritConjugator()
    except ImportError:
        print("  [skip] conjugate not importable — showing INRIA data only")
        engine = None

    total_pass = total_fail = 0

    # ── 1. Finite Tenses ─────────────────────────────────────────────────────
    for (tense_raw, voice_raw), forms_dict in sorted(data["finite"].items()):
        engine_tense = INRIA_TO_ENGINE_TENSE.get(tense_raw)
        engine_voice = INRIA_TO_ENGINE_VOICE.get(voice_raw)
        if engine_tense is None or engine_voice is None:
            continue

        print(f"\n  ── {tense_raw} {voice_raw} ──")

        for (person, number), inria_forms in sorted(forms_dict.items()):
            inria_str = " / ".join(inria_forms)

            if engine is None:
                print(f"    {person}{number}  {inria_str}")
                continue

            try:
                result = engine.conjugate(root, cls, person, number,
                                          engine_voice, engine_tense, use_db=False)
                engine_forms = {f.strip() for f in result.split(" OR ")}
                ok = any(f in engine_forms for f in inria_forms)

                sym = "✅" if ok else "❌"
                print(f"    {sym} {person}{number}  engine={result!r:30}  inria={inria_str!r}")
                if ok:
                    total_pass += 1
                else:
                    total_fail += 1
            except Exception as e:
                print(f"    💥 {person}{number}  ERROR: {e}")
                total_fail += 1

    # ── 2. Participles ───────────────────────────────────────────────────────
    if data["participles"]:
        print(f"\n  ── Participles ──")
        if engine:
            try:
                block = engine.conjugate(root, cls, "3", "sg", "active", "krdantas", use_db=False)
            except Exception as e:
                block = f"ERROR: {e}"
        else:
            block = ""

        for type_key, forms in sorted(data["participles"].items()):
            forms_str = "  /  ".join(forms)
            if engine:
                ok = any(f in block for f in forms)
                sym = "✅" if ok else "❌"
                print(f"    {sym} [{type_key}]  inria={forms_str!r}")
            else:
                print(f"    [{type_key}]  {forms_str}")
            if engine:
                if ok: total_pass += 1
                else:  total_fail += 1

    # ── 3. Indeclinables ────────────────────────────────────────────────────
    if data["indeclinables"]:
        print(f"\n  ── Indeclinables ──")
        block = ""
        if engine:
            try:
                block = engine.conjugate(root, cls, "3", "sg", "active", "krdantas", use_db=False)
            except Exception:
                pass

        for type_key, forms in sorted(data["indeclinables"].items()):
            forms_str = "  /  ".join(forms)
            if engine:
                # Strip leading dash from preverb-form (-gamya → gamya match anywhere)
                ok = any(f.lstrip('-') in block for f in forms)
                sym = "✅" if ok else "❌"
                print(f"    {sym} [{type_key}]  inria={forms_str!r}")
            else:
                print(f"    [{type_key}]  {forms_str}")
            if engine:
                if ok: total_pass += 1
                else:  total_fail += 1

    print(f"\n  ══ {section}: ✅ {total_pass}  ❌ {total_fail} ══")
    return total_pass, total_fail


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    html_path = sys.argv[1]
    section   = sys.argv[2] if len(sys.argv) > 2 else "Primary Conjugation"
    dump_json = "--json" in sys.argv

    if not os.path.exists(html_path):
        print(f"File not found: {html_path}")
        sys.exit(1)

    html = Path(html_path).read_text(encoding='utf-8', errors='replace')
    root, cls_str = extract_root_from_html(html)
    print(f"\n  Root: {root}  Class: {cls_str}  Section: {section}")

    data = parse_inria_html(html, section)
    n_finite = len(data["finite"])
    n_part   = len(data["participles"])
    n_indecl = len(data["indeclinables"])
    print(f"  Parsed: {n_finite} tense/voice tables, {n_part} participle types, {n_indecl} indeclinable types")

    if dump_json:
        out = {
            "finite": {
                f"{t}|{v}": {f"{p}{n}": forms for (p, n), forms in cells.items()}
                for (t, v), cells in data["finite"].items()
            },
            "participles": data["participles"],
            "indeclinables": data["indeclinables"],
        }
        json_path = html_path.replace(".html", ".json")
        Path(json_path).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"  Saved JSON → {json_path}")
    else:
        try:
            cls_int = int(cls_str)
        except ValueError:
            cls_int = 1
        compare_with_engine(data, root, cls_int, section)
