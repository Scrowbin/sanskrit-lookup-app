#  General case terminations if the nouns and adjectives end in K, Kh, G, Gh, C, Ch, J, Jh, Ṭ, Ṭh, Ḍ, Ḍh, Ṇ, T, Th, D, Dh, P, Ph, B, Bh, R, Ś, Ṣ and h
import pynini as pn

# 1. Matchers
mf_tags = pn.union("[Masc]", "[Fem]")
n_tags = pn.union("[Neut]")
all_genders = pn.union("[Masc]", "[Fem]", "[Neut]")
stem_tag = "[CONS_STEM]"

# 2. Dynamic Bases
# The transparent base keeps the stem completely intact and directly attaches vowel suffixes.
transparent_mf = pn.cross(stem_tag, "") + pn.cross(mf_tags, "")
transparent_n = pn.cross(stem_tag, "") + pn.cross(n_tags, "")
transparent_blind = pn.cross(stem_tag, "") + pn.cross(all_genders, "")

# The Pada base inserts a boundary marker '#' before consonant suffixes.
# This explicitly flags the junction for your downstream absolute final sandhi rules.
pada_mf = pn.cross(stem_tag, "#") + pn.cross(mf_tags, "")
pada_n = pn.cross(stem_tag, "#") + pn.cross(n_tags, "")
pada_blind = pn.cross(stem_tag, "#") + pn.cross(all_genders, "")

"""
3. MASCULINE & FEMININE TERMINATIONS
"""
# --- Pada Cases (Nom/Voc Sg) ---
# Suffix drops, leaving the bare stem to undergo word-final sandhi
nom_sg_mf = pada_mf + pn.cross("[Nom][Sg]", "")  # vāc -> vāc# (downstream -> vāk)
voc_sg_mf = pada_mf + pn.cross("[Voc][Sg]", "")

# --- Transparent Cases (Vowel Initial) ---
acc_sg_mf = transparent_mf + pn.cross("[Acc][Sg]", "am")
nom_du_mf = transparent_mf + pn.cross("[Nom][Du]", "au")
acc_du_mf = transparent_mf + pn.cross("[Acc][Du]", "au")
voc_du_mf = transparent_mf + pn.cross("[Voc][Du]", "au")
nom_pl_mf = transparent_mf + pn.cross("[Nom][Pl]", "as")
acc_pl_mf = transparent_mf + pn.cross("[Acc][Pl]", "as")
voc_pl_mf = transparent_mf + pn.cross("[Voc][Pl]", "as")


"""
4. NEUTER TERMINATIONS
"""
# --- Pada Cases (Nom/Acc/Voc Sg) ---
nom_sg_n = pada_n + pn.cross("[Nom][Sg]", "")  # jagat -> jagat#
acc_sg_n = pada_n + pn.cross("[Acc][Sg]", "")
voc_sg_n = pada_n + pn.cross("[Voc][Sg]", "")

# --- Transparent Cases (Nom/Acc/Voc Du) ---
nom_du_n = transparent_n + pn.cross("[Nom][Du]", "ī")
acc_du_n = transparent_n + pn.cross("[Acc][Du]", "ī")
voc_du_n = transparent_n + pn.cross("[Voc][Du]", "ī")

# --- Strong Cases (Nom/Acc/Voc Pl) ---
# NOTE: Neuter plurals require inserting a nasal before the final consonant
# REMEMBER TO APPLY NEUTER NASAL INSERTION RULE!!
nom_pl_n = transparent_n + pn.cross("[Nom][Pl]", "i")
acc_pl_n = transparent_n + pn.cross("[Acc][Pl]", "i")
voc_pl_n = transparent_n + pn.cross("[Voc][Pl]", "i")


"""
5. GENDER-BLIND CASES (Ins, Dat, Abl, Gen, Loc)
"""
# --- Transparent Cases (Vowel Initial) ---
ins_sg = transparent_blind + pn.cross("[Ins][Sg]", "ā")
dat_sg = transparent_blind + pn.cross("[Dat][Sg]", "e")
abl_sg = transparent_blind + pn.cross("[Abl][Sg]", "as")
gen_sg = transparent_blind + pn.cross("[Gen][Sg]", "as")
loc_sg = transparent_blind + pn.cross("[Loc][Sg]", "i")
gen_du = transparent_blind + pn.cross("[Gen][Du]", "os")
loc_du = transparent_blind + pn.cross("[Loc][Du]", "os")
gen_pl = transparent_blind + pn.cross("[Gen][Pl]", "ām")

# --- Pada Cases (Consonant Initial) ---
# These attach the ending but keep the '#' so your sandhi engine knows to fire.
ins_du = pada_blind + pn.cross("[Ins][Du]", "bhyām")  # vāc -> vāc#bhyām (-> vāgbhyām)
dat_du = pada_blind + pn.cross("[Dat][Du]", "bhyām")
abl_du = pada_blind + pn.cross("[Abl][Du]", "bhyām")

ins_pl = pada_blind + pn.cross("[Ins][Pl]", "bhis")
dat_pl = pada_blind + pn.cross("[Dat][Pl]", "bhyas")
abl_pl = pada_blind + pn.cross("[Abl][Pl]", "bhyas")

loc_pl = pada_blind + pn.cross("[Loc][Pl]", "su")  # vāc -> vāc#su (-> vākṣu via Ruki)


# 6. CONSOLIDATED CONSONANT STEM PARADIGM

# Masculine & Feminine (Standard Consonant Stems like vāc, marut, etc.)
cons_mf_paradigm = pn.union(
    nom_sg_mf,
    voc_sg_mf,
    acc_sg_mf,
    nom_du_mf,
    acc_du_mf,
    voc_du_mf,
    nom_pl_mf,
    acc_pl_mf,
    voc_pl_mf,
    ins_sg,
    dat_sg,
    abl_sg,
    gen_sg,
    loc_sg,
    ins_du,
    dat_du,
    abl_du,
    gen_du,
    loc_du,
    ins_pl,
    dat_pl,
    abl_pl,
    gen_pl,
    loc_pl,
).optimize()

# Neuter (Standard Consonant Stems like jagat)
cons_n_paradigm = pn.union(
    nom_sg_n,
    acc_sg_n,
    voc_sg_n,
    nom_du_n,
    acc_du_n,
    voc_du_n,
    nom_pl_n,
    acc_pl_n,
    voc_pl_n,
    ins_sg,
    dat_sg,
    abl_sg,
    gen_sg,
    loc_sg,
    ins_du,
    dat_du,
    abl_du,
    gen_du,
    loc_du,
    ins_pl,
    dat_pl,
    abl_pl,
    gen_pl,
    loc_pl,
).optimize()

# Final Master Transducer for all General Consonant Stems
cons_stem_paradigm = pn.union(cons_mf_paradigm, cons_n_paradigm).optimize()
