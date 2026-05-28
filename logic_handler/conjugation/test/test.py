import sys, io, csv, time, re
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "grammar")))

# Force UTF-8 output so IAST characters render on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from conjugate import SanskritConjugator

# ── Value mappings from roots.csv → engine API ────────────────────────────────
# (Legacy maps removed since verbs_clean.csv uses engine-native terms directly)

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
    csv_file=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "verbs_clean.csv")), output_report="benchmark_failures.csv"
):
    print(f"Loading database from {csv_file}...")
    t_start = time.perf_counter()

    inria_db = {}
    with open(csv_file, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cls = row.get("class", "")
            class_str = cls.split(" ")[0] if cls else None
            class_val = (
                int(class_str) if class_str and class_str.isdigit() else class_str
            )
            
            derivation = row.get("derivation", "primary")
            if class_str == "11":
                class_val = "denom"
                derivation = "denominative"
            elif class_str == "":
                class_val = None

            key = (
                normalize_root(row["stem_iast"]),
                class_val,
                row["tense"],
                row["voice"],
                row["person"],
                row["number"],
                derivation,
            )
            
            # Convert trailing s/r → ḥ so both sides are comparable.
            form = normalize(row["form_iast"])
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
        # Phase 2 & 3 Fixes Coverage
        ("ruh", 1, "Ruh-class h+dental sandhi (rūḍha)"),
        ("viś", 6, "ś/ṣ permitted finals (viṭ)"),
        ("nind", 1, "Heavy syllable guṇa blocking (anindat)"),
        ("sṛj", 6, "Desiderative RUKI exemption (sisṛkṣati)"),
        ("stu", 2, "Class-2 Vṛddhi optionality (staumi/stomi)"),
        ("jan", 4, "Mit-root causative shortening (janayati)"),
        ("mṛj", 2, "Class 2 mṛj palatal-retroflex sandhi (mārṣṭi)"),
        # Known Gaps (Unimplemented)
        ("svap", 2, "Samprasāraṇa cluster (śvapit/suṣvāpa)"),
        ("śās", 2, "Class 2 zero-grade irregular (śiṣṭe)"),
        ("rudh", 7, "Class 7 imperative 2sg bare root (runddhi)"),
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

    ALL_TENSES = ["present", "imperfect", "imperative", "optative", "benedictive", "future", "conditional", "perfect", "periphrastic_future", "aorist", "injunctive"]
    ALL_VOICES = ["active", "middle", "passive"]
    ALL_PERSONS = ["1", "2", "3"]
    ALL_NUMBERS = ["sg", "du", "pl"]

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
                                        if set(expected_forms) != set(actual_list):
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



# ── Extended suite status constants ──────────────────────────────────────────
PASS  = "✅ PASS"
FAIL  = "❌ FAIL"
CRASH = "💥 CRASH"


def run_extended_suite():
    print("\n" + "="*60)
    print("  STARTING EXTENDED SUITE (test2.py equivalent)")
    print("="*60 + "\n")
    
    api = SanskritConjugator()
    """
    test2.py — Extended test suite beyond roots.csv regression benchmark.

    Three layers:
      1. WHITNEY EXAMPLES   — curated form-level cases keyed to Whitney grammar rules,
                              one case per rule, with citation.
      2. ROOT PARADIGMS     — full present-system paradigm spot-checks for one
                              representative root per class / phonology type.
      3. PROPERTY TESTS     — sandhi invariants that must hold for *every* output
                              regardless of root (no stray tags, clean boundaries, etc.).
    """




    # ─────────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────────


    results = []
                   # list of dicts, printed at the end

    def check(label, root, cls, person, number, *,
              voice="active", tense="present", derivative="primary",
              expected, note=""):
        """Run one conjugation and record pass/fail."""
        try:
            actual = api.conjugate(root, cls, person, number,
                                   voice=voice, tense=tense,
                                   derivative=derivative, use_db=False)
            actual_forms = [f.strip() for f in actual] if isinstance(actual, list) else [actual.strip()]
            expected_forms = expected if isinstance(expected, list) else [expected]
            ok = any(a in expected_forms for a in actual_forms)
            status = PASS if ok else FAIL
            results.append({
                "status":   status,
                "label":    label,
                "root":     root,
                "expected": " / ".join(expected_forms),
                "actual":   " OR ".join(actual_forms),
                "note":     note,
            })
        except Exception as e:
            results.append({
                "status":   CRASH,
                "label":    label,
                "root":     root,
                "expected": str(expected),
                "actual":   f"EXCEPTION: {e}",
                "note":     note,
            })

    def prop(label, root, cls, person, number, *,
             voice="active", tense="present", derivative="primary",
             predicate, note=""):
        """Run a property test: predicate(output_string) must be True."""
        try:
            actual = api.conjugate(root, cls, person, number,
                                   voice=voice, tense=tense,
                                   derivative=derivative, use_db=False)
            ok = predicate(actual)
            results.append({
                "status":   PASS if ok else FAIL,
                "label":    label,
                "root":     root,
                "expected": f"<predicate: {note}>",
                "actual":   actual,
                "note":     note,
            })
        except Exception as e:
            results.append({
                "status":   CRASH,
                "label":    label,
                "root":     root,
                "expected": f"<predicate: {note}>",
                "actual":   f"EXCEPTION: {e}",
                "note":     note,
            })

    # ─────────────────────────────────────────────────────────────────────────────
    # LAYER 1 — Whitney Examples
    # Each case cites the Whitney §section it exercises.
    # Source: Whitney, "Sanskrit Grammar" (2nd ed., 1889).
    # ─────────────────────────────────────────────────────────────────────────────

    print("=" * 60)
    print("  LAYER 1 — Whitney Examples")
    print("=" * 60)

    # § 109  Visarga before voiceless: aḥ + k → ak (internal)
    check("W§109 visarga + voiceless",
          "namas", None, "3", "sg",
          tense="present", voice="active", derivative="denominative",
          expected="namasyati",
          note="Whitney §109: denominative lexical stem namas -> namasyati")

    # § 120  ca/ja palatals revert before i/y
    check("W§120 palatal reversion — yuj present",
          "yuj", 7, "3", "sg",
          tense="present", voice="active",
          expected="yunakti",
          note="Whitney §120: nasal infix, palatal reversion yunakti")

    # § 125  Cerebralisation (Ruki) — s → ṣ after r/u/k/i
    check("W§125 Ruki — kṛ future",
          "kṛ", 8, "3", "sg",
          tense="future", voice="active",
          expected="kariṣyati",
          note="Whitney §125: Ruki rule, s→ṣ after i/u/r/k")

    # § 151  Aspirate throwback (Grassmann's Law)
    check("W§151 Grassmann — budh present act 3sg",
          "budh", 1, "3", "sg",
          tense="present", voice="active",
          expected="bodhati",   # aspirate thrown back, root-initial deaspirated
          note="Whitney §151: Grassmann's Law, bh+dh → b+dh")

    check("W§151 Grassmann — duh present act 3sg",
          "duh", 2, "3", "sg",
          tense="present", voice="active",
          expected="dogdhi",
          note="Whitney §151: Grassmann + h-sandhi, duh → dogdhi")

    # § 157  h-sandhi: dh + t → gdh / ḍh
    check("W§157 h-sandhi — duh imperfect act 3sg",
          "duh", 2, "3", "sg",
          tense="imperfect", voice="active",
          expected="adhok",
          note="Whitney §157: final h before t, voiced devoicing")

    # § 160  Nasal assimilation before stops
    check("W§160 nasal assimilation — yuj imperfect act 3sg",
          "yuj", 7, "3", "sg",
          tense="imperfect", voice="active",
          expected="ayunak",   # or ayuṅkta depending on voice
          note="Whitney §160: nasal assimilates to following stop")

    # § 182  Guṇa of ṛ → ar before consonant
    check("W§182 Guṇa ṛ→ar — kṛ present act 3sg",
          "kṛ", 8, "3", "sg",
          tense="present", voice="active",
          expected="karoti",
          note="Whitney §182: guṇa of ṛ gives ar, kṛ → karoti")

    # § 189  Vṛddhi of a → ā in certain aorists
    check("W§189 Vṛddhi — gam s-aorist act 3sg",
          "gam", 1, "3", "sg",
          tense="aorist", voice="active",
          expected="agamat",
          note="Whitney §189: root aorist, a-reduplication gam → agamat")

    # § 222  Class-1 thematic a-present
    check("W§222 Class-1 thematic — bhū present act 3sg",
          "bhū", 1, "3", "sg",
          tense="present", voice="active",
          expected="bhavati",
          note="Whitney §222: class-1 guṇa+thematic, bhū → bhavati")

    # § 233  Class-2 athematic strong/weak stems
    check("W§233 Class-2 athematic — ad present act 3sg",
          "ad", 2, "3", "sg",
          tense="present", voice="active",
          expected="atti",
          note="Whitney §233: class-2, ad → atti (tt assimilation)")

    check("W§233 Class-2 strong stem — vac present act 3sg",
          "vac", 2, "3", "sg",
          tense="present", voice="active",
          expected="vakti",
          note="Whitney §233: suppletive strong stem vac → vakti")

    # § 258  Class-3 reduplication
    check("W§258 Class-3 reduplication — hu present act 3sg",
          "hu", 3, "3", "sg",
          tense="present", voice="active",
          expected="juhoti",
          note="Whitney §258: class-3, hu reduplicated → juhoti")

    check("W§258 Class-3 long-ā — dā present act 3sg",
          "dā", 3, "3", "sg",
          tense="present", voice="active",
          expected="dadāti",
          note="Whitney §258: class-3, long-ā root dā → dadāti")

    # § 276  Class-4 ya-present
    check("W§276 Class-4 ya-present — div present act 3sg",
          "div", 4, "3", "sg",
          tense="present", voice="active",
          expected="dīvyati",
          note="Whitney §276: class-4 ya-suffix, div → dīvyati (internal lengthening)")

    # § 281  Class-5 nu/no athematic
    check("W§281 Class-5 strong — su present act 3sg",
          "su", 5, "3", "sg",
          tense="present", voice="active",
          expected="sunoti",
          note="Whitney §281: class-5 strong stem -no-, su → sunoti")

    check("W§281 Class-5 — śru present act 3sg",
          "śru", 5, "3", "sg",
          tense="present", voice="active",
          expected="śṛṇoti",
          note="Whitney §281: class-5, śru with nasal infix → śṛṇoti")

    # § 290  Class-6 thematic no-guṇa
    check("W§290 Class-6 no-guṇa — tud present act 3sg",
          "tud", 6, "3", "sg",
          tense="present", voice="active",
          expected="tudati",
          note="Whitney §290: class-6 thematic, no guṇa, tud → tudati")

    # § 295  Class-7 nasal infix
    check("W§295 Class-7 infix — yuj present act 1sg",
          "yuj", 7, "1", "sg",
          tense="present", voice="active",
          expected="yunajmi",
          note="Whitney §295: class-7 nasal infix strong form")

    check("W§295 Class-7 infix — bhid present act 3sg",
          "bhid", 7, "3", "sg",
          tense="present", voice="active",
          expected="bhinatti",
          note="Whitney §295: class-7, bhid → bhinatti")

    # § 298  Class-8 u/o athematic (like class 5 but without n-infix)
    check("W§298 Class-8 — tan present act 3sg",
          "tan", 8, "3", "sg",
          tense="present", voice="active",
          expected="tanoti",
          note="Whitney §298: class-8 strong -o-, tan → tanoti")

    # § 306  Class-9 nā/nī athematic + nati (cerebralisation)
    check("W§306 Class-9 nati — krī present act 3sg",
          "krī", 9, "3", "sg",
          tense="present", voice="active",
          expected="krīṇāti",
          note="Whitney §306: class-9, krī → krīṇāti (nati: n→ṇ after ī)")

    check("W§306 Class-9 — vṛ present mid 3sg",
          "vṛ", 9, "3", "sg",
          tense="present", voice="middle",
          expected="vṛṇīte",
          note="Whitney §306: class-9, vṛ ātmanepada → vṛṇīte")

    # § 1041 Causative -aya suffix
    check("W§1041 Causative — bhū caus present act 3sg",
          "bhū", 1, "3", "sg",
          tense="present", voice="active", derivative="causative",
          expected="bhāvayati",
          note="Whitney §1041: causative -aya, bhū → bhāvayati (vṛddhi)")

    check("W§1041 Class-10 (inherent caus) — cur present act 3sg",
          "cur", 10, "3", "sg",
          tense="present", voice="active",
          expected="corayati",
          note="Whitney §1041: class-10 = causative-style, cur → corayati")

    # § 1026 Desiderative reduplication
    check("W§1026 Desiderative — ji desid present act 3sg",
          "ji", 1, "3", "sg",
          tense="present", voice="active", derivative="desiderative",
          expected="jigīṣati",
          note="Whitney §1026: desiderative, ji → jigīṣati")

    # § 1070 Periphrastic Perfect (with āṃ)
    check("W§1070 Periphrastic perfect āṃ — cur perfect act 3sg",
          "cur", 10, "3", "sg",
          tense="perfect", voice="active",
          expected="corayāṃcakāra",
          note="Whitney §1070: periphrastic perfect with ām normalized to āṃ before c")

    # § 1087 Prefix Sandhi Special Cases
    check("W§1087 Prefix sam+kṛ — sam+kṛ present act 3sg",
          "sam+kṛ", 8, "3", "sg",
          tense="present", voice="active",
          expected="saṃskaroti",
          note="Whitney §1087c: sam+kṛ -> saṃskṛ")

    check("W§1087 Prefix api+dhā — api+dhā present act 3sg",
          "api+dhā", 3, "3", "sg",
          tense="present", voice="active",
          expected="pidadhāti",
          note="Whitney §1087: api loses a before dhā")

    check("W§1087 Prefix parā+i — parā+i present act 3sg",
          "parā+i", 2, "3", "sg",
          tense="present", voice="active",
          expected="palāyeti",
          note="Whitney §1087d: parā+i becomes palāy")

    check("W§1087 Prefix ā-never-first — ā+vi+kṛ present act 3sg",
          "ā+vi+kṛ", 8, "3", "sg",
          tense="present", voice="active",
          expected="vyākaroti",
          note="Structural: ā is floated to just before the root")

    # § 1000 s-Aorist (sigmatic)
    check("W§1000 s-Aorist — yuj aorist act 3sg",
          "yuj", 7, "3", "sg",
          tense="aorist", voice="active",
          expected=["ayaukṣīt", "ayokṣīt"],
          note="Whitney §1000: aniṭ s-aorist, yuj → ayaukṣīt")

    # § 840  Perfect reduplication
    check("W§840 Perfect — bhū perfect act 3sg",
          "bhū", 1, "3", "sg",
          tense="perfect", voice="active",
          expected="babhūva",
          note="Whitney §840: perfect reduplication, bhū → babhūva")

    check("W§840 Perfect u-reduplication — vac perfect act 3sg",
          "vac", 2, "3", "sg",
          tense="perfect", voice="active",
          expected="uvāca",
          note="Whitney §840: vac, u-reduplication → uvāca")

    # § 928  Passive ya-present
    check("W§928 Passive — kṛ passive present 3sg",
          "kṛ", 8, "3", "sg",
          tense="present", voice="passive",
          expected="kriyate",
          note="Whitney §928: passive ya-suffix, kṛ → kriyate")

    check("W§928 Passive palatal sandhi — yaj passive present 3sg",
          "yaj", 1, "3", "sg",
          tense="present", voice="passive",
          expected="ijyate",
          note="Whitney §928: passive, yaj → ijyate (palatal before y)")

    # § 963  Benedictive (āśīrliṅ)
    check("W§963 Benedictive — bhū bened act 3sg",
          "bhū", 1, "3", "sg",
          tense="benedictive", voice="active",
          expected="bhūyāt",
          note="Whitney §963: benedictive active, bhū → bhūyāt")

    check("W§963 Benedictive active — śru bened act 3sg",
          "śru", 5, "3", "sg",
          tense="benedictive", voice="active",
          expected="śrūyāt",
          note="INRIA paradigm: śru benedictive active 3sg = śrūyāt")

    # § 954  Conditional
    check("W§954 Conditional — bhū cond act 3sg",
          "bhū", 1, "3", "sg",
          tense="conditional", voice="active",
          expected="abhaviṣyat",
          note="Whitney §954: conditional = past of future, bhū → abhaviṣyat")

    # § 671  Periphrastic future (periphrastic_future)
    check("W§671 Periphrastic future — nī pfut act 3sg",
          "nī", 1, "3", "sg",
          tense="periphrastic_future", voice="active",
          expected="netā",
          note="Whitney §671: periphrastic future, nī → netā (+ asti implied)")

    # § 560  Ātmanepada-only root
    check("W§560 Ātmanepada-only — labh present mid 3sg",
          "labh", 1, "3", "sg",
          tense="present", voice="middle",
          expected="labhate",
          note="Whitney §560: ātmanepada-only, labh → labhate")

    # § 801  Perfect-as-present (vid)
    check("W§801 Perfect-as-present — vid perfect act 3sg",
          "vid", 2, "3", "sg",
          tense="perfect", voice="active",
          expected="veda",
          note="Whitney §801: vid, perfect used as present 'he knows'")

    # Denominative
    check("Whitney denom — namas present act 3sg",
          "namas", None, "3", "sg",
          tense="present", voice="active", derivative="denominative",
          expected="namasyati",
          note="Denominative -ya suffix, namas → namasyati")

    # ─────────────────────────────────────────────────────────────────────────────
    # NEW ADDITIONS FOR LAYER 1 (Internal Sandhi, Aorist Variants, Causative-Passive)
    # ─────────────────────────────────────────────────────────────────────────────

    # § 212-213 Palatal to Cerebral Sandhi (mṛj + ti -> mārṣṭi)
    check("W§212 Palatal Sandhi — mṛj present act 3sg",
          "mṛj", 2, "3", "sg",
          tense="present", voice="active",
          expected="mārṣṭi",
          note="NEW (Internal Sandhi): j/ś/ṣ before t becomes ṣṭ, mṛj → mārṣṭi")

    # § 898 iṣ-Aorist
    check("W§898 iṣ-Aorist — lū aorist act 3sg",
          "lū", 9, "3", "sg",
          tense="aorist", voice="active",
          expected="alāvīt",
          note="NEW (Aorist Variants): seṭ iṣ-aorist with vṛddhi, lū → alāvīt")

    # § 717 Vowel-final Class 2 (Tricky glide sandhi)
    check("W§717 Vowel-final Cl.2 — i present act 3pl",
          "i", 2, "3", "pl",
          tense="present", voice="active",
          expected="yanti",
          note="NEW (Present System Variants): short vowel root i → yanti in weak plural")

    # § 1046 Causative-Passive Combo
    check("W§1046 Causative Passive — bhū caus pass 3sg",
          "bhū", 1, "3", "sg",
          tense="present", voice="passive", derivative="causative",
          expected="bhāvyate",
          note="NEW (Derivatives): Causative base + passive ya-suffix, bhū → bhāvyate")

    # ─────────────────────────────────────────────────────────────────────────────
    # LAYER 2 — Root Paradigms
    # Spot-check the full present-tense paradigm (3 persons × 3 numbers × 2 voices)
    # for one representative root per class / phonology type.
    # ─────────────────────────────────────────────────────────────────────────────

    print()
    print("=" * 60)
    print("  LAYER 2 — Root Paradigms (present system)")
    print("=" * 60)

    # Each entry: (label, root, cls, voice, paradigm_dict)
    # paradigm_dict maps (person, number) → expected form(s)
    PARADIGMS = [

        ("bhū cl.1 active", "bhū", 1, "active", {
            ("1","sg"): "bhavāmi",
            ("2","sg"): "bhavasi",
            ("3","sg"): "bhavati",
            ("1","du"): "bhavāvaḥ",
            ("2","du"): "bhavathaḥ",
            ("3","du"): "bhavataḥ",
            ("1","pl"): "bhavāmaḥ",
            ("2","pl"): "bhavatha",
            ("3","pl"): "bhavanti",
        }),

        ("ad cl.2 active", "ad", 2, "active", {
            ("3","sg"): "atti",
            ("3","du"): "attaḥ",
            ("3","pl"): "adanti",
            ("2","sg"): "atsi",
            ("1","sg"): "admi",
        }),

        ("hu cl.3 active", "hu", 3, "active", {
            ("3","sg"): "juhoti",
            ("3","du"): "juhutaḥ",
            ("3","pl"): "juhvati",
            ("1","sg"): "juhomi",
        }),

        ("div cl.4 active", "div", 4, "active", {
            ("3","sg"): "dīvyati",
            ("3","pl"): "dīvyanti",
            ("1","sg"): "dīvyāmi",
        }),

        ("su cl.5 active", "su", 5, "active", {
            ("3","sg"): "sunoti",
            ("3","du"): "sunutaḥ",
            ("3","pl"): "sunvanti",
            ("1","sg"): "sunomi",
        }),

        ("tud cl.6 active", "tud", 6, "active", {
            ("3","sg"): "tudati",
            ("3","pl"): "tudanti",
            ("1","sg"): "tudāmi",
            ("2","sg"): "tudasi",
        }),

        ("yuj cl.7 active", "yuj", 7, "active", {
            ("3","sg"): "yunakti",
            ("3","du"): "yuṅktaḥ",
            ("3","pl"): "yuñjanti",
            ("1","sg"): "yunajmi",
        }),

        ("tan cl.8 active", "tan", 8, "active", {
            ("3","sg"): "tanoti",
            ("3","du"): "tanutaḥ",
            ("3","pl"): "tanvanti",
            ("1","sg"): "tanomi",
        }),

        ("krī cl.9 active", "krī", 9, "active", {
            ("3","sg"): "krīṇāti",
            ("3","du"): "krīṇītaḥ",
            ("3","pl"): "krīṇanti",
            ("1","sg"): "krīṇāmi",
        }),

        ("cur cl.10 active", "cur", 10, "active", {
            ("3","sg"): "corayati",
            ("3","pl"): "corayanti",
            ("1","sg"): "corayāmi",
            ("2","sg"): "corayasi",
        }),

        # ── Phonology types ──────────────────────────────────────────────────────

        ("kṛ cl.8 active (ṛ-root)", "kṛ", 8, "active", {
            ("3","sg"): "karoti",
            ("3","du"): "kurutaḥ",
            ("3","pl"): "kurvanti",
            ("1","sg"): "karomi",
        }),

        ("duh cl.2 active (h-sandhi)", "duh", 2, "active", {
            ("3","sg"): "dogdhi",
            ("3","pl"): "duhanti",
            ("2","sg"): "dhokṣi",   # Grassmann in 2sg
        }),

        ("han cl.2 active (gh-deletion)", "han", 2, "active", {
            ("3","sg"): "hanti",
            ("3","du"): "hataḥ",
            ("3","pl"): "ghnanti",
            ("1","sg"): "hanmi",
        }),

        ("gam cl.1 active (suppletive)", "gam", 1, "active", {
            ("3","sg"): "gacchati",
            ("3","pl"): "gacchanti",
            ("1","sg"): "gacchāmi",
        }),

        ("labh cl.1 middle (ātm.-only)", "labh", 1, "middle", {
            ("3","sg"): "labhate",
            ("3","du"): "labhete",
            ("3","pl"): "labhante",
            ("1","sg"): "labhe",
        }),

        ("yaj cl.1 passive (palatal sandhi)", "yaj", 1, "passive", {
            ("3","sg"): "ijyate",
            ("3","pl"): "ijyante",
            ("1","sg"): "ijye",
        }),

        ("kṛ cl.8 passive (ṛ-root passive)", "kṛ", 8, "passive", {
            ("3","sg"): "kriyate",
            ("3","pl"): "kriyante",
        }),

        # ── NEW ADDITIONS (Edge cases) ───────────────────────────────────────────

        ("i cl.2 active (ultra-short root)", "i", 2, "active", {
            ("3","sg"): "eti",
            ("3","pl"): "yanti",
            ("1","sg"): "emi",
        }),

        ("scand cl.1 active (conjunct root)", "scand", 1, "active", {
            ("3","sg"): "skandati",
            ("3","pl"): "skandanti",
        }),
    ]

    for label, root, cls, voice, paradigm in PARADIGMS:
        for (person, number), expected in paradigm.items():
            check(f"Paradigm [{label}] {person}{number}",
                  root, cls, person, number,
                  voice=voice, tense="present",
                  expected=expected)

    # ─────────────────────────────────────────────────────────────────────────────
    # LAYER 3 — Property-Based / Sandhi Invariant Tests
    # These check structural properties of the output string, not specific forms.
    # They should hold for every call regardless of root.
    # ─────────────────────────────────────────────────────────────────────────────

    print()
    print("=" * 60)
    print("  LAYER 3 — Property / Sandhi Invariant Tests")
    print("=" * 60)

    # Roots × tenses to stress-test properties across a range of outputs
    PROP_SAMPLE = [
        ("bhū",  1, "present",   "active"),
        ("kṛ",   8, "aorist",    "active"),
        ("yuj",  7, "future",    "active"),
        ("duh",  2, "imperfect", "active"),
        ("gam",  1, "perfect",   "active"),
        ("labh", 1, "present",   "middle"),
        ("kṛ",   8, "present",   "passive"),
        ("yaj",  1, "present",   "passive"),
        ("tan",  8, "optative",  "active"),
        ("hu",   3, "imperative","active"),
        ("cur",  10,"present",   "active"),
        ("śru",  5, "benedictive","active"),
    ]

    for root, cls, tense, voice in PROP_SAMPLE:
        for person in ["1", "2", "3"]:
            for number in ["sg", "du", "pl"]:
                tag = f"{root}/{tense}/{voice}/{person}{number}"

                # P1: No XML/HTML tags in output
                prop(f"P1 no-tags [{tag}]",
                     root, cls, person, number,
                     voice=voice, tense=tense,
                     predicate=lambda lst: not any("<" in f or ">" in f for f in lst),
                     note="Output must not contain < or > characters")

                # P2: No stray ASCII punctuation
                prop(f"P2 clean-chars [{tag}]",
                     root, cls, person, number,
                     voice=voice, tense=tense,
                     predicate=lambda lst: not any(re.search(r'[{}()\[\]\\|@#$%^&*_=+`~]', f) for f in lst),
                     note="Output must not contain stray punctuation")

                # P3: No double spaces or leading/trailing whitespace
                prop(f"P3 whitespace [{tag}]",
                     root, cls, person, number,
                     voice=voice, tense=tense,
                     predicate=lambda lst: all(f == f.strip() and "  " not in f for f in lst),
                     note="No leading/trailing/double whitespace")

                # P4: All characters are valid Unicode (no replacement chars U+FFFD)
                prop(f"P4 valid-unicode [{tag}]",
                     root, cls, person, number,
                     voice=voice, tense=tense,
                     predicate=lambda lst: not any("\ufffd" in f for f in lst),
                     note="No Unicode replacement characters")

                # P5: Non-empty output
                prop(f"P5 non-empty [{tag}]",
                     root, cls, person, number,
                     voice=voice, tense=tense,
                     predicate=lambda lst: len(lst) > 0 and all(len(f.strip()) > 0 for f in lst),
                     note="Output must not be empty string")

                # P6: No consecutive identical consonants beyond valid Sanskrit geminates
                prop(f"P6 no-runaway-geminate [{tag}]",
                     root, cls, person, number,
                     voice=voice, tense=tense,
                     predicate=lambda lst: not any(re.search(r'(.)\1{2,}', f) for f in lst),
                     note="No character repeated 3+ times consecutively")

                # P7: If result contains alternatives, each alternative must itself be non-empty
                prop(f"P7 or-alternatives-valid [{tag}]",
                     root, cls, person, number,
                     voice=voice, tense=tense,
                     predicate=lambda lst: all(f.strip() for f in lst),
                     note="Each alternative must be non-empty")

                # ── NEW ADDITIONS FOR LAYER 3 (Rigidity, Hiatus) ────────────────

                # P8: Rigidity of the Augment (Past tenses must start with a/ā)
                if tense in ["imperfect", "aorist", "conditional"]:
                    prop(f"P8 rigidity-of-augment [{tag}]",
                         root, cls, person, number,
                         voice=voice, tense=tense,
                         predicate=lambda lst: all(f.strip().startswith(('a', 'ā', 'ai', 'au')) for f in lst),
                         note="NEW: Imperfect/Aorist/Conditional MUST begin with an augment vowel")

                # P9: No Internal Hiatus (Engine shouldn't hallucinate unjoined vowels like 'aa' or 'ii')
                prop(f"P9 no-internal-hiatus [{tag}]",
                     root, cls, person, number,
                     voice=voice, tense=tense,
                     predicate=lambda lst: not any(re.search(r'(aa|ii|uu|aā|iī|uū)', f) for f in lst),
                     note="NEW: Catches broken vowel Sandhi where identical vowels fail to merge into long vowels")

    # ─────────────────────────────────────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────────────────────────────────────

    total   = len(results)
    passed  = sum(1 for r in results if r["status"] == PASS)
    failed  = [r for r in results if r["status"] == FAIL]
    crashed = [r for r in results if r["status"] == CRASH]
    pct     = f"{100 * passed / total:.1f}%" if total else "n/a"

    # Print failures
    if failed or crashed:
        print()
        print("─" * 60)
        print("  FAILURES & CRASHES")
        print("─" * 60)
        for r in failed + crashed:
            print(f"  {r['status']} [{r['label']}]")
            print(f"       root     : {r['root']}")
            print(f"       expected : {r['expected']}")
            print(f"       actual   : {r['actual']}")
            if r["note"]:
                print(f"       note     : {r['note']}")

    print()
    print("=" * 60)
    print("  EXTENDED SUITE RESULTS")
    print("=" * 60)

    # Layer breakdown
    w_results  = [r for r in results if r["label"].startswith("W§") or r["label"].startswith("Whitney")]
    p_results  = [r for r in results if r["label"].startswith("Paradigm")]
    pr_results = [r for r in results if r["label"].startswith("P")]

    def layer_line(name, subset):
        n = len(subset)
        p = sum(1 for r in subset if r["status"] == PASS)
        f = sum(1 for r in subset if r["status"] == FAIL)
        c = sum(1 for r in subset if r["status"] == CRASH)
        pct_l = f"{100*p/n:.0f}%" if n else "n/a"
        return f"  {name:<28} {p:>5}✅ {f:>5}❌ {c:>5}💥  ({pct_l})"

    print(layer_line("Whitney examples",    w_results))
    print(layer_line("Root paradigms",      p_results))
    print(layer_line("Property invariants", pr_results))
    print("  " + "─" * 52)
    print(f"  {'TOTAL':<28} {passed:>5}✅ {len(failed):>5}❌ {len(crashed):>5}💥  ({pct})")
    print("=" * 60)

if __name__ == "__main__":
    run_focused_benchmark()
    # run_extended_suite()
