import sys, io
# Force UTF-8 output so IAST characters render on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from conjugate import SanskritConjugator
import csv

def normalize_for_comparison(word):
    """Fixes INRIA's underlying 's' and 'r' to surface 'ḥ'."""
    if not word: return word
    if word.endswith('s') or word.endswith('r'):
        return word[:-1] + 'ḥ'
    return word

def run_focused_benchmark(csv_file="verbs_clean.csv", output_report="benchmark_failures.csv"):
    print("Loading INRIA database...")

    # ── INRIA lookup key includes derivation so primary and causative rows for
    # the same root don't overwrite each other.
    # Key: (stem_iast, tense, voice, person, number, derivation)
    # NOTE: INRIA uses "du" for dual, not "d".
    inria_db = {}
    with open(csv_file, mode='r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            key = (
                row['stem_iast'],
                row['tense'],
                row['voice'],
                row['person'],
                row['number'],        # "sg" / "du" / "pl"
                row['derivation'],    # "primary" / "causative" / "desiderative" / "intensive"
            )
            normalized = normalize_for_comparison(row['form_iast'])
            bucket = inria_db.setdefault(key, [])
            if normalized not in bucket:
                bucket.append(normalized)

    # ── Test suite ────────────────────────────────────────────────────────────
    # Each entry: (root_iast, primary_class, description)
    # The root_iast must match INRIA's stem_iast exactly.
    test_suite = [
        ("bhū",  1,  "Guna + Thematic / Standard Seṭ Future"),
        ("ad",   2,  "Athematic + Devoicing (atti / atsyati)"),
        ("hu",   3,  "Reduplication / a-Aorist / ṣ+dhv→ḍhv Sandhi (ahoḍhvam)"),
        ("div",  4,  "Internal Lengthening (dīvyati)"),
        ("su",   5,  "Athematic Sign (-nu/-no-)"),
        ("tud",  6,  "Thematic + No Guna / Aniṭ Luṭ (tottā)"),
        ("yuj",  7,  "Infix + Palatal Sandhi (yunakti / yokṣyati)"),
        ("tan",  8,  "Athematic Sign (-u/-o-)"),
        ("krī",  9,  "Athematic Sign (-nā/-nī-) + Nati (krīṇāti)"),
        ("cur",  10, "Causative-style (-aya-)"),
        ("kṛ",   8,  "Guṇa of ṛ + Ruki / ṣṭ Sandhi (akārṣṭam)"),
        ("budh", 1,  "Grassmann Throwback + Devoicing / iṣ-Aorist (abodhiṣam)"),
        ("duh",  2,  "Grassmann Throwback + H-Sandhi + Ruki (dhokṣyati)"),
        
        # --- New Edge Cases Added for Extended Coverage ---
        ("gam",  1,  "Suppletive Present (gaccha) / Root Aorist (agamat)"),
        ("dviṣ", 2,  "Aniṭ S-Aorist / Palatal Sandhi (adikṣat)"),
        ("muc",  6,  "Nasal Infix (muñca) / a-Aorist (amucat)"),
    ]

    # ── Derivation → how to call the FST ─────────────────────────────────────
    # "primary"     → api.conjugate(root, primary_class, ...)
    # "causative"   → api.conjugate(root, 10, ...) — causatives behave like cl10
    # "desiderative"→ not yet implemented; counted as UNSUPPORTED
    # "intensive"   → not yet implemented; counted as UNSUPPORTED
    UNSUPPORTED_DERIVATIONS = set()

    # ── Grammar space to iterate ──────────────────────────────────────────────
    ALL_TENSES  = ["present", "imperfect", "imperative", "optative",
                   "future", "conditional", "perfect", "periphrastic_future", "aorist", "injunctive"]
    ALL_VOICES  = ["active", "middle", "passive"]
    ALL_PERSONS = ["1", "2", "3"]
    ALL_NUMBERS = ["sg", "du", "pl"]   # INRIA uses "du", not "d"

    api = SanskritConjugator()

    # ── Counters ──────────────────────────────────────────────────────────────
    totals      = {"pass": 0, "fail": 0, "error": 0, "skip_inria": 0, "unsupported": 0, "impossible": 0}
    per_root    = {}   # root → same dict as totals
    failed_rows = []

    print("Running tests...")

    for root, primary_class, desc in test_suite:
        per_root[root] = {"pass": 0, "fail": 0, "error": 0,
                          "skip_inria": 0, "unsupported": 0, "impossible": 0}
        counts = per_root[root]

        # Iterate over BOTH primary and secondary derivations
        for derivation in ["primary", "causative", "desiderative", "intensive"]:

            # Map derivation → effective class for FST call
            if derivation == "primary":
                effective_class = primary_class
                fst_derivative = None
            elif derivation == "causative":
                effective_class = 10   # causative always behaves like cl10 (-aya-)
                fst_derivative = None
            elif derivation == "desiderative":
                effective_class = 1
                fst_derivative = "desiderative"
            else:
                effective_class = primary_class
                fst_derivative = derivation

            for tense in ALL_TENSES:
                for voice in ALL_VOICES:
                    for person in ALL_PERSONS:
                        for number in ALL_NUMBERS:

                            # Check for impossible combinations first
                            is_impossible = (voice == "passive" and tense in ("perfect", "future", "periphrastic_future", "conditional"))
                            
                            inria_key = (root, tense, voice, person, number, derivation)
                            if inria_key not in inria_db:
                                if is_impossible:
                                    counts["impossible"] += 1
                                    totals["impossible"] += 1
                                else:
                                    counts["skip_inria"] += 1
                                    totals["skip_inria"] += 1
                                continue

                            expected_forms = inria_db[inria_key]

                            # --- Unsupported derivation: record and skip FST call ---
                            if derivation in UNSUPPORTED_DERIVATIONS:
                                counts["unsupported"] += 1
                                totals["unsupported"] += 1
                                failed_rows.append({
                                    "Root":             root,
                                    "Class":            f"{primary_class} ({derivation})",
                                    "Derivation":       derivation,
                                    "Tense":            tense,
                                    "Voice":            voice,
                                    "Person":           person,
                                    "Number":           number,
                                    "Expected (INRIA)": " OR ".join(expected_forms),
                                    "Actual (FST)":     "UNSUPPORTED",
                                    "Error_Type":       f"Unsupported derivation: {derivation}",
                                })
                                continue

                            # --- Supported: call the FST ---
                            try:
                                actual = api.conjugate(
                                    root, effective_class, person, number,
                                    voice=voice, tense=tense, derivative=fst_derivative
                                )

                                actual_list = actual.split(" OR ")
                                if any(a in expected_forms for a in actual_list):
                                    counts["pass"] += 1
                                    totals["pass"] += 1
                                else:
                                    counts["fail"] += 1
                                    totals["fail"] += 1
                                    failed_rows.append({
                                        "Root":             root,
                                        "Class":            f"{effective_class} ({derivation})",
                                        "Derivation":       derivation,
                                        "Tense":            tense,
                                        "Voice":            voice,
                                        "Person":           person,
                                        "Number":           number,
                                        "Expected (INRIA)": " OR ".join(expected_forms),
                                        "Actual (FST)":     actual,
                                        "Error_Type":       "Mismatch",
                                    })

                            except Exception as e:
                                counts["error"] += 1
                                totals["error"] += 1
                                failed_rows.append({
                                    "Root":             root,
                                    "Class":            f"{effective_class} ({derivation})",
                                    "Derivation":       derivation,
                                    "Tense":            tense,
                                    "Voice":            voice,
                                    "Person":           person,
                                    "Number":           number,
                                    "Expected (INRIA)": " OR ".join(expected_forms),
                                    "Actual (FST)":     "CRASHED",
                                    "Error_Type":       f"Exception: {e}",
                                })

    # ── Write failure CSV ──────────────────────────────────────────────────────
    if failed_rows:
        fieldnames = ["Root", "Class", "Derivation", "Tense", "Voice", "Person",
                      "Number", "Expected (INRIA)", "Actual (FST)", "Error_Type"]
        with open(output_report, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(failed_rows)
        print(f"\n📄 Failure report → {output_report}  ({len(failed_rows)} rows)")

    # ── Terminal summary ───────────────────────────────────────────────────────
    tested = totals["pass"] + totals["fail"] + totals["error"]
    pct    = f"{100 * totals['pass'] / tested:.1f}%" if tested else "n/a"

    print("\n" + "="*52)
    print("          FOCUSED BENCHMARK RESULTS")
    print("="*52)
    print(f"  ✅ Pass:          {totals['pass']:>6}  ({pct})")
    print(f"  ❌ Fail:          {totals['fail']:>6}")
    print(f"  💥 Crash:         {totals['error']:>6}")
    print(f"  🚧 Unsupported:   {totals['unsupported']:>6}  (desid / intens)")
    print(f"  🛑 Impossible:    {totals['impossible']:>6}  (e.g., passive perfect)")
    print(f"  👻 Not in INRIA:  {totals['skip_inria']:>6}  (valid skips)")
    print("="*52)

    print("\n  Per-root breakdown:")
    print(f"  {'Root':<8} {'✅':>6} {'❌':>6} {'💥':>6} {'🚧':>6}")
    print("  " + "-"*34)
    for root, _, desc in test_suite:
        c = per_root[root]
        print(f"  {root:<8} {c['pass']:>6} {c['fail']:>6} {c['error']:>6} {c['unsupported']:>6}  {desc}")

if __name__ == "__main__":
    run_focused_benchmark("../data/verbs_clean.csv", "benchmark_failures.csv")
