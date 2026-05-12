import pynini as pn

masc_tag = pn.cross("[Masc]", "")
fem_tag = pn.cross("[Fem]", "")
neut_tag = pn.cross("[Neut]", "")
mf_blind = pn.cross(pn.union("[Masc]", "[Fem]"), "")
"""
Singular
"""
# --- Masculine singular i-stem (e.g., agni) ---
nom_sg_masc_i = (
    pn.cross("[I_STEM]", "") + masc_tag + pn.cross("[Nom][Sg]", "s")
)  # agni -> agnis
acc_sg_masc_i = (
    pn.cross("[I_STEM]", "") + masc_tag + pn.cross("[Acc][Sg]", "m")
)  # agni -> agnim
ins_sg_masc_i = (
    pn.cross("[I_STEM]", "") + masc_tag + pn.cross("[Ins][Sg]", "nā")
)  # agni -> agninā
dat_sg_masc_i = (
    pn.cross("i[I_STEM]", "aye") + masc_tag + pn.cross("[Dat][Sg]", "")
)  # agni -> agnaye
abl_sg_masc_i = (
    pn.cross("i[I_STEM]", "es") + masc_tag + pn.cross("[Abl][Sg]", "")
)  # agni -> agnes
gen_sg_masc_i = (
    pn.cross("i[I_STEM]", "es") + masc_tag + pn.cross("[Gen][Sg]", "")
)  # agni -> agnes
loc_sg_masc_i = (
    pn.cross("i[I_STEM]", "au") + masc_tag + pn.cross("[Loc][Sg]", "")
)  # agni -> agnau
voc_sg_masc_i = (
    pn.cross("i[I_STEM]", "e") + masc_tag + pn.cross("[Voc][Sg]", "")
)  # agni -> agne

# --- Feminine singular i-stem (e.g., gati) ---
nom_sg_fem_i = pn.cross("[I_STEM]", "") + fem_tag + pn.cross("[Nom][Sg]", "s")
acc_sg_fem_i = pn.cross("[I_STEM]", "") + fem_tag + pn.cross("[Acc][Sg]", "m")
ins_sg_fem_i = pn.cross("i[I_STEM]", "yā") + fem_tag + pn.cross("[Ins][Sg]", "")
dat_sg_fem_i = pn.cross("i[I_STEM]", "aye") + fem_tag + pn.cross("[Dat][Sg]", "")

# Union for the two valid forms (-es or -yās)
abl_sg_fem_i = (
    (pn.cross("i[I_STEM]", "es") | pn.cross("i[I_STEM]", "yās"))
    + fem_tag
    + pn.cross("[Abl][Sg]", "")
)
gen_sg_fem_i = (
    (pn.cross("i[I_STEM]", "es") | pn.cross("i[I_STEM]", "yās"))
    + fem_tag
    + pn.cross("[Gen][Sg]", "")
)

loc_sg_fem_i = pn.cross("i[I_STEM]", "au") + fem_tag + pn.cross("[Loc][Sg]", "")
voc_sg_fem_i = pn.cross("i[I_STEM]", "e") + fem_tag + pn.cross("[Voc][Sg]", "")

# --- Neuter singular i-stem (e.g., vāri) ---
nom_sg_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Nom][Sg]", "")
acc_sg_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Acc][Sg]", "")
ins_sg_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Ins][Sg]", "nā")
dat_sg_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Dat][Sg]", "ne")
abl_sg_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Abl][Sg]", "nas")
gen_sg_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Gen][Sg]", "nas")
loc_sg_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Loc][Sg]", "ni")

# Vocative can be bare stem or take 'e'
voc_sg_neut_i = (
    (pn.cross("[I_STEM]", "") | pn.cross("i[I_STEM]", "e"))
    + neut_tag
    + pn.cross("[Voc][Sg]", "")
)


"""
Dual
"""
# --- Masc/Fem dual i-stem (e.g., agni / gati) --- Uses mf_blind
nom_du_i = pn.cross("i[I_STEM]", "ī") + mf_blind + pn.cross("[Nom][Du]", "")
acc_du_i = pn.cross("i[I_STEM]", "ī") + mf_blind + pn.cross("[Acc][Du]", "")
voc_du_i = pn.cross("i[I_STEM]", "ī") + mf_blind + pn.cross("[Voc][Du]", "")

ins_du_i = pn.cross("[I_STEM]", "") + mf_blind + pn.cross("[Ins][Du]", "bhyām")
dat_du_i = pn.cross("[I_STEM]", "") + mf_blind + pn.cross("[Dat][Du]", "bhyām")
abl_du_i = pn.cross("[I_STEM]", "") + mf_blind + pn.cross("[Abl][Du]", "bhyām")

gen_du_i = pn.cross("i[I_STEM]", "yos") + mf_blind + pn.cross("[Gen][Du]", "")
loc_du_i = pn.cross("i[I_STEM]", "yos") + mf_blind + pn.cross("[Loc][Du]", "")

# --- Neuter dual i-stem (e.g., vāri) ---
nom_du_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Nom][Du]", "nī")
acc_du_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Acc][Du]", "nī")
voc_du_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Voc][Du]", "nī")

ins_du_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Ins][Du]", "bhyām")
dat_du_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Dat][Du]", "bhyām")
abl_du_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Abl][Du]", "bhyām")

gen_du_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Gen][Du]", "nos")
loc_du_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Loc][Du]", "nos")


"""
Plural
"""
# --- Masc/Fem plural i-stem (e.g., agni / gati) ---
nom_pl_i = pn.cross("i[I_STEM]", "ayas") + mf_blind + pn.cross("[Nom][Pl]", "")
voc_pl_i = pn.cross("i[I_STEM]", "ayas") + mf_blind + pn.cross("[Voc][Pl]", "")

acc_pl_masc_i = pn.cross("i[I_STEM]", "īn") + masc_tag + pn.cross("[Acc][Pl]", "")
acc_pl_fem_i = pn.cross("i[I_STEM]", "īs") + fem_tag + pn.cross("[Acc][Pl]", "")

ins_pl_i = pn.cross("[I_STEM]", "") + mf_blind + pn.cross("[Ins][Pl]", "bhis")
dat_pl_i = pn.cross("[I_STEM]", "") + mf_blind + pn.cross("[Dat][Pl]", "bhyas")
abl_pl_i = pn.cross("[I_STEM]", "") + mf_blind + pn.cross("[Abl][Pl]", "bhyas")

gen_pl_i = pn.cross("i[I_STEM]", "īnām") + mf_blind + pn.cross("[Gen][Pl]", "")
loc_pl_i = pn.cross("[I_STEM]", "") + mf_blind + pn.cross("[Loc][Pl]", "su")

# --- Neuter plural i-stem (e.g., vāri) ---
nom_pl_neut_i = pn.cross("i[I_STEM]", "īni") + neut_tag + pn.cross("[Nom][Pl]", "")
acc_pl_neut_i = pn.cross("i[I_STEM]", "īni") + neut_tag + pn.cross("[Acc][Pl]", "")
voc_pl_neut_i = pn.cross("i[I_STEM]", "īni") + neut_tag + pn.cross("[Voc][Pl]", "")

ins_pl_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Ins][Pl]", "bhis")
dat_pl_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Dat][Pl]", "bhyas")
abl_pl_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Abl][Pl]", "bhyas")

gen_pl_neut_i = pn.cross("i[I_STEM]", "īnām") + neut_tag + pn.cross("[Gen][Pl]", "")
loc_pl_neut_i = pn.cross("[I_STEM]", "") + neut_tag + pn.cross("[Loc][Pl]", "su")
nom_sg_f_ii = pn.cross("ī[I_bar_STEM]", "ī") + fem_tag + pn.cross("[Nom][Sg]", "")
acc_sg_f_ii = pn.cross("ī[I_bar_STEM]", "īm") + fem_tag + pn.cross("[Acc][Sg]", "")
ins_sg_f_ii = pn.cross("ī[I_bar_STEM]", "yā") + fem_tag + pn.cross("[Ins][Sg]", "")
dat_sg_f_ii = pn.cross("ī[I_bar_STEM]", "yai") + fem_tag + pn.cross("[Dat][Sg]", "")
abl_sg_f_ii = pn.cross("ī[I_bar_STEM]", "yās") + fem_tag + pn.cross("[Abl][Sg]", "")
gen_sg_f_ii = pn.cross("ī[I_bar_STEM]", "yās") + fem_tag + pn.cross("[Gen][Sg]", "")
loc_sg_f_ii = pn.cross("ī[I_bar_STEM]", "yām") + fem_tag + pn.cross("[Loc][Sg]", "")
voc_sg_f_ii = pn.cross("ī[I_bar_STEM]", "i") + fem_tag + pn.cross("[Voc][Sg]", "")

# --- Dual ---
nom_du_f_ii = pn.cross("ī[I_bar_STEM]", "yau") + fem_tag + pn.cross("[Nom][Du]", "")
acc_du_f_ii = pn.cross("ī[I_bar_STEM]", "yau") + fem_tag + pn.cross("[Acc][Du]", "")
voc_du_f_ii = pn.cross("ī[I_bar_STEM]", "yau") + fem_tag + pn.cross("[Voc][Du]", "")

ins_du_f_ii = pn.cross("[I_bar_STEM]", "") + fem_tag + pn.cross("[Ins][Du]", "bhyām")
dat_du_f_ii = pn.cross("[I_bar_STEM]", "") + fem_tag + pn.cross("[Dat][Du]", "bhyām")
abl_du_f_ii = pn.cross("[I_bar_STEM]", "") + fem_tag + pn.cross("[Abl][Du]", "bhyām")

gen_du_f_ii = pn.cross("ī[I_bar_STEM]", "yos") + fem_tag + pn.cross("[Gen][Du]", "")
loc_du_f_ii = pn.cross("ī[I_bar_STEM]", "yos") + fem_tag + pn.cross("[Loc][Du]", "")

# --- Plural ---
nom_pl_f_ii = pn.cross("ī[I_bar_STEM]", "yas") + fem_tag + pn.cross("[Nom][Pl]", "")
acc_pl_f_ii = pn.cross("ī[I_bar_STEM]", "īs") + fem_tag + pn.cross("[Acc][Pl]", "")
voc_pl_f_ii = pn.cross("ī[I_bar_STEM]", "yas") + fem_tag + pn.cross("[Voc][Pl]", "")

ins_pl_f_ii = pn.cross("[I_bar_STEM]", "") + fem_tag + pn.cross("[Ins][Pl]", "bhis")
dat_pl_f_ii = pn.cross("[I_bar_STEM]", "") + fem_tag + pn.cross("[Dat][Pl]", "bhyas")
abl_pl_f_ii = pn.cross("[I_bar_STEM]", "") + fem_tag + pn.cross("[Abl][Pl]", "bhyas")

gen_pl_f_ii = pn.cross("ī[I_bar_STEM]", "īnām") + fem_tag + pn.cross("[Gen][Pl]", "")
loc_pl_f_ii = pn.cross("[I_bar_STEM]", "") + fem_tag + pn.cross("[Loc][Pl]", "su")
"""

Feminine Ī-STEM (e.g., devī)
"""
# --- Singular ---
nom_sg_f_ii = pn.cross("ī[I_bar_STEM]", "ī") + fem_tag + pn.cross("[Nom][Sg]", "")
acc_sg_f_ii = pn.cross("ī[I_bar_STEM]", "īm") + fem_tag + pn.cross("[Acc][Sg]", "")
ins_sg_f_ii = pn.cross("ī[I_bar_STEM]", "yā") + fem_tag + pn.cross("[Ins][Sg]", "")
dat_sg_f_ii = pn.cross("ī[I_bar_STEM]", "yai") + fem_tag + pn.cross("[Dat][Sg]", "")
abl_sg_f_ii = pn.cross("ī[I_bar_STEM]", "yās") + fem_tag + pn.cross("[Abl][Sg]", "")
gen_sg_f_ii = pn.cross("ī[I_bar_STEM]", "yās") + fem_tag + pn.cross("[Gen][Sg]", "")
loc_sg_f_ii = pn.cross("ī[I_bar_STEM]", "yām") + fem_tag + pn.cross("[Loc][Sg]", "")
voc_sg_f_ii = pn.cross("ī[I_bar_STEM]", "i") + fem_tag + pn.cross("[Voc][Sg]", "")

# --- Dual ---
nom_du_f_ii = pn.cross("ī[I_bar_STEM]", "yau") + fem_tag + pn.cross("[Nom][Du]", "")
acc_du_f_ii = pn.cross("ī[I_bar_STEM]", "yau") + fem_tag + pn.cross("[Acc][Du]", "")
voc_du_f_ii = pn.cross("ī[I_bar_STEM]", "yau") + fem_tag + pn.cross("[Voc][Du]", "")

ins_du_f_ii = pn.cross("[I_bar_STEM]", "") + fem_tag + pn.cross("[Ins][Du]", "bhyām")
dat_du_f_ii = pn.cross("[I_bar_STEM]", "") + fem_tag + pn.cross("[Dat][Du]", "bhyām")
abl_du_f_ii = pn.cross("[I_bar_STEM]", "") + fem_tag + pn.cross("[Abl][Du]", "bhyām")

gen_du_f_ii = pn.cross("ī[I_bar_STEM]", "yos") + fem_tag + pn.cross("[Gen][Du]", "")
loc_du_f_ii = pn.cross("ī[I_bar_STEM]", "yos") + fem_tag + pn.cross("[Loc][Du]", "")

# --- Plural ---
nom_pl_f_ii = pn.cross("ī[I_bar_STEM]", "yas") + fem_tag + pn.cross("[Nom][Pl]", "")
acc_pl_f_ii = pn.cross("ī[I_bar_STEM]", "īs") + fem_tag + pn.cross("[Acc][Pl]", "")
voc_pl_f_ii = pn.cross("ī[I_bar_STEM]", "yas") + fem_tag + pn.cross("[Voc][Pl]", "")

ins_pl_f_ii = pn.cross("[I_bar_STEM]", "") + fem_tag + pn.cross("[Ins][Pl]", "bhis")
dat_pl_f_ii = pn.cross("[I_bar_STEM]", "") + fem_tag + pn.cross("[Dat][Pl]", "bhyas")
abl_pl_f_ii = pn.cross("[I_bar_STEM]", "") + fem_tag + pn.cross("[Abl][Pl]", "bhyas")

gen_pl_f_ii = pn.cross("ī[I_bar_STEM]", "īnām") + fem_tag + pn.cross("[Gen][Pl]", "")
loc_pl_f_ii = (
    pn.cross("[I_bar_STEM]", "") + fem_tag + pn.cross("[Loc][Pl]", "su")
)  # Union Compiler

masc_i_paradigm = pn.union(
    nom_sg_masc_i,
    acc_sg_masc_i,
    ins_sg_masc_i,
    dat_sg_masc_i,
    abl_sg_masc_i,
    gen_sg_masc_i,
    loc_sg_masc_i,
    voc_sg_masc_i,
    nom_du_i,
    acc_du_i,
    voc_du_i,
    ins_du_i,
    dat_du_i,
    abl_du_i,
    gen_du_i,
    loc_du_i,  # Shared M/F
    nom_pl_i,
    acc_pl_masc_i,
    voc_pl_i,
    ins_pl_i,
    dat_pl_i,
    abl_pl_i,
    gen_pl_i,
    loc_pl_i,  # Shared M/F except Acc
).optimize()

# 2. Feminine Short i-stem (e.g., gati)
fem_i_paradigm = pn.union(
    nom_sg_fem_i,
    acc_sg_fem_i,
    ins_sg_fem_i,
    dat_sg_fem_i,
    abl_sg_fem_i,
    gen_sg_fem_i,
    loc_sg_fem_i,
    voc_sg_fem_i,
    nom_du_i,
    acc_du_i,
    voc_du_i,
    ins_du_i,
    dat_du_i,
    abl_du_i,
    gen_du_i,
    loc_du_i,  # Shared M/F
    nom_pl_i,
    acc_pl_fem_i,
    voc_pl_i,
    ins_pl_i,
    dat_pl_i,
    abl_pl_i,
    gen_pl_i,
    loc_pl_i,  # Shared M/F except Acc
).optimize()

# 3. Neuter Short i-stem (e.g., vāri)
neut_i_paradigm = pn.union(
    nom_sg_neut_i,
    acc_sg_neut_i,
    ins_sg_neut_i,
    dat_sg_neut_i,
    abl_sg_neut_i,
    gen_sg_neut_i,
    loc_sg_neut_i,
    voc_sg_neut_i,
    nom_du_neut_i,
    acc_du_neut_i,
    voc_du_neut_i,
    ins_du_neut_i,
    dat_du_neut_i,
    abl_du_neut_i,
    gen_du_neut_i,
    loc_du_neut_i,
    nom_pl_neut_i,
    acc_pl_neut_i,
    voc_pl_neut_i,
    ins_pl_neut_i,
    dat_pl_neut_i,
    abl_pl_neut_i,
    gen_pl_neut_i,
    loc_pl_neut_i,
).optimize()

# 4. Feminine Long ī-stem (e.g., devī)
fem_ii_paradigm = pn.union(
    nom_sg_f_ii,
    acc_sg_f_ii,
    ins_sg_f_ii,
    dat_sg_f_ii,
    abl_sg_f_ii,
    gen_sg_f_ii,
    loc_sg_f_ii,
    voc_sg_f_ii,
    nom_du_f_ii,
    acc_du_f_ii,
    voc_du_f_ii,
    ins_du_f_ii,
    dat_du_f_ii,
    abl_du_f_ii,
    gen_du_f_ii,
    loc_du_f_ii,
    nom_pl_f_ii,
    acc_pl_f_ii,
    voc_pl_f_ii,
    ins_pl_f_ii,
    dat_pl_f_ii,
    abl_pl_f_ii,
    gen_pl_f_ii,
    loc_pl_f_ii,
).optimize()

# 5. Master I-Stem Transducer
all_i_stems_paradigm = pn.union(
    masc_i_paradigm, fem_i_paradigm, neut_i_paradigm, fem_ii_paradigm
).optimize()
