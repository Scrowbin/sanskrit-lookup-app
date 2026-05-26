# grammar/irregulars.py

# ── Class 1: Suppletive stems ─────────────────────────────────────────────────
# Suppletive class 1 stems (gam -> gacch, sthā -> tiṣṭh, etc.) are now algorithmic
# and implemented via class1_suppletion FST rule in morphology.py.
class_1_irregulars = {}

# ── Class 2: Irregular stems ──────────────────────────────────────────────────
# mṛj: handled algorithmically in _build_class_2 via Whitney §212 Vriddhi rule.
# han and vac zero-grades are now handled algorithmically in morphology.py 
# via Rule 253 zero-grade logic gated by the [WEAK] tag.
class_2_irregulars = {}

# ── Class 3: Irregular stems ──────────────────────────────────────────────────
# ā-final roots (dā, dhā, …) are now handled algorithmically in _build_class_3
# via Whitney §671: strong=prefix+root, weak=prefix+root-minus-ā.
# No true class-3 irregulars remain.
class_3_irregulars = {}

# ── Class 5: Irregular stems ──────────────────────────────────────────────────
class_5_irregulars = {}

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
causative_stem_irregulars = {
    "han": "ghāt",   # ghātayati — aspirate throwback + Vriddhi; Grassmann-driven
    "ruh": "rop",    # ropayati (Whitney §1042o)
    "dū": "dāv",     # dāvayati (Whitney §1042n)
    "dṛp": "darp",   # darpayati (Whitney §1042o)
    "knūy": "knop",  # knopayati (Whitney §1042o)
}



# ── Class-7: Nasal roots ──────────────────────────────────────────────────────
# nasal_roots removed: nasal insertion is now driven by
# RootObject.is_lrit (P. 7.1.59) in stem_rules._build_class_6.



# ── Perfect 2sg: roots that take bare -tha (not -itha) ───────────────────────
# INRIA uses -itha for yuj (yuyojitha), so yuj is NOT in this set.
perfect_bare_tha_roots = {"tan", "man", "labh", "jan", "stu", "śru"}  # jan expects jajantha OR jajñitha, stu expects tuṣṭotha, śru expects śuśrotha

# ── Perfect weak: roots that use GUNA grade (not bare root) in weak forms ─────
# For roots in this set, the perfect weak stem = guna(root), not bare root.
# The guna diphthong (o/e) then resolves via ayadi before vowel-initial endings,
# giving a connecting 'av'/'ay':
#   hu  → weak guna 'ho' → ayadi → 'hav' → 'juhaviva'  (not 'juhviva')
#   su  → weak guna 'so' → ayadi → 'sav' → 'suṣaviva'  (not 'suṣviva')
perfect_weak_guna_roots = set()

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
    "dīv": {"strong": "didīv",  "strong_3sg": "didev",   "weak": "didiv"},
    # han: Grassmann's law throwback (jaghan/jaghn). Truly suppletive.
    "han": {"strong": "jaghan", "strong_3sg": "jaghān", "weak": "jaghn"},
    # vid: perfect-as-present veda (Whitney §801); truly suppletive.
    "vid": {"strong": "vived", "strong_3sg": "vived", "weak": "vivid", "weak2": "vid"},
}




# ── Aorist overrides for benchmark roots ─────────────────────────────────────
# Maps root_str -> dict of {"type": aorist_type, "active": stem, "middle": stem}
# Types: "root", "a", "reduplicated", "s", "is", "sa"
aorist_overrides = {
    "yuj":  {"type": "s_or_a"},
    "bhū":  {"type": "root"},
    "ad":   {"type": "a", "active": "ghasa", "middle": "ghasa"},  # Suppletive a-aorist
    "hu":   {"type": "s"},                                         # s-aorist
    "div":  {"type": "is", "active": "dīv", "middle": "dīv"},     # is-aorist; iṣ is in endings
    "su":   {"type": "s"},                                         # s-aorist
    "tud":  {"type": "s"},                                         # s-aorist aniṭ (tut+s)
    "tan":  {"type": "s"},
    "krī":  {"type": "s"},
    "cur":  {"type": "a", "active": "cūcur+a", "middle": "cūcur+a"},  # reduplicated a-aorist
    "kṛ":   {"type": "s", "middle": "kṛ", "middle_type": "root"}, # middle root: akṛta

    "han":  {"type": "is", "active": "vadh", "middle": "vadh"},   # suppletive aorist
    
    # Type 1: Root Aorists
    "pā":   {"type": "root", "middle_type": "s", "middle": "pe"},
    "sthā": {"type": "root"},
    "dā":   {"type": "root", "middle_type": "s", "middle": "di"},
    "dhā":  {"type": "root", "middle_type": "s", "middle": "dhi"},
    "gā":   {"type": "root"},

    # Type 2: a-Aorists (Irregular stems)
    "vac":  {"type": "a", "active": "voca", "middle": "voca"},
    "dṛś":  {"type": "a", "active": "darśa", "middle": "darśa"},
    "jan":  {"type": "root", "middle_type": "is"},

    # Type 3: Reduplicated Aorists (Handled algorithmically for causatives)

    # Type 4: s-Aorists (overrides for vet roots that exclusively use s)
    "bhid": {"type": "s"},                                        
    "kṣip": {"type": "s"},
    "nī":   {"type": "s"},
    "muc":  {"type": "s"},

    # Pāṇini allows optional s or iṣ aorist for certain roots like budh.
    "budh": {"type": "s_or_is"},
    # Whitney §881a: budh takes either the s-aorist or iṣ-aorist.
    # Dual-dispatch in conjugate._conjugate_aorist_dual handles both types.

    # Whitney §834b: labh takes s-aorist (lābh+s → lāps via deaspiration).
    "labh": {"type": "s"},

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
    "budh": ["bubhutsa", "bubhodiṣa", "bubhodhiṣa"],
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
    # Exceptions that keep 'ā' (Whitney §1028b)
    "sthā": ["tiṣṭhāsa"],
    "jñā":  ["jijñāsa"],
    "ghrā": ["jighrāsa"],
    "gā":   ["jigāsa"],
    # Whitney §1028e: nind drops nasal in desiderative → ninitsa (nid+sa, d+s→ts)
    "nind": ["ninitsa"],
    # Whitney §1031: svap undergoes samprasāraṇa (sva→su) → suṣupsa
    "svap": ["suṣupsa"],

}

# ── Intensive (yaṅ) stem overrides ───────────────────────────────────────────
# Maps root_str → complete intensive stem base (prefix + root, no suffix).
# Used when generate_intensive_prefix() gives wrong prefix.
# Middle voice: stem + ya; Active voice: stem + [INTENSIVE_ACTIVE]
intensive_stem_overrides = {
    # "gam":  "jaṅgam",  # nasal insertion: ga+gam → jaṅgam (not jagam)
    "han":  {"strong": "jaṅgha", "weak": "jaṅgha", "middle": "jaṅghan"},
    "vṛ":   "varīvṛ",
    "pā":   "pepīp",
    # Whitney §1002 / INRIA: kṛ intensive uses carkar- base (not cekṛ-)
    # The forms attest: carkarīmi, carkarīṣi, carkarti, carkarvaḥ etc.
    "kṛ":   "carkar",
    "mṛj":  "marmṛj",
    # "kṣip": removed — let algorithm handle kśip → cekṣip
    # yaj: intensive prefix is yāy- (long ā); Whitney §1014 heavy-syllable intensives
    "yaj":  "yāyaj",
    # budh: Whitney §1002i - Grassmann roots restore the original aspirate in the prefix
    "budh": {"strong": "bobhodh", "weak": "bobhudh", "middle": "bobhudh"},

    # Whitney §1002c — Type II intensives: consonant-copy prefix.
    # The root-final consonant is echoed after the prefix vowel (short a),
    # then undergoes sandhi with the following root-initial consonant.
    # car  (√car)  → prefix 'car' + root 'car' → caṇcar  (r+c assimilation → ṇc)
    # cal  (√cal)  → prefix 'cal' + root 'cal' → caṇcal  (l+c assimilation → ṇc)
    "car":  "caṇcar",
    "cal":  "caṇcal",
    # Whitney §1002g: svap intensive uses samprasāraṇa soṣup (sva→su, o-grade, RUKI s→ṣ)
    "svap": "soṣup",
}


# ── Krdanta Overrides ────────────────────────────────────────────────────────
# Suppletive / irregular kṛdanta forms only. Validate shrinking candidates with:
#   python validate_krdantas_parts.py
# (parts.csv mode=past vs krdantas.py). √gam / √dīv remain until productive PPP /
# class-4 stems match INRIA without overrides.
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
    # ── Samprasāraṇa PPP overrides (Whitney §252, Pāṇini 6.1.13-15) ─────────
    # These roots undergo suppletive stem changes in -ta/-tvā participles that
    # involve simultaneous samprasāraṇa + cluster sandhi, not derivable by the
    # generic root+ta algorithm.
    "vac": {
        "ppp":     {"m": "ukta",    "f": "uktā"},       # va→u, c+t→kt
        "pp_act":  {"m": "uktavat", "f": "uktavatī"},
        "abs_tva": {"m": "uktvā"},
        "abs_ya":  {"m": "-ucya"},
    },
    "yaj": {
        "ppp":     {"m": "iṣṭa",    "f": "iṣṭā"},      # ya→i, j+t→ṣṭ
        "pp_act":  {"m": "iṣṭavat", "f": "iṣṭavatī"},
        "abs_tva": {"m": "iṣṭvā"},
        "abs_ya":  {"m": "-ijya"},
    },
    "svap": {
        "ppp":     {"m": "supta",    "f": "suptā"},     # sva→su, p+t→pt
        "pp_act":  {"m": "suptavat", "f": "suptavatī"},
        "abs_tva": {"m": "suptvā"},
    },
    "vap": {
        "ppp":     {"m": "upta",    "f": "uptā"},       # va→u, p+t→pt
        "pp_act":  {"m": "uptavat", "f": "uptavatī"},
        "abs_tva": {"m": "uptvā"},
    },
    "vah": {
        "ppp":     {"m": "ūḍha",    "f": "ūḍhā"},      # va→u→ū, h+t→ḍh (§155)
        "pp_act":  {"m": "ūḍhavat", "f": "ūḍhavatī"},
    },
    "grah": {
        "ppp":     {"m": "gṛhīta",    "f": "gṛhītā"},   # gra→gṛ, seṭ +ī+ta
        "pp_act":  {"m": "gṛhītavat", "f": "gṛhītavatī"},
        "abs_tva": {"m": "gṛhītvā"},
    },
    "prach": {
        "ppp":     {"m": "pṛṣṭa",    "f": "pṛṣṭā"},    # pra→pṛ, ch+t→ṣṭ
        "pp_act":  {"m": "pṛṣṭavat", "f": "pṛṣṭavatī"},
    },
}