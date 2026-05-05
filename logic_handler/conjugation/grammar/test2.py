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

import sys, io, re, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from conjugate import SanskritConjugator

api = SanskritConjugator()

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

PASS = "✅"
FAIL = "❌"
CRASH = "💥"

results = []   # list of dicts, printed at the end

def check(label, root, cls, person, number, *,
          voice="active", tense="present", derivative="primary",
          expected, note=""):
    """Run one conjugation and record pass/fail."""
    try:
        actual = api.conjugate(root, cls, person, number,
                               voice=voice, tense=tense,
                               derivative=derivative, use_db=False)
        actual_forms = [f.strip() for f in actual.split(" OR ")]
        expected_forms = expected if isinstance(expected, list) else [expected]
        ok = any(a in expected_forms for a in actual_forms)
        status = PASS if ok else FAIL
        results.append({
            "status":   status,
            "label":    label,
            "root":     root,
            "expected": " / ".join(expected_forms),
            "actual":   actual,
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
                 predicate=lambda s: "<" not in s and ">" not in s,
                 note="Output must not contain < or > characters")

            # P2: No stray ASCII punctuation (only IAST diacritics + letters + space + OR)
            prop(f"P2 clean-chars [{tag}]",
                 root, cls, person, number,
                 voice=voice, tense=tense,
                 predicate=lambda s: not re.search(r'[{}()\[\]\\|@#$%^&*_=+`~]', s),
                 note="Output must not contain stray punctuation")

            # P3: No double spaces or leading/trailing whitespace
            prop(f"P3 whitespace [{tag}]",
                 root, cls, person, number,
                 voice=voice, tense=tense,
                 predicate=lambda s: s == s.strip() and "  " not in s,
                 note="No leading/trailing/double whitespace")

            # P4: All characters are valid Unicode (no replacement chars U+FFFD)
            prop(f"P4 valid-unicode [{tag}]",
                 root, cls, person, number,
                 voice=voice, tense=tense,
                 predicate=lambda s: "\ufffd" not in s,
                 note="No Unicode replacement characters")

            # P5: Non-empty output
            prop(f"P5 non-empty [{tag}]",
                 root, cls, person, number,
                 voice=voice, tense=tense,
                 predicate=lambda s: len(s.strip()) > 0,
                 note="Output must not be empty string")

            # P6: No consecutive identical consonants beyond valid Sanskrit geminates
            prop(f"P6 no-runaway-geminate [{tag}]",
                 root, cls, person, number,
                 voice=voice, tense=tense,
                 predicate=lambda s: not re.search(r'(.)\1{2,}', s),
                 note="No character repeated 3+ times consecutively")

            # P7: If result contains " OR ", each alternative must itself be non-empty
            prop(f"P7 or-alternatives-valid [{tag}]",
                 root, cls, person, number,
                 voice=voice, tense=tense,
                 predicate=lambda s: all(p.strip() for p in s.split(" OR ")),
                 note="Each OR-separated alternative must be non-empty")

            # ── NEW ADDITIONS FOR LAYER 3 (Rigidity, Hiatus) ────────────────

            # P8: Rigidity of the Augment (Past tenses must start with a/ā)
            if tense in ["imperfect", "aorist", "conditional"]:
                prop(f"P8 rigidity-of-augment [{tag}]",
                     root, cls, person, number,
                     voice=voice, tense=tense,
                     predicate=lambda s: all(f.strip().startswith(('a', 'ā', 'ai', 'au')) for f in s.split(" OR ")),
                     note="NEW: Imperfect/Aorist/Conditional MUST begin with an augment vowel")

            # P9: No Internal Hiatus (Engine shouldn't hallucinate unjoined vowels like 'aa' or 'ii')
            prop(f"P9 no-internal-hiatus [{tag}]",
                 root, cls, person, number,
                 voice=voice, tense=tense,
                 predicate=lambda s: not re.search(r'(aa|ii|uu|aā|iī|uū)', s),
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