# grammar/irregulars.py

# ── Class 1: Suppletive stems ─────────────────────────────────────────────────
class_1_irregulars = {
    "gam":  "gaccha",
    "sthā": "tiṣṭha",
    "pā":   "piba",
    "sad":  "sīda",
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
}

# ── Causative Guna roots ──────────────────────────────────────────────────────
# Most causatives take Vṛddhi (bhū→bhāv, su→sāv).
# These roots take Guna instead (prevents unexpected au/ai diphthong stems).
guna_causative_roots = {
    "yuj",   # yojayati  (NOT yaujayati)
    "budh",  # bodhayati (NOT baudhayati)
    "duh",   # dohayati  (causative; passive uses Vṛddhi of the root)
    "muc",   # mocayati
    "gup",   # gopayati
    "tij",   # tejayati
    "kup",   # kopayati
    "cur",   # corayati  (NOT caurayati)
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
    "muc": "muñca",
    "vid": "vinda",
    "lip": "limpa",
}

# ── Perfect reduplication overrides ──────────────────────────────────────────
# Key: root IAST → reduplication prefix string
perfect_redupe_overrides = {
    "bhū": "ba",   # babhūva (NOT bubhūva)
    "krī": "ci",   # cikraya  (NOT crikraya; algorithm gives cri- which is wrong)
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
perfect_weak_guna_roots = {"hu", "su"}

# ── Perfect suppletive stems ──────────────────────────────────────────────────
# Roots with completely irregular perfect stems (not derivable by rule).
# Key: root IAST → dict with "strong" (sg active) and "weak" (all others) stems.
# The stems are bare (no boundary prefix); _build_perfect_system prepends prefix+.
perfect_stem_overrides = {
    "tan": {"strong": "tatan", "weak": "ten"},
    # tan perfect: 3sg/1sg strong = tatana (short a, Whitney §794d)
    # Weak du/pl = teniva, tenima, tenivahe, etc.
}

# ── Imperfect active overrides: √ad (class 2) ────────────────────────────────
ad_imperfect_active_overrides = {
    "[3sg]": "at",
    "[2sg]": "as",
}