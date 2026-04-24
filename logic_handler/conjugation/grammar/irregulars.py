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
    "yuj",   # yokṣyati  (yoj+sya → yok+sya → yokṣya)
    "ad",    # atsyati   (d+sya → tsya by devoicing)
    "hu",    # hoṣyati   (ho+sya → hoṣya by ruki)
    "krī",   # kreṣyāmi  (krī guna=kre; kre+sya → kreṣya by ruki)
    "tud",   # totsyati  (tud is Aniṭ)
}


# ── Causative stem irregulars ─────────────────────────────────────────────────
# Roots whose causative base is NOT built by regular Vṛddhi/Guna + aya rule.
# Key: root IAST → Value: causative BASE (without the +aya suffix).
# _build_class_10 appends "+aya" after this base.
causative_stem_irregulars = {
    "krī": "krāp",   # krāpayati (NOT krāyayati; -p- from Pāṇ. 7.3.36 ṇic)
}

# ── Class-2 irregulars ────────────────────────────────────────────────────────
class_2_irregulars = {
    "brū": "bravī",
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
perfect_weak_guna_roots = set()

# ── Perfect suppletive stems ──────────────────────────────────────────────────
# Roots with completely irregular perfect stems (not derivable by rule).
# Key: root IAST → dict with "strong" (sg active) and "weak" (all others) stems.
# The stems are bare (no boundary prefix); _build_perfect_system prepends prefix+.
perfect_stem_overrides = {
    "tan": {"strong": "tatan", "weak": "ten"},
    "bhū": {"strong": "babhūv", "weak": "babhūv"},
}

# ── Imperfect active overrides: √ad (class 2) ────────────────────────────────
ad_imperfect_active_overrides = {
    "[3sg]": "at",
    "[2sg]": "as",
}

# ── Aorist overrides for benchmark roots ─────────────────────────────────────
# Maps root_str -> dict of {"type": aorist_type, "active": stem, "middle": stem}
# Types: "root", "a", "reduplicated", "s", "is", "sa"
aorist_overrides = {
    "bhū":  {"type": "root"},
    "ad":   {"type": "a", "active": "ghasa", "middle": "ghasa"}, # Suppletive
    "hu":   {"type": "s"},
    "div":  {"type": "is"},
    "su":   {"type": "s"},
    "tud":  {"type": "a"},
    "yuj":  {"type": "root"},
    "tan":  {"type": "s"},
    "krī":  {"type": "s"},
    "cur":  {"type": "is"},
    "kṛ":   {"type": "s", "middle": "kṛ"}, # Middle is root aorist akṛta
    "budh": {"type": "s", "active": "bodhiṣ", "middle": "budh"}, # Middle is s aorist abudhat
    "duh":  {"type": "s", "middle": "duh"},
    "gam":  {"type": "root"},
    "dviṣ": {"type": "s", "active": "dvikṣ", "middle": "dvikṣ"},
    "muc":  {"type": "a"}
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
    "yuj":  ["yuyukṣa"]
}