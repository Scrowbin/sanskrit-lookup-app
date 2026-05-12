import pynini as pn

# 1. Define our dynamic gender matchers
any_g = pn.union("[Masc]", "[Fem]", "[Neut]")
mf_g = pn.union("[Masc]", "[Fem]")  # For Masc/Fem shared cases

"""
1. Consonant t-stem (e.g., marut, trivṛt)
"""
# --- Gender-Specific Cases (Nom, Acc, Voc) ---
# Masc/Fem
nom_sg_t_mf = pn.cross("[T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Nom][Sg]", "")
acc_sg_t_mf = (
    pn.cross("[T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Acc][Sg]", "am")
)
voc_sg_t_mf = pn.cross("[T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Voc][Sg]", "")

nom_du_t_mf = (
    pn.cross("[T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Nom][Du]", "au")
)
acc_du_t_mf = (
    pn.cross("[T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Acc][Du]", "au")
)
voc_du_t_mf = (
    pn.cross("[T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Voc][Du]", "au")
)

nom_pl_t_mf = (
    pn.cross("[T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Nom][Pl]", "as")
)
acc_pl_t_mf = (
    pn.cross("[T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Acc][Pl]", "as")
)
voc_pl_t_mf = (
    pn.cross("[T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Voc][Pl]", "as")
)

# Neuter
nom_sg_t_n = pn.cross("[T_STEM][Neut][Nom][Sg]", "")
acc_sg_t_n = pn.cross("[T_STEM][Neut][Acc][Sg]", "")
voc_sg_t_n = pn.cross("[T_STEM][Neut][Voc][Sg]", "")

nom_du_t_n = pn.cross("[T_STEM][Neut][Nom][Du]", "ī")
acc_du_t_n = pn.cross("[T_STEM][Neut][Acc][Du]", "ī")
voc_du_t_n = pn.cross("[T_STEM][Neut][Voc][Du]", "ī")

# Neuter Plural consumes the 't' for nasal insertion
nom_pl_t_n = pn.cross("t[T_STEM][Neut][Nom][Pl]", "nti")
acc_pl_t_n = pn.cross("t[T_STEM][Neut][Acc][Pl]", "nti")
voc_pl_t_n = pn.cross("t[T_STEM][Neut][Voc][Pl]", "nti")


# --- Gender-Blind Cases (Ins, Dat, Abl, Gen, Loc) ---
# We create a base that drops the stem tag and ANY gender tag
t_base = pn.cross("[T_STEM]", "") + pn.cross(any_g, "")

ins_sg_t = t_base + pn.cross("[Ins][Sg]", "ā")
dat_sg_t = t_base + pn.cross("[Dat][Sg]", "e")
abl_sg_t = t_base + pn.cross("[Abl][Sg]", "as")
gen_sg_t = t_base + pn.cross("[Gen][Sg]", "as")
loc_sg_t = t_base + pn.cross("[Loc][Sg]", "i")

ins_du_t = t_base + pn.cross("[Ins][Du]", "bhyām")
dat_du_t = t_base + pn.cross("[Dat][Du]", "bhyām")
abl_du_t = t_base + pn.cross("[Abl][Du]", "bhyām")
gen_du_t = t_base + pn.cross("[Gen][Du]", "os")
loc_du_t = t_base + pn.cross("[Loc][Du]", "os")

ins_pl_t = t_base + pn.cross("[Ins][Pl]", "bhis")
dat_pl_t = t_base + pn.cross("[Dat][Pl]", "bhyas")
abl_pl_t = t_base + pn.cross("[Abl][Pl]", "bhyas")
gen_pl_t = t_base + pn.cross("[Gen][Pl]", "ām")
loc_pl_t = t_base + pn.cross("[Loc][Pl]", "su")


"""
2. Consonant as-stem & is-stem (e.g., manas, havis)
"""
# --- Gender-Specific Cases (Nom, Acc, Voc - Neut) ---
nom_sg_s_n = pn.cross("[S_STEM][Neut][Nom][Sg]", "")
acc_sg_s_n = pn.cross("[S_STEM][Neut][Acc][Sg]", "")
voc_sg_s_n = pn.cross("[S_STEM][Neut][Voc][Sg]", "")

nom_du_s_n = pn.cross("[S_STEM][Neut][Nom][Du]", "ī")
acc_du_s_n = pn.cross("[S_STEM][Neut][Acc][Du]", "ī")
voc_du_s_n = pn.cross("[S_STEM][Neut][Voc][Du]", "ī")

# Plurals consume the stem for nasal insertion/lengthening
nom_pl_as_n = pn.cross("as[AS_STEM][Neut][Nom][Pl]", "āṃsi")
acc_pl_as_n = pn.cross("as[AS_STEM][Neut][Acc][Pl]", "āṃsi")
voc_pl_as_n = pn.cross("as[AS_STEM][Neut][Voc][Pl]", "āṃsi")

nom_pl_is_n = pn.cross("is[IS_STEM][Neut][Nom][Pl]", "īṃsi")
acc_pl_is_n = pn.cross("is[IS_STEM][Neut][Acc][Pl]", "īṃsi")
voc_pl_is_n = pn.cross("is[IS_STEM][Neut][Voc][Pl]", "īṃsi")


# --- Gender-Blind Cases (Ins, Dat, Abl, Gen, Loc) ---
# Base for both AS and IS stems (assuming you tag them both as S_STEM)
s_base = pn.cross("[S_STEM]", "") + pn.cross(any_g, "")

ins_sg_s = s_base + pn.cross("[Ins][Sg]", "ā")
dat_sg_s = s_base + pn.cross("[Dat][Sg]", "e")
abl_sg_s = s_base + pn.cross("[Abl][Sg]", "as")
gen_sg_s = s_base + pn.cross("[Gen][Sg]", "as")
loc_sg_s = s_base + pn.cross("[Loc][Sg]", "i")

ins_du_s = s_base + pn.cross("[Ins][Du]", "bhyām")
dat_du_s = s_base + pn.cross("[Dat][Du]", "bhyām")
abl_du_s = s_base + pn.cross("[Abl][Du]", "bhyām")
gen_du_s = s_base + pn.cross("[Gen][Du]", "os")
loc_du_s = s_base + pn.cross("[Loc][Du]", "os")

ins_pl_s = s_base + pn.cross("[Ins][Pl]", "bhis")
dat_pl_s = s_base + pn.cross("[Dat][Pl]", "bhyas")
abl_pl_s = s_base + pn.cross("[Abl][Pl]", "bhyas")
gen_pl_s = s_base + pn.cross("[Gen][Pl]", "ām")
loc_pl_s = s_base + pn.cross("[Loc][Pl]", "su")


t_mf_paradigm = pn.union(
    nom_sg_t_mf,
    acc_sg_t_mf,
    voc_sg_t_mf,
    nom_du_t_mf,
    acc_du_t_mf,
    voc_du_t_mf,
    nom_pl_t_mf,
    acc_pl_t_mf,
    voc_pl_t_mf,
    ins_sg_t,
    dat_sg_t,
    abl_sg_t,
    gen_sg_t,
    loc_sg_t,
    ins_du_t,
    dat_du_t,
    abl_du_t,
    gen_du_t,
    loc_du_t,
    ins_pl_t,
    dat_pl_t,
    abl_pl_t,
    gen_pl_t,
    loc_pl_t,
)

t_n_paradigm = pn.union(
    nom_sg_t_n,
    acc_sg_t_n,
    voc_sg_t_n,
    nom_du_t_n,
    acc_du_t_n,
    voc_du_t_n,
    nom_pl_t_n,
    acc_pl_t_n,
    voc_pl_t_n,
    ins_sg_t,
    dat_sg_t,
    abl_sg_t,
    gen_sg_t,
    loc_sg_t,
    ins_du_t,
    dat_du_t,
    abl_du_t,
    gen_du_t,
    loc_du_t,
    ins_pl_t,
    dat_pl_t,
    abl_pl_t,
    gen_pl_t,
    loc_pl_t,
)

t_stem_paradigm = pn.union(t_mf_paradigm, t_n_paradigm).optimize()

# Neuter as-stems (e.g., manas)
as_n_paradigm = pn.union(
    nom_sg_s_n,
    acc_sg_s_n,
    voc_sg_s_n,
    nom_du_s_n,
    acc_du_s_n,
    voc_du_s_n,
    nom_pl_as_n,
    acc_pl_as_n,
    voc_pl_as_n,
    ins_sg_s,
    dat_sg_s,
    abl_sg_s,
    gen_sg_s,
    loc_sg_s,
    ins_du_s,
    dat_du_s,
    abl_du_s,
    gen_du_s,
    loc_du_s,
    ins_pl_s,
    dat_pl_s,
    abl_pl_s,
    gen_pl_s,
    loc_pl_s,
)

# Neuter is-stems (e.g., havis)
is_n_paradigm = pn.union(
    nom_sg_s_n,
    acc_sg_s_n,
    voc_sg_s_n,
    nom_du_s_n,
    acc_du_s_n,
    voc_du_s_n,
    nom_pl_is_n,
    acc_pl_is_n,
    voc_pl_is_n,
    ins_sg_s,
    dat_sg_s,
    abl_sg_s,
    gen_sg_s,
    loc_sg_s,
    ins_du_s,
    dat_du_s,
    abl_du_s,
    gen_du_s,
    loc_du_s,
    ins_pl_s,
    dat_pl_s,
    abl_pl_s,
    gen_pl_s,
    loc_pl_s,
)

s_stem_paradigm = pn.union(as_n_paradigm, is_n_paradigm).optimize()
