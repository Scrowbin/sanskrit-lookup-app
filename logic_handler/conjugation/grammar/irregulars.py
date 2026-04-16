# grammar/irregulars.py

# Class 1: Stems that replace the root entirely
class_1_irregulars = {
    "gam": "gaccha",  # gaccha + ti = gacchati
    "sthā": "tiṣṭha", # tiṣṭha + ti = tiṣṭhati
    "pā": "piba",     # piba + ti = pibati
    "sad": "sīda"     # sīda + ti = sīdati
}

# Class 2: These are often just regular but have tricky Sandhi.
# Only use this dict for things that change the ROOT vowel irregularly.
class_2_irregulars = {
    "brū": "bravī",   # bravī + ti = bravīti (Strong stem)
    "as": "as",       # We'll handle 's' (weak) vs 'as' (strong) in logic
    "han": "han"      # Becomes 'ha' in some weak forms
}

# Class 6: Nasal roots (your list was good, but these are Class 7 usually)
nasal_roots = {
    "muc": "muñca",
    "vid": "vinda",
    "lip": "limpa"
}
#set roots for future tense
set_roots = ["bhū", "div", "cur", "tud","kṛ"]