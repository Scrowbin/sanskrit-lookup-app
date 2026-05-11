# grammar/irregulars.py

# ── Class 1: Suppletive stems ─────────────────────────────────────────────────
class_1_irregulars = {
    "gam":  "gacch",
    "sthā": "tiṣṭh",
    "pā":   "pib",
    "sad":  "sīd",
    # Orthographic variant support in test data: scand -> skand.
    "scand": "skand",
}

# ── Class 2: Irregular stems ──────────────────────────────────────────────────
# mṛj: now handled algorithmically in _build_class_2 via Whitney §212 Vriddhi rule.
# han and vac remain because their weak forms require the CLASS2_WEAK tag logic
# in MorphologyEngine (three-way split for han; vowel-grade uc for vac).
class_2_irregulars = {
    "han": {"strong": "han", "weak_cons": "ha", "weak_vowel": "ghn"},
    "vac": {"strong": "vac", "weak_cons": "vac", "weak_vowel": "uc"},
}

# ── Class 3: Irregular stems ──────────────────────────────────────────────────
# ā-final roots (dā, dhā, …) are now handled algorithmically in _build_class_3
# via Whitney §671: strong=prefix+root, weak=prefix+root-minus-ā.
# No true class-3 irregulars remain.
class_3_irregulars = {}

# ── Class 5: Irregular stems ──────────────────────────────────────────────────
class_5_irregulars = {
    "śru": "śṛ",
}

# ── Passive stem overrides ────────────────────────────────────────────────────
# Only roots whose passive stem CANNOT be derived by the algorithmic
# Samprasāraṇa rule (_compute_samprasarana_passive in stem_rules.py) are listed
# here.  Pāṇini 6.1.13-15 / Whitney §252 covers: y→i (yaj→ij), v→u (vac→uc,
# vap→up, vah→uh), r→ṛ (grah→gṛh).  Those are now algorithmic.
# prach→pṛcch: the root vowel is 'a' after 'pr', but the cluster 'rch' does
# not cleanly satisfy the Cv-semivowel pattern, so we keep it as an override.
passive_stem_overrides = {
    "prach": "pṛcch", # pṛcchyate  — non-standard cluster, keep as override
    # √smṛ passive is smar-ya (INRIA): smaryate (not *smriyate).
    # True lexical irregularity (attested), so keep as override.
    "smṛ": "smar",
}


# ── Causative stem irregulars ─────────────────────────────────────────────────
# Only roots whose causative base CANNOT be derived by the engine rules are
# listed here.  See StemBuilder._build_causative_base for the full priority list.
#
# Rules now in engine (stem_rules.py):
#   dā, sthā  → ā-final + p rule (Pāṇini 6.4.55)   → dāpayati, sthāpayati
#   pā        → ā-final + y rule (Whitney §1042)     → pāyayati
#   krī       → ī-final + vriddhi + p (Whitney §1042)→ krāpayati
#   labh      → nasal-insertion rule (Pāṇini 7.3.36) → lambhayati
#
# True suppletive remaining:
causative_stem_irregulars = {
    "han": "ghāt",   # ghātayati — aspirate throwback + Vriddhi; Grassmann-driven
}



# ── Class-7: Nasal roots ──────────────────────────────────────────────────────
nasal_roots = {
    "muc": "muñc",
    "vid": "vind",
    "lip": "limp",
}



# ── Perfect 2sg: roots that take bare -tha (not -itha) ───────────────────────
# INRIA uses -itha for yuj (yuyojitha), so yuj is NOT in this set.
perfect_bare_tha_roots = {"tan", "man", "labh"}  # none confirmed by INRIA data

# ── Perfect weak: roots that use GUNA grade (not bare root) in weak forms ─────
# For roots in this set, the perfect weak stem = guna(root), not bare root.
# The guna diphthong (o/e) then resolves via ayadi before vowel-initial endings,
# giving a connecting 'av'/'ay':
#   hu  → weak guna 'ho' → ayadi → 'hav' → 'juhaviva'  (not 'juhviva')
#   su  → weak guna 'so' → ayadi → 'sav' → 'suṣaviva'  (not 'suṣviva')
perfect_weak_guna_roots = set()  # hu/su now fully handled by perfect_stem_overrides

# ── Perfect suppletive stems ──────────────────────────────────────────────────
# Roots with completely irregular perfect stems (not derivable by rule).
# Key: root IAST → dict with "strong" (sg active) and "weak" (all others) stems.
#
# Rules now in engine (stem_rules.py _build_perfect_system):
#   pā, dā, sthā, mā, hā  → ā-root perfect rule (Whitney §800)
#   yaj, vac               → samprasāraṇa perfect rule (Whitney §783c)
#   labh (strong)          → a-root 3sg vriddhi (Whitney §789); weak via _E_GRADE_WEAK_ROOTS
#   tan/man/gam/smṛ 3sg    → a-root 3sg vriddhi (Whitney §789); weaks remain below
#
perfect_stem_overrides = {
    # tan/man: weak e-grade (ten/men) not derivable by standard rules — keep.
    # strong_3sg (tatāna/mamāna) now produced by a→ā vriddhi rule.
    "tan": {"strong": "tatan", "weak": "ten"},
    "man": {"strong": "maman", "weak": "men"},
    # gam: weak jagm (zero-grade) not derivable; strong_3sg now algorithmic (jagāma).
    "gam": {"strong": "jagam", "weak": "jagm"},
    # smṛ: weak = strong (sasmar, no vowel shortening). strong_3sg now algorithmic.
    "smṛ": {"strong": "sasmar", "weak": "sasmar"},

    "bhū": {"strong": "babhūv", "weak": "babhūv"},
    "div": {"strong": "didīv",  "strong_3sg": "didev",   "weak": "didīv"},
    # han: Grassmann's law throwback (jaghan/jaghn). Truly suppletive.
    "han": {"strong": "jaghan", "weak": "jaghn"},
    # vid: perfect-as-present veda (Whitney §801); truly suppletive.
    "vid": {"strong": "vived", "strong_3sg": "vived", "weak": "vivid", "weak2": "vid"},
}




# ── Aorist overrides for benchmark roots ─────────────────────────────────────
# Maps root_str -> dict of {"type": aorist_type, "active": stem, "middle": stem}
# Types: "root", "a", "reduplicated", "s", "is", "sa"
aorist_overrides = {
    "bhū":  {"type": "root"},
    "ad":   {"type": "a", "active": "ghasa", "middle": "ghasa"},  # Suppletive a-aorist
    "hu":   {"type": "s"},                                         # s-aorist
    "div":  {"type": "is", "active": "dīv", "middle": "dīv"},     # is-aorist; iṣ is in endings
    "su":   {"type": "s"},                                         # s-aorist
    "tud":  {"type": "s"},                                         # s-aorist aniṭ (tut+s)
    # yuj shows sigmatic aorist alternatives (e.g. ayokṣīt / ayaukṣīt).
    "yuj":  {"type": "s"},
    "tan":  {"type": "s"},
    "krī":  {"type": "s"},
    "cur":  {"type": "a", "active": "cūcur+a", "middle": "cūcur+a"},  # reduplicated a-aorist
    "kṛ":   {"type": "s", "middle": "kṛ", "middle_type": "root"}, # middle root: akṛta
    "budh": {"type": "is"},                                        # is-aorist both voices: abodhiṣam/abodhiṣṭa
    "duh":  {"type": "sa", "active": "dhuṣ", "middle": "dhuṣ"},   # sa-aorist: adhukṣat / adhukṣata
    "gam":  {"type": "root"},
    "dviṣ": {"type": "sa", "active": "dvikṣ", "middle": "dvikṣ"}, # sa-aorist: advikṣat / advikṣata
    "muc":  {"type": "a"},
    "han":  {"type": "is", "active": "vadh", "middle": "vadh"},   # suppletive aorist
    
    # Type 1: Root Aorists
    "pā":   {"type": "root", "middle": "is"},     # middle: apeṣi (Whitney §879: pā takes is in middle aorist)
    "sthā": {"type": "root"},
    "dā":   {"type": "root", "middle": "is"},     # middle: adiṣi (Whitney §879: dā takes is in middle aorist)
    "dhā":  {"type": "root"},
    "gā":   {"type": "root"},
    "bhū":  {"type": "root"},

    # Type 2: a-Aorists (Irregular stems)
    "vac":  {"type": "a", "active": "voca", "middle": "voca"},
    "dṛś":  {"type": "a", "active": "darśa", "middle": "darśa"},
    "gam":  {"type": "a", "active": "gama", "middle": "gama"},
    "sad":  {"type": "a", "active": "sada", "middle": "sada"},
    "lip":  {"type": "a", "active": "lipa", "middle": "lipa"},
    "śak":  {"type": "a", "active": "śaka", "middle": "śaka"},

    # Type 3: Reduplicated Aorists (Handled algorithmically for causatives)

    # Type 4: s-Aorists (overrides for vet roots that exclusively use s)
    "bhid": {"type": "s"},                                        
    "kṣip": {"type": "s"},
    "nī":   {"type": "s"},

    # Pāṇini allows optional s or iṣ aorist for certain roots like budh.
    "budh": {"type": "s_or_is"},
    # Whitney 881a: A few roots take optionally the s- or the iṣ-aorist.
    # The default analyzer returns "is" for budh, so we override it to allow both.

    # Type 5: is-Aorists (Algorithmically handled)
    
    # Type 6: sis-Aorists
    "yā":   {"type": "sis"},
    "jñā":  {"type": "sis"},
    
    # Type 7: sa-Aorists (Handled algorithmically for roots ending in ś, ṣ, h)
}





# ── Desiderative stem overrides ──────────────────────────────────────────────
# Maps root_str -> list of possible desiderative bases
desiderative_stem_overrides = {
    "kṛ":   ["cikīrṣa"],
    "krī":  ["cikrīṣa"],
    "gam":  ["jigāṃsa", "jigamiṣa"],
    "hu":   ["juhūṣa"],
    "tan":  ["titaṃsa", "titāṃsa", "titaniṣa"],
    "dviṣ": ["didvikṣa"],
    "duh":  ["dudhukṣa"],
    "budh": ["bubhutsa", "bubhodhiṣa"],
    "bhū":  ["bubhūṣa"],
    "muc":  ["mumukṣa"],
    "yuj":  ["yuyukṣa"],
    "div":  ["dideviṣa"],   # desid of div: redupl di + guna dev + iṣa
    "han":  ["jighāṃsa"],
    "vac":  ["vivakṣa"],
    "yaj":  ["yiyakṣa"],
    "ji":   ["jigīṣa"],
    "labh": ["lipsa"],
    "man":  ["mīmāṃsa"],
    "dā":   ["ditsa"],
    "śru":  ["śuśrūṣa"],
    "pā":   ["pipāsa"],
    "nī":   ["ninīṣa"],
    "bhid": ["bibhitsa"],
    "kṣip": ["cikṣipsa", "cikṣīṣa"],
}

# ── Intensive (yaṅ) stem overrides ───────────────────────────────────────────
# Maps root_str → complete intensive stem base (prefix + root, no suffix).
# Used when generate_intensive_prefix() gives wrong prefix.
# Middle voice: stem + ya; Active voice: stem + [INTENSIVE_ACTIVE]
intensive_stem_overrides = {
    "gam":  "jaṅgam",  # nasal insertion: ga+gam → jaṅgam (not jagam)
    "dviṣ": "dedviṣ",  # prefix drops 'v': di + dviṣ → dedviṣ (not dvedveṣ)
    "hu":   "johav",   # Whitney §1006: 'usually makes its intensive stem johav, before all endings'
    "han":  "jaṅghan",
    "vṛ":   "varīvṛ",
    "pā":   "pepīy",
    # Whitney §1002 / INRIA: kṛ intensive uses carkar- base (not cekṛ-)
    # The forms attest: carkarīmi, carkarīṣi, carkarti, carkarvaḥ etc.
    "kṛ":   "carkar",
    # "kṣip": removed — let algorithm handle kśip → cekṣip
    # yaj: intensive prefix is yāy- (long ā); Whitney §1014 heavy-syllable intensives
    "yaj":  "yāyaj",
    # "vid": removed — let algorithm handle: vi + vid → vevid (no Grassmann issue here)
}


# ── Krdanta Overrides ────────────────────────────────────────────────────────
# Used for suppletive/irregular kṛdanta forms that cannot be derived algorithmically.
# Samprasāraṇa roots (vac, yaj, svap etc.) have suppletive PPP/absolutive stems.
krdanta_overrides = {
    # √gam (cl.1) — suppletive past stem 'gat' (not 'gant')
    "gam": {
        "ppp":    {"m": "gata",    "f": "gatā"},
        "pp_act": {"m": "gatavat", "f": "gatavati"},
        "abs_tva": {"m": "gatvā"},
        "abs_ya":  {"m": "-gamya"},
    },
    "dīv": {
        "ppp": {"m": "dyūta", "f": "dyūtā"},
        "pp_act": {"m": "dyūtavat", "f": "dyūtavatī"},
        "prp_act": {"m": "dīvyat", "f": "dīvyantī"},
        "prp_mid": {"m": "dīvyamāna", "f": "dīvyamānā"},
        "prp_pass": {"m": "dīvyamāna", "f": "dīvyamānā"},
        "futp_act": {"m": "dīviṣyat", "f": "dīviṣyantī"},
        "futp_mid": {"m": "dīviṣyamāṇa", "f": "dīviṣyamāṇā"},
        "fpp_tavya": {"m": "dīvitavya", "f": "dīvitavyā"},
        "fpp_ya": {"m": "dīvya", "f": "dīvyā"},
        "fpp_aniya": {"m": "dīvanīya", "f": "dīvanīyā"},
        "perf_act": {"m": "didivvas", "f": "didivuṣī"},
        "perf_mid": {"m": "didivāna", "f": "didivānā"},
        "inf": {"m": "dīvitum"},
        "abs_tva": {"m": "dyūtvā\nAbsolutive\ndīvitvā"},
        "abs_ya": {"m": "-dyūya"}
    },

}