import pynini as pn

"""
Singular
"""
# Masculine (e.g., śátru)
nom_sg_m_u = pn.cross("[U_STEM][Masc][Nom][Sg]", "s")  # śátru + s -> śátrus
acc_sg_m_u = pn.cross("[U_STEM][Masc][Acc][Sg]", "m")  # śátru + m -> śátrum
ins_sg_m_u = pn.cross("[U_STEM][Masc][Ins][Sg]", "nā")  # śátru + nā -> śátrunā
dat_sg_m_u = pn.cross(
    "u[U_STEM][Masc][Dat][Sg]", "ave"
)  # śátru + e -> śátrave (u -> ave)
abl_sg_m_u = pn.cross(
    "u[U_STEM][Masc][Abl][Sg]", "os"
)  # śátru + as -> śátros (u -> os)
gen_sg_m_u = pn.cross("u[U_STEM][Masc][Gen][Sg]", "os")  # śátru + as -> śátros
loc_sg_m_u = pn.cross("u[U_STEM][Masc][Loc][Sg]", "au")  # śátru + i -> śátrau (u -> au)
voc_sg_m_u = pn.cross("u[U_STEM][Masc][Voc][Sg]", "o")  # śátru + Ø -> śátro (u -> o)

# Feminine (e.g., dhenú)
nom_sg_f_u = pn.cross("[U_STEM][Fem][Nom][Sg]", "s")  # dhenú + s -> dhenús
acc_sg_f_u = pn.cross("[U_STEM][Fem][Acc][Sg]", "m")  # dhenú + m -> dhenúm
ins_sg_f_u = pn.cross("u[U_STEM][Fem][Ins][Sg]", "vā")  # dhenú + ā -> dhenvā (u -> vā)
dat_sg_f_u = pn.cross("u[U_STEM][Fem][Dat][Sg]", "ave")  # dhenú + e -> dhenáve

# Feminine has two valid forms for Abl/Gen (-os or -vās)
abl_sg_f_u = pn.union(
    pn.cross("u[U_STEM][Fem][Abl][Sg]", "os"),
    pn.cross("u[U_STEM][Fem][Abl][Sg]", "vās"),
)
gen_sg_f_u = pn.union(
    pn.cross("u[U_STEM][Fem][Gen][Sg]", "os"),
    pn.cross("u[U_STEM][Fem][Gen][Sg]", "vās"),
)

loc_sg_f_u = pn.cross("u[U_STEM][Fem][Loc][Sg]", "au")  # dhenú + i -> dhenaú
voc_sg_f_u = pn.cross("u[U_STEM][Fem][Voc][Sg]", "o")  # dhenú + Ø -> dhenó

# Neuter (e.g., madhu)
neut_tag = pn.cross("[Neut]", "")
nom_sg_n_u = pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Nom][Sg]", "")
acc_sg_n_u = pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Acc][Sg]", "")
ins_sg_n_u = pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Ins][Sg]", "nā")
dat_sg_n_u = pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Dat][Sg]", "ne")
abl_sg_n_u = pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Abl][Sg]", "nas")
gen_sg_n_u = pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Gen][Sg]", "nas")
loc_sg_n_u = pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Loc][Sg]", "ni")
voc_sg_n_u = (
    (pn.cross("[U_STEM]", "") | pn.cross("u[U_STEM]", "o"))
    + neut_tag
    + pn.cross("[Voc][Sg]", "")
)
"""
Dual
"""
# Masculine
nom_du_m_u = pn.cross(
    "u[U_STEM][Masc][Nom][Du]", "ū"
)  # śátru + au -> śátrū (lengthens)
acc_du_m_u = pn.cross("u[U_STEM][Masc][Acc][Du]", "ū")  # śátru + au -> śátrū
# Whitney §341b: u optionally lengthens to ū before bh-suffixes
ins_du_m_u = pn.union(
    pn.cross("[U_STEM][Masc][Ins][Du]", "bhyām"),   # śátrubhyām (short)
    pn.cross("u[U_STEM][Masc][Ins][Du]", "ūbhyām"),  # śátrūbhyām (long)
)
dat_du_m_u = pn.union(
    pn.cross("[U_STEM][Masc][Dat][Du]", "bhyām"),
    pn.cross("u[U_STEM][Masc][Dat][Du]", "ūbhyām"),
)
abl_du_m_u = pn.union(
    pn.cross("[U_STEM][Masc][Abl][Du]", "bhyām"),
    pn.cross("u[U_STEM][Masc][Abl][Du]", "ūbhyām"),
)
gen_du_m_u = pn.cross(
    "u[U_STEM][Masc][Gen][Du]", "vos"
)  # śátru + os -> śátrvos (u -> vos)
loc_du_m_u = pn.cross("u[U_STEM][Masc][Loc][Du]", "vos")  # śátru + os -> śátrvos
voc_du_m_u = pn.cross("u[U_STEM][Masc][Voc][Du]", "ū")  # śátru + au -> śátrū

# Feminine
nom_du_f_u = pn.cross("u[U_STEM][Fem][Nom][Du]", "ū")
acc_du_f_u = pn.cross("u[U_STEM][Fem][Acc][Du]", "ū")
ins_du_f_u = pn.union(
    pn.cross("[U_STEM][Fem][Ins][Du]", "bhyām"),
    pn.cross("u[U_STEM][Fem][Ins][Du]", "ūbhyām"),
)
dat_du_f_u = pn.union(
    pn.cross("[U_STEM][Fem][Dat][Du]", "bhyām"),
    pn.cross("u[U_STEM][Fem][Dat][Du]", "ūbhyām"),
)
abl_du_f_u = pn.union(
    pn.cross("[U_STEM][Fem][Abl][Du]", "bhyām"),
    pn.cross("u[U_STEM][Fem][Abl][Du]", "ūbhyām"),
)
gen_du_f_u = pn.cross("u[U_STEM][Fem][Gen][Du]", "vos")
loc_du_f_u = pn.cross("u[U_STEM][Fem][Loc][Du]", "vos")
voc_du_f_u = pn.cross("u[U_STEM][Fem][Voc][Du]", "ū")

# Neuter
nom_du_n_u = pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Nom][Du]", "nī")
acc_du_n_u = pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Acc][Du]", "nī")
voc_du_n_u = pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Voc][Du]", "nī")
ins_du_n_u = pn.union(
    pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Ins][Du]", "bhyām"),
    pn.cross("u[U_STEM]", "ū") + neut_tag + pn.cross("[Ins][Du]", "bhyām"),
)
dat_du_n_u = pn.union(
    pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Dat][Du]", "bhyām"),
    pn.cross("u[U_STEM]", "ū") + neut_tag + pn.cross("[Dat][Du]", "bhyām"),
)
abl_du_n_u = pn.union(
    pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Abl][Du]", "bhyām"),
    pn.cross("u[U_STEM]", "ū") + neut_tag + pn.cross("[Abl][Du]", "bhyām"),
)
gen_du_n_u = pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Gen][Du]", "nos")
loc_du_n_u = pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Loc][Du]", "nos")
"""
Plural
"""
# Masculine
nom_pl_m_u = pn.cross(
    "u[U_STEM][Masc][Nom][Pl]", "avas"
)  # śátru + as -> śátravas (u -> avas)
acc_pl_m_u = pn.cross(
    "u[U_STEM][Masc][Acc][Pl]", "ūn"
)  # śátru + as -> śátrūn (u -> ūn)
# Whitney §341b: u optionally lengthens to ū before bh-suffixes
ins_pl_m_u = pn.union(
    pn.cross("[U_STEM][Masc][Ins][Pl]", "bhis"),    # śátrubhis (short)
    pn.cross("u[U_STEM][Masc][Ins][Pl]", "ūbhis"),   # śátrūbhis (long)
)
dat_pl_m_u = pn.union(
    pn.cross("[U_STEM][Masc][Dat][Pl]", "bhyas"),
    pn.cross("u[U_STEM][Masc][Dat][Pl]", "ūbhyas"),
)
abl_pl_m_u = pn.union(
    pn.cross("[U_STEM][Masc][Abl][Pl]", "bhyas"),
    pn.cross("u[U_STEM][Masc][Abl][Pl]", "ūbhyas"),
)
gen_pl_m_u = pn.cross(
    "u[U_STEM][Masc][Gen][Pl]", "ūnām"
)  # śátru + ām -> śátrūṇām (u -> ūnām)
loc_pl_m_u = pn.cross("[U_STEM][Masc][Loc][Pl]", "su")  # śátru + su -> śátruṣu
voc_pl_m_u = pn.cross("u[U_STEM][Masc][Voc][Pl]", "avas")  # śátru + as -> śátravas

# Feminine
nom_pl_f_u = pn.cross("u[U_STEM][Fem][Nom][Pl]", "avas")  # dhenú + as -> dhenávas
acc_pl_f_u = pn.cross("u[U_STEM][Fem][Acc][Pl]", "ūs")  # dhenú + as -> dhenús (u -> ūs)
voc_pl_f_u = pn.cross("u[U_STEM][Fem][Voc][Pl]", "avas")
ins_pl_f_u = pn.union(
    pn.cross("[U_STEM][Fem][Ins][Pl]", "bhis"),
    pn.cross("u[U_STEM][Fem][Ins][Pl]", "ūbhis"),
)
dat_pl_f_u = pn.union(
    pn.cross("[U_STEM][Fem][Dat][Pl]", "bhyas"),
    pn.cross("u[U_STEM][Fem][Dat][Pl]", "ūbhyas"),
)
abl_pl_f_u = pn.union(
    pn.cross("[U_STEM][Fem][Abl][Pl]", "bhyas"),
    pn.cross("u[U_STEM][Fem][Abl][Pl]", "ūbhyas"),
)
gen_pl_f_u = pn.cross("u[U_STEM][Fem][Gen][Pl]", "ūnām")
loc_pl_f_u = pn.cross("[U_STEM][Fem][Loc][Pl]", "su")

# Neuter
nom_pl_n_u = pn.cross("u[U_STEM]", "ūni") + neut_tag + pn.cross("[Nom][Pl]", "")
acc_pl_n_u = pn.cross("u[U_STEM]", "ūni") + neut_tag + pn.cross("[Acc][Pl]", "")
voc_pl_n_u = pn.cross("u[U_STEM]", "ūni") + neut_tag + pn.cross("[Voc][Pl]", "")
ins_pl_n_u = pn.union(
    pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Ins][Pl]", "bhis"),
    pn.cross("u[U_STEM]", "ū") + neut_tag + pn.cross("[Ins][Pl]", "bhis"),
)
dat_pl_n_u = pn.union(
    pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Dat][Pl]", "bhyas"),
    pn.cross("u[U_STEM]", "ū") + neut_tag + pn.cross("[Dat][Pl]", "bhyas"),
)
abl_pl_n_u = pn.union(
    pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Abl][Pl]", "bhyas"),
    pn.cross("u[U_STEM]", "ū") + neut_tag + pn.cross("[Abl][Pl]", "bhyas"),
)
gen_pl_n_u = pn.cross("u[U_STEM]", "ūnām") + neut_tag + pn.cross("[Gen][Pl]", "")
loc_pl_n_u = pn.cross("[U_STEM]", "") + neut_tag + pn.cross("[Loc][Pl]", "su")

"""
Feminine Ū-STEM (e.g., vadhū)
"""
# Singular
nom_sg_f_uu = pn.cross(
    "ū[Ū_STEM][Fem][Nom][Sg]", "ūs"
)  # vadhū -> vadhūs (Keeps the 's'!)
acc_sg_f_uu = pn.cross("ū[Ū_STEM][Fem][Acc][Sg]", "ūm")  # vadhū -> vadhūm
ins_sg_f_uu = pn.cross("ū[Ū_STEM][Fem][Ins][Sg]", "vā")  # vadhū -> vadhvā (ū -> vā)
dat_sg_f_uu = pn.cross("ū[Ū_STEM][Fem][Dat][Sg]", "vai")  # vadhū -> vadhvai
abl_sg_f_uu = pn.cross("ū[Ū_STEM][Fem][Abl][Sg]", "vās")  # vadhū -> vadhvās
gen_sg_f_uu = pn.cross("ū[Ū_STEM][Fem][Gen][Sg]", "vās")  # vadhū -> vadhvās
loc_sg_f_uu = pn.cross("ū[Ū_STEM][Fem][Loc][Sg]", "vām")  # vadhū -> vadhvām
voc_sg_f_uu = pn.cross(
    "ū[Ū_STEM][Fem][Voc][Sg]", "u"
)  # vadhū -> vadhu (Shortens to u!)

# Dual
nom_du_f_uu = pn.cross("ū[Ū_STEM][Fem][Nom][Du]", "vau")  # vadhū -> vadhvau
acc_du_f_uu = pn.cross("ū[Ū_STEM][Fem][Acc][Du]", "vau")
voc_du_f_uu = pn.cross("ū[Ū_STEM][Fem][Voc][Du]", "vau")

ins_du_f_uu = pn.cross("[Ū_STEM][Fem][Ins][Du]", "bhyām")  # vadhū + bhyām
dat_du_f_uu = pn.cross("[Ū_STEM][Fem][Dat][Du]", "bhyām")
abl_du_f_uu = pn.cross("[Ū_STEM][Fem][Abl][Du]", "bhyām")

gen_du_f_uu = pn.cross("ū[Ū_STEM][Fem][Gen][Du]", "vos")  # vadhū -> vadhvos
loc_du_f_uu = pn.cross("ū[Ū_STEM][Fem][Loc][Du]", "vos")

# Plural
nom_pl_f_uu = pn.cross("ū[Ū_STEM][Fem][Nom][Pl]", "vas")  # vadhū -> vadhvas
acc_pl_f_uu = pn.cross("ū[Ū_STEM][Fem][Acc][Pl]", "ūs")  # vadhū -> vadhūs
voc_pl_f_uu = pn.cross("ū[Ū_STEM][Fem][Voc][Pl]", "vas")

ins_pl_f_uu = pn.cross("[Ū_STEM][Fem][Ins][Pl]", "bhis")  # vadhū + bhis
dat_pl_f_uu = pn.cross("[Ū_STEM][Fem][Dat][Pl]", "bhyas")
abl_pl_f_uu = pn.cross("[Ū_STEM][Fem][Abl][Pl]", "bhyas")

gen_pl_f_uu = pn.cross("ū[Ū_STEM][Fem][Gen][Pl]", "ūnām")  # vadhū -> vadhūnām
loc_pl_f_uu = pn.cross("[Ū_STEM][Fem][Loc][Pl]", "su")  # vadhū + su (Strict underlying)

# Union Compiler
masc_u_paradigm = pn.union(
    nom_sg_m_u,
    acc_sg_m_u,
    ins_sg_m_u,
    dat_sg_m_u,
    abl_sg_m_u,
    gen_sg_m_u,
    loc_sg_m_u,
    voc_sg_m_u,
    nom_du_m_u,
    acc_du_m_u,
    ins_du_m_u,
    dat_du_m_u,
    abl_du_m_u,
    gen_du_m_u,
    loc_du_m_u,
    voc_du_m_u,
    nom_pl_m_u,
    acc_pl_m_u,
    ins_pl_m_u,
    dat_pl_m_u,
    abl_pl_m_u,
    gen_pl_m_u,
    loc_pl_m_u,
    voc_pl_m_u,
).optimize()

# 2. Feminine Short u-stem (e.g., dhenú)
fem_u_paradigm = pn.union(
    nom_sg_f_u,
    acc_sg_f_u,
    ins_sg_f_u,
    dat_sg_f_u,
    abl_sg_f_u,
    gen_sg_f_u,
    loc_sg_f_u,
    voc_sg_f_u,
    nom_du_f_u,
    acc_du_f_u,
    ins_du_f_u,
    dat_du_f_u,
    abl_du_f_u,
    gen_du_f_u,
    loc_du_f_u,
    voc_du_f_u,
    nom_pl_f_u,
    acc_pl_f_u,
    voc_pl_f_u,
    ins_pl_f_u,
    dat_pl_f_u,
    abl_pl_f_u,
    gen_pl_f_u,
    loc_pl_f_u,
).optimize()

# 3. Neuter Short u-stem (e.g., madhu)
neut_u_paradigm = pn.union(
    nom_sg_n_u,
    acc_sg_n_u,
    ins_sg_n_u,
    dat_sg_n_u,
    abl_sg_n_u,
    gen_sg_n_u,
    loc_sg_n_u,
    voc_sg_n_u,
    nom_du_n_u,
    acc_du_n_u,
    voc_du_n_u,
    ins_du_n_u,
    dat_du_n_u,
    abl_du_n_u,
    gen_du_n_u,
    loc_du_n_u,
    nom_pl_n_u,
    acc_pl_n_u,
    voc_pl_n_u,
    ins_pl_n_u,
    dat_pl_n_u,
    abl_pl_n_u,
    gen_pl_n_u,
    loc_pl_n_u,
).optimize()

# 4. Feminine Long ū-stem (e.g., vadhū)
fem_uu_paradigm = pn.union(
    nom_sg_f_uu,
    acc_sg_f_uu,
    ins_sg_f_uu,
    dat_sg_f_uu,
    abl_sg_f_uu,
    gen_sg_f_uu,
    loc_sg_f_uu,
    voc_sg_f_uu,
    nom_du_f_uu,
    acc_du_f_uu,
    voc_du_f_uu,
    ins_du_f_uu,
    dat_du_f_uu,
    abl_du_f_uu,
    gen_du_f_uu,
    loc_du_f_uu,
    nom_pl_f_uu,
    acc_pl_f_uu,
    voc_pl_f_uu,
    ins_pl_f_uu,
    dat_pl_f_uu,
    abl_pl_f_uu,
    gen_pl_f_uu,
    loc_pl_f_uu,
).optimize()

# 5. Master U/Ū-Stem Transducer
all_u_stems_paradigm = pn.union(
    masc_u_paradigm, fem_u_paradigm, neut_u_paradigm, fem_uu_paradigm
).optimize()
