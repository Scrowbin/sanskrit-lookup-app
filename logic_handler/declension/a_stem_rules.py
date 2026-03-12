import pynini as pn
from rules import *
'''
Singular
'''
# Masculine
nom_sg = pn.cross("a[A_STEM][Masc][Nom][Sg]", "as")      
acc_sg = pn.cross("a[A_STEM][Masc][Acc][Sg]", "am")   
ins_sg = pn.cross("a[A_STEM][Masc][Ins][Sg]", "ena") 
dat_sg = pn.cross("a[A_STEM][Masc][Dat][Sg]", "āya")
abl_sg = pn.cross("a[A_STEM][Masc][Abl][Sg]", "āt")
gen_sg = pn.cross("a[A_STEM][Masc][Gen][Sg]", "asya")
loc_sg = pn.cross("a[A_STEM][Masc][Loc][Sg]", "e")       
voc_sg = pn.cross("a[A_STEM][Masc][Voc][Sg]", "a")      

# Feminine
nom_sg_f = pn.cross("ā[Ā_STEM][Fem][Nom][Sg]", "ā")      
acc_sg_f = pn.cross("ā[Ā_STEM][Fem][Acc][Sg]", "ām")    
ins_sg_f = pn.cross("ā[Ā_STEM][Fem][Ins][Sg]", "ayā")  
dat_sg_f = pn.cross("ā[Ā_STEM][Fem][Dat][Sg]", "āyai")
abl_sg_f = pn.cross("ā[Ā_STEM][Fem][Abl][Sg]", "āyās")
gen_sg_f = pn.cross("ā[Ā_STEM][Fem][Gen][Sg]", "āyās")
loc_sg_f = pn.cross("ā[Ā_STEM][Fem][Loc][Sg]", "āyām")
voc_sg_f = pn.cross("ā[Ā_STEM][Fem][Voc][Sg]", "e")  

# Neuter
nom_sg_n = pn.cross("a[A_STEM][Neut][Nom][Sg]", "am")
acc_sg_n = pn.cross("a[A_STEM][Neut][Acc][Sg]", "am")
ins_sg_n = pn.cross("a[A_STEM][Neut][Ins][Sg]", "ena")
dat_sg_n = pn.cross("a[A_STEM][Neut][Dat][Sg]", "āya")
abl_sg_n = pn.cross("a[A_STEM][Neut][Abl][Sg]", "āt") 
gen_sg_n = pn.cross("a[A_STEM][Neut][Gen][Sg]", "asya")
loc_sg_n = pn.cross("a[A_STEM][Neut][Loc][Sg]", "e")
voc_sg_n = pn.cross("a[A_STEM][Neut][Voc][Sg]", "a")

'''
Dual
'''
# Masculine
nom_du = pn.cross("a[A_STEM][Masc][Nom][Du]", "au")     
acc_du = pn.cross("a[A_STEM][Masc][Acc][Du]", "au")   
ins_du = pn.cross("a[A_STEM][Masc][Ins][Du]", "ābhyām")  
dat_du = pn.cross("a[A_STEM][Masc][Dat][Du]", "ābhyām") 
abl_du = pn.cross("a[A_STEM][Masc][Abl][Du]", "ābhyām")
gen_du = pn.cross("a[A_STEM][Masc][Gen][Du]", "ayos") 
loc_du = pn.cross("a[A_STEM][Masc][Loc][Du]", "ayos")
voc_du = pn.cross("a[A_STEM][Masc][Voc][Du]", "au") 

# Feminine
nom_du_f = pn.cross("ā[Ā_STEM][Fem][Nom][Du]", "e")  
acc_du_f = pn.cross("ā[Ā_STEM][Fem][Acc][Du]", "e") 
ins_du_f = pn.cross("ā[Ā_STEM][Fem][Ins][Du]", "ābhyām")
dat_du_f = pn.cross("ā[Ā_STEM][Fem][Dat][Du]", "ābhyām")
abl_du_f = pn.cross("ā[Ā_STEM][Fem][Abl][Du]", "ābhyām")
gen_du_f = pn.cross("ā[Ā_STEM][Fem][Gen][Du]", "ayos")
loc_du_f = pn.cross("ā[Ā_STEM][Fem][Loc][Du]", "ayos")
voc_du_f = pn.cross("ā[Ā_STEM][Fem][Voc][Du]", "e")

# Neuter
nom_du_n = pn.cross("a[A_STEM][Neut][Nom][Du]", "e")
acc_du_n = pn.cross("a[A_STEM][Neut][Acc][Du]", "e")
ins_du_n = pn.cross("a[A_STEM][Neut][Ins][Du]", "ābhyām")
dat_du_n = pn.cross("a[A_STEM][Neut][Dat][Du]", "ābhyām")
abl_du_n = pn.cross("a[A_STEM][Neut][Abl][Du]", "ābhyām")
gen_du_n = pn.cross("a[A_STEM][Neut][Gen][Du]", "ayos")
loc_du_n = pn.cross("a[A_STEM][Neut][Loc][Du]", "ayos")
voc_du_n = pn.cross("a[A_STEM][Neut][Voc][Du]", "e") 

''' 
Plural
'''
# Masculine
nom_pl = pn.cross("a[A_STEM][Masc][Nom][Pl]", "ās")
acc_pl = pn.cross("a[A_STEM][Masc][Acc][Pl]", "ān")
ins_pl = pn.cross("a[A_STEM][Masc][Ins][Pl]", "ais")     
dat_pl = pn.cross("a[A_STEM][Masc][Dat][Pl]", "ebhyas") 
abl_pl = pn.cross("a[A_STEM][Masc][Abl][Pl]", "ebhyas")
gen_pl = pn.cross("a[A_STEM][Masc][Gen][Pl]", "ānām") 
loc_pl = pn.cross("a[A_STEM][Masc][Loc][Pl]", "esu") 
voc_pl = pn.cross("a[A_STEM][Masc][Voc][Pl]", "ās") 

# Feminine
nom_pl_f = pn.cross("ā[Ā_STEM][Fem][Nom][Pl]", "ās")
acc_pl_f = pn.cross("ā[Ā_STEM][Fem][Acc][Pl]", "ās")
ins_pl_f = pn.cross("ā[Ā_STEM][Fem][Ins][Pl]", "ābhis")
dat_pl_f = pn.cross("ā[Ā_STEM][Fem][Dat][Pl]", "ābhyas")
abl_pl_f = pn.cross("ā[Ā_STEM][Fem][Abl][Pl]", "ābhyas")
gen_pl_f = pn.cross("ā[Ā_STEM][Fem][Gen][Pl]", "ānām")
loc_pl_f = pn.cross("ā[Ā_STEM][Fem][Loc][Pl]", "āsu")
voc_pl_f = pn.cross("ā[Ā_STEM][Fem][Voc][Pl]", "ās")

# Neuter
nom_pl_n = pn.cross("a[A_STEM][Neut][Nom][Pl]", "āni")
acc_pl_n = pn.cross("a[A_STEM][Neut][Acc][Pl]", "āni")
ins_pl_n = pn.cross("a[A_STEM][Neut][Ins][Pl]", "ais")
dat_pl_n = pn.cross("a[A_STEM][Neut][Dat][Pl]", "ebhyas")
abl_pl_n = pn.cross("a[A_STEM][Neut][Abl][Pl]", "ebhyas")
gen_pl_n = pn.cross("a[A_STEM][Neut][Gen][Pl]", "ānām")
loc_pl_n = pn.cross("a[A_STEM][Neut][Loc][Pl]", "esu")
voc_pl_n = pn.cross("a[A_STEM][Neut][Voc][Pl]", "āni")

masc_a_stem_paradigm = pn.union(
    nom_sg, acc_sg, ins_sg, dat_sg, abl_sg, gen_sg, loc_sg, voc_sg,
    nom_du, acc_du, ins_du, dat_du, abl_du, gen_du, loc_du, voc_du,
    nom_pl, acc_pl, ins_pl, dat_pl, abl_pl, gen_pl, loc_pl, voc_pl
).optimize()

fem_a_stem_paradigm = pn.union(
    nom_sg_f, acc_sg_f, ins_sg_f, dat_sg_f, abl_sg_f, gen_sg_f, loc_sg_f, voc_sg_f,
    nom_du_f, acc_du_f, ins_du_f, dat_du_f, abl_du_f, gen_du_f, loc_du_f, voc_du_f,
    nom_pl_f, acc_pl_f, ins_pl_f, dat_pl_f, abl_pl_f, gen_pl_f, loc_pl_f, voc_pl_f
).optimize()

neut_a_stem_paradigm = pn.union(
    nom_sg_n, acc_sg_n, ins_sg_n, dat_sg_n, abl_sg_n, gen_sg_n, loc_sg_n, voc_sg_n,
    nom_du_n, acc_du_n, ins_du_n, dat_du_n, abl_du_n, gen_du_n, loc_du_n, voc_du_n,
    nom_pl_n, acc_pl_n, ins_pl_n, dat_pl_n, abl_pl_n, gen_pl_n, loc_pl_n, voc_pl_n
).optimize()
