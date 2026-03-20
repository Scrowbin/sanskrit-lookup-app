import pynini as pn
from rules import *

# 1. Dynamic Matchers
mn_g = pn.union("[Masc]", "[Neut]")

# 2. Dynamic Bases (Three grades!)
# Strong base: keeps the 'vāṅs' intact
strong_m = pn.cross("vāṅs[VAS_STEM]", "vāṅs") + pn.cross("[Masc]", "")
strong_n = pn.cross("vāṅs[VAS_STEM]", "vāṅs") + pn.cross("[Neut]", "")

# Middle base (Consonant endings & Sg Neuters): becomes 'vat'
middle_m = pn.cross("vāṅs[VAS_STEM]", "vat") + pn.cross("[Masc]", "")
middle_n = pn.cross("vāṅs[VAS_STEM]", "vat") + pn.cross("[Neut]", "")
middle_blind = pn.cross("vāṅs[VAS_STEM]", "vat") + pn.cross(mn_g, "")

# Weakest base (Zero-grade before vowels): becomes 'uṣ'
weak_m = pn.cross("vāṅs[VAS_STEM]", "uṣ") + pn.cross("[Masc]", "")
weak_n = pn.cross("vāṅs[VAS_STEM]", "uṣ") + pn.cross("[Neut]", "")
weak_blind = pn.cross("vāṅs[VAS_STEM]", "uṣ") + pn.cross(mn_g, "")


'''
3. MASCULINE SPECIFIC CASES
'''
# --- Sg Exceptions ---
nom_sg_m = pn.cross("vāṅs[VAS_STEM][Masc][Nom][Sg]", "vān")  # vidvāṅs -> vidvān
voc_sg_m = pn.cross("vāṅs[VAS_STEM][Masc][Voc][Sg]", "van")  # vidvāṅs -> vidvan (Short 'a'!)

# --- Strong Cases (Stem stays 'vāṅs') ---
acc_sg_m = strong_m + pn.cross("[Acc][Sg]", "am")            # vidvāṅs -> vidvāṅsam
nom_du_m = strong_m + pn.cross("[Nom][Du]", "au")            # vidvāṅs -> vidvāṅsau
acc_du_m = strong_m + pn.cross("[Acc][Du]", "au")
voc_du_m = strong_m + pn.cross("[Voc][Du]", "au")
nom_pl_m = strong_m + pn.cross("[Nom][Pl]", "as")            # vidvāṅs -> vidvāṅsas
voc_pl_m = strong_m + pn.cross("[Voc][Pl]", "as")

# --- Weakest Cases (Stem becomes 'uṣ') ---
acc_pl_m = weak_m + pn.cross("[Acc][Pl]", "as")              # vidvāṅs -> viduṣas


'''
4. NEUTER SPECIFIC CASES
'''
# --- Middle Cases (Nom/Acc/Voc Sg) ---
nom_sg_n = middle_n + pn.cross("[Nom][Sg]", "")              # vidvāṅs -> vidvat
acc_sg_n = middle_n + pn.cross("[Acc][Sg]", "")
voc_sg_n = middle_n + pn.cross("[Voc][Sg]", "")

# --- Weakest Cases (Nom/Acc/Voc Du) ---
nom_du_n = weak_n + pn.cross("[Nom][Du]", "ī")               # vidvāṅs -> viduṣī
acc_du_n = weak_n + pn.cross("[Acc][Du]", "ī")
voc_du_n = weak_n + pn.cross("[Voc][Du]", "ī")

# --- Strong Cases (Nom/Acc/Voc Pl) ---
nom_pl_n = strong_n + pn.cross("[Nom][Pl]", "i")             # vidvāṅs -> vidvāṅsi
acc_pl_n = strong_n + pn.cross("[Acc][Pl]", "i")
voc_pl_n = strong_n + pn.cross("[Voc][Pl]", "i")


'''
5. GENDER-BLIND MIDDLE CASES (Consonant Endings)
The stem behaves exactly like a t-stem here!
'''
ins_du = middle_blind + pn.cross("[Ins][Du]", "bhyām")       # vidvāṅs -> vidvatbhyām (Sandhi -> dbhyām)
dat_du = middle_blind + pn.cross("[Dat][Du]", "bhyām")
abl_du = middle_blind + pn.cross("[Abl][Du]", "bhyām")
ins_pl = middle_blind + pn.cross("[Ins][Pl]", "bhis")        # vidvāṅs -> vidvatbhis (Sandhi -> dbhis)
dat_pl = middle_blind + pn.cross("[Dat][Pl]", "bhyas")
abl_pl = middle_blind + pn.cross("[Abl][Pl]", "bhyas")
loc_pl = middle_blind + pn.cross("[Loc][Pl]", "su")          # vidvāṅs -> vidvatsu


'''
6. GENDER-BLIND WEAKEST CASES (Vowel Endings)
The stem collapses to 'uṣ'
'''
ins_sg = weak_blind + pn.cross("[Ins][Sg]", "ā")             # vidvāṅs -> viduṣā
dat_sg = weak_blind + pn.cross("[Dat][Sg]", "e")             # vidvāṅs -> viduṣe
abl_sg = weak_blind + pn.cross("[Abl][Sg]", "as")
gen_sg = weak_blind + pn.cross("[Gen][Sg]", "as")
loc_sg = weak_blind + pn.cross("[Loc][Sg]", "i")             # vidvāṅs -> viduṣi
gen_du = weak_blind + pn.cross("[Gen][Du]", "os")            # vidvāṅs -> viduṣos
loc_du = weak_blind + pn.cross("[Loc][Du]", "os")
