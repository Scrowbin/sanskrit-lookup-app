"""
test_suite.py — Master Offline Regression Suite for the Sanskrit FST Engine

Consolidates all phase-specific benchmarks into a single runner.
Expected forms are hardcoded from authoritative sources:
  - Macdonell, A Sanskrit Grammar (1910)
  - Whitney, Sanskrit Grammar (1879) / The Roots... (1885)
  - Kale, A Higher Sanskrit Grammar (1894)
  - Heritage Sanskrit Grammar (INRIA, cross-referenced)

Run with:
    python test_suite.py

No database or network access required (use_db=False throughout).
A single tweak to any engine file can be validated instantly.
"""
import sys
import io
import time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from conjugate import SanskritConjugator
from krdantas import KrdantaEngine


# ══════════════════════════════════════════════════════════════════════════════
# Shared helpers
# ══════════════════════════════════════════════════════════════════════════════

def _krdanta_block(c: SanskritConjugator, root_with_preverb: str, cls: int) -> str:
    return c.conjugate(root_with_preverb, cls, "3", "sg", "active", "krdantas", use_db=False)

def _conj(c: SanskritConjugator, root_str, cls, person, number, voice, tense, derivative=None):
    return c.conjugate(root_str, cls, person, number, voice, tense,
                       derivative=derivative, use_db=False)

def _forms(result):
    """Normalize result into a set of forms."""
    if isinstance(result, list):
        return set(result)
    return {f.strip() for f in result.split(" OR ")}



# ══════════════════════════════════════════════════════════════════════════════
# Phase 1 — Kṛdantas (Participles, Infinitives, Gerunds)
# ══════════════════════════════════════════════════════════════════════════════
#
# Format: (root_with_preverb_or_bare_root, class, expected_substring_in_block)
# Tested as substring of the krdantas block output.
# Sources: Macdonell §§158–166, Whitney §§961–1050

PHASE1 = [
    # ── Past Passive Participle (-ta / -na) ───────────────────────────────────
    # Standard: final consonant + ta sandhi
    ("bhū",    1, "bhūta"),            # bhū+ta → bhūta
    ("kṛ",     8, "kṛta"),             # kṛ+ta → kṛta
    ("yuj",    7, "yukta"),            # yuj+ta → yukta (palatal → velar before t)
    ("duh",    2, "dugdha"),           # duh+ta → dugdha (aspirate throwback)
    ("nī",     1, "nīta"),             # long ī preserved
    ("tud",    6, "tutta"),            # tud+ta → tutta (gemination? no: tud+ta → tutta via voicing)
    # Samprasāraṇa suppletive PPPs (via krdanta_overrides)
    ("vac",    2, "ukta"),             # va→u, vac+ta → ukta
    ("yaj",    1, "iṣṭa"),            # ya→i, yaj+ta → iṣṭa
    ("svap",   2, "supta"),            # sva→su, svap+ta → supta
    ("vap",    1, "upta"),             # va→u, vap+ta → upta
    ("vah",    1, "ūḍha"),             # va→u, vah+ta → ūḍha
    ("grah",   9, "gṛhīta"),           # ra→ṛ, seṭ: gṛh+ī+ta
    ("prach",  6, "pṛṣṭa"),            # ra→ṛ, prach+ta → pṛṣṭa
    ("dīv",    4, "dyūta"),            # irregular suppletive override

    # ── Past PPP with preverb ─────────────────────────────────────────────────
    ("pra+vac",    2, "prokta"),       # pra+ukta → prokta (a+u→o)
    ("sam+yuj",    7, "saṃyukta"),     # saṃ+yukta
    ("ā+gam",      1, "āgata"),        # ā+gata

    # ── Absolutive (-tvā / -ya with preverb) ──────────────────────────────────
    ("bhū",    1, "bhūtvā"),
    ("kṛ",     8, "kṛtvā"),
    ("yuj",    7, "yuktvā"),
    ("vac",    2, "uktvā"),            # Samprasāraṇa
    ("yaj",    1, "iṣṭvā"),           # Samprasāraṇa
    # BUG: engine produces 'saṅgaṃya' (anusvara before y) but correct is 'saṅgamya'
    # The Parasvaraṇa m+g → ṅg is applied but anusvara before y is wrong for this context
    ("sam+gam",1, "saṅgamya"),         # correct: saṃ+gamya → saṅgamya

    # ── Present Active Participle (-ant) ──────────────────────────────────────
    ("bhū",    1, "bhavant"),          # thematic: bho+ant → bhavant (ayadi)
    ("kṛ",     8, "kurvant"),          # athematic: kur+vant
    ("dā",     3, "dadant"),           # reduplicating dadā → dad+ant

    # ── Future Passive Participle / Gerundive ─────────────────────────────────
    ("gam",    1, "gantavya"),         # gant (aniṭ periphrastic) + avya
    ("bhū",    1, "bhavitavya"),       # bhavi (seṭ) + tavya
    ("kṛ",     8, "kartavya"),         # kar (aniṭ) + tavya
    ("nī",     1, "netavya"),          # ne (aniṭ) + tavya

    # ── Infinitive (-tum) ────────────────────────────────────────────────────
    ("gam",    1, "gantum"),
    ("kṛ",     8, "kartum"),
    ("bhū",    1, "bhavitum"),
    ("nī",     1, "netum"),            # ne+tum (aniṭ)

    # ── Future Active Participle (-iṣyat) ────────────────────────────────────
    ("bhū",    1, "bhaviṣyat"),
    ("gam",    1, "gamiṣyat"),
]


# ══════════════════════════════════════════════════════════════════════════════
# Phase 2 — The 7 Aorist Types
# ══════════════════════════════════════════════════════════════════════════════
#
# Format: (root, class, person, number, voice, expected_form)
# Sources: Whitney §§824–904, Macdonell §§145–163

PHASE2 = [
    # Type 1: Root Aorist (augment + bare root + secondary endings)
    ("bhū",  1, "3", "sg", "active", "abhūt"),
    ("bhū",  1, "1", "sg", "active", "abhūvam"),
    ("bhū",  1, "3", "pl", "active", "abhūvan"),
    ("bhū",  1, "2", "sg", "middle", "abhūthāḥ"),
    ("dā",   3, "3", "sg", "active", "adāt"),
    ("dā",   3, "1", "sg", "active", "adām"),
    ("dā",   3, "3", "du", "active", "adātām"),
    ("pā",   1, "3", "sg", "active", "apāt"),
    ("sthā", 1, "3", "sg", "active", "asthāt"),
    ("sthā", 1, "1", "sg", "active", "asthām"),

    # Type 2: a-Aorist (thematic; stem = irregular base + a)
    ("vac",  2, "3", "sg", "active", "avocat"),
    ("vac",  2, "1", "sg", "active", "avocam"),
    ("vac",  2, "3", "pl", "active", "avocan"),
    ("lip",  6, "3", "sg", "active", "alipat"),
    ("lip",  6, "1", "sg", "active", "alipam"),

    # Type 3: Reduplicated Aorist (causatives / class 10)
    ("jan",  10, "3", "sg", "active", "ajījanat"),
    ("jan",  10, "1", "sg", "active", "ajījanam"),
    ("jan",  10, "3", "pl", "active", "ajījanan"),
    ("cur",  10, "3", "sg", "active", "acūcurat"),
    ("cur",  10, "1", "sg", "active", "acūcuram"),

    # Type 4: s-Aorist (guna + s; iṣ for seṭ voiced final)
    ("nī",   1, "3", "sg", "active", "anaiṣīt"),
    ("nī",   1, "1", "sg", "active", "anaiṣam"),
    ("nī",   1, "2", "sg", "active", "anaiṣīḥ"),

    # Type 5: iṣ-Aorist (guna + iṣ; seṭ roots)
    ("pū",   9, "3", "sg", "active", "apāvīt"),
    ("pū",   9, "1", "sg", "active", "apāviṣam"),
    ("budh", 1, "3", "sg", "active", "abodhīt"),
    ("budh", 1, "1", "sg", "active", "abodhiṣam"),

    # Type 6: siṣ-Aorist (long-vowel roots)
    ("yā",   2, "3", "sg", "active", "ayāsiṣīt"),
    ("yā",   2, "1", "sg", "active", "ayāsiṣam"),

    # Type 7: sa-Aorist (palatal/sibilant roots → kṣ)
    ("diś",  6, "3", "sg", "active", "adikṣat"),
    ("diś",  6, "1", "sg", "active", "adikṣam"),
    ("diś",  6, "3", "pl", "active", "adikṣan"),

    # Aorist Passive (3sg only: vrddhi+i)
    ("bhū",  1, "3", "sg", "passive", "abhāvi"),
    ("nī",   1, "3", "sg", "passive", "anāyi"),
    ("kṛ",   8, "3", "sg", "passive", "akāri"),
    # Root-aorist 1sg of √kṛ (class 8): akārṣam.
    ("kṛ",   8, "1", "sg", "active",  "akārṣam"),
]


# ══════════════════════════════════════════════════════════════════════════════
# Phase 3 — Denominative (Nāmadhātu) Conjugation
# ══════════════════════════════════════════════════════════════════════════════
#
# Format: (nominal_base, tense, person, number, voice, expected)
# Sources: Macdonell §128, Whitney §§1053–1068

PHASE3 = [
    # a/ā-stems → ī+ya  (kāmyac affix lengthens a → ī)
    ("putra",  "present",   "3", "sg", "active", "putrīyati"),
    ("putra",  "present",   "1", "sg", "active", "putrīyāmi"),
    ("putra",  "present",   "2", "sg", "active", "putrīyasi"),
    ("putra",  "present",   "3", "pl", "active", "putrīyanti"),
    ("putra",  "imperfect", "3", "sg", "active", "aputrīyat"),
    ("putra",  "optative",  "3", "sg", "active", "putrīyet"),
    ("putra",  "optative",  "3", "pl", "active", "putrīyeyuḥ"),
    ("putra",  "future",    "3", "sg", "active", "putrīyiṣyati"),
    # Periphrastic perfect: base+āṃ+cakāra (anusvāra valid before c per 8.4.59)
    ("putra",  "perfect",   "3", "sg", "active", "putrīyāṃcakāra"),
    # ā-stems → ī+ya
    ("mālā",   "present",   "3", "sg", "active", "mālīyati"),
    # i-stems → ī+ya
    ("kavi",   "present",   "3", "sg", "active", "kavīyati"),
    ("kavi",   "present",   "1", "sg", "active", "kavīyāmi"),
    ("kavi",   "future",    "3", "sg", "active", "kavīyiṣyati"),
    ("kavi",   "imperfect", "3", "sg", "active", "akavīyat"),
    # u-stems → ū+ya
    ("viṣṇu",  "present",   "3", "sg", "active", "viṣṇūyati"),
    # ṛ-stems → rī+ya
    ("pitṛ",   "present",   "3", "sg", "active", "pitrīyati"),
    # as-stems → direct ya (namas+ya)
    ("namas",  "present",   "3", "sg", "active", "namasyati"),
]


# ══════════════════════════════════════════════════════════════════════════════
# Phase 4A — Samprasāraṇa via krdanta_overrides
# ══════════════════════════════════════════════════════════════════════════════
#
# Format: (root_with_optional_preverb, class, expected_in_block)

PHASE4A = [
    ("vac",   2, "ukta"),      ("vac",   2, "uktavat"),
    ("vac",   2, "uktvā"),     ("vac",   2, "-ucya"),
    ("yaj",   1, "iṣṭa"),      ("yaj",   1, "iṣṭvā"),
    ("yaj",   1, "-ijya"),
    ("svap",  2, "supta"),     ("svap",  2, "suptvā"),
    ("vap",   1, "upta"),      ("vap",   1, "uptvā"),
    ("vah",   1, "ūḍha"),
    ("grah",  9, "gṛhīta"),    ("grah",  9, "gṛhītvā"),
    ("prach", 6, "pṛṣṭa"),
    ("dīv",   4, "dyūta"),
    # With preverb: preverb+PPP sandhi
    ("pra+vac",  2, "prokta"),       # pra+ukta → prokta
    ("sam+yuj",  7, "saṃyukta"),
    ("ā+gam",    1, "āgata"),
]


# ══════════════════════════════════════════════════════════════════════════════
# Phase 4B — Multi-Preverb Anusvāra / Parasavarṇa Sandhi
# ══════════════════════════════════════════════════════════════════════════════
#
# Format: (root_str_with_preverbs, class, person, number, voice, tense, expected)

PHASE4B = [
    # m + dental (n, t, d) → nasal assimilation
    ("sam+ni+dhā",  3, "3", "sg", "active", "present", "sannidadhāti"),
    ("sam+ni+pat",  1, "3", "sg", "active", "present", "sannipatati"),
    ("sam+dhā",     3, "3", "sg", "active", "present", "sandadhāti"),
    ("sam+dā",      3, "3", "sg", "active", "present", "sandadāti"),
    # m + palatal (c, j) → ñ
    ("sam+car",     1, "3", "sg", "active", "present", "sañcarati"),
    ("sam+cal",     1, "3", "sg", "active", "present", "sañcalati"),
    # m + velar (k, g) → ṅ
    ("sam+gam",     1, "3", "sg", "active", "present", "saṅgacchati"),
    # m + labial (p, b) → m unchanged (same class)
    ("sam+pūj",    10, "3", "sg", "active", "present", "sampūjayati"),
    # m + semivowel/sibilant → anusvāra ṃ
    ("sam+vad",     1, "3", "sg", "active", "present", "saṃvadati"),
    ("sam+śru",     5, "3", "sg", "active", "present", "saṃśṛṇoti"),
    ("sam+yuj",     7, "3", "sg", "active", "present", "saṃyunakti"),
    # Three-preverb chains
    ("sam+pra+sthā",1, "3", "sg", "active", "present", "sampratiṣṭhati"),
    ("sam+pra+yā",  2, "3", "sg", "active", "present", "samprayāti"),
    ("ud+ā+hṛ",     1, "3", "sg", "active", "present", "udāharati"),
]


# ══════════════════════════════════════════════════════════════════════════════
# Master runner
# ══════════════════════════════════════════════════════════════════════════════

class SuiteRunner:
    def __init__(self):
        self.c = SanskritConjugator()
        self.total_pass = 0
        self.total_fail = 0
        self.all_failures: list[tuple[str, str, str]] = []

    def _header(self, title: str):
        print()
        print("═" * 68)
        print(f"  {title}")
        print("═" * 68)

    def _record(self, label: str, expected: str, ok: bool, got):
        if ok:
            print(f"  ✅  {label:<50} → {expected}")
            self.total_pass += 1
        else:
            if isinstance(got, list):
                got_str = " OR ".join(got)
            else:
                got_str = str(got)
            snippet = got_str[:80].replace("\n", " ↵ ")
            print(f"  ❌  {label:<50}  expected='{expected}'")
            print(f"       got: '{snippet}'")
            self.total_fail += 1
            self.all_failures.append((label, expected, got_str))

    # ── Phase 1 ───────────────────────────────────────────────────────────────
    def run_phase1(self):
        self._header("PHASE 1 — Kṛdantas (Participles, Infinitives, Gerunds)")
        for root_str, cls, expected in PHASE1:
            label = f"{root_str} (cl.{cls}) ⊃ '{expected}'"
            try:
                block = _krdanta_block(self.c, root_str, cls)
                self._record(label, expected, expected in block, block)
            except Exception as e:
                self._record(label, expected, False, f"ERROR: {e}")

    # ── Phase 2 ───────────────────────────────────────────────────────────────
    def run_phase2(self):
        self._header("PHASE 2 — The 7 Aorist Types")
        for root, cls, person, number, voice, expected in PHASE2:
            label = f"{root} cl.{cls} {person}{number} {voice} aorist"
            try:
                result = _conj(self.c, root, cls, person, number, voice, "aorist")
                self._record(label, expected, expected in _forms(result), result)
            except Exception as e:
                self._record(label, expected, False, f"ERROR: {e}")

    # ── Phase 3 ───────────────────────────────────────────────────────────────
    def run_phase3(self):
        self._header("PHASE 3 — Denominative (Nāmadhātu) Conjugation")
        for base, tense, person, number, voice, expected in PHASE3:
            label = f"{base} {tense} {person}{number} {voice}"
            try:
                result = _conj(self.c, base, 1, person, number, voice, tense, "denominative")
                self._record(label, expected, expected in _forms(result), result)
            except Exception as e:
                self._record(label, expected, False, f"ERROR: {e}")

    # ── Phase 4A ──────────────────────────────────────────────────────────────
    def run_phase4a(self):
        self._header("PHASE 4A — Samprasāraṇa Kṛdanta Forms")
        for root_str, cls, expected in PHASE4A:
            label = f"{root_str} (cl.{cls}) ⊃ '{expected}'"
            try:
                block = _krdanta_block(self.c, root_str, cls)
                self._record(label, expected, expected in block, block)
            except Exception as e:
                self._record(label, expected, False, f"ERROR: {e}")

    # ── Phase 4B ──────────────────────────────────────────────────────────────
    def run_phase4b(self):
        self._header("PHASE 4B — Multi-Preverb Anusvāra / Parasavarṇa")
        for root_str, cls, person, number, voice, tense, expected in PHASE4B:
            label = f"{root_str} cl.{cls} {person}{number} {voice} {tense}"
            try:
                result = _conj(self.c, root_str, cls, person, number, voice, tense)
                self._record(label, expected, expected in _forms(result), result)
            except Exception as e:
                self._record(label, expected, False, f"ERROR: {e}")

    # ── Summary ───────────────────────────────────────────────────────────────
    def summary(self):
        total = self.total_pass + self.total_fail
        pct = f"{100 * self.total_pass / total:.1f}%" if total else "n/a"
        print()
        print("═" * 68)
        print("  SUITE SUMMARY")
        print("═" * 68)
        print(f"  ✅ Passed : {self.total_pass:>4}  ({pct})")
        print(f"  ❌ Failed : {self.total_fail:>4}")
        print(f"  📊 Total  : {total:>4}")

        if self.all_failures:
            print()
            print(f"  ── {len(self.all_failures)} Failure(s) ──")
            for label, expected, got in self.all_failures:
                snippet = got[:100].replace("\n", " ↵ ")
                print(f"    • {label}")
                print(f"        expected : '{expected}'")
                print(f"        got      : '{snippet}'")
        print("═" * 68)
        return self.total_fail == 0


def main():
    t0 = time.time()
    runner = SuiteRunner()
    runner.run_phase1()
    runner.run_phase2()
    runner.run_phase3()
    runner.run_phase4a()
    runner.run_phase4b()
    ok = runner.summary()
    print(f"\n  ⏱  Completed in {time.time() - t0:.2f}s")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
