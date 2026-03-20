import pynini as pn
from rules import *

# We only need a Masc/Neut matcher here
mn_g = pn.union("[Masc]", "[Neut]")

'''
1. IN-STEMS (e.g., yogin, balin)
'''
# --- Nom/Acc/Voc Singular & Plural Exceptions ---
nom_sg_in_m = pn.cross("in[IN_STEM][Masc][Nom][Sg]", "ī")    # yogin -> yogī
voc_sg_in_m = pn.cross("[IN_STEM][Masc][Voc][Sg]", "")       # yogin -> yogin (Tag drops)

nom_sg_in_n = pn.cross("in[IN_STEM][Neut][Nom][Sg]", "i")    # yogin -> yogi
acc_sg_in_n = pn.cross("in[IN_STEM][Neut][Acc][Sg]", "i")    
voc_sg_in_n = pn.cross("in[IN_STEM][Neut][Voc][Sg]", "i")    

nom_pl_in_n = pn.cross("in[IN_STEM][Neut][Nom][Pl]", "īni")  # yogin -> yogīni
acc_pl_in_n = pn.cross("in[IN_STEM][Neut][Acc][Pl]", "īni")  
voc_pl_in_n = pn.cross("in[IN_STEM][Neut][Voc][Pl]", "īni")  

# --- Consonant Endings (Drop the 'n') ---
in_cons_base = pn.cross("in[IN_STEM]", "i") + pn.cross(mn_g, "")

ins_du_in = in_cons_base + pn.cross("[Ins][Du]", "bhyām")    # yogin -> yogibhyām
dat_du_in = in_cons_base + pn.cross("[Dat][Du]", "bhyām")
abl_du_in = in_cons_base + pn.cross("[Abl][Du]", "bhyām")

ins_pl_in = in_cons_base + pn.cross("[Ins][Pl]", "bhis")     # yogin -> yogibhis
dat_pl_in = in_cons_base + pn.cross("[Dat][Pl]", "bhyas")
abl_pl_in = in_cons_base + pn.cross("[Abl][Pl]", "bhyas")
loc_pl_in = in_cons_base + pn.cross("[Loc][Pl]", "su")       # yogin -> yogisu (Strict underlying s)

# --- Vowel Endings (Stem stays intact, just append) ---
in_vow_base = pn.cross("[IN_STEM]", "") + pn.cross(mn_g, "")

acc_sg_in_m = in_vow_base + pn.cross("[Acc][Sg]", "am")      # yogin -> yoginam
ins_sg_in = in_vow_base + pn.cross("[Ins][Sg]", "ā")         # yogin -> yoginā
dat_sg_in = in_vow_base + pn.cross("[Dat][Sg]", "e")         
abl_sg_in = in_vow_base + pn.cross("[Abl][Sg]", "as")        
gen_sg_in = in_vow_base + pn.cross("[Gen][Sg]", "as")        
loc_sg_in = in_vow_base + pn.cross("[Loc][Sg]", "i")         

nom_du_in = in_vow_base + pn.cross("[Nom][Du]", "au")        # yogin -> yoginau (Masc) / yoginī (Neut covered by standard 'ī' rule if mapped separately, chart shows yoginī)
# (Note: Neuter Dual N.A.V takes 'ī', so we add a specific override below)
nom_du_in_n = pn.cross("[IN_STEM][Neut][Nom][Du]", "ī")      
acc_du_in_n = pn.cross("[IN_STEM][Neut][Acc][Du]", "ī")
voc_du_in_n = pn.cross("[IN_STEM][Neut][Voc][Du]", "ī")
acc_du_in_m = pn.cross("[IN_STEM][Masc][Acc][Du]", "au")
voc_du_in_m = pn.cross("[IN_STEM][Masc][Voc][Du]", "au")

gen_du_in = in_vow_base + pn.cross("[Gen][Du]", "os")        
loc_du_in = in_vow_base + pn.cross("[Loc][Du]", "os")        

nom_pl_in_m = in_vow_base + pn.cross("[Nom][Pl]", "as")      # yogin -> yoginas
acc_pl_in_m = in_vow_base + pn.cross("[Acc][Pl]", "as")      
voc_pl_in_m = in_vow_base + pn.cross("[Voc][Pl]", "as")      
gen_pl_in = in_vow_base + pn.cross("[Gen][Pl]", "ām")        


'''
2. AN-STEMS (e.g., rājan, ātman, nāman)
'''
# --- Strong Cases (Stem lengthens to 'ān') ---
nom_sg_an_m = pn.cross("an[AN_STEM][Masc][Nom][Sg]", "ā")    # rājan -> rājā
acc_sg_an_m = pn.cross("an[AN_STEM][Masc][Acc][Sg]", "ānam") # rājan -> rājānam

nom_du_an_m = pn.cross("an[AN_STEM][Masc][Nom][Du]", "ānau") # rājan -> rājānau
acc_du_an_m = pn.cross("an[AN_STEM][Masc][Acc][Du]", "ānau")
voc_du_an_m = pn.cross("an[AN_STEM][Masc][Voc][Du]", "ānau")

nom_pl_an_m = pn.cross("an[AN_STEM][Masc][Nom][Pl]", "ānas") # rājan -> rājānas
voc_pl_an_m = pn.cross("an[AN_STEM][Masc][Voc][Pl]", "ānas")

nom_pl_an_n = pn.cross("an[AN_STEM][Neut][Nom][Pl]", "āni")  # nāman -> nāmāni
acc_pl_an_n = pn.cross("an[AN_STEM][Neut][Acc][Pl]", "āni")
voc_pl_an_n = pn.cross("an[AN_STEM][Neut][Voc][Pl]", "āni")

# --- Neuter Short Cases ---
nom_sg_an_n = pn.cross("an[AN_STEM][Neut][Nom][Sg]", "a")    # nāman -> nāma
acc_sg_an_n = pn.cross("an[AN_STEM][Neut][Acc][Sg]", "a")
voc_sg_an_n = pn.cross("an[AN_STEM][Neut][Voc][Sg]", "a")    # Chart shows both 'nāman' and 'nāma' exist for Voc Sg! You can union this if desired.

# --- Consonant Endings (Drop the 'n') ---
an_cons_base = pn.cross("an[AN_STEM]", "a") + pn.cross(mn_g, "")

ins_du_an = an_cons_base + pn.cross("[Ins][Du]", "bhyām")    # rājan -> rājabhyām
dat_du_an = an_cons_base + pn.cross("[Dat][Du]", "bhyām")
abl_du_an = an_cons_base + pn.cross("[Abl][Du]", "bhyām")

ins_pl_an = an_cons_base + pn.cross("[Ins][Pl]", "bhis")     # rājan -> rājabhis
dat_pl_an = an_cons_base + pn.cross("[Dat][Pl]", "bhyas")
abl_pl_an = an_cons_base + pn.cross("[Abl][Pl]", "bhyas")
loc_pl_an = an_cons_base + pn.cross("[Loc][Pl]", "su")       # rājan -> rājasu

# --- Weak Vowel Endings (Stem stays intact, just append) ---
# Underlying forms like 'rājanas' or 'nāmanī' pass perfectly here!
an_vow_base = pn.cross("[AN_STEM]", "") + pn.cross(mn_g, "")

voc_sg_an_m = an_vow_base + pn.cross("[Voc][Sg]", "")        # rājan -> rājan
ins_sg_an = an_vow_base + pn.cross("[Ins][Sg]", "ā")         # rājan -> rājanā (Sandhi will make rājñā)
dat_sg_an = an_vow_base + pn.cross("[Dat][Sg]", "e")
abl_sg_an = an_vow_base + pn.cross("[Abl][Sg]", "as")
gen_sg_an = an_vow_base + pn.cross("[Gen][Sg]", "as")
loc_sg_an = an_vow_base + pn.cross("[Loc][Sg]", "i")

nom_du_an_n = an_vow_base + pn.cross("[Nom][Du]", "ī")       # nāman -> nāmanī (Sandhi will make nāmnī)
acc_du_an_n = an_vow_base + pn.cross("[Acc][Du]", "ī")
voc_du_an_n = an_vow_base + pn.cross("[Voc][Du]", "ī")

gen_du_an = an_vow_base + pn.cross("[Gen][Du]", "os")
loc_du_an = an_vow_base + pn.cross("[Loc][Du]", "os")

acc_pl_an_m = an_vow_base + pn.cross("[Acc][Pl]", "as")      # rājan -> rājanas (Sandhi will make rājñas)
gen_pl_an = an_vow_base + pn.cross("[Gen][Pl]", "ām")



