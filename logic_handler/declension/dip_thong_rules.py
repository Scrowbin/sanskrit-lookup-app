import pynini as pn
from rules import *

'''
e-stem (e.g., se)
'''
# its also ay stem but they are essentially the same
nom_sg_e = pn.cross("e[E_STEM][Nom][Sg]", "es")      
acc_sg_e = pn.cross("e[E_STEM][Acc][Sg]", "ayam")    
ins_sg_e = pn.cross("e[E_STEM][Ins][Sg]", "ayā")     
dat_sg_e = pn.cross("e[E_STEM][Dat][Sg]", "aye")     
abl_sg_e = pn.cross("e[E_STEM][Abl][Sg]", "es")      
gen_sg_e = pn.cross("e[E_STEM][Gen][Sg]", "es")      
loc_sg_e = pn.cross("e[E_STEM][Loc][Sg]", "ayi")     
voc_sg_e = pn.cross("[E_STEM][Voc][Sg]", "")

nom_du_e = pn.cross("e[E_STEM][Nom][Du]", "ayau")    
acc_du_e = pn.cross("e[E_STEM][Acc][Du]", "ayau")     
voc_du_e = pn.cross("e[E_STEM][Voc][Du]", "ayau")     
ins_du_e = pn.cross("[E_STEM][Ins][Du]", "bhyām")    
dat_du_e = pn.cross("[E_STEM][Dat][Du]", "bhyām")   
abl_du_e = pn.cross("[E_STEM][Abl][Du]", "bhyām")   
gen_du_e = pn.cross("e[E_STEM][Gen][Du]", "ayos")    
loc_du_e = pn.cross("e[E_STEM][Loc][Du]", "ayos")     

nom_pl_e = pn.cross("e[E_STEM][Nom][Pl]", "ayas")    
acc_pl_e = pn.cross("e[E_STEM][Acc][Pl]", "ayas")    
voc_pl_e = pn.cross("e[E_STEM][Voc][Pl]", "ayas")     
ins_pl_e = pn.cross("[E_STEM][Ins][Pl]", "bhis")     
dat_pl_e = pn.cross("[E_STEM][Dat][Pl]", "bhyas")    
abl_pl_e = pn.cross("[E_STEM][Abl][Pl]", "bhyas")   
gen_pl_e = pn.cross("e[E_STEM][Gen][Pl]", "ayām")    
loc_pl_e = pn.cross("[E_STEM][Loc][Pl]", "su")

'''
o-stem (e.g., go)
'''
# Singular
nom_sg_o = pn.cross("o[O_STEM][Nom][Sg]", "aus")     # go -> gaus
acc_sg_o = pn.cross("o[O_STEM][Acc][Sg]", "ām")      # go -> gām (Irregular!)
ins_sg_o = pn.cross("o[O_STEM][Ins][Sg]", "avā")     # go -> gavā (o -> av)
dat_sg_o = pn.cross("o[O_STEM][Dat][Sg]", "ave")     # go -> gave (o -> av)
abl_sg_o = pn.cross("o[O_STEM][Abl][Sg]", "os")      # go -> gos 
gen_sg_o = pn.cross("o[O_STEM][Gen][Sg]", "os")      # go -> gos
loc_sg_o = pn.cross("o[O_STEM][Loc][Sg]", "avi")     # go -> gavi (o -> av)
voc_sg_o = pn.cross("o[O_STEM][Voc][Sg]", "aus")     # go -> gaus

# Dual
nom_du_o = pn.cross("o[O_STEM][Nom][Du]", "āvau")    # go -> gāvau (o -> āv)
acc_du_o = pn.cross("o[O_STEM][Acc][Du]", "āvau")    
voc_du_o = pn.cross("o[O_STEM][Voc][Du]", "āvau")    

ins_du_o = pn.cross("[O_STEM][Ins][Du]", "bhyām")    # go + bhyām
dat_du_o = pn.cross("[O_STEM][Dat][Du]", "bhyām")    
abl_du_o = pn.cross("[O_STEM][Abl][Du]", "bhyām")    

gen_du_o = pn.cross("o[O_STEM][Gen][Du]", "avos")    # go -> gavos (o -> av)
loc_du_o = pn.cross("o[O_STEM][Loc][Du]", "avos")    

# Plural
nom_pl_o = pn.cross("o[O_STEM][Nom][Pl]", "āvas")    # go -> gāvas (o -> āv)
acc_pl_o = pn.cross("o[O_STEM][Acc][Pl]", "ās")      # go -> gās (Irregular!)
voc_pl_o = pn.cross("o[O_STEM][Voc][Pl]", "āvas")    

ins_pl_o = pn.cross("[O_STEM][Ins][Pl]", "bhis")     # go + bhis
dat_pl_o = pn.cross("[O_STEM][Dat][Pl]", "bhyas")    
abl_pl_o = pn.cross("[O_STEM][Abl][Pl]", "bhyas")    

gen_pl_o = pn.cross("o[O_STEM][Gen][Pl]", "avām")    # go -> gavām (o -> av)
loc_pl_o = pn.cross("[O_STEM][Loc][Pl]", "su")       # go + su (Strict underlying dental)

'''
au-stem (e.g., nau)
'''
# Singular
nom_sg_au = pn.cross("[AU_STEM][Nom][Sg]", "s")      # nau -> naus
acc_sg_au = pn.cross("au[AU_STEM][Acc][Sg]", "āvam") # nau -> nāvam (au -> āv)
ins_sg_au = pn.cross("au[AU_STEM][Ins][Sg]", "āvā")  # nau -> nāvā
dat_sg_au = pn.cross("au[AU_STEM][Dat][Sg]", "āve")  # nau -> nāve
abl_sg_au = pn.cross("au[AU_STEM][Abl][Sg]", "āvas") # nau -> nāvas
gen_sg_au = pn.cross("au[AU_STEM][Gen][Sg]", "āvas") # nau -> nāvas
loc_sg_au = pn.cross("au[AU_STEM][Loc][Sg]", "āvi")  # nau -> nāvi
voc_sg_au = pn.cross("[AU_STEM][Voc][Sg]", "s")      # nau -> naus

# Dual
nom_du_au = pn.cross("au[AU_STEM][Nom][Du]", "āvau") # nau -> nāvau
acc_du_au = pn.cross("au[AU_STEM][Acc][Du]", "āvau") 
voc_du_au = pn.cross("au[AU_STEM][Voc][Du]", "āvau") 
ins_du_au = pn.cross("[AU_STEM][Ins][Du]", "bhyām")  # nau + bhyām
dat_du_au = pn.cross("[AU_STEM][Dat][Du]", "bhyām")  
abl_du_au = pn.cross("[AU_STEM][Abl][Du]", "bhyām")  
gen_du_au = pn.cross("au[AU_STEM][Gen][Du]", "āvos") # nau -> nāvos
loc_du_au = pn.cross("au[AU_STEM][Loc][Du]", "āvos") 

# Plural
nom_pl_au = pn.cross("au[AU_STEM][Nom][Pl]", "āvas") # nau -> nāvas
acc_pl_au = pn.cross("au[AU_STEM][Acc][Pl]", "āvas") # nau -> nāvas
voc_pl_au = pn.cross("au[AU_STEM][Voc][Pl]", "āvas") 
ins_pl_au = pn.cross("[AU_STEM][Ins][Pl]", "bhis")   # nau + bhis
dat_pl_au = pn.cross("[AU_STEM][Dat][Pl]", "bhyas")  
abl_pl_au = pn.cross("[AU_STEM][Abl][Pl]", "bhyas")  
gen_pl_au = pn.cross("au[AU_STEM][Gen][Pl]", "āvām") # nau -> nāvām
loc_pl_au = pn.cross("[AU_STEM][Loc][Pl]", "su")     # nau + su


# '''
# ai-stem (e.g., rai)
# '''
# nom_sg_ai = pn.cross("ai[AI_STEM][Nom][Sg]", "ās")       
# acc_sg_ai = pn.cross("ai[AI_STEM][Acc][Sg]", "āyam")     
# ins_sg_ai = pn.cross("ai[AI_STEM][Ins][Sg]", "āyā")      
# dat_sg_ai = pn.cross("ai[AI_STEM][Dat][Sg]", "āye")      
# abl_sg_ai = pn.cross("ai[AI_STEM][Abl][Sg]", "āyas")     
# gen_sg_ai = pn.cross("ai[AI_STEM][Gen][Sg]", "āyas")     
# loc_sg_ai = pn.cross("ai[AI_STEM][Loc][Sg]", "āyi")      
# voc_sg_ai = pn.cross("ai[AI_STEM][Voc][Sg]", "ās")       
#
# nom_du_ai = pn.cross("ai[AI_STEM][Nom][Du]", "āyau")     
# acc_du_ai = pn.cross("ai[AI_STEM][Acc][Du]", "āyau")     
# voc_du_ai = pn.cross("ai[AI_STEM][Voc][Du]", "āyau")     
# ins_du_ai = pn.cross("ai[AI_STEM][Ins][Du]", "ābhyām")   
# dat_du_ai = pn.cross("ai[AI_STEM][Dat][Du]", "ābhyām")   
# abl_du_ai = pn.cross("ai[AI_STEM][Abl][Du]", "ābhyām")   
# gen_du_ai = pn.cross("ai[AI_STEM][Gen][Du]", "āyos")     
# loc_du_ai = pn.cross("ai[AI_STEM][Loc][Du]", "āyos")     
#
# nom_pl_ai = pn.cross("ai[AI_STEM][Nom][Pl]", "āyas")     
# acc_pl_ai = pn.cross("ai[AI_STEM][Acc][Pl]", "āyas")     
# voc_pl_ai = pn.cross("ai[AI_STEM][Voc][Pl]", "āyas")     
# ins_pl_ai = pn.cross("ai[AI_STEM][Ins][Pl]", "ābhis")    
# dat_pl_ai = pn.cross("ai[AI_STEM][Dat][Pl]", "ābhyas")   
# abl_pl_ai = pn.cross("ai[AI_STEM][Abl][Pl]", "ābhyas")   
# gen_pl_ai = pn.cross("ai[AI_STEM][Gen][Pl]", "āyām")     
# loc_pl_ai = pn.cross("ai[AI_STEM][Loc][Pl]", "āsu")

