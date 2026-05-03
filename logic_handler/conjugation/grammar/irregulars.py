# grammar/irregulars.py

# ── Class 1: Suppletive stems ─────────────────────────────────────────────────
class_1_irregulars = {
    "gam":  "gacch",
    "sthā": "tiṣṭh",
    "pā":   "pib",
    "sad":  "sīd",
}

# ── Class 2: Irregular stems ──────────────────────────────────────────────────
class_2_irregulars = {
    "han": {"strong": "han", "weak_cons": "ha", "weak_vowel": "ghn"},
    "vac": {"strong": "vac", "weak_cons": "vac", "weak_vowel": "uc"},
}

# ── Class 3: Irregular stems ──────────────────────────────────────────────────
class_3_irregulars = {
    "dā": {"strong": "dadā", "weak": "dad"},
}

# ── Class 5: Irregular stems ──────────────────────────────────────────────────
class_5_irregulars = {
    "śru": "śṛ",
}

# ── Passive stem overrides ────────────────────────────────────────────────────
passive_stem_overrides = {
    "vac": "uc",     # ucyate (Samprasāraṇa: v→u, a→zero, c stays)
    "yaj": "ij",    # ijyate
    "svap": "sup",  # supyate
    "vap": "up",    # upyate
    "vah": "uh",    # uhyate
    "grah": "gṛh",  # gṛhyate
    "prach": "pṛcch", # pṛchyate
}

# ── Aniṭ roots (future takes bare -sya-, not -iṣya-) ─────────────────────────
# Decision is made on the POST-GUNA form in stem_rules._build_future_system.
# Diphthong-final guna forms (e/o) ALSO count as consonant-ending for Seṭ
# (they resolve via ayadi before the following i: bho+iṣya → bhaviṣya).
# Aniṭ roots override this and always take bare -sya-.
aset_roots = {
    "yaj",   # yakṣyati
    "vac",   # vakṣyati
    "vah",   # vakṣyati
    "dviṣ",  # dvekṣyati
    "duh",   # dhokṣyati
    "yuj",   # yokṣyati
    "ad",    # atsyati
    "hu",    # hoṣyati
    "krī",   # kreṣyāmi
    "tud",   # totsyati
    "gam",   # gantā (periphrastic future is aniṭ)
}


# ── Causative stem irregulars ─────────────────────────────────────────────────
# Roots whose causative base is NOT built by regular Vṛddhi/Guna + aya rule.
# Key: root IAST → Value: causative BASE (without the +aya suffix).
# _build_class_10 appends "+aya" after this base.
causative_stem_irregulars = {
    "krī": "krāp",   # krāpayati
    "div": "dev",    # devayati (guna of div — no vriddhi since i is short penultimate)
    "gam": "gam",    # gamayati (a-vowel root: no change)
    "han": "ghāt",   # ghātayati
    "pūj": "pūj",    # pūjayati (long-ū root: no vrddhi/guna change)
    "cur": "cor",    # corayati (guna of u → o; NOT vrddhi)
}



# ── Class-7: Nasal roots ──────────────────────────────────────────────────────
nasal_roots = {
    "muc": "muñc",
    "vid": "vind",
    "lip": "limp",
}

# ── Perfect reduplication overrides ──────────────────────────────────────────
# Key: root IAST → reduplication prefix string
perfect_redupe_overrides = {
    "bhū": "ba",   # babhūva (NOT bubhūva)
    "krī": "ci",   # cikraya  (NOT crikraya; algorithm gives cri- which is wrong)
    "dviṣ": "di",  # didveṣa (reduplication drops 'v')
}

# ── Perfect 2sg: roots that take bare -tha (not -itha) ───────────────────────
# INRIA uses -itha for yuj (yuyojitha), so yuj is NOT in this set.
perfect_bare_tha_roots = set()  # none confirmed by INRIA data

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
# The stems are bare (no boundary prefix); _build_perfect_system prepends prefix+.
perfect_stem_overrides = {
    "tan": {"strong": "tatan", "weak": "ten"},
    "bhū": {"strong": "babhūv", "weak": "babhūv"},
    # hu: weak before vowels (juhav+iva) vs zero-grade before consonants (juhuv+thaḥ)
    "hu":  {"strong": "juhāv", "weak": "juhav", "weak2": "juhuv"},
    # su: weak before vowels (suṣav+iva) vs zero-grade before consonants (suṣuv+thaḥ)
    "su":  {"strong": "suṣāv", "weak": "suṣav", "weak2": "suṣuv"},
    "gam": {"strong": "jagām", "weak": "jagm"},
    "div": {"strong": "didev", "weak": "didiv"},  # didev+a=dideva / didiviva
    "pā":  {"strong": "papā", "weak": "pap"},     # 3sg papau is handled via ending, but strong stem is papā
    "dā":  {"strong": "dadā", "weak": "dad"},
    "sthā": {"strong": "tasthā", "weak": "tasth"},
    "mā":  {"strong": "mamā", "weak": "mam"},
    "hā":  {"strong": "jahā", "weak": "jah"},
    "han": {"strong": "jaghān", "weak": "jaghn"},
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
    "yuj":  {"type": "root"},
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
    "pā":   {"type": "root"},
    "sthā": {"type": "root"},
    "dā":   {"type": "root"},
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

    # Type 5: is-Aorists (Algorithmically handled)
    
    # Type 6: sis-Aorists
    "yā":   {"type": "sis"},
    "jñā":  {"type": "sis"},
    
    # Type 7: sa-Aorists (Handled algorithmically for roots ending in ś, ṣ, h)
}


# ── Future stem overrides ─────────────────────────────────────────────────────
# Roots whose future stem is NOT guna(root) + sya/iṣya.
# Maps root_str → {"stem": bare_stem, "anit": bool}
future_stem_overrides = {
    "div": {"stem": "dīv"},          # dīviṣyati — uses class-4 lengthened stem, no guna
    "gam": {"stem": "gam"},          # gamiṣyati (Seṭ despite anudātta)
    "kṛ":  {"stem": "kar", "anit": False},  # kariṣyati: guna of ṛ = ar; Seṭ (overrides lexicon)
    "krī": {"stem": "kre", "anit": True},   # kreṣyati: Aniṭ (overrides lexicon)
    "kṣip": {"stem": "kṣep", "anit": True}, # kṣepsyati: Aniṭ override for veṭ root
}

# Periphrastic-future stem overrides (where stem ≠ guna + i)
periphrastic_stem_overrides = {
    "gam": "gan",    # gantā: the 'tā' ending provides the t; n comes from nasal insertion
    "div": "dīv",    # dīvitā (uses lengthened class-4 stem + i from builder)
    "nī":  "ne",     # netā (ainiṭ: ne+tā, no connecting i) — compare nētum, netavya
    "jī":  "je",     # jetā (ainiṭ: je+tā)
    "bhī":  "bhe",    # bhetā (ainiṭ)
    "pā":  "pā",     # pātā (ainiṭ: pā+tā)
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
    "budh": "bobhodh", # Grassmann throwback: bo + bodh → bobhodh
    "han":  "jaṅghan",
    "hu":   "johū",
    "bhū":  "bobhū",
    "vṛ":   "varīvṛ",
    "pā":   "pepīy",
    "kṛ":   "cekṛ",
    "kṣip": "cekṣip",
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
    # √vac (cl.2) — Samprasāraṇa: va→u, → ukta, uktvā
    "vac": {
        "ppp":    {"m": "ukta",    "f": "uktā"},
        "pp_act": {"m": "uktavat", "f": "uktavatī"},
        "abs_tva": {"m": "uktvā"},
        "abs_ya":  {"m": "-ucya"},
    },
    # √yaj (cl.1/4) — Samprasāraṇa: ya→i, aj→ij → iṣṭa
    "yaj": {
        "ppp":    {"m": "iṣṭa",    "f": "iṣṭā"},
        "pp_act": {"m": "iṣṭavat", "f": "iṣṭavatī"},
        "abs_tva": {"m": "iṣṭvā"},
        "abs_ya":  {"m": "-ijya"},
    },
    # √svap (cl.2) — Samprasāraṇa: sva→su → supta
    "svap": {
        "ppp":    {"m": "supta",    "f": "suptā"},
        "pp_act": {"m": "suptavat", "f": "suptavatī"},
        "abs_tva": {"m": "suptvā"},
        "abs_ya":  {"m": "-supya"},
    },
    # √vap (cl.1) — Samprasāraṇa: va→u → upta
    "vap": {
        "ppp":    {"m": "upta",    "f": "uptā"},
        "pp_act": {"m": "uptavat", "f": "uptavatī"},
        "abs_tva": {"m": "uptvā"},
        "abs_ya":  {"m": "-upya"},
    },
    # √vah (cl.1) — Samprasāraṇa: va→u → ūḍha (h→ḍh)
    "vah": {
        "ppp":    {"m": "ūḍha",    "f": "ūḍhā"},
        "pp_act": {"m": "ūḍhavat", "f": "ūḍhavaṭī"},
        "abs_tva": {"m": "ūḍhvā"},
        "abs_ya":  {"m": "-uhya"},
    },
    # √grah (cl.9) — Samprasāraṇa: ra→ṛ → gṛhīta (seṭ: takes i)
    "grah": {
        "ppp":    {"m": "gṛhīta",    "f": "gṛhītā"},
        "pp_act": {"m": "gṛhītavat", "f": "gṛhītavatī"},
        "abs_tva": {"m": "gṛhītvā"},
        "abs_ya":  {"m": "-gṛhya"},
    },
    # √prach (cl.6) — Samprasāraṇa → pṛṣṭa
    "prach": {
        "ppp":    {"m": "pṛṣṭa",    "f": "pṛṣṭā"},
        "pp_act": {"m": "pṛṣṭavat", "f": "pṛṣṭavatī"},
        "abs_tva": {"m": "pṛṣṭvā"},
        "abs_ya":  {"m": "-pṛcchya"},
    },
}