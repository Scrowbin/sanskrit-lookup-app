import pynini as pn
from rules import *

'''
Singular
'''
# Masculine singular i-stem (e.g., agni)
nom_sg_masc_i = pn.cross("[I_STEM][Nom][Sg]", "s")      # agni + [Nom][Sg] -> agnis
acc_sg_masc_i = pn.cross("[I_STEM][Acc][Sg]", "m")      # agni + [Acc][Sg] -> agnim
ins_sg_masc_i = pn.cross("[I_STEM][Ins][Sg]", "nā")     # agni + [Ins][Sg] -> agninā (appends)
dat_sg_masc_i = pn.cross("i[I_STEM][Dat][Sg]", "aye")   # agni + [Dat][Sg] -> agnaye (i -> aye)
abl_sg_masc_i = pn.cross("i[I_STEM][Abl][Sg]", "es")    # agni + [Abl][Sg] -> agnes
gen_sg_masc_i = pn.cross("i[I_STEM][Gen][Sg]", "es")    # agni + [Gen][Sg] -> agnes
loc_sg_masc_i = pn.cross("i[I_STEM][Loc][Sg]", "au")    # agni + [Loc][Sg] -> agnau
voc_sg_masc_i = pn.cross("i[I_STEM][Voc][Sg]", "e")     # agni + [Voc][Sg] -> agne

# Feminine singular i-stem (e.g., gati)
nom_sg_fem_i = pn.cross("[I_STEM][Nom][Sg]", "s")       # gati + [Nom][Sg] -> gatis
acc_sg_fem_i = pn.cross("[I_STEM][Acc][Sg]", "m")       # gati + [Acc][Sg] -> gatim
ins_sg_fem_i = pn.cross("i[I_STEM][Ins][Sg]", "yā")     # gati + [Ins][Sg] -> gatyā (i -> yā)
dat_sg_fem_i = pn.cross("i[I_STEM][Dat][Sg]", "aye")    # gati + [Dat][Sg] -> gataye
# The table shows feminine Abl/Gen has two valid forms (-es or -yās). 
abl_sg_fem_i = pn.union(pn.cross("i[I_STEM][Abl][Sg]", "es"), pn.cross("i[I_STEM][Abl][Sg]", "yās"))
gen_sg_fem_i = pn.union(pn.cross("iI_STEM][Gen][Sg]", "es"), pn.cross("i[I_STEM][Gen][Sg]", "yās"))
loc_sg_fem_i = pn.cross("i[I_STEM][Loc][Sg]", "au")     # gati + [Loc][Sg] -> gatau
voc_sg_fem_i = pn.cross("i[I_STEM][Voc][Sg]", "e")      # gati + [Voc][Sg] -> gate

# Neuter singular i-stem (e.g., vāri)
nom_sg_neut_i = pn.cross("[I_STEM][Nom][Sg]", "")        # vāri + [Nom][Sg] -> vāri (no change)
acc_sg_neut_i = pn.cross("[I_STEM][Acc][Sg]", "")        # vāri + [Acc][Sg] -> vāri
ins_sg_neut_i = pn.cross("[I_STEM][Ins][Sg]", "nā")      # vāri + [Ins][Sg] -> vārinā 
dat_sg_neut_i = pn.cross("[I_STEM][Dat][Sg]", "ne")      # vāri + [Dat][Sg] -> vārine 
abl_sg_neut_i = pn.cross("[I_STEM][Abl][Sg]", "nas")     # vāri + [Abl][Sg] -> vārinas 
gen_sg_neut_i = pn.cross("[I_STEM][Gen][Sg]", "nas")     # vāri + [Gen][Sg] -> vārinas 
loc_sg_neut_i = pn.cross("[I_STEM][Loc][Sg]", "ni")      # vāri + [Loc][Sg] -> vārini 
# Vocative can be bare stem or take 'e'
voc_sg_neut_i = pn.union(
    pn.cross("[I_STEM][Voc][Sg]", ""),                   # -> vāri
    pn.cross("i[I_STEM][Voc][Sg]", "e")                  # -> vāre (i -> e)
)

'''
Dual
'''
# Masc/Fem dual i-stem (e.g., agni / gati)

# exact same shit for masc and fem dual
nom_du_i = pn.cross("i[I_STEM][Nom][Du]", "ī")          # agni + [Nom][Du] -> agnī (lengthens)
acc_du_i = pn.cross("i[I_STEM][Acc][Du]", "ī")          # agni + [Acc][Du] -> agnī
voc_du_i = pn.cross("i[I_STEM][Voc][Du]", "ī")          # agni + [Voc][Du] -> agnī

ins_du_i = pn.cross("[I_STEM][Ins][Du]", "bhyām")       # agni + [Ins][Du] -> agnibhyām (appends)
dat_du_i = pn.cross("[I_STEM][Dat][Du]", "bhyām")       # agni + [Dat][Du] -> agnibhyām
abl_du_i = pn.cross("[I_STEM][Abl][Du]", "bhyām")       # agni + [Abl][Du] -> agnibhyām

gen_du_i = pn.cross("i[I_STEM][Gen][Du]", "yos")        # agni + [Gen][Du] -> agnyos (i -> yos)
loc_du_i = pn.cross("i[I_STEM][Loc][Du]", "yos")        # agni + [Loc][Du] -> agnyos

# Neuter dual i-stem (e.g., vāri)
nom_du_neut_i = pn.cross("[I_STEM][Nom][Du]", "nī")      # vāri + [Nom][Du] -> vārinī 
acc_du_neut_i = pn.cross("[I_STEM][Acc][Du]", "nī")      # vāri + [Acc][Du] -> vārinī
voc_du_neut_i = pn.cross("[I_STEM][Voc][Du]", "nī")      # vāri + [Voc][Du] -> vārinī

ins_du_neut_i = pn.cross("[I_STEM][Ins][Du]", "bhyām")   # vāri + [Ins][Du] -> vāribhyām
dat_du_neut_i = pn.cross("[I_STEM][Dat][Du]", "bhyām")   # vāri + [Dat][Du] -> vāribhyām
abl_du_neut_i = pn.cross("[I_STEM][Abl][Du]", "bhyām")   # vāri + [Abl][Du] -> vāribhyām

gen_du_neut_i = pn.cross("[I_STEM][Gen][Du]", "nos")     # vāri + [Gen][Du] -> vārinos 
loc_du_neut_i = pn.cross("[I_STEM][Loc][Du]", "nos")     # vāri + [Loc][Du] -> vārinos

'''
Plural
'''

# Masc/Fem plural i-stem (e.g., agni / gati)
nom_pl_i = pn.cross("i[I_STEM][Nom][Pl]", "ayas")       # agni + [Nom][Pl] -> agnayas (i -> ayas)
voc_pl_i = pn.cross("i[I_STEM][Voc][Pl]", "ayas")       # agni + [Voc][Pl] -> agnayas

acc_pl_i = pn.cross("i[I_STEM][Acc][Pl]", "īn")         # agni + [Acc][Pl] -> agnīn (i -> īn)

ins_pl_i = pn.cross("[I_STEM][Ins][Pl]", "bhis")        # agni + [Ins][Pl] -> agnibhis (appends)
dat_pl_i = pn.cross("[I_STEM][Dat][Pl]", "bhyas")       # agni + [Dat][Pl] -> agnibhyas
abl_pl_i = pn.cross("[I_STEM][Abl][Pl]", "bhyas")       # agni + [Abl][Pl] -> agnibhyas

gen_pl_i = pn.cross("i[I_STEM][Gen][Pl]", "īnām")       # agni + [Gen][Pl] -> agnīnām (i -> īnām)
loc_pl_i = pn.cross("[I_STEM][Loc][Pl]", "su")          # agni + [Loc][Pl] -> agniṣu (appends ṣu)

# Neuter plural i-stem (e.g., vāri)
nom_pl_neut_i = pn.cross("i[I_STEM][Nom][Pl]", "īni")    # vāri + [Nom][Pl] -> vārīni (i -> īni)
acc_pl_neut_i = pn.cross("i[I_STEM][Acc][Pl]", "īni")    # vāri + [Acc][Pl] -> vārīni
voc_pl_neut_i = pn.cross("i[I_STEM][Voc][Pl]", "īni")    # vāri + [Voc][Pl] -> vārīni

ins_pl_neut_i = pn.cross("[I_STEM][Ins][Pl]", "bhis")    # vāri + [Ins][Pl] -> vāribhis
dat_pl_neut_i = pn.cross("[I_STEM][Dat][Pl]", "bhyas")   # vāri + [Dat][Pl] -> vāribhyas
abl_pl_neut_i = pn.cross("[I_STEM][Abl][Pl]", "bhyas")   # vāri + [Abl][Pl] -> vāribhyas

gen_pl_neut_i = pn.cross("i[I_STEM][Gen][Pl]", "īnām")   # vāri + [Gen][Pl] -> vārīnām (i -> īnām)
loc_pl_neut_i = pn.cross("[I_STEM][Loc][Pl]", "su")      # vāri + [Loc][Pl] -> vāriṣu

'''
Feminine Ī-STEM (e.g., devī)
'''
# Singular
nom_sg_f_ii = pn.cross("ī[I_bar_STEM][Fem][Nom][Sg]", "ī")       # devī -> devī (Drops the 's'!)
acc_sg_f_ii = pn.cross("ī[I_bar_STEM][Fem][Acc][Sg]", "īm")      # devī -> devīm
ins_sg_f_ii = pn.cross("ī[I_bar_STEM][Fem][Ins][Sg]", "yā")      # devī -> devyā (ī -> yā)
dat_sg_f_ii = pn.cross("ī[I_bar_STEM][Fem][Dat][Sg]", "yai")     # devī -> devyai
abl_sg_f_ii = pn.cross("ī[I_bar_STEM][Fem][Abl][Sg]", "yās")     # devī -> devyās
gen_sg_f_ii = pn.cross("ī[I_bar_STEM][Fem][Gen][Sg]", "yās")     # devī -> devyās
loc_sg_f_ii = pn.cross("ī[I_bar_STEM][Fem][Loc][Sg]", "yām")     # devī -> devyām
voc_sg_f_ii = pn.cross("ī[I_bar_STEM][Fem][Voc][Sg]", "i")       # devī -> devi (Shortens to i!)

# Dual
nom_du_f_ii = pn.cross("ī[I_bar_STEM][Fem][Nom][Du]", "yau")     # devī -> devyau
acc_du_f_ii = pn.cross("ī[I_bar_STEM][Fem][Acc][Du]", "yau")     
voc_du_f_ii = pn.cross("ī[I_bar_STEM][Fem][Voc][Du]", "yau")     

ins_du_f_ii = pn.cross("[I_bar_STEM][Fem][Ins][Du]", "bhyām")    # devī + bhyām
dat_du_f_ii = pn.cross("[I_bar_STEM][Fem][Dat][Du]", "bhyām")    
abl_du_f_ii = pn.cross("[I_bar_STEM][Fem][Abl][Du]", "bhyām")    

gen_du_f_ii = pn.cross("ī[I_bar_STEM][Fem][Gen][Du]", "yos")     # devī -> devyos
loc_du_f_ii = pn.cross("ī[I_bar_STEM][Fem][Loc][Du]", "yos")     

# Plural
nom_pl_f_ii = pn.cross("ī[I_bar_STEM][Fem][Nom][Pl]", "yas")     # devī -> devyas
acc_pl_f_ii = pn.cross("ī[I_bar_STEM][Fem][Acc][Pl]", "īs")      # devī -> devīs
voc_pl_f_ii = pn.cross("ī[I_bar_STEM][Fem][Voc][Pl]", "yas")     

ins_pl_f_ii = pn.cross("[I_bar_STEM][Fem][Ins][Pl]", "bhis")     # devī + bhis
dat_pl_f_ii = pn.cross("[I_bar_STEM][Fem][Dat][Pl]", "bhyas")    
abl_pl_f_ii = pn.cross("[I_bar_STEM][Fem][Abl][Pl]", "bhyas")    

gen_pl_f_ii = pn.cross("ī[I_bar_STEM][Fem][Gen][Pl]", "īnām")    # devī -> devīnām
loc_pl_f_ii = pn.cross("[I_bar_STEM][Fem][Loc][Pl]", "su")       # devī + su (Strict underlying)

# Union Compiler
fem_ii_paradigm = pn.union(
    nom_sg_f_ii, acc_sg_f_ii, ins_sg_f_ii, dat_sg_f_ii, abl_sg_f_ii, gen_sg_f_ii, loc_sg_f_ii, voc_sg_f_ii,
    nom_du_f_ii, acc_du_f_ii, voc_du_f_ii, ins_du_f_ii, dat_du_f_ii, abl_du_f_ii, gen_du_f_ii, loc_du_f_ii,
    nom_pl_f_ii, acc_pl_f_ii, voc_pl_f_ii, ins_pl_f_ii, dat_pl_f_ii, abl_pl_f_ii, gen_pl_f_ii, loc_pl_f_ii
).optimize()
