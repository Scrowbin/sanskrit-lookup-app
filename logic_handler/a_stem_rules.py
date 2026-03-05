import pynini as pn
from rules import *

'''
Singular
'''
nom_sg = pn.cross("[Nom][Sg]", "ḥ")      # deva + [Nom][Sg] -> devaḥ
acc_sg = pn.cross("[Acc][Sg]", "m")      # deva + [Acc][Sg] -> devam
ins_sg = pn.cross("a[Ins][Sg]", "ena")   # deva + [Ins][Sg] -> devena 
dat_sg = pn.cross("a[Dat][Sg]", "āya")   # deva + [Dat][Sg] -> devāya
abl_sg = pn.cross("a[Abl][Sg]", "āt")    # deva + [Abl][Sg] -> devāt
gen_sg = pn.cross("[Gen][Sg]", "sya")    # deva + [Gen][Sg] -> devasya
loc_sg = pn.cross("a[Loc][Sg]", "e")     # deva + [Loc][Sg] -> deve
voc_sg = pn.cross("[Voc][Sg]", "")       # deva + [Voc][Sg] -> deva (no change)

a_stem_masc_singular = pn.union(
    nom_sg, 
    acc_sg, 
    ins_sg, 
    dat_sg, 
    abl_sg, 
    gen_sg, 
    loc_sg, 
    voc_sg
).optimize()

a_stem_singular_declension = pn.cdrewrite(
    a_stem_masc_singular,
    "",  # Left context (none required)
    "",  # Right context (none required)
    ALPHA
)

''' Dual '''
# Nomiinative, Accusasive, Vocative all au ending
nom_du = pn.cross("a[Nom][Du]", "au")      # deva + [Nom][Du] -> devau
acc_du = pn.cross("a[Acc][Du]", "au")      # deva + [Acc][Du] -> devau
voc_du = pn.cross("a[Voc][Du]", "au")      # deva + [Voc][Du] -> devau

# Instrumental, Dative, and Ablative all share the '-ābhyām' ending
ins_du = pn.cross("a[Ins][Du]", "ābhyām")  # deva + [Ins][Du] -> devābhyām
dat_du = pn.cross("a[Dat][Du]", "ābhyām")  # deva + [Dat][Du] -> devābhyām
abl_du = pn.cross("a[Abl][Du]", "ābhyām")  # deva + [Abl][Du] -> devābhyām

# Genitive and Locative both share the '-ayoḥ' ending
gen_du = pn.cross("a[Gen][Du]", "ayoḥ")    # deva + [Gen][Du] -> devayoḥ
loc_du = pn.cross("a[Loc][Du]", "ayoḥ")    # deva + [Loc][Du] -> devayoḥ
# There's no vocative for it lol

a_stem_masc_dual = pn.union(
    nom_du, 
    acc_du, 
    voc_du,
    ins_du, 
    dat_du, 
    abl_du,
    gen_du, 
    loc_du
).optimize()

a_stem_dual_declension = pn.cdrewrite(
    a_stem_masc_dual,
    "",
    "",
    ALPHA
)

'''Plural'''
nom_pl = pn.cross("a[Nom][Pl]", "āḥ")      # deva + [Nom][Pl] -> devāḥ 
acc_pl = pn.cross("a[Acc][Pl]", "ān")      # deva + [Acc][Pl] -> devān
ins_pl = pn.cross("a[Ins][Pl]", "aiḥ")     # deva + [Ins][Pl] -> devaiḥ 

# Dative and Ablative share the '-ebhyaḥ' ending
dat_pl = pn.cross("a[Dat][Pl]", "ebhyaḥ")  # deva + [Dat][Pl] -> devebhyaḥ 
abl_pl = pn.cross("a[Abl][Pl]", "ebhyaḥ")  # deva + [Abl][Pl] -> devebhyaḥ

gen_pl = pn.cross("a[Gen][Pl]", "ānām")    # deva + [Gen][Pl] -> devānām
loc_pl = pn.cross("a[Loc][Pl]", "eṣu")     # deva + [Loc][Pl] -> deveṣu 

# Vocative shares the '-āḥ' ending with Nominative
voc_pl = pn.cross("a[Voc][Pl]", "āḥ")      # deva + [Voc][Pl] -> devāḥ 

a_stem_masc_plural = pn.union(
    nom_pl, 
    acc_pl, 
    ins_pl, 
    dat_pl, 
    abl_pl, 
    gen_pl, 
    loc_pl, 
    voc_pl
).optimize()

a_stem_plural_declension = pn.cdrewrite(
    a_stem_masc_plural,
    "", 
    "", 
    ALPHA
)
complete_a_stem_masc = pn.union(
    a_stem_masc_singular,
    a_stem_masc_dual,
    a_stem_masc_plural
).optimize()

apply_a_stem_declension = pn.cdrewrite(
    complete_a_stem_masc,
    "", 
    "", 
    ALPHA
)
