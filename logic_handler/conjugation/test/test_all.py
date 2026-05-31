import argparse
import sys
import io
import csv
import time
import os
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "grammar")))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from conjugate import SanskritConjugator

INRIA_TO_ENGINE_ROOT = {
    "dīv": "div",
}

LEGACY_FAILURE_COLUMNS = frozenset({"Trust_Tier", "Tier_Reason"})

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


def _effective_class(root, inria_class, derivation, root_to_class):
    if derivation == "denominative":
        return "denom"
    if inria_class is not None:
        return inria_class
    if root.endswith("a") or derivation == "causative":
        return 10
    return root_to_class.get(root, 1)


def _paradigm_eligible(tense: str, derivative: str) -> bool:
    """``conjugate_paradigm`` covers all lakāra rows except kṛdanta blocks."""
    return tense != "krdantas"


def _record_cell_result(
    totals,
    failed_rows,
    multiple_expected_rows,
    *,
    root,
    effective_class,
    derivation,
    tense,
    voice,
    person,
    number,
    expected_forms,
    actual_list,
    error_msg=None,
):
    if error_msg is not None:
        totals["error"] += 1
        failed_rows.append(
            {
                "Root": root,
                "Class": effective_class,
                "Derivation": derivation,
                "Tense": tense,
                "Voice": voice,
                "Person": person,
                "Number": number,
                "Expected (INRIA)": " OR ".join(expected_forms),
                "Actual (FST)": "CRASHED",
                "Error_Type": error_msg,
            }
        )
        return

    if any(a in expected_forms for a in actual_list):
        if len(expected_forms) > 1 and set(expected_forms) != set(actual_list):
            totals["partial"] += 1
            multiple_expected_rows.append(
                {
                    "Root": root,
                    "Class": effective_class,
                    "Derivation": derivation,
                    "Tense": tense,
                    "Voice": voice,
                    "Person": person,
                    "Number": number,
                    "Expected (INRIA)": " OR ".join(expected_forms),
                    "Actual (FST)": " OR ".join(actual_list),
                }
            )
        else:
            totals["pass"] += 1
    else:
        totals["fail"] += 1
        failed_rows.append(
            {
                "Root": root,
                "Class": effective_class,
                "Derivation": derivation,
                "Tense": tense,
                "Voice": voice,
                "Person": person,
                "Number": number,
                "Expected (INRIA)": " OR ".join(expected_forms),
                "Actual (FST)": " OR ".join(actual_list) if actual_list else "CRASHED",
                "Error_Type": "Mismatch",
            }
        )


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

    # Group by (root, class, tense, voice, derivation) for conjugate_paradigm batches.
    paradigm_groups = defaultdict(dict)
    for key, expected_forms in inria_db.items():
        root, inria_class, tense, voice, person, number, derivation = key
        gkey = (root, inria_class, tense, voice, derivation)
        paradigm_groups[gkey][(person, number)] = expected_forms

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
    paradigm_batches = 0
    single_cell_calls = 0

    UNSUPPORTED_DERIVATIONS = set()

    def _process_cell(
        root,
        inria_class,
        tense,
        voice,
        derivation,
        person,
        number,
        expected_forms,
        actual_list,
        error_msg=None,
    ):
        nonlocal count
        count += 1
        if count % 1000 == 0:
            print(f"Processed {count}/{total_keys} forms...")

        effective_class = _effective_class(
            root, inria_class, derivation, root_to_class
        )
        _record_cell_result(
            totals,
            failed_rows,
            multiple_expected_rows,
            root=root,
            effective_class=effective_class,
            derivation=derivation,
            tense=tense,
            voice=voice,
            person=person,
            number=number,
            expected_forms=expected_forms,
            actual_list=actual_list or [],
            error_msg=error_msg,
        )

    for gkey, cells in paradigm_groups.items():
        root, inria_class, tense, voice, derivation = gkey

        if derivation in UNSUPPORTED_DERIVATIONS:
            continue

        if max_cases is not None and count >= max_cases:
            break

        effective_class = _effective_class(
            root, inria_class, derivation, root_to_class
        )
        engine_root = INRIA_TO_ENGINE_ROOT.get(root, root)
        call_kwargs = dict(
            voice=voice,
            tense=tense,
            derivative=derivation,
            use_db=False,
        )

        use_paradigm = _paradigm_eligible(tense, derivation) and len(cells) >= 2

        if use_paradigm:
            paradigm_batches += 1
            try:
                paradigm = api.conjugate_paradigm(
                    engine_root, effective_class, **call_kwargs
                )
            except Exception as e:
                err = f"Exception: {e}"
                for (person, number), expected_forms in cells.items():
                    if max_cases is not None and count >= max_cases:
                        break
                    _process_cell(
                        root,
                        inria_class,
                        tense,
                        voice,
                        derivation,
                        person,
                        number,
                        expected_forms,
                        [],
                        error_msg=err,
                    )
                continue

            for (person, number), expected_forms in cells.items():
                if max_cases is not None and count >= max_cases:
                    break
                key = f"{person}{number}"
                actual_list = paradigm.get(key, [])
                if (
                    len(actual_list) == 1
                    and isinstance(actual_list[0], str)
                    and actual_list[0].startswith("Error:")
                ):
                    _process_cell(
                        root,
                        inria_class,
                        tense,
                        voice,
                        derivation,
                        person,
                        number,
                        expected_forms,
                        [],
                        error_msg=actual_list[0],
                    )
                else:
                    _process_cell(
                        root,
                        inria_class,
                        tense,
                        voice,
                        derivation,
                        person,
                        number,
                        expected_forms,
                        actual_list,
                    )
        else:
            for (person, number), expected_forms in cells.items():
                if max_cases is not None and count >= max_cases:
                    break
                single_cell_calls += 1
                try:
                    actual = api.conjugate(
                        engine_root,
                        effective_class,
                        person,
                        number,
                        **call_kwargs,
                    )
                    actual_list = actual if isinstance(actual, list) else [actual]
                    _process_cell(
                        root,
                        inria_class,
                        tense,
                        voice,
                        derivation,
                        person,
                        number,
                        expected_forms,
                        actual_list,
                    )
                except Exception as e:
                    _process_cell(
                        root,
                        inria_class,
                        tense,
                        voice,
                        derivation,
                        person,
                        number,
                        expected_forms,
                        [],
                        error_msg=f"Exception: {e}",
                    )

    print(
        f"  Engine calls: {paradigm_batches} paradigm batch(es), "
        f"{single_cell_calls} single-cell conjugate(s)\n"
    )

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
    print(summary)
    
    with open("full_benchmark_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)


    if failed_rows:
        with open(output_report, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "Root", "Class", "Derivation", "Tense", "Voice",
                    "Person", "Number", "Expected (INRIA)", "Actual (FST)", "Error_Type",
                ],
            )
            writer.writeheader()
            writer.writerows(failed_rows)
        print(f"\nSaved {len(failed_rows)} failures to {output_report}")

    if multiple_expected_rows:
        with open("full_correct_multiple_expected.csv", mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Root", "Class", "Derivation", "Tense", "Voice", "Person", "Number", "Expected (INRIA)", "Actual (FST)"])
            writer.writeheader()
            writer.writerows(multiple_expected_rows)
        print(f"Saved {len(multiple_expected_rows)} partial matches to full_correct_multiple_expected.csv")

def _parse_class(class_val):
    if class_val is None or class_val == "":
        return None
    s = str(class_val).strip()
    if s.isdigit():
        return int(s)
    return s


def _split_expected(expected_str: str) -> list[str]:
    if not expected_str:
        return []
    return [p.strip() for p in expected_str.split(" OR ")]


def _conjugate_row(api, row):
    """Re-run engine for one failure-row dict; returns (actual_list, error_msg|None)."""
    root = row["Root"]
    effective_class = _parse_class(row.get("Class"))
    derivation = row.get("Derivation") or "primary"
    tense = row["Tense"]
    voice = row["Voice"]
    person = str(row["Person"])
    number = row["Number"]

    engine_root = INRIA_TO_ENGINE_ROOT.get(root, root)
    actual = api.conjugate(
        engine_root,
        effective_class,
        person,
        number,
        voice=voice,
        tense=tense,
        derivative=derivation,
        use_db=False,
    )
    actual_list = actual if isinstance(actual, list) else [actual]
    return actual_list, None


def run_failures_rerun(
    failures_csv="full_benchmark_failures.csv",
    output_report=None,
    fixed_report="full_benchmark_fixed.csv",
    summary_file="full_benchmark_rerun_summary.txt",
):
    """Re-test only rows listed in a prior failures CSV (~30k vs ~160k)."""
    failures_csv = os.path.abspath(failures_csv)
    if output_report is None:
        output_report = failures_csv

    if not os.path.isfile(failures_csv):
        raise FileNotFoundError(failures_csv)

    print(f"Loading failure cases from {failures_csv}...")
    t_start = time.perf_counter()

    cases = []
    with open(failures_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = {k: v for k, v in raw.items() if k not in LEGACY_FAILURE_COLUMNS}
            cases.append(row)

    print(f"  {len(cases)} cases to re-test\n")

    rerun_groups = defaultdict(list)
    for row in cases:
        gkey = (
            row["Root"],
            row.get("Class"),
            row["Tense"],
            row["Voice"],
            row.get("Derivation") or "primary",
        )
        rerun_groups[gkey].append(row)

    api = SanskritConjugator()
    still_failed = []
    fixed_rows = []
    totals = {"pass": 0, "fail": 0, "error": 0}
    processed = 0

    def _rerun_score_row(row, actual_list, error_msg=None):
        nonlocal processed
        processed += 1
        if processed % 2000 == 0:
            print(f"  {processed}/{len(cases)}...")

        expected_forms = _split_expected(row.get("Expected (INRIA)", ""))
        if error_msg is not None:
            totals["error"] += 1
            still_failed.append(
                {
                    **row,
                    "Expected (INRIA)": row.get("Expected (INRIA)", ""),
                    "Actual (FST)": "CRASHED",
                    "Error_Type": error_msg,
                }
            )
            return

        if any(a in expected_forms for a in actual_list):
            totals["pass"] += 1
            fixed_rows.append(
                {
                    **row,
                    "Actual (FST)": " OR ".join(actual_list),
                    "Previous_Actual": row.get("Actual (FST)", ""),
                }
            )
        else:
            totals["fail"] += 1
            still_failed.append(
                {
                    **row,
                    "Expected (INRIA)": row.get("Expected (INRIA)", ""),
                    "Actual (FST)": " OR ".join(actual_list) if actual_list else "",
                    "Error_Type": "Mismatch",
                }
            )

    for gkey, group_rows in rerun_groups.items():
        root, class_raw, tense, voice, derivation = gkey
        effective_class = _parse_class(class_raw)
        engine_root = INRIA_TO_ENGINE_ROOT.get(root, root)
        call_kwargs = dict(
            voice=voice,
            tense=tense,
            derivative=derivation,
            use_db=False,
        )

        if _paradigm_eligible(tense, derivation) and len(group_rows) >= 2:
            try:
                paradigm = api.conjugate_paradigm(
                    engine_root, effective_class, **call_kwargs
                )
            except Exception as e:
                for row in group_rows:
                    _rerun_score_row(row, [], error_msg=f"Exception: {e}")
                continue

            for row in group_rows:
                key = f"{row['Person']}{row['Number']}"
                actual_list = paradigm.get(key, [])
                if (
                    len(actual_list) == 1
                    and isinstance(actual_list[0], str)
                    and actual_list[0].startswith("Error:")
                ):
                    _rerun_score_row(row, [], error_msg=actual_list[0])
                else:
                    _rerun_score_row(row, actual_list)
        else:
            for row in group_rows:
                try:
                    actual_list, _ = _conjugate_row(api, row)
                    _rerun_score_row(row, actual_list)
                except Exception as e:
                    _rerun_score_row(row, [], error_msg=f"Exception: {e}")

    t_total = time.perf_counter() - t_start
    tested = totals["pass"] + totals["fail"] + totals["error"]
    prev_n = len(cases)
    fixed_pct = f"{100 * totals['pass'] / prev_n:.1f}%" if prev_n else "n/a"

    summary = f"""
{"=" * 52}
     FAILURES RE-RUN (subset benchmark)
{"=" * 52}
  Prior failures:  {prev_n:>6}
  ✅ Now pass:     {totals['pass']:>6}  ({fixed_pct} of prior fails)
  ❌ Still fail:   {totals['fail']:>6}
  💥 Crash:        {totals['error']:>6}
  ⏱  Total time:   {t_total:.1f}s
{"=" * 52}
"""
    print(summary)

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary)

    out_fields = [
        "Root",
        "Class",
        "Derivation",
        "Tense",
        "Voice",
        "Person",
        "Number",
        "Expected (INRIA)",
        "Actual (FST)",
        "Error_Type",
    ]
    if still_failed:
        with open(output_report, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(still_failed)
        print(f"Updated {len(still_failed)} failures -> {output_report}")
    else:
        print("No remaining failures.")

    if fixed_rows:
        fixed_fields = list(fixed_rows[0].keys())
        with open(fixed_report, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fixed_fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(fixed_rows)
        print(f"Saved {len(fixed_rows)} newly passing rows -> {fixed_report}")

    print(f"Summary -> {summary_file}")
    return totals


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sanskrit conjugation benchmark")
    parser.add_argument(
        "--rerun-failures",
        metavar="CSV",
        nargs="?",
        const="full_benchmark_failures.csv",
        help="Re-test only rows from a failures CSV (default: full_benchmark_failures.csv)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output failures CSV for --rerun-failures (default: overwrite input)",
    )
    args = parser.parse_args()

    if args.rerun_failures is not None:
        run_failures_rerun(failures_csv=args.rerun_failures, output_report=args.output)
    else:
        run_full_benchmark()
