import pynini as pn

# Assumed global tags from your architecture
masc_tag = pn.cross("[Masc]", "")
fem_tag = pn.cross("[Fem]", "")
neut_tag = pn.cross("[Neut]", "")
mf_blind = pn.union(masc_tag, fem_tag)

t_stem_tag = pn.cross("[T_STEM]", "")

"""
===============================================================================
1. MASCULINE & FEMININE Ṭ-STEMS (Shared Endings)
===============================================================================
"""
# --- Singular ---
nom_sg_mf_t = pn.cross("[T_STEM]", "") + mf_blind + pn.cross("[Nom][Sg]", "")
acc_sg_mf_t = pn.cross("[T_STEM]", "") + mf_blind + pn.cross("[Acc][Sg]", "am")
ins_sg_mf_t = pn.cross("[T_STEM]", "") + mf_blind + pn.cross("[Ins][Sg]", "ā")
dat_sg_mf_t = pn.cross("[T_STEM]", "") + mf_blind + pn.cross("[Dat][Sg]", "e")
abl_sg_mf_t = pn.cross("[T_STEM]", "") + mf_blind + pn.cross("[Abl][Sg]", "as")
gen_sg_mf_t = pn.cross("[T_STEM]", "") + mf_blind + pn.cross("[Gen][Sg]", "as")
loc_sg_mf_t = pn.cross("[T_STEM]", "") + mf_blind + pn.cross("[Loc][Sg]", "i")
# voc_sg_mf_t = nom_sg_mf_t
voc_sg_mf_t = pn.cross("[T_STEM]", "") + mf_blind + pn.cross("[Voc][Sg]", "")

# --- Dual ---
nom_du_mf_t = pn.cross("[T_STEM]", "") + mf_blind + pn.cross("[Nom][Du]", "au")
acc_du_mf_t = pn.cross("[T_STEM]", "") + mf_blind + pn.cross("[Acc][Du]", "au")
# voc_du_mf_t = nom_du_mf_t
voc_du_mf_t = pn.cross("[T_STEM]", "") + mf_blind + pn.cross("[Voc][Du]", "au")

# Consonant Sandhi: ṭ + bhyām -> ḍbhyām
ins_du_mf_t = pn.cross("ṭ[T_STEM]", "ḍ") + mf_blind + pn.cross("[Ins][Du]", "bhyām")
dat_du_mf_t = pn.cross("ṭ[T_STEM]", "ḍ") + mf_blind + pn.cross("[Dat][Du]", "bhyām")
abl_du_mf_t = pn.cross("ṭ[T_STEM]", "ḍ") + mf_blind + pn.cross("[Abl][Du]", "bhyām")

gen_du_mf_t = pn.cross("ṭ[T_STEM]", "ṭyos") + mf_blind + pn.cross("[Gen][Du]", "")
loc_du_mf_t = pn.cross("ṭ[T_STEM]", "ṭyos") + mf_blind + pn.cross("[Loc][Du]", "")

# --- Plural ---
nom_pl_mf_t = pn.cross("[T_STEM]", "") + mf_blind + pn.cross("[Nom][Pl]", "as")
acc_pl_mf_t = pn.cross("[T_STEM]", "") + mf_blind + pn.cross("[Acc][Pl]", "as")
# voc_pl_mf_t = nom_pl_mf_t
voc_pl_mf_t = pn.cross("[T_STEM]", "") + mf_blind + pn.cross("[Voc][Pl]", "as")

# Consonant Sandhi: ṭ + bhis/bhyas -> ḍbhis/ḍbhyas
ins_pl_mf_t = pn.cross("ṭ[T_STEM]", "ḍ") + mf_blind + pn.cross("[Ins][Pl]", "bhis")
dat_pl_mf_t = pn.cross("ṭ[T_STEM]", "ḍ") + mf_blind + pn.cross("[Dat][Pl]", "bhyas")
abl_pl_mf_t = pn.cross("ṭ[T_STEM]", "ḍ") + mf_blind + pn.cross("[Abl][Pl]", "bhyas")

gen_pl_mf_t = pn.cross("[T_STEM]", "") + mf_blind + pn.cross("[Gen][Pl]", "ām")

# Consonant Sandhi: ṭ + su -> ṭṣu (Retroflexion)
loc_pl_mf_t = pn.cross("[T_STEM]", "") + mf_blind + pn.cross("[Loc][Pl]", "ṣu")


"""
===============================================================================
2. NEUTER Ṭ-STEMS (Divergent Nom/Acc/Voc)
===============================================================================
"""
# --- Singular ---
nom_sg_nt_t = pn.cross("[T_STEM]", "") + neut_tag + pn.cross("[Nom][Sg]", "")
acc_sg_nt_t = pn.cross("[T_STEM]", "") + neut_tag + pn.cross("[Acc][Sg]", "")
# voc_sg_nt_t = nom_sg_nt_t
voc_sg_nt_t = pn.cross("[T_STEM]", "") + neut_tag + pn.cross("[Voc][Sg]", "")

# --- Dual ---
# e.g., virāṭ -> virāṭī
nom_du_nt_t = pn.cross("[T_STEM]", "") + neut_tag + pn.cross("[Nom][Du]", "ī")
acc_du_nt_t = pn.cross("[T_STEM]", "") + neut_tag + pn.cross("[Acc][Du]", "ī")
# voc_du_nt_t = nom_du_nt_t
voc_du_nt_t = pn.cross("[T_STEM]", "") + neut_tag + pn.cross("[Voc][Du]", "ī")

# --- Plural ---
# Consonant Sandhi + Nasal Infix: ṭ -> nṭi (e.g., virāṭ -> virāṇṭi / virānṭi)
nom_pl_nt_t = pn.cross("ṭ[T_STEM]", "nṭi") + neut_tag + pn.cross("[Nom][Pl]", "")
acc_pl_nt_t = pn.cross("ṭ[T_STEM]", "nṭi") + neut_tag + pn.cross("[Acc][Pl]", "")
# voc_pl_nt_t = nom_pl_nt_t
voc_pl_nt_t = pn.cross("ṭ[T_STEM]", "nṭi") + neut_tag + pn.cross("[Voc][Pl]", "")


# --- Shared Weak Neuter Forms (Identical to Masculine endings, distinct gender tag) ---
ins_sg_nt_t = pn.cross("[T_STEM]", "") + neut_tag + pn.cross("[Ins][Sg]", "ā")
dat_sg_nt_t = pn.cross("[T_STEM]", "") + neut_tag + pn.cross("[Dat][Sg]", "e")
abl_sg_nt_t = pn.cross("[T_STEM]", "") + neut_tag + pn.cross("[Abl][Sg]", "as")
gen_sg_nt_t = pn.cross("[T_STEM]", "") + neut_tag + pn.cross("[Gen][Sg]", "as")
loc_sg_nt_t = pn.cross("[T_STEM]", "") + neut_tag + pn.cross("[Loc][Sg]", "i")

ins_du_nt_t = pn.cross("ṭ[T_STEM]", "ḍ") + neut_tag + pn.cross("[Ins][Du]", "bhyām")
dat_du_nt_t = pn.cross("ṭ[T_STEM]", "ḍ") + neut_tag + pn.cross("[Dat][Du]", "bhyām")
abl_du_nt_t = pn.cross("ṭ[T_STEM]", "ḍ") + neut_tag + pn.cross("[Abl][Du]", "bhyām")
gen_du_nt_t = pn.cross("ṭ[T_STEM]", "ṭyos") + neut_tag + pn.cross("[Gen][Du]", "")
loc_du_nt_t = pn.cross("ṭ[T_STEM]", "ṭyos") + neut_tag + pn.cross("[Loc][Du]", "")

ins_pl_nt_t = pn.cross("ṭ[T_STEM]", "ḍ") + neut_tag + pn.cross("[Ins][Pl]", "bhis")
dat_pl_nt_t = pn.cross("ṭ[T_STEM]", "ḍ") + neut_tag + pn.cross("[Dat][Pl]", "bhyas")
abl_pl_nt_t = pn.cross("ṭ[T_STEM]", "ḍ") + neut_tag + pn.cross("[Abl][Pl]", "bhyas")
gen_pl_nt_t = pn.cross("[T_STEM]", "") + neut_tag + pn.cross("[Gen][Pl]", "ām")
loc_pl_nt_t = pn.cross("[T_STEM]", "") + neut_tag + pn.cross("[Loc][Pl]", "ṣu")


"""
===============================================================================
3. PARADIGM COMPILERS & OPTIMIZATION
===============================================================================
"""
# Consolidated MF Transducer
masc_fem_t_paradigm = pn.union(
    nom_sg_mf_t,
    acc_sg_mf_t,
    ins_sg_mf_t,
    dat_sg_mf_t,
    abl_sg_mf_t,
    gen_sg_mf_t,
    loc_sg_mf_t,
    voc_sg_mf_t,
    nom_du_mf_t,
    acc_du_mf_t,
    voc_du_mf_t,
    ins_du_mf_t,
    dat_du_mf_t,
    abl_du_mf_t,
    gen_du_mf_t,
    loc_du_mf_t,
    nom_pl_mf_t,
    acc_pl_mf_t,
    voc_pl_mf_t,
    ins_pl_mf_t,
    dat_pl_mf_t,
    abl_pl_mf_t,
    gen_pl_mf_t,
    loc_pl_mf_t,
).optimize()

# Consolidated Neuter Transducer
neut_t_paradigm = pn.union(
    nom_sg_nt_t,
    acc_sg_nt_t,
    voc_sg_nt_t,
    ins_sg_nt_t,
    dat_sg_nt_t,
    abl_sg_nt_t,
    gen_sg_nt_t,
    loc_sg_nt_t,
    nom_du_nt_t,
    acc_du_nt_t,
    voc_du_nt_t,
    ins_du_nt_t,
    dat_du_nt_t,
    abl_du_nt_t,
    gen_du_nt_t,
    loc_du_nt_t,
    nom_pl_nt_t,
    acc_pl_nt_t,
    voc_pl_nt_t,
    ins_pl_nt_t,
    dat_pl_nt_t,
    abl_pl_nt_t,
    gen_pl_nt_t,
    loc_pl_nt_t,
).optimize()

# Unified Consonant T-Stem Master Transducer
all_t_stems_paradigm = pn.union(masc_fem_t_paradigm, neut_t_paradigm).optimize()
