# grammar/irregulars.py

# ── Class 1: Suppletive stems ─────────────────────────────────────────────────
class_1_irregulars = {
    "gam":  "gacch",
    "sthā": "tiṣṭh",
    "pā":   "pib",
    "sad":  "sīd",
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
    "muc":  {"type": "a"}
}


# ── Future stem overrides ─────────────────────────────────────────────────────
# Roots whose future stem is NOT guna(root) + sya/iṣya.
# Maps root_str → {"stem": bare_stem, "anit": bool}
future_stem_overrides = {
    "div": {"stem": "dīv"},  # dīviṣyati — future uses class-4 lengthened stem, no guna
    "gam": {"stem": "gam"},  # gamiṣyati (Seṭ)
}

# Periphrastic-future stem overrides (where stem ≠ guna + i)
periphrastic_stem_overrides = {
    "gam": "gan",    # gantā: the 'tā' ending provides the t; n comes from nasal insertion
    "div": "dīv",    # dīvitā (uses lengthened class-4 stem + i from builder)
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
}

# ── Intensive (yaṅ) stem overrides ───────────────────────────────────────────
# Maps root_str → complete intensive stem base (prefix + root, no suffix).
# Used when generate_intensive_prefix() gives wrong prefix.
# Middle voice: stem + ya; Active voice: stem + [INTENSIVE_ACTIVE]
intensive_stem_overrides = {
    "gam":  "jaṅgam",  # nasal insertion: ga+gam → jaṅgam (not jagam)
    "dviṣ": "dedviṣ",  # prefix drops 'v': di + dviṣ → dedviṣ (not dvedveṣ)
    "budh": "bobhodh", # Grassmann throwback: bo + bodh → bobhodh
}