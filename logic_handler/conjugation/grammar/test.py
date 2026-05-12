import sys, io, csv, time

# Force UTF-8 output so IAST characters render on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from conjugate import SanskritConjugator

# ── Value mappings from roots.csv → engine API ────────────────────────────────

MODE_MAP = {
    "pres": "present",
    "ipft": "imperfect",
    "impv": "imperative",
    "opt": "optative",
    "ben": "benedictive",
    "sfut": "future",
    "cond": "conditional",
    "perf": "perfect",
    "pfut": "periphrastic_future",
    "aor": "aorist",
    "inj": "injunctive",
}

VOICE_MAP = {
    "para": "active",
    "atma": "middle",
    "pass": "passive",
}

NUMBER_MAP = {
    "s": "sg",
    "d": "du",
    "p": "pl",
}

DERIV_MAP = {
    "": "primary",
    "caus": "causative",
    "desid": "desiderative",
    "intens": "intensive",
}

IMPOSSIBLE = {
    # passive has no perfect / future system
    ("passive", "perfect"),
    ("passive", "future"),
    ("passive", "periphrastic_future"),
    ("passive", "conditional"),
}


def normalize_root(root: str) -> str:
    """Remove INRIA homonym markers like bhu#1 → bhu."""
    if not root:
        return root
    return root.split("#")[0]


def normalize(form: str) -> str:
    """Convert roots.csv pausa-s/r to visarga ḥ so it matches engine output.
    roots.csv stores forms with trailing -s (e.g. tiṣṭhāvas) while the engine
    produces the standard pausa form with visarga (tiṣṭhāvaḥ).
    """
    if not form:
        return form
    if form.endswith("s") or form.endswith("r"):
        return form[:-1] + "ḥ"
    return form


def run_focused_benchmark(
    csv_file="../data/roots.csv", output_report="benchmark_failures.csv"
):
    print("Loading INRIA database...")
    t_start = time.perf_counter()

    inria_db = {}
    with open(csv_file, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cls = row.get("class", "")
            class_str = cls.split(" ")[0] if cls else None
            class_val = (
                int(class_str) if class_str and class_str.isdigit() else class_str
            )

            key = (
                normalize_root(row["root_IAST"]),
                class_val,
                MODE_MAP.get(row["mode"], row["mode"]),
                VOICE_MAP.get(row["voice"], row["voice"]),
                row["person"],
                NUMBER_MAP.get(row["number"], row["number"]),
                "denominative"
                if row.get("class") == "denom"
                else DERIV_MAP.get(row.get("modification", ""), "primary"),
            )
            # roots.csv stores pausa forms with trailing -s (e.g. tiṣṭhāvas).
            # Our engine produces the visarga form (tiṣṭhāvaḥ). normalize()
            # converts trailing s/r → ḥ so both sides are comparable.
            form = normalize(row["form_IAST"])
            bucket = inria_db.setdefault(key, [])
            if form not in bucket:
                bucket.append(form)

    print(f"  Loaded in {time.perf_counter() - t_start:.2f}s\n")

    # ── Test suite ─────────────────────────────────────────────────────────────
    # Each entry: (root_iast, primary_class, description)
    # Set primary_class="denom" to call the engine with derivative="denominative".
    # The root_iast must match INRIA's stem_iast exactly.
    test_suite = [
        # All 10 primary classes
        ("bhū", 1, "Class 1  – Guṇa + Thematic / Standard Seṭ Future"),
        ("ad", 2, "Class 2  – Athematic + Devoicing (atti / atsyati)"),
        ("hu", 3, "Class 3  – Reduplication / a-Aorist / ṣ+dhv→ḍhv Sandhi (ahoḍhvam)"),
        ("dīv", 4, "Class 4  – Internal Lengthening (dīvyati)"),
        ("su", 5, "Class 5  – Athematic Sign (-nu/-no-)"),
        ("tud", 6, "Class 6  – Thematic + No Guṇa / Aniṭ Luṭ (tottā)"),
        ("yuj", 7, "Class 7  – Nasal Infix + Palatal Sandhi (yunakti / yokṣyati)"),
        ("tan", 8, "Class 8  – Athematic Sign (-u/-o-)"),
        ("krī", 9, "Class 9  – Athematic Sign (-nā/-nī-) + Nati (krīṇāti)"),
        ("cur", 10, "Class 10 – Causative-style (-aya-)"),
        # Phonological edge cases
        ("kṛ", 8, "Guṇa of ṛ + Ruki / ṣṭ Sandhi (akārṣṭam)"),
        ("budh", 1, "Grassmann Throwback + Devoicing / iṣ-Aorist (abodhiṣam)"),
        ("duh", 2, "Grassmann Throwback + H-Sandhi + Ruki (dhokṣyati)"),
        ("gam", 1, "Suppletive Present (gaccha) / Root Aorist (agamat)"),
        ("dviṣ", 2, "Aniṭ S-Aorist / Palatal Sandhi (adviṣat)"),
        ("muc", 6, "Nasal Infix (muñca) / a-Aorist (amucat)"),
        # Expanded classical suite
        ("vac", 2, "Suppletive strong stem (vakti / ucyate)"),
        ("han", 2, "gh-deletion (hanti / jighāṃsati)"),
        ("pā", 1, "Long-vowel root + yan sandhi (pāti / pātum)"),
        ("nī", 1, "Long-vowel root + periphrastic perfect"),
        ("śru", 5, "u-final + Benedictive (śrūyāt)"),
        ("dā", 3, "Reduplicating class, long-ā (dadāti)"),
        ("sthā", 1, "Long-ā root, suppletive aorist (asthāt)"),
        ("bhid", 7, "Class 7 nasal infix, s-aorist (abhaiṭsīt)"),
        ("kṣip", 6, "Thematic no-guṇa, veṭ future"),
        ("vṛ", 9, "Veṭ root with both future forms (variṣyati / varīṣyati)"),
        # Additional coverage gaps
        ("yaj", 1, "Passive sandhi ya-infix + palatal (ijyate)"),
        ("labh", 1, "Ātmanepada-only root (labhate)"),
        ("smṛ", 1, "ṛ-final class 1, different aorist type from kṛ (asmart)"),
        ("man", 4, "Nasal-final root, non-suppletive (manyate)"),
        ("vid", 2, "Perfect-as-present anomaly (veda = he knows)"),
        # Denominatives
        ("namas", "denom", "Denominative from nominal stem (namasyati)"),
        ("lavaṇa", "denom", "Denominative: "),
        ("lohita", "denom", "Denominative: "),
    ]

    # ── Root remappings ────────────────────────────────────────────────────────
    # Some INRIA stems differ from the true grammatical root used by our engine.
    INRIA_TO_ENGINE_ROOT = {
        "dīv": "div",  # INRIA stem dīv → engine root div (class-4 lengthening is internal)
    }

    UNSUPPORTED_DERIVATIONS = set()  # add e.g. "desiderative" here to skip and flag it

    # ── Grammar space (derived from the maps above) ────────────────────────────
    ALL_TENSES = list(MODE_MAP.values())
    ALL_VOICES = list(VOICE_MAP.values())
    ALL_PERSONS = ["1", "2", "3"]
    ALL_NUMBERS = list(NUMBER_MAP.values())

    api = SanskritConjugator()

    totals = {
        "pass": 0,
        "fail": 0,
        "error": 0,
        "skip_inria": 0,
        "unsupported": 0,
        "impossible": 0,
    }
    per_root = {}
    failed_rows = []
    multiple_expected_rows = []

    print("Running tests...\n")

    for root, primary_class, desc in test_suite:
        per_root[root] = {
            "pass": 0,
            "fail": 0,
            "error": 0,
            "skip_inria": 0,
            "unsupported": 0,
            "impossible": 0,
        }
        counts = per_root[root]
        t_root = time.perf_counter()
        is_denom = primary_class == "denom"

        # Denominatives only run as "denominative"; regular roots run all 4 derivations
        derivations = (
            ["denominative"]
            if is_denom
            else ["primary", "causative", "desiderative", "intensive"]
        )

        for derivation in derivations:
            effective_class = None if is_denom else primary_class
            fst_derivative = derivation

            for tense in ALL_TENSES:
                for voice in ALL_VOICES:
                    for person in ALL_PERSONS:
                        for number in ALL_NUMBERS:
                            is_impossible = (voice, tense) in IMPOSSIBLE

                            is_present_system = tense in (
                                "present",
                                "imperfect",
                                "imperative",
                                "optative",
                            )
                            is_passive = voice == "passive"

                            if is_denom:
                                query_class = "denom"
                            elif (
                                derivation != "primary"
                                or is_passive
                                or not is_present_system
                            ):
                                query_class = None
                            else:
                                query_class = effective_class

                            norm_root = normalize_root(root)
                            inria_key = (
                                norm_root,
                                query_class,
                                tense,
                                voice,
                                person,
                                number,
                                derivation,
                            )

                            if inria_key not in inria_db:
                                if is_impossible:
                                    counts["impossible"] += 1
                                    totals["impossible"] += 1
                                else:
                                    counts["skip_inria"] += 1
                                    totals["skip_inria"] += 1
                                continue

                            expected_forms = inria_db[inria_key]

                            if derivation in UNSUPPORTED_DERIVATIONS:
                                counts["unsupported"] += 1
                                totals["unsupported"] += 1
                                failed_rows.append(
                                    {
                                        "Root": root,
                                        "Class": f"{primary_class} ({derivation})",
                                        "Derivation": derivation,
                                        "Tense": tense,
                                        "Voice": voice,
                                        "Person": person,
                                        "Number": number,
                                        "Expected (INRIA)": " OR ".join(expected_forms),
                                        "Actual (FST)": "UNSUPPORTED",
                                        "Error_Type": f"Unsupported derivation: {derivation}",
                                    }
                                )
                                continue

                            try:
                                engine_root = INRIA_TO_ENGINE_ROOT.get(root, root)
                                call_kwargs = dict(
                                    voice=voice,
                                    tense=tense,
                                    derivative=fst_derivative,
                                    use_db=False,
                                )
                                if is_denom:
                                    actual = api.conjugate(
                                        engine_root,
                                        effective_class,
                                        person,
                                        number,
                                        **call_kwargs,
                                    )
                                else:
                                    actual = api.conjugate(
                                        engine_root,
                                        effective_class,
                                        person,
                                        number,
                                        **call_kwargs,
                                    )

                                actual_list = (
                                    actual if isinstance(actual, list) else [actual]
                                )
                                if any(a in expected_forms for a in actual_list):
                                    counts["pass"] += 1
                                    totals["pass"] += 1
                                    if len(expected_forms) > 1:
                                        multiple_expected_rows.append(
                                            {
                                                "Root": root,
                                                "Class": f"{primary_class} ({derivation})",
                                                "Derivation": derivation,
                                                "Tense": tense,
                                                "Voice": voice,
                                                "Person": person,
                                                "Number": number,
                                                "Expected (INRIA)": " OR ".join(
                                                    expected_forms
                                                ),
                                                "Actual (FST)": " OR ".join(
                                                    actual_list
                                                ),
                                            }
                                        )
                                else:
                                    counts["fail"] += 1
                                    totals["fail"] += 1
                                    failed_rows.append(
                                        {
                                            "Root": root,
                                            "Class": f"{primary_class} ({derivation})",
                                            "Derivation": derivation,
                                            "Tense": tense,
                                            "Voice": voice,
                                            "Person": person,
                                            "Number": number,
                                            "Expected (INRIA)": " OR ".join(
                                                expected_forms
                                            ),
                                            "Actual (FST)": " OR ".join(actual_list)
                                            if actual_list
                                            else "CRASHED: No valid path",
                                            "Error_Type": "Mismatch",
                                        }
                                    )

                            except Exception as e:
                                counts["error"] += 1
                                totals["error"] += 1
                                failed_rows.append(
                                    {
                                        "Root": root,
                                        "Class": f"{primary_class} ({derivation})",
                                        "Derivation": derivation,
                                        "Tense": tense,
                                        "Voice": voice,
                                        "Person": person,
                                        "Number": number,
                                        "Expected (INRIA)": " OR ".join(expected_forms),
                                        "Actual (FST)": "CRASHED",
                                        "Error_Type": f"Exception: {e}",
                                    }
                                )

        # ── Per-root completion line ───────────────────────────────────────────
        elapsed = time.perf_counter() - t_root
        tested_root = counts["pass"] + counts["fail"] + counts["error"]
        pct_root = (
            f"{100 * counts['pass'] / tested_root:.0f}%" if tested_root else "n/a"
        )
        print(
            f"  ✔ {root:<10} {pct_root:>4}  "
            f"({counts['pass']}✅ {counts['fail']}❌ {counts['error']}💥)  "
            f"{elapsed:.2f}s  — {desc}"
        )

    # ── Write failure CSV ──────────────────────────────────────────────────────
    if failed_rows:
        fieldnames = [
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
        with open(output_report, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(failed_rows)
        print(f"\n📄 Failure report → {output_report}  ({len(failed_rows)} rows)")

    if multiple_expected_rows:
        fieldnames = [
            "Root",
            "Class",
            "Derivation",
            "Tense",
            "Voice",
            "Person",
            "Number",
            "Expected (INRIA)",
            "Actual (FST)",
        ]
        with open(
            "correct_multiple_expected.csv", mode="w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(multiple_expected_rows)
        print(
            f"📄 Multiple expected matches → correct_multiple_expected.csv  ({len(multiple_expected_rows)} rows)"
        )

    # ── Terminal summary ───────────────────────────────────────────────────────
    t_total = time.perf_counter() - t_start
    tested = totals["pass"] + totals["fail"] + totals["error"]
    pct = f"{100 * totals['pass'] / tested:.1f}%" if tested else "n/a"

    print("\n" + "=" * 52)
    print("          FOCUSED BENCHMARK RESULTS")
    print("=" * 52)
    print(f"  ✅ Pass:          {totals['pass']:>6}  ({pct})")
    print(f"  ❌ Fail:          {totals['fail']:>6}")
    print(f"  💥 Crash:         {totals['error']:>6}")
    print(f"  🚧 Unsupported:   {totals['unsupported']:>6}  (desid / intens)")
    print(f"  🛑 Impossible:    {totals['impossible']:>6}  (e.g., passive perfect)")
    print(f"  👻 Not in INRIA:  {totals['skip_inria']:>6}  (valid skips)")
    print(f"  ⏱  Total time:    {t_total:.1f}s")
    print("=" * 52)

    print("\n  Per-root breakdown:")
    print(f"  {'Root':<10} {'✅':>6} {'❌':>6} {'💥':>6} {'🚧':>6}  Description")
    print("  " + "-" * 72)
    for root, primary_class, desc in test_suite:
        c = per_root[root]
        print(
            f"  {root:<10} {c['pass']:>6} {c['fail']:>6} {c['error']:>6} {c['unsupported']:>6}  {desc}"
        )


if __name__ == "__main__":
    run_focused_benchmark("../data/roots.csv", "benchmark_failures.csv")
    # 3) Optionally run a full sweep and dump failures to CSV
    # Uncomment to run the full benchmark
    # run_focused_benchmark("data/roots.csv", "benchmark_failures.csv")
