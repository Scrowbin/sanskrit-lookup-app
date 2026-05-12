import pynini as pn

mf_blind = pn.cross(pn.union("[Masc]", "[Fem]"), "")
"""
e-stem (e.g., se)
"""
# Singular
nom_sg_e = pn.cross("e[E_STEM]", "es") + mf_blind + pn.cross("[Nom][Sg]", "")
acc_sg_e = pn.cross("e[E_STEM]", "ayam") + mf_blind + pn.cross("[Acc][Sg]", "")
ins_sg_e = pn.cross("e[E_STEM]", "ayā") + mf_blind + pn.cross("[Ins][Sg]", "")
dat_sg_e = pn.cross("e[E_STEM]", "aye") + mf_blind + pn.cross("[Dat][Sg]", "")
abl_sg_e = pn.cross("e[E_STEM]", "es") + mf_blind + pn.cross("[Abl][Sg]", "")
gen_sg_e = pn.cross("e[E_STEM]", "es") + mf_blind + pn.cross("[Gen][Sg]", "")
loc_sg_e = pn.cross("e[E_STEM]", "ayi") + mf_blind + pn.cross("[Loc][Sg]", "")
voc_sg_e = (
    pn.cross("e[E_STEM]", "e") + mf_blind + pn.cross("[Voc][Sg]", "")
)  # Note: voc sg is usually just the stem 'e'

# Dual
nom_du_e = pn.cross("e[E_STEM]", "ayau") + mf_blind + pn.cross("[Nom][Du]", "")
acc_du_e = pn.cross("e[E_STEM]", "ayau") + mf_blind + pn.cross("[Acc][Du]", "")
voc_du_e = pn.cross("e[E_STEM]", "ayau") + mf_blind + pn.cross("[Voc][Du]", "")

ins_du_e = pn.cross("e[E_STEM]", "e") + mf_blind + pn.cross("[Ins][Du]", "bhyām")
dat_du_e = pn.cross("e[E_STEM]", "e") + mf_blind + pn.cross("[Dat][Du]", "bhyām")
abl_du_e = pn.cross("e[E_STEM]", "e") + mf_blind + pn.cross("[Abl][Du]", "bhyām")

gen_du_e = pn.cross("e[E_STEM]", "ayos") + mf_blind + pn.cross("[Gen][Du]", "")
loc_du_e = pn.cross("e[E_STEM]", "ayos") + mf_blind + pn.cross("[Loc][Du]", "")

# Plural
nom_pl_e = pn.cross("e[E_STEM]", "ayas") + mf_blind + pn.cross("[Nom][Pl]", "")
acc_pl_e = pn.cross("e[E_STEM]", "ayas") + mf_blind + pn.cross("[Acc][Pl]", "")
voc_pl_e = pn.cross("e[E_STEM]", "ayas") + mf_blind + pn.cross("[Voc][Pl]", "")

ins_pl_e = pn.cross("e[E_STEM]", "e") + mf_blind + pn.cross("[Ins][Pl]", "bhis")
dat_pl_e = pn.cross("e[E_STEM]", "e") + mf_blind + pn.cross("[Dat][Pl]", "bhyas")
abl_pl_e = pn.cross("e[E_STEM]", "e") + mf_blind + pn.cross("[Abl][Pl]", "bhyas")

gen_pl_e = pn.cross("e[E_STEM]", "ayām") + mf_blind + pn.cross("[Gen][Pl]", "")
loc_pl_e = pn.cross("e[E_STEM]", "e") + mf_blind + pn.cross("[Loc][Pl]", "su")


"""
o-stem (e.g., go)
"""
# Singular
nom_sg_o = (
    pn.cross("o[O_STEM]", "aus") + mf_blind + pn.cross("[Nom][Sg]", "")
)  # go -> gaus
acc_sg_o = (
    pn.cross("o[O_STEM]", "ām") + mf_blind + pn.cross("[Acc][Sg]", "")
)  # go -> gām
ins_sg_o = (
    pn.cross("o[O_STEM]", "avā") + mf_blind + pn.cross("[Ins][Sg]", "")
)  # go -> gavā
dat_sg_o = (
    pn.cross("o[O_STEM]", "ave") + mf_blind + pn.cross("[Dat][Sg]", "")
)  # go -> gave
abl_sg_o = (
    pn.cross("o[O_STEM]", "os") + mf_blind + pn.cross("[Abl][Sg]", "")
)  # go -> gos
gen_sg_o = (
    pn.cross("o[O_STEM]", "os") + mf_blind + pn.cross("[Gen][Sg]", "")
)  # go -> gos
loc_sg_o = (
    pn.cross("o[O_STEM]", "avi") + mf_blind + pn.cross("[Loc][Sg]", "")
)  # go -> gavi
voc_sg_o = (
    pn.cross("o[O_STEM]", "aus") + mf_blind + pn.cross("[Voc][Sg]", "")
)  # go -> gaus

# Dual
nom_du_o = (
    pn.cross("o[O_STEM]", "āvau") + mf_blind + pn.cross("[Nom][Du]", "")
)  # go -> gāvau
acc_du_o = pn.cross("o[O_STEM]", "āvau") + mf_blind + pn.cross("[Acc][Du]", "")
voc_du_o = pn.cross("o[O_STEM]", "āvau") + mf_blind + pn.cross("[Voc][Du]", "")

ins_du_o = (
    pn.cross("o[O_STEM]", "o") + mf_blind + pn.cross("[Ins][Du]", "bhyām")
)  # go + bhyām
dat_du_o = pn.cross("o[O_STEM]", "o") + mf_blind + pn.cross("[Dat][Du]", "bhyām")
abl_du_o = pn.cross("o[O_STEM]", "o") + mf_blind + pn.cross("[Abl][Du]", "bhyām")

gen_du_o = (
    pn.cross("o[O_STEM]", "avos") + mf_blind + pn.cross("[Gen][Du]", "")
)  # go -> gavos
loc_du_o = pn.cross("o[O_STEM]", "avos") + mf_blind + pn.cross("[Loc][Du]", "")

# Plural
nom_pl_o = (
    pn.cross("o[O_STEM]", "āvas") + mf_blind + pn.cross("[Nom][Pl]", "")
)  # go -> gāvas
acc_pl_o = (
    pn.cross("o[O_STEM]", "ās") + mf_blind + pn.cross("[Acc][Pl]", "")
)  # go -> gās
voc_pl_o = pn.cross("o[O_STEM]", "āvas") + mf_blind + pn.cross("[Voc][Pl]", "")

ins_pl_o = (
    pn.cross("o[O_STEM]", "o") + mf_blind + pn.cross("[Ins][Pl]", "bhis")
)  # go + bhis
dat_pl_o = pn.cross("o[O_STEM]", "o") + mf_blind + pn.cross("[Dat][Pl]", "bhyas")
abl_pl_o = pn.cross("o[O_STEM]", "o") + mf_blind + pn.cross("[Abl][Pl]", "bhyas")

gen_pl_o = (
    pn.cross("o[O_STEM]", "avām") + mf_blind + pn.cross("[Gen][Pl]", "")
)  # go -> gavām
loc_pl_o = (
    pn.cross("o[O_STEM]", "o") + mf_blind + pn.cross("[Loc][Pl]", "su")
)  # go + su


"""
au-stem (e.g., nau)
"""
# Singular
nom_sg_au = (
    pn.cross("au[AU_STEM]", "aus") + mf_blind + pn.cross("[Nom][Sg]", "")
)  # nau -> naus
acc_sg_au = (
    pn.cross("au[AU_STEM]", "āvam") + mf_blind + pn.cross("[Acc][Sg]", "")
)  # nau -> nāvam
ins_sg_au = (
    pn.cross("au[AU_STEM]", "āvā") + mf_blind + pn.cross("[Ins][Sg]", "")
)  # nau -> nāvā
dat_sg_au = (
    pn.cross("au[AU_STEM]", "āve") + mf_blind + pn.cross("[Dat][Sg]", "")
)  # nau -> nāve
abl_sg_au = (
    pn.cross("au[AU_STEM]", "āvas") + mf_blind + pn.cross("[Abl][Sg]", "")
)  # nau -> nāvas
gen_sg_au = (
    pn.cross("au[AU_STEM]", "āvas") + mf_blind + pn.cross("[Gen][Sg]", "")
)  # nau -> nāvas
loc_sg_au = (
    pn.cross("au[AU_STEM]", "āvi") + mf_blind + pn.cross("[Loc][Sg]", "")
)  # nau -> nāvi
voc_sg_au = (
    pn.cross("au[AU_STEM]", "aus") + mf_blind + pn.cross("[Voc][Sg]", "")
)  # nau -> naus

# Dual
nom_du_au = (
    pn.cross("au[AU_STEM]", "āvau") + mf_blind + pn.cross("[Nom][Du]", "")
)  # nau -> nāvau
acc_du_au = pn.cross("au[AU_STEM]", "āvau") + mf_blind + pn.cross("[Acc][Du]", "")
voc_du_au = pn.cross("au[AU_STEM]", "āvau") + mf_blind + pn.cross("[Voc][Du]", "")

ins_du_au = (
    pn.cross("au[AU_STEM]", "au") + mf_blind + pn.cross("[Ins][Du]", "bhyām")
)  # nau + bhyām
dat_du_au = pn.cross("au[AU_STEM]", "au") + mf_blind + pn.cross("[Dat][Du]", "bhyām")
abl_du_au = pn.cross("au[AU_STEM]", "au") + mf_blind + pn.cross("[Abl][Du]", "bhyām")

gen_du_au = (
    pn.cross("au[AU_STEM]", "āvos") + mf_blind + pn.cross("[Gen][Du]", "")
)  # nau -> nāvos
loc_du_au = pn.cross("au[AU_STEM]", "āvos") + mf_blind + pn.cross("[Loc][Du]", "")

# Plural
nom_pl_au = (
    pn.cross("au[AU_STEM]", "āvas") + mf_blind + pn.cross("[Nom][Pl]", "")
)  # nau -> nāvas
acc_pl_au = (
    pn.cross("au[AU_STEM]", "āvas") + mf_blind + pn.cross("[Acc][Pl]", "")
)  # nau -> nāvas
voc_pl_au = pn.cross("au[AU_STEM]", "āvas") + mf_blind + pn.cross("[Voc][Pl]", "")

ins_pl_au = (
    pn.cross("au[AU_STEM]", "au") + mf_blind + pn.cross("[Ins][Pl]", "bhis")
)  # nau + bhis
dat_pl_au = pn.cross("au[AU_STEM]", "au") + mf_blind + pn.cross("[Dat][Pl]", "bhyas")
abl_pl_au = pn.cross("au[AU_STEM]", "au") + mf_blind + pn.cross("[Abl][Pl]", "bhyas")

gen_pl_au = (
    pn.cross("au[AU_STEM]", "āvām") + mf_blind + pn.cross("[Gen][Pl]", "")
)  # nau -> nāvām
loc_pl_au = (
    pn.cross("au[AU_STEM]", "au") + mf_blind + pn.cross("[Loc][Pl]", "su")
)  # nau + su


"""
ai-stem (e.g., rai)
"""
# Singular
nom_sg_ai = pn.cross("ai[AI_STEM]", "ās") + mf_blind + pn.cross("[Nom][Sg]", "")
acc_sg_ai = pn.cross("ai[AI_STEM]", "āyam") + mf_blind + pn.cross("[Acc][Sg]", "")
ins_sg_ai = pn.cross("ai[AI_STEM]", "āyā") + mf_blind + pn.cross("[Ins][Sg]", "")
dat_sg_ai = pn.cross("ai[AI_STEM]", "āye") + mf_blind + pn.cross("[Dat][Sg]", "")
abl_sg_ai = pn.cross("ai[AI_STEM]", "āyas") + mf_blind + pn.cross("[Abl][Sg]", "")
gen_sg_ai = pn.cross("ai[AI_STEM]", "āyas") + mf_blind + pn.cross("[Gen][Sg]", "")
loc_sg_ai = pn.cross("ai[AI_STEM]", "āyi") + mf_blind + pn.cross("[Loc][Sg]", "")
voc_sg_ai = pn.cross("ai[AI_STEM]", "ās") + mf_blind + pn.cross("[Voc][Sg]", "")

# Dual
nom_du_ai = pn.cross("ai[AI_STEM]", "āyau") + mf_blind + pn.cross("[Nom][Du]", "")
acc_du_ai = pn.cross("ai[AI_STEM]", "āyau") + mf_blind + pn.cross("[Acc][Du]", "")
voc_du_ai = pn.cross("ai[AI_STEM]", "āyau") + mf_blind + pn.cross("[Voc][Du]", "")

# Before consonant endings, ai -> ā (e.g., rai + bhyām -> rābhyām)
ins_du_ai = pn.cross("ai[AI_STEM]", "ā") + mf_blind + pn.cross("[Ins][Du]", "bhyām")
dat_du_ai = pn.cross("ai[AI_STEM]", "ā") + mf_blind + pn.cross("[Dat][Du]", "bhyām")
abl_du_ai = pn.cross("ai[AI_STEM]", "ā") + mf_blind + pn.cross("[Abl][Du]", "bhyām")

gen_du_ai = pn.cross("ai[AI_STEM]", "āyos") + mf_blind + pn.cross("[Gen][Du]", "")
loc_du_ai = pn.cross("ai[AI_STEM]", "āyos") + mf_blind + pn.cross("[Loc][Du]", "")

# Plural
nom_pl_ai = pn.cross("ai[AI_STEM]", "āyas") + mf_blind + pn.cross("[Nom][Pl]", "")
acc_pl_ai = pn.cross("ai[AI_STEM]", "āyas") + mf_blind + pn.cross("[Acc][Pl]", "")
voc_pl_ai = pn.cross("ai[AI_STEM]", "āyas") + mf_blind + pn.cross("[Voc][Pl]", "")

# Before consonant endings, ai -> ā
ins_pl_ai = pn.cross("ai[AI_STEM]", "ā") + mf_blind + pn.cross("[Ins][Pl]", "bhis")
dat_pl_ai = pn.cross("ai[AI_STEM]", "ā") + mf_blind + pn.cross("[Dat][Pl]", "bhyas")
abl_pl_ai = pn.cross("ai[AI_STEM]", "ā") + mf_blind + pn.cross("[Abl][Pl]", "bhyas")

gen_pl_ai = pn.cross("ai[AI_STEM]", "āyām") + mf_blind + pn.cross("[Gen][Pl]", "")
loc_pl_ai = pn.cross("ai[AI_STEM]", "ā") + mf_blind + pn.cross("[Loc][Pl]", "su")


# 1. E-STEM CONSOLIDATION (e.g., se)
e_stem_paradigm = pn.union(
    nom_sg_e,
    acc_sg_e,
    ins_sg_e,
    dat_sg_e,
    abl_sg_e,
    gen_sg_e,
    loc_sg_e,
    voc_sg_e,
    nom_du_e,
    acc_du_e,
    voc_du_e,
    ins_du_e,
    dat_du_e,
    abl_du_e,
    gen_du_e,
    loc_du_e,
    nom_pl_e,
    acc_pl_e,
    voc_pl_e,
    ins_pl_e,
    dat_pl_e,
    abl_pl_e,
    gen_pl_e,
    loc_pl_e,
).optimize()

# 2. O-STEM CONSOLIDATION (e.g., go)
o_stem_paradigm = pn.union(
    nom_sg_o,
    acc_sg_o,
    ins_sg_o,
    dat_sg_o,
    abl_sg_o,
    gen_sg_o,
    loc_sg_o,
    voc_sg_o,
    nom_du_o,
    acc_du_o,
    voc_du_o,
    ins_du_o,
    dat_du_o,
    abl_du_o,
    gen_du_o,
    loc_du_o,
    nom_pl_o,
    acc_pl_o,
    voc_pl_o,
    ins_pl_o,
    dat_pl_o,
    abl_pl_o,
    gen_pl_o,
    loc_pl_o,
).optimize()

# 3. AU-STEM CONSOLIDATION (e.g., nau)
au_stem_paradigm = pn.union(
    nom_sg_au,
    acc_sg_au,
    ins_sg_au,
    dat_sg_au,
    abl_sg_au,
    gen_sg_au,
    loc_sg_au,
    voc_sg_au,
    nom_du_au,
    acc_du_au,
    voc_du_au,
    ins_du_au,
    dat_du_au,
    abl_du_au,
    gen_du_au,
    loc_du_au,
    nom_pl_au,
    acc_pl_au,
    voc_pl_au,
    ins_pl_au,
    dat_pl_au,
    abl_pl_au,
    gen_pl_au,
    loc_pl_au,
).optimize()

# 4. AI-STEM CONSOLIDATION (e.g., rai)
ai_stem_paradigm = pn.union(
    nom_sg_ai,
    acc_sg_ai,
    ins_sg_ai,
    dat_sg_ai,
    abl_sg_ai,
    gen_sg_ai,
    loc_sg_ai,
    voc_sg_ai,
    nom_du_ai,
    acc_du_ai,
    voc_du_ai,
    ins_du_ai,
    dat_du_ai,
    abl_du_ai,
    gen_du_ai,
    loc_du_ai,
    nom_pl_ai,
    acc_pl_ai,
    voc_pl_ai,
    ins_pl_ai,
    dat_pl_ai,
    abl_pl_ai,
    gen_pl_ai,
    loc_pl_ai,
).optimize()

# 5. MASTER DIPHTHONG UNION
diphthong_stems_paradigm = pn.union(
    e_stem_paradigm, o_stem_paradigm, au_stem_paradigm, ai_stem_paradigm
).optimize()
