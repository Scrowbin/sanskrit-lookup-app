import pynini as pn

mf_blind = pn.cross(pn.union("[Masc]", "[Fem]"), "")

"""
ś-stem (e.g., etādṛś, diś, dṛś)
Note: For these stems, 'ś' changes to 'k' in Nom/Voc Sg and before consonant endings.
'#' junction markers let _junction_sandhi in engine.py voice k→g before bh endings,
and RUKI converts k#su → kṣu.
"""
# --- Dynamic Bases ---
sh_vowel = pn.cross("[SH_STEM]", "") + mf_blind  # Keeps the 'ś' before vowel endings
sh_cons = (
    pn.cross("ś[SH_STEM]", "k") + mf_blind
)  # Changes 'ś' to 'k' before consonant endings & Nom Sg

# Singular
nom_sg_sh = sh_cons + pn.cross("[Nom][Sg]", "")  # etādṛś -> etādṛk
acc_sg_sh = sh_vowel + pn.cross("[Acc][Sg]", "am")  # etādṛś -> etādṛśam
ins_sg_sh = sh_vowel + pn.cross("[Ins][Sg]", "ā")
dat_sg_sh = sh_vowel + pn.cross("[Dat][Sg]", "e")
abl_sg_sh = sh_vowel + pn.cross("[Abl][Sg]", "as")
gen_sg_sh = sh_vowel + pn.cross("[Gen][Sg]", "as")
loc_sg_sh = sh_vowel + pn.cross("[Loc][Sg]", "i")
voc_sg_sh = sh_cons + pn.cross("[Voc][Sg]", "")  # etādṛś -> etādṛk

# Dual
nom_du_sh = sh_vowel + pn.cross("[Nom][Du]", "au")
acc_du_sh = sh_vowel + pn.cross("[Acc][Du]", "au")
voc_du_sh = sh_vowel + pn.cross("[Voc][Du]", "au")

ins_du_sh = sh_cons + pn.cross("[Ins][Du]", "#bhyām")  # etādṛk#bhyām → etādṛgbhyām
dat_du_sh = sh_cons + pn.cross("[Dat][Du]", "#bhyām")
abl_du_sh = sh_cons + pn.cross("[Abl][Du]", "#bhyām")

gen_du_sh = sh_vowel + pn.cross("[Gen][Du]", "os")
loc_du_sh = sh_vowel + pn.cross("[Loc][Du]", "os")

# Plural
nom_pl_sh = sh_vowel + pn.cross("[Nom][Pl]", "as")
acc_pl_sh = sh_vowel + pn.cross("[Acc][Pl]", "as")
voc_pl_sh = sh_vowel + pn.cross("[Voc][Pl]", "as")

ins_pl_sh = sh_cons + pn.cross("[Ins][Pl]", "#bhis")   # etādṛk#bhis → etādṛgbhiḥ
dat_pl_sh = sh_cons + pn.cross("[Dat][Pl]", "#bhyas")  # etādṛk#bhyas → etādṛgbhyaḥ
abl_pl_sh = sh_cons + pn.cross("[Abl][Pl]", "#bhyas")

gen_pl_sh = sh_vowel + pn.cross("[Gen][Pl]", "ām")
loc_pl_sh = sh_cons + pn.cross("[Loc][Pl]", "#su")     # etādṛk#su → etādṛkṣu (via RUKI)


# 1. SH-STEM CONSOLIDATION (e.g., etādṛś)
sh_stem_paradigm = pn.union(
    nom_sg_sh,
    acc_sg_sh,
    ins_sg_sh,
    dat_sg_sh,
    abl_sg_sh,
    gen_sg_sh,
    loc_sg_sh,
    voc_sg_sh,
    nom_du_sh,
    acc_du_sh,
    voc_du_sh,
    ins_du_sh,
    dat_du_sh,
    abl_du_sh,
    gen_du_sh,
    loc_du_sh,
    nom_pl_sh,
    acc_pl_sh,
    voc_pl_sh,
    ins_pl_sh,
    dat_pl_sh,
    abl_pl_sh,
    gen_pl_sh,
    loc_pl_sh,
).optimize()
"""
ś-stem NEUTER (e.g., etādṛś)
Oblique cases (Ins-Loc) are identical to Masc/Fem, but Nom/Acc/Voc get neuter treatment.
"""
# --- Dynamic Bases for Neuter ---
sh_vowel_n = pn.cross("[SH_STEM]", "") + pn.cross("[Neut]", "")
sh_cons_n = pn.cross("ś[SH_STEM]", "k") + pn.cross("[Neut]", "")

# Singular
nom_sg_sh_n = sh_cons_n + pn.cross("[Nom][Sg]", "")  # etādṛś -> etādṛk
acc_sg_sh_n = sh_cons_n + pn.cross("[Acc][Sg]", "")  # etādṛś -> etādṛk
voc_sg_sh_n = sh_cons_n + pn.cross("[Voc][Sg]", "")  # etādṛś -> etādṛk

# Dual (Takes 'ī')
nom_du_sh_n = sh_vowel_n + pn.cross("[Nom][Du]", "ī")  # etādṛś -> etādṛśī
acc_du_sh_n = sh_vowel_n + pn.cross("[Acc][Du]", "ī")
voc_du_sh_n = sh_vowel_n + pn.cross("[Voc][Du]", "ī")

# Plural (Infixes anusvāra 'ṃ' before 'ś', plus 'i')
# Whitney §217b: the nasal before ś in neuter plural is anusvāra ṃ (not palatal ñ).
# e.g., etādṛś -> etādṛṃśi
sh_pl_n = pn.cross("ś[SH_STEM]", "ṃś") + pn.cross("[Neut]", "")

nom_pl_sh_n = sh_pl_n + pn.cross("[Nom][Pl]", "i")
acc_pl_sh_n = sh_pl_n + pn.cross("[Acc][Pl]", "i")
voc_pl_sh_n = sh_pl_n + pn.cross("[Voc][Pl]", "i")

# Oblique Cases (Mechanically identical to Masc/Fem but gated for [Neut])
ins_sg_sh_n = sh_vowel_n + pn.cross("[Ins][Sg]", "ā")
dat_sg_sh_n = sh_vowel_n + pn.cross("[Dat][Sg]", "e")
abl_sg_sh_n = sh_vowel_n + pn.cross("[Abl][Sg]", "as")
gen_sg_sh_n = sh_vowel_n + pn.cross("[Gen][Sg]", "as")
loc_sg_sh_n = sh_vowel_n + pn.cross("[Loc][Sg]", "i")

ins_du_sh_n = sh_cons_n + pn.cross("[Ins][Du]", "#bhyām")  # k#bh → gbh via junction sandhi
dat_du_sh_n = sh_cons_n + pn.cross("[Dat][Du]", "#bhyām")
abl_du_sh_n = sh_cons_n + pn.cross("[Abl][Du]", "#bhyām")

gen_du_sh_n = sh_vowel_n + pn.cross("[Gen][Du]", "os")
loc_du_sh_n = sh_vowel_n + pn.cross("[Loc][Du]", "os")

ins_pl_sh_n = sh_cons_n + pn.cross("[Ins][Pl]", "#bhis")   # k#bh → gbh via junction sandhi
dat_pl_sh_n = sh_cons_n + pn.cross("[Dat][Pl]", "#bhyas")
abl_pl_sh_n = sh_cons_n + pn.cross("[Abl][Pl]", "#bhyas")

gen_pl_sh_n = sh_vowel_n + pn.cross("[Gen][Pl]", "ām")
loc_pl_sh_n = sh_cons_n + pn.cross("[Loc][Pl]", "#su")     # k#su → kṣu via RUKI

# 2. NEUTER SH-STEM CONSOLIDATION
sh_neut_paradigm = pn.union(
    nom_sg_sh_n,
    acc_sg_sh_n,
    voc_sg_sh_n,
    nom_du_sh_n,
    acc_du_sh_n,
    voc_du_sh_n,
    nom_pl_sh_n,
    acc_pl_sh_n,
    voc_pl_sh_n,
    ins_sg_sh_n,
    dat_sg_sh_n,
    abl_sg_sh_n,
    gen_sg_sh_n,
    loc_sg_sh_n,
    ins_du_sh_n,
    dat_du_sh_n,
    abl_du_sh_n,
    gen_du_sh_n,
    loc_du_sh_n,
    ins_pl_sh_n,
    dat_pl_sh_n,
    abl_pl_sh_n,
    gen_pl_sh_n,
    loc_pl_sh_n,
).optimize()

# 3. MASTER SH-STEM UNION
sh_stem_master_paradigm = pn.union(
    sh_stem_paradigm,
    sh_neut_paradigm,
).optimize()
