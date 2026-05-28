import sys, io, csv, time
import os
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "grammar")))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from conjugate import SanskritConjugator
from dhatupatha_analyzer import DHATUPATHA_ANALYZER, _CLASS_LOOKUP_ALIASES, to_slp1

def normalize(form: str) -> str:
    if not form:
        return form
    if form.endswith("s") or form.endswith("r"):
        return form[:-1] + "ḥ"
    return form

def normalize_root(root: str) -> str:
    if not root:
        return root
    return root.replace("~", "").replace("!", "")


def _has_lexical_entry_for_class(root: str, class_num: int) -> bool:
    if not isinstance(class_num, int):
        return True
    candidates = [to_slp1(root)]
    if candidates[0].startswith("s"):
        candidates.append("z" + candidates[0][1:])
    if candidates[0].startswith("n"):
        candidates.append("R" + candidates[0][1:])

    def _clean(raw: str) -> str:
        c = raw
        for pfx in ("qu", "wu", "o~", "Y"):
            if c.startswith(pfx):
                c = c[len(pfx):]
        return c.replace("\\", "").replace("^", "").replace("~", "")

    for entry in DHATUPATHA_ANALYZER._entries_by_class.get(class_num, []):
        clean = _clean(entry["raw"])
        for cand in candidates:
            if clean == cand or (cand.endswith("h") and clean == cand[:-1] + "H"):
                return True
            if clean.startswith(cand) or (cand.endswith("h") and clean.startswith(cand[:-1] + "H")):
                return True
    return False


def _classify_trust_tier(root: str, inria_class, effective_class, derivation: str, error_type: str):
    if error_type.startswith("Exception"):
        return ("Tier C", "engine_exception")

    # Denominatives are class-mapped heuristically by design; keep neutral.
    if derivation == "denominative":
        return ("Tier A", "denominative_path")

    if isinstance(inria_class, int):
        if _has_lexical_entry_for_class(root, inria_class):
            return ("Tier C", "same_class_lexical_exists")

        alias_class = _CLASS_LOOKUP_ALIASES.get((root, inria_class))
        if alias_class is not None:
            return ("Tier B", f"explicit_alias_{inria_class}_to_{alias_class}")

        if isinstance(effective_class, int) and effective_class != inria_class and _has_lexical_entry_for_class(root, effective_class):
            return ("Tier B", f"inria_class_{inria_class}_missing_lexical_{effective_class}_exists")

        for cls in range(1, 11):
            if cls != inria_class and _has_lexical_entry_for_class(root, cls):
                return ("Tier B", f"inria_class_{inria_class}_missing_other_class_{cls}_exists")

    return ("Tier A", "no_clear_class_conflict")

def run_full_benchmark(
    csv_file=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "verbs_clean.csv")),
    output_report="full_benchmark_failures.csv",
    max_cases=None,
):
    print(f"Loading full database from {csv_file}...")
    t_start = time.perf_counter()

    # Dictionary to map root -> primary class(es)
    root_to_class = {}
    inria_db = {}
    
    with open(csv_file, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cls = row.get("class", "")
            class_str = cls.split(" ")[0] if cls else None
            class_val = int(class_str) if class_str and class_str.isdigit() else class_str
            
            derivation = row.get("derivation", "primary")
            if class_str == "11":
                class_val = "denom"
                derivation = "denominative"
            elif class_str == "":
                class_val = None

            stem = normalize_root(row["stem_iast"])
            if class_val is not None and class_val != "denom":
                if stem not in root_to_class:
                    root_to_class[stem] = class_val

            key = (
                stem,
                class_val,
                row["tense"],
                row["voice"],
                row["person"],
                row["number"],
                derivation,
            )
            
            form = normalize(row["form_iast"])
            bucket = inria_db.setdefault(key, [])
            if form not in bucket:
                bucket.append(form)

    print(f"  Loaded {len(inria_db)} unique derivations in {time.perf_counter() - t_start:.2f}s\n")

    INRIA_TO_ENGINE_ROOT = {
        "dīv": "div",
    }

    api = SanskritConjugator()

    totals = {
        "pass": 0,
        "partial": 0,
        "fail": 0,
        "error": 0,
    }

    failed_rows = []
    multiple_expected_rows = []

    print("Running full benchmark (this will take a while)...\n")

    count = 0
    total_keys = len(inria_db)
    
    # We will track unsupported ones too
    UNSUPPORTED_DERIVATIONS = set() 

    for key, expected_forms in inria_db.items():
        root, inria_class, tense, voice, person, number, derivation = key
        
        count += 1
        if count % 1000 == 0:
            print(f"Processed {count}/{total_keys} forms...")

        if max_cases is not None and count > max_cases:
            break

        if derivation in UNSUPPORTED_DERIVATIONS:
            continue

        try:
            engine_root = INRIA_TO_ENGINE_ROOT.get(root, root)
            
            # Decide effective class
            if derivation == "denominative":
                effective_class = "denom"
            elif inria_class is not None:
                effective_class = inria_class
            else:
                if root.endswith("a") or derivation == "causative":
                    effective_class = 10
                else:
                    effective_class = root_to_class.get(root, 1) # fallback to class 1

            call_kwargs = dict(
                voice=voice,
                tense=tense,
                derivative=derivation,
                use_db=False,
            )
            
            actual = api.conjugate(
                engine_root,
                effective_class,
                person,
                number,
                **call_kwargs,
            )

            actual_list = actual if isinstance(actual, list) else [actual]
            
            if any(a in expected_forms for a in actual_list):
                if len(expected_forms) > 1 and set(expected_forms) != set(actual_list):
                    totals["partial"] += 1
                    multiple_expected_rows.append({
                        "Root": root, "Class": effective_class, "Derivation": derivation,
                        "Tense": tense, "Voice": voice, "Person": person, "Number": number,
                        "Expected (INRIA)": " OR ".join(expected_forms),
                        "Actual (FST)": " OR ".join(actual_list)
                    })
                else:
                    totals["pass"] += 1
            else:
                totals["fail"] += 1
                tier, reason = _classify_trust_tier(root, inria_class, effective_class, derivation, "Mismatch")
                failed_rows.append({
                    "Root": root, "Class": effective_class, "Derivation": derivation,
                    "Tense": tense, "Voice": voice, "Person": person, "Number": number,
                    "Expected (INRIA)": " OR ".join(expected_forms),
                    "Actual (FST)": " OR ".join(actual_list) if actual_list else "CRASHED",
                    "Error_Type": "Mismatch",
                    "Trust_Tier": tier,
                    "Tier_Reason": reason,
                })

        except Exception as e:
            totals["error"] += 1
            tier, reason = _classify_trust_tier(root, inria_class, effective_class, derivation, f"Exception: {e}")
            failed_rows.append({
                "Root": root, "Class": effective_class, "Derivation": derivation,
                "Tense": tense, "Voice": voice, "Person": person, "Number": number,
                "Expected (INRIA)": " OR ".join(expected_forms),
                "Actual (FST)": "CRASHED",
                "Error_Type": f"Exception: {e}",
                "Trust_Tier": tier,
                "Tier_Reason": reason,
            })

    t_total = time.perf_counter() - t_start
    tested = totals["pass"] + totals["partial"] + totals["fail"] + totals["error"]
    pct = f"{100 * (totals['pass'] + totals['partial']) / tested:.1f}%" if tested else "n/a"

    summary = f"""
{"=" * 52}
          FULL BENCHMARK RESULTS
{"=" * 52}
  ✅ Pass:          {totals['pass']:>6}  ({pct})
  ⚠️ Partial:       {totals['partial']:>6}
  ❌ Fail:          {totals['fail']:>6}
  💥 Crash:         {totals['error']:>6}
  ⏱  Total time:    {t_total:.1f}s
{"=" * 52}
"""
    if failed_rows:
        tier_counts = defaultdict(int)
        for row in failed_rows:
            tier_counts[row.get("Trust_Tier", "Tier C")] += 1
        summary += (
            f"Trust Tiers on failures:\n"
            f"  Tier A (likely acceptable/source-tolerant): {tier_counts['Tier A']}\n"
            f"  Tier B (likely INRIA/Vidyut class conflict): {tier_counts['Tier B']}\n"
            f"  Tier C (likely engine bug): {tier_counts['Tier C']}\n"
            f"{'=' * 52}\n"
        )
    print(summary)
    
    with open("full_benchmark_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)


    if failed_rows:
        with open(output_report, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Root", "Class", "Derivation", "Tense", "Voice", "Person", "Number", "Expected (INRIA)", "Actual (FST)", "Error_Type", "Trust_Tier", "Tier_Reason"])
            writer.writeheader()
            writer.writerows(failed_rows)
        print(f"\nSaved {len(failed_rows)} failures to {output_report}")

    if multiple_expected_rows:
        with open("full_correct_multiple_expected.csv", mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Root", "Class", "Derivation", "Tense", "Voice", "Person", "Number", "Expected (INRIA)", "Actual (FST)"])
            writer.writeheader()
            writer.writerows(multiple_expected_rows)
        print(f"Saved {len(multiple_expected_rows)} partial matches to full_correct_multiple_expected.csv")

if __name__ == "__main__":
    run_full_benchmark()
