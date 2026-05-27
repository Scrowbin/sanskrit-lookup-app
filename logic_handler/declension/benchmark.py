import csv
import sys
import io
import time
import re
import xml.etree.ElementTree as ET
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── Import the actual declension engine ──────────────────────────────────────
sys.path.insert(0, ".")
from engine import DeclensionEngine, CASES, NUMBERS

from indic_transliteration import sanscript

def slp1_to_iast(text: str) -> str:
    """Convert a standard SLP1-encoded string to IAST using indic-transliteration."""
    if not text:
        return text
    # Word-final s/r → visarga (underlying form → surface)
    if len(text) > 1 and (text.endswith("s") or text.endswith("r")):
        text = text[:-1] + "H"
    return sanscript.transliterate(text, sanscript.SLP1, sanscript.IAST)


# Valid single-codepoint IAST output chars.
_VALID_IAST = frozenset(
    "aāiīuūṛṝḷḹeoṃḥ"
    "kgcjṭḍṇtdpbmnyrlvśṣshṅñḻ "
)

def _is_clean_iast(text: str) -> bool:
    """Return False if text contains any character not in the IAST alphabet."""
    return all(ch in _VALID_IAST for ch in text)


# ── Tag mapping: XML → engine format ─────────────────────────────────────────
_GENDER_MAP  = {"mas": "m",   "neu": "n",   "fem": "f"}
_CASE_MAP    = {"nom": "Nom", "acc": "Acc", "ins": "Ins",
                "dat": "Dat", "abl": "Abl", "gen": "Gen",
                "loc": "Loc", "voc": "Voc"}
_NUMBER_MAP  = {"sg": "Sg",   "du": "Du",   "pl": "Pl"}


# ── Benchmark ─────────────────────────────────────────────────────────────────
def run_xml_nominal_benchmark(xml_file_path: str, failures_csv: str | None = None):
    xml_path = Path(xml_file_path)
    if failures_csv is None:
        failures_csv = str(xml_path.parent / "benchmark_failures.csv")

    print(f"Loading gold standard paradigms from {xml_file_path}...")
    t_start = time.perf_counter()

    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
    except Exception as e:
        print(f"💥 Failed to parse XML file: {e}")
        return

    print("Compiling DeclensionEngine (may take a few seconds)...")
    engine = DeclensionEngine()

    totals      = {"pass": 0, "fail": 0, "error": 0}
    failed_cases: list[dict] = []

    paradigm_cache: dict[tuple[str, str], dict] = {}

    print("Running declension benchmark...\n")

    for f_tag in root.findall("f"):
        form_slp1 = f_tag.get("form", "")
        expected  = slp1_to_iast(form_slp1)
        if not _is_clean_iast(expected):
            continue

        s_tag = f_tag.find("s")
        if s_tag is None:
            continue

        stem_slp1 = s_tag.get("stem", "")
        stem_slp1_clean = re.sub(r"#\d+$", "", stem_slp1)
        stem_iast       = slp1_to_iast(stem_slp1_clean)
        
        if not _is_clean_iast(stem_iast):
            continue
            
        stem_iast = stem_iast.replace("ḥ", "s") if stem_iast.endswith("ḥ") else stem_iast

        for na_tag in f_tag.findall("na"):
            case = number = gender = None
            for child in na_tag:
                t = child.tag
                if   t in _CASE_MAP:    case   = _CASE_MAP[t]
                elif t in _NUMBER_MAP:  number = _NUMBER_MAP[t]
                elif t in _GENDER_MAP:  gender = _GENDER_MAP[t]

            if not all([case, number, gender]):
                continue

            cache_key = (stem_iast, gender)
            try:
                if cache_key not in paradigm_cache:
                    paradigm_cache[cache_key] = engine.declense(stem_iast, gender)
                paradigm = paradigm_cache[cache_key]

                actual_forms = paradigm.get((case, number), [])
                actual_forms = [f.strip() for f in actual_forms]

                if expected in actual_forms:
                    totals["pass"] += 1
                else:
                    totals["fail"] += 1
                    failed_cases.append({
                        "stem":     stem_iast,
                        "gender":   gender,
                        "case":     case,
                        "number":   number,
                        "expected": expected,
                        "actual":   " OR ".join(actual_forms) if actual_forms else "NO PATH",
                    })

            except Exception as e:
                totals["error"] += 1
                failed_cases.append({
                    "stem":     stem_iast,
                    "gender":   gender,
                    "case":     case,
                    "number":   number,
                    "expected": expected,
                    "actual":   f"CRASHED: {e}",
                })

    # ── Report ────────────────────────────────────────────────────────────────
    t_total    = time.perf_counter() - t_start
    total_tests = sum(totals.values())
    accuracy    = (totals["pass"] / total_tests * 100) if total_tests else 0.0

    print("\n" + "=" * 52)
    print("         NOMINAL DECLENSION BENCHMARK RESULTS")
    print("=" * 52)
    print(f"  ✅ Pass:          {totals['pass']:>6}  ({accuracy:.1f}%)")
    print(f"  ❌ Fail:          {totals['fail']:>6}")
    print(f"  💥 Crash:         {totals['error']:>6}")
    print(f"  ⏱  Total time:    {t_total:.2f}s")
    print("=" * 52)

    if failed_cases:
        print("\n❌ Sample Mismatches (first 15):")
        print(f"  {'Stem':<12} {'Gen/Case/Num':<16} {'Expected':<14} {'Actual (FST)'}")
        print("  " + "-" * 70)
        for fc in failed_cases[:15]:
            feat = f"{fc['gender']}/{fc['case']}/{fc['number']}"
            print(f"  {fc['stem']:<12} {feat:<16} {fc['expected']:<14} {fc['actual']}")
        if len(failed_cases) > 15:
            print(f"  ... and {len(failed_cases) - 15} more.")

        with open(failures_csv, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=["stem", "gender", "case", "number", "expected", "actual"],
            )
            writer.writeheader()
            writer.writerows(failed_cases)
        print(f"\n📄 Full failure list saved to: {failures_csv}")
    else:
        print("\n🎉 No failures — nothing to save.")


if __name__ == "__main__":
    run_xml_nominal_benchmark("./grammar/data/SL_morph.xml")