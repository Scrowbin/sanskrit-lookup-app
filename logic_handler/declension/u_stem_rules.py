import pynini as pn
from rules import *

'''
Singular
'''
# Masculine (e.g., śátru)
nom_sg_m_u = pn.cross("[U_STEM][Masc][Nom][Sg]", "s")      # śátru + s -> śátrus
acc_sg_m_u = pn.cross("[U_STEM][Masc][Acc][Sg]", "m")      # śátru + m -> śátrum
ins_sg_m_u = pn.cross("[U_STEM][Masc][Ins][Sg]", "nā")     # śátru + nā -> śátrunā 
dat_sg_m_u = pn.cross("u[U_STEM][Masc][Dat][Sg]", "ave")   # śátru + e -> śátrave (u -> ave)
abl_sg_m_u = pn.cross("u[U_STEM][Masc][Abl][Sg]", "os")    # śátru + as -> śátros (u -> os)
gen_sg_m_u = pn.cross("u[U_STEM][Masc][Gen][Sg]", "os")    # śátru + as -> śátros
loc_sg_m_u = pn.cross("u[U_STEM][Masc][Loc][Sg]", "au")    # śátru + i -> śátrau (u -> au)
voc_sg_m_u = pn.cross("u[U_STEM][Masc][Voc][Sg]", "o")     # śátru + Ø -> śátro (u -> o)

# Feminine (e.g., dhenú)
nom_sg_f_u = pn.cross("[U_STEM][Fem][Nom][Sg]", "s")       # dhenú + s -> dhenús
acc_sg_f_u = pn.cross("[U_STEM][Fem][Acc][Sg]", "m")       # dhenú + m -> dhenúm
ins_sg_f_u = pn.cross("u[U_STEM][Fem][Ins][Sg]", "vā")     # dhenú + ā -> dhenvā (u -> vā)
dat_sg_f_u = pn.cross("u[U_STEM][Fem][Dat][Sg]", "ave")    # dhenú + e -> dhenáve

# Feminine has two valid forms for Abl/Gen (-os or -vās)
abl_sg_f_u = pn.union(pn.cross("u[U_STEM][Fem][Abl][Sg]", "os"), pn.cross("u[U_STEM][Fem][Abl][Sg]", "vās"))
gen_sg_f_u = pn.union(pn.cross("u[U_STEM][Fem][Gen][Sg]", "os"), pn.cross("u[U_STEM][Fem][Gen][Sg]", "vās"))

loc_sg_f_u = pn.cross("u[U_STEM][Fem][Loc][Sg]", "au")     # dhenú + i -> dhenaú
voc_sg_f_u = pn.cross("u[U_STEM][Fem][Voc][Sg]", "o")      # dhenú + Ø -> dhenó

'''
Dual
'''
# Masculine
nom_du_m_u = pn.cross("u[U_STEM][Masc][Nom][Du]", "ū")      # śátru + au -> śátrū (lengthens)
acc_du_m_u = pn.cross("u[U_STEM][Masc][Acc][Du]", "ū")      # śátru + au -> śátrū
ins_du_m_u = pn.cross("[U_STEM][Masc][Ins][Du]", "bhyām")   # śátru + bhyām -> śátrubhyām
dat_du_m_u = pn.cross("[U_STEM][Masc][Dat][Du]", "bhyām")   # śátru + bhyām -> śátrubhyām
abl_du_m_u = pn.cross("[U_STEM][Masc][Abl][Du]", "bhyām")   # śátru + bhyām -> śátrubhyām
gen_du_m_u = pn.cross("u[U_STEM][Masc][Gen][Du]", "vos")    # śátru + os -> śátrvos (u -> vos)
loc_du_m_u = pn.cross("u[U_STEM][Masc][Loc][Du]", "vos")    # śátru + os -> śátrvos
voc_du_m_u = pn.cross("u[U_STEM][Masc][Voc][Du]", "ū")      # śátru + au -> śátrū

# Feminine
nom_du_f_u = pn.cross("u[U_STEM][Fem][Nom][Du]", "ū")      
acc_du_f_u = pn.cross("u[U_STEM][Fem][Acc][Du]", "ū")      
ins_du_f_u = pn.cross("[U_STEM][Fem][Ins][Du]", "bhyām")   
dat_du_f_u = pn.cross("[U_STEM][Fem][Dat][Du]", "bhyām")   
abl_du_f_u = pn.cross("[U_STEM][Fem][Abl][Du]", "bhyām")   
gen_du_f_u = pn.cross("u[U_STEM][Fem][Gen][Du]", "vos")    
loc_du_f_u = pn.cross("u[U_STEM][Fem][Loc][Du]", "vos")    
voc_du_f_u = pn.cross("u[U_STEM][Fem][Voc][Du]", "ū")

'''
Plural
'''
# Masculine
nom_pl_m_u = pn.cross("u[U_STEM][Masc][Nom][Pl]", "avas")   # śátru + as -> śátravas (u -> avas)
acc_pl_m_u = pn.cross("u[U_STEM][Masc][Acc][Pl]", "ūn")     # śátru + as -> śátrūn (u -> ūn)
ins_pl_m_u = pn.cross("[U_STEM][Masc][Ins][Pl]", "bhis")    # śátru + bhis -> śátrubhis
dat_pl_m_u = pn.cross("[U_STEM][Masc][Dat][Pl]", "bhyas")   # śátru + bhyas -> śátrubhyas
abl_pl_m_u = pn.cross("[U_STEM][Masc][Abl][Pl]", "bhyas")   # śátru + bhyas -> śátrubhyas
gen_pl_m_u = pn.cross("u[U_STEM][Masc][Gen][Pl]", "ūnām")   # śátru + ām -> śátrūṇām (u -> ūnām)
loc_pl_m_u = pn.cross("[U_STEM][Masc][Loc][Pl]", "su")      # śátru + su -> śátruṣu 
voc_pl_m_u = pn.cross("u[U_STEM][Masc][Voc][Pl]", "avas")   # śátru + as -> śátravas

# Feminine
nom_pl_f_u = pn.cross("u[U_STEM][Fem][Nom][Pl]", "avas")    # dhenú + as -> dhenávas
acc_pl_f_u = pn.cross("u[U_STEM][Fem][Acc][Pl]", "ūs")      # dhenú + as -> dhenús (u -> ūs)
voc_pl_f_u = pn.cross("u[U_STEM][Fem][Voc][Pl]", "avas")
ins_pl_f_u = pn.cross("[U_STEM][Fem][Ins][Pl]", "bhis")     
dat_pl_f_u = pn.cross("[U_STEM][Fem][Dat][Pl]", "bhyas")    
abl_pl_f_u = pn.cross("[U_STEM][Fem][Abl][Pl]", "bhyas")    
gen_pl_f_u = pn.cross("u[U_STEM][Fem][Gen][Pl]", "ūnām")    
loc_pl_f_u = pn.cross("[U_STEM][Fem][Loc][Pl]", "su")       


'''
Feminine Ū-STEM (e.g., vadhū)
'''
# Singular
nom_sg_f_uu = pn.cross("ū[Ū_STEM][Fem][Nom][Sg]", "ūs")      # vadhū -> vadhūs (Keeps the 's'!)
acc_sg_f_uu = pn.cross("ū[Ū_STEM][Fem][Acc][Sg]", "ūm")      # vadhū -> vadhūm
ins_sg_f_uu = pn.cross("ū[Ū_STEM][Fem][Ins][Sg]", "vā")      # vadhū -> vadhvā (ū -> vā)
dat_sg_f_uu = pn.cross("ū[Ū_STEM][Fem][Dat][Sg]", "vai")     # vadhū -> vadhvai
abl_sg_f_uu = pn.cross("ū[Ū_STEM][Fem][Abl][Sg]", "vās")     # vadhū -> vadhvās
gen_sg_f_uu = pn.cross("ū[Ū_STEM][Fem][Gen][Sg]", "vās")     # vadhū -> vadhvās
loc_sg_f_uu = pn.cross("ū[Ū_STEM][Fem][Loc][Sg]", "vām")     # vadhū -> vadhvām
voc_sg_f_uu = pn.cross("ū[Ū_STEM][Fem][Voc][Sg]", "u")       # vadhū -> vadhu (Shortens to u!)

# Dual
nom_du_f_uu = pn.cross("ū[Ū_STEM][Fem][Nom][Du]", "vau")     # vadhū -> vadhvau
acc_du_f_uu = pn.cross("ū[Ū_STEM][Fem][Acc][Du]", "vau")     
voc_du_f_uu = pn.cross("ū[Ū_STEM][Fem][Voc][Du]", "vau")     

ins_du_f_uu = pn.cross("[Ū_STEM][Fem][Ins][Du]", "bhyām")    # vadhū + bhyām
dat_du_f_uu = pn.cross("[Ū_STEM][Fem][Dat][Du]", "bhyām")    
abl_du_f_uu = pn.cross("[Ū_STEM][Fem][Abl][Du]", "bhyām")    

gen_du_f_uu = pn.cross("ū[Ū_STEM][Fem][Gen][Du]", "vos")     # vadhū -> vadhvos
loc_du_f_uu = pn.cross("ū[Ū_STEM][Fem][Loc][Du]", "vos")     

# Plural
nom_pl_f_uu = pn.cross("ū[Ū_STEM][Fem][Nom][Pl]", "vas")     # vadhū -> vadhvas
acc_pl_f_uu = pn.cross("ū[Ū_STEM][Fem][Acc][Pl]", "ūs")      # vadhū -> vadhūs
voc_pl_f_uu = pn.cross("ū[Ū_STEM][Fem][Voc][Pl]", "vas")     

ins_pl_f_uu = pn.cross("[Ū_STEM][Fem][Ins][Pl]", "bhis")     # vadhū + bhis
dat_pl_f_uu = pn.cross("[Ū_STEM][Fem][Dat][Pl]", "bhyas")    
abl_pl_f_uu = pn.cross("[Ū_STEM][Fem][Abl][Pl]", "bhyas")    

gen_pl_f_uu = pn.cross("ū[Ū_STEM][Fem][Gen][Pl]", "ūnām")    # vadhū -> vadhūnām
loc_pl_f_uu = pn.cross("[Ū_STEM][Fem][Loc][Pl]", "su")       # vadhū + su (Strict underlying)

# Union Compiler
fem_uu_paradigm = pn.union(
    nom_sg_f_uu, acc_sg_f_uu, ins_sg_f_uu, dat_sg_f_uu, abl_sg_f_uu, gen_sg_f_uu, loc_sg_f_uu, voc_sg_f_uu,
    nom_du_f_uu, acc_du_f_uu, voc_du_f_uu, ins_du_f_uu, dat_du_f_uu, abl_du_f_uu, gen_du_f_uu, loc_du_f_uu,
    nom_pl_f_uu, acc_pl_f_uu, voc_pl_f_uu, ins_pl_f_uu, dat_pl_f_uu, abl_pl_f_uu, gen_pl_f_uu, loc_pl_f_uu
).optimize()
