import pynini as pn
from rules import *


'''
Agent Nouns (e.g., dātṛ - Masc, svásṛ - Fem) 
Strong cases use Vṛddhi (ā)
'''
# Singular
nom_sg_agt = pn.cross("ṛ[R_STEM][Agt][Nom][Sg]", "ā")
acc_sg_agt = pn.cross("ṛ[R_STEM][Agt][Acc][Sg]", "āram")
ins_sg_agt = pn.cross("ṛ[R_STEM][Agt][Ins][Sg]", "rā")
dat_sg_agt = pn.cross("ṛ[R_STEM][Agt][Dat][Sg]", "re")
abl_sg_agt = pn.cross("ṛ[R_STEM][Agt][Abl][Sg]", "ur")
gen_sg_agt = pn.cross("ṛ[R_STEM][Agt][Gen][Sg]", "ur")
loc_sg_agt = pn.cross("ṛ[R_STEM][Agt][Loc][Sg]", "ari")
voc_sg_agt = pn.cross("ṛ[R_STEM][Agt][Voc][Sg]", "ar")

# Dual
nom_du_agt = pn.cross("ṛ[R_STEM][Agt][Nom][Du]", "ārau")
acc_du_agt = pn.cross("ṛ[R_STEM][Agt][Acc][Du]", "ārau")
ins_du_agt = pn.cross("[R_STEM][Agt][Ins][Du]", "bhyām")
dat_du_agt = pn.cross("[R_STEM][Agt][Dat][Du]", "bhyām")
abl_du_agt = pn.cross("[R_STEM][Agt][Abl][Du]", "bhyām")
gen_du_agt = pn.cross("ṛ[R_STEM][Agt][Gen][Du]", "ros")
loc_du_agt = pn.cross("ṛ[R_STEM][Agt][Loc][Du]", "ros")
voc_du_agt = pn.cross("ṛ[R_STEM][Agt][Voc][Du]", "ārau")

# Plural
nom_pl_agt = pn.cross("ṛ[R_STEM][Agt][Nom][Pl]", "āras")
acc_pl_m_agt = pn.cross("ṛ[R_STEM][Agt][Masc][Acc][Pl]", "ṝn")
acc_pl_f_agt = pn.cross("ṛ[R_STEM][Agt][Fem][Acc][Pl]", "ṝs")
ins_pl_agt = pn.cross("[R_STEM][Agt][Ins][Pl]", "bhis")
dat_pl_agt = pn.cross("[R_STEM][Agt][Dat][Pl]", "bhyas")
abl_pl_agt = pn.cross("[R_STEM][Agt][Abl][Pl]", "bhyas")
gen_pl_agt = pn.cross("ṛ[R_STEM][Agt][Gen][Pl]", "ṝnām")  # Strict underlying dental n
loc_pl_agt = pn.cross("[R_STEM][Agt][Loc][Pl]", "su")     # Strict underlying dental s
voc_pl_agt = pn.cross("ṛ[R_STEM][Agt][Voc][Pl]", "āras")

agt_paradigm = pn.union(
    nom_sg_agt, acc_sg_agt, ins_sg_agt, dat_sg_agt, abl_sg_agt, gen_sg_agt, loc_sg_agt, voc_sg_agt,
    nom_du_agt, acc_du_agt, ins_du_agt, dat_du_agt, abl_du_agt, gen_du_agt, loc_du_agt, voc_du_agt,
    nom_pl_agt, acc_pl_m_agt, acc_pl_f_agt, ins_pl_agt, dat_pl_agt, abl_pl_agt, gen_pl_agt, loc_pl_agt, voc_pl_agt
).optimize()


'''
Kinship Nouns (e.g., pitṛ - Masc, mātṛ - Fem) 
Strong cases use Guṇa (a)
'''
# Singular
nom_sg_kin = pn.cross("ṛ[R_STEM][Kin][Nom][Sg]", "ā")
acc_sg_kin = pn.cross("ṛ[R_STEM][Kin][Acc][Sg]", "aram")
ins_sg_kin = pn.cross("ṛ[R_STEM][Kin][Ins][Sg]", "rā")
dat_sg_kin = pn.cross("ṛ[R_STEM][Kin][Dat][Sg]", "re")
abl_sg_kin = pn.cross("ṛ[R_STEM][Kin][Abl][Sg]", "ur")
gen_sg_kin = pn.cross("ṛ[R_STEM][Kin][Gen][Sg]", "ur")
loc_sg_kin = pn.cross("ṛ[R_STEM][Kin][Loc][Sg]", "ari")
voc_sg_kin = pn.cross("ṛ[R_STEM][Kin][Voc][Sg]", "ar")

# Dual
nom_du_kin = pn.cross("ṛ[R_STEM][Kin][Nom][Du]", "arau")
acc_du_kin = pn.cross("ṛ[R_STEM][Kin][Acc][Du]", "arau")
ins_du_kin = pn.cross("[R_STEM][Kin][Ins][Du]", "bhyām")
dat_du_kin = pn.cross("[R_STEM][Kin][Dat][Du]", "bhyām")
abl_du_kin = pn.cross("[R_STEM][Kin][Abl][Du]", "bhyām")
gen_du_kin = pn.cross("ṛ[R_STEM][Kin][Gen][Du]", "ros")
loc_du_kin = pn.cross("ṛ[R_STEM][Kin][Loc][Du]", "ros")
voc_du_kin = pn.cross("ṛ[R_STEM][Kin][Voc][Du]", "arau")

# Plural
# solution for this: scans if the string includes acc + plural, if has the tag then add the gendered tag
nom_pl_kin = pn.cross("ṛ[R_STEM][Kin][Nom][Pl]", "aras")
acc_pl_m_kin = pn.cross("ṛ[R_STEM][Kin][Masc][Acc][Pl]", "ṝn")
acc_pl_f_kin = pn.cross("ṛ[R_STEM][Kin][Fem][Acc][Pl]", "ṝs")
ins_pl_kin = pn.cross("[R_STEM][Kin][Ins][Pl]", "bhis")
dat_pl_kin = pn.cross("[R_STEM][Kin][Dat][Pl]", "bhyas")
abl_pl_kin = pn.cross("[R_STEM][Kin][Abl][Pl]", "bhyas")
gen_pl_kin = pn.cross("ṛ[R_STEM][Kin][Gen][Pl]", "ṝnām")  # Strict underlying dental n
loc_pl_kin = pn.cross("[R_STEM][Kin][Loc][Pl]", "su")     # Strict underlying dental s
voc_pl_kin = pn.cross("ṛ[R_STEM][Kin][Voc][Pl]", "aras")

kin_paradigm = pn.union(
    nom_sg_kin, acc_sg_kin, ins_sg_kin, dat_sg_kin, abl_sg_kin, gen_sg_kin, loc_sg_kin, voc_sg_kin,
    nom_du_kin, acc_du_kin, ins_du_kin, dat_du_kin, abl_du_kin, gen_du_kin, loc_du_kin, voc_du_kin,
    nom_pl_kin, acc_pl_m_kin, acc_pl_f_kin, ins_pl_kin, dat_pl_kin, abl_pl_kin, gen_pl_kin, loc_pl_kin, voc_pl_kin
).optimize()


'''
Neuter Nouns (e.g., dhātṛ) 
n-insertion before vowel endings
'''
# Singular
nom_sg_neut = pn.cross("[R_STEM][Neut][Nom][Sg]", "")
acc_sg_neut = pn.cross("[R_STEM][Neut][Acc][Sg]", "")
ins_sg_neut = pn.cross("[R_STEM][Neut][Ins][Sg]", "nā")
dat_sg_neut = pn.cross("[R_STEM][Neut][Dat][Sg]", "ne")
abl_sg_neut = pn.cross("[R_STEM][Neut][Abl][Sg]", "nas")
gen_sg_neut = pn.cross("[R_STEM][Neut][Gen][Sg]", "nas")
loc_sg_neut = pn.cross("[R_STEM][Neut][Loc][Sg]", "ni")
voc_sg_neut = pn.union(
    pn.cross("[R_STEM][Neut][Voc][Sg]", ""),
    pn.cross("ṛ[R_STEM][Neut][Voc][Sg]", "ar")
)

# Dual
nom_du_neut = pn.cross("[R_STEM][Neut][Nom][Du]", "nī")
acc_du_neut = pn.cross("[R_STEM][Neut][Acc][Du]", "nī")
ins_du_neut = pn.cross("[R_STEM][Neut][Ins][Du]", "bhyām")
dat_du_neut = pn.cross("[R_STEM][Neut][Dat][Du]", "bhyām")
abl_du_neut = pn.cross("[R_STEM][Neut][Abl][Du]", "bhyām")
gen_du_neut = pn.cross("[R_STEM][Neut][Gen][Du]", "nos")
loc_du_neut = pn.cross("[R_STEM][Neut][Loc][Du]", "nos")
voc_du_neut = pn.cross("[R_STEM][Neut][Voc][Du]", "nī")

# Plural
nom_pl_neut = pn.cross("ṛ[R_STEM][Neut][Nom][Pl]", "ṝni")
acc_pl_neut = pn.cross("ṛ[R_STEM][Neut][Acc][Pl]", "ṝni")
ins_pl_neut = pn.cross("[R_STEM][Neut][Ins][Pl]", "bhis")
dat_pl_neut = pn.cross("[R_STEM][Neut][Dat][Pl]", "bhyas")
abl_pl_neut = pn.cross("[R_STEM][Neut][Abl][Pl]", "bhyas")
gen_pl_neut = pn.cross("ṛ[R_STEM][Neut][Gen][Pl]", "ṝnām") # Strict underlying dental n
loc_pl_neut = pn.cross("[R_STEM][Neut][Loc][Pl]", "su")    # Strict underlying dental s
voc_pl_neut = pn.cross("ṛ[R_STEM][Neut][Voc][Pl]", "ṝni")

neut_r_paradigm = pn.union(
    nom_sg_neut, acc_sg_neut, ins_sg_neut, dat_sg_neut, abl_sg_neut, gen_sg_neut, loc_sg_neut, voc_sg_neut,
    nom_du_neut, acc_du_neut, ins_du_neut, dat_du_neut, abl_du_neut, gen_du_neut, loc_du_neut, voc_du_neut,
    nom_pl_neut, acc_pl_neut, ins_pl_neut, dat_pl_neut, abl_pl_neut, gen_pl_neut, loc_pl_neut, voc_pl_neut
).optimize()
