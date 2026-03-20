import pynini as pn
from rules import *

# 1. Dynamic Matchers
mn_g = pn.union("[Masc]", "[Neut]")
ant_tags = pn.union("[ANT_STEM]", "[MANT_STEM]", "[VANT_STEM]")
m_v_tags = pn.union("[MANT_STEM]", "[VANT_STEM]")

# 2. Dynamic Bases
# Strong base: keeps the 'nt' intact
strong_m = pn.cross(ant_tags, "") + pn.cross("[Masc]", "")
strong_n = pn.cross(ant_tags, "") + pn.cross("[Neut]", "")

# Weak base: consumes 'nt' and replaces it with 't'
weak_m = pn.cross("nt", "t") + pn.cross(ant_tags, "") + pn.cross("[Masc]", "")
weak_n = pn.cross("nt", "t") + pn.cross(ant_tags, "") + pn.cross("[Neut]", "")
weak_blind = pn.cross("nt", "t") + pn.cross(ant_tags, "") + pn.cross(mn_g, "")


'''
3. MASCULINE SPECIFIC CASES
'''
# --- Nom/Voc Sg Exceptions ---
# -ant stems drop the 't'
nom_sg_ant = pn.cross("nt[ANT_STEM][Masc][Nom][Sg]", "n")   # bhāvant -> bhāvan
voc_sg_ant = pn.cross("nt[ANT_STEM][Masc][Voc][Sg]", "n")   

# -mant and -vant stems lengthen the vowel in the Nom Sg (ant -> ān)
nom_sg_mvant = pn.cross("ant", "ān") + pn.cross(m_v_tags, "") + pn.cross("[Masc][Nom][Sg]", "") # paśumant -> paśumān
voc_sg_mvant = pn.cross("nt", "n") + pn.cross(m_v_tags, "") + pn.cross("[Masc][Voc][Sg]", "")   # paśumant -> paśuman

# --- Strong Cases (Stem stays 'nt') ---
acc_sg_m = strong_m + pn.cross("[Acc][Sg]", "am")           # bhāvant -> bhāvantam
nom_du_m = strong_m + pn.cross("[Nom][Du]", "au")
acc_du_m = strong_m + pn.cross("[Acc][Du]", "au")
voc_du_m = strong_m + pn.cross("[Voc][Du]", "au")
nom_pl_m = strong_m + pn.cross("[Nom][Pl]", "as")
voc_pl_m = strong_m + pn.cross("[Voc][Pl]", "as")

# --- Weak Cases (Stem drops 'n') ---
acc_pl_m = weak_m + pn.cross("[Acc][Pl]", "as")             # bhāvant -> bhāvatas


'''
4. NEUTER SPECIFIC CASES
'''
# --- Weak Cases (Nom/Acc/Voc Sg & Du) ---
nom_sg_n = weak_n + pn.cross("[Nom][Sg]", "")               # bhāvant -> bhāvat
acc_sg_n = weak_n + pn.cross("[Acc][Sg]", "")
voc_sg_n = weak_n + pn.cross("[Voc][Sg]", "")

nom_du_n = weak_n + pn.cross("[Nom][Du]", "ī")              # bhāvant -> bhāvatī
acc_du_n = weak_n + pn.cross("[Acc][Du]", "ī")
voc_du_n = weak_n + pn.cross("[Voc][Du]", "ī")

# --- Strong Cases (Nom/Acc/Voc Pl) ---
nom_pl_n = strong_n + pn.cross("[Nom][Pl]", "i")            # bhāvant -> bhāvanti
acc_pl_n = strong_n + pn.cross("[Acc][Pl]", "i")
voc_pl_n = strong_n + pn.cross("[Voc][Pl]", "i")


'''
5. GENDER-BLIND WEAK CASES (Ins, Dat, Abl, Gen, Loc)
'''
# The 'weak_blind' base automatically handles dropping the 'n' 
# and allowing either [Masc] or [Neut] to pass through!
ins_sg = weak_blind + pn.cross("[Ins][Sg]", "ā")            # bhāvant -> bhāvatā
dat_sg = weak_blind + pn.cross("[Dat][Sg]", "e")
abl_sg = weak_blind + pn.cross("[Abl][Sg]", "as")
gen_sg = weak_blind + pn.cross("[Gen][Sg]", "as")
loc_sg = weak_blind + pn.cross("[Loc][Sg]", "i")

ins_du = weak_blind + pn.cross("[Ins][Du]", "bhyām")        # bhāvant -> bhāvatbhyām (Sandhi -> dbhyām)
dat_du = weak_blind + pn.cross("[Dat][Du]", "bhyām")
abl_du = weak_blind + pn.cross("[Abl][Du]", "bhyām")
gen_du = weak_blind + pn.cross("[Gen][Du]", "os")
loc_du = weak_blind + pn.cross("[Loc][Du]", "os")

ins_pl = weak_blind + pn.cross("[Ins][Pl]", "bhis")         # bhāvant -> bhāvatbhis (Sandhi -> dbhis)
dat_pl = weak_blind + pn.cross("[Dat][Pl]", "bhyas")
abl_pl = weak_blind + pn.cross("[Abl][Pl]", "bhyas")
gen_pl = weak_blind + pn.cross("[Gen][Pl]", "ām")
loc_pl = weak_blind + pn.cross("[Loc][Pl]", "su")           # bhāvant -> bhāvatsu
