import pynini as pn

# 1. Dynamic Matchers
mn_g = pn.union("[Masc]", "[Neut]")
ant_tags = pn.union("[ANT_STEM]", "[MANT_STEM]", "[VANT_STEM]")
m_v_tags = pn.union("[MANT_STEM]", "[VANT_STEM]")

# 2. Dynamic Bases (Fixed to cleanly purge tags during cross)
strong_m = pn.cross(ant_tags, "") + pn.cross("[Masc]", "")
strong_n = pn.cross(ant_tags, "") + pn.cross("[Neut]", "")

weak_m = pn.cross("nt", "t") + pn.cross(ant_tags, "") + pn.cross("[Masc]", "")
weak_n = pn.cross("nt", "t") + pn.cross(ant_tags, "") + pn.cross("[Neut]", "")
weak_blind = pn.cross("nt", "t") + pn.cross(ant_tags, "") + pn.cross(mn_g, "")
weak_blind_pada = pn.cross("nt", "t#") + pn.cross(ant_tags, "") + pn.cross(mn_g, "")


"""
3. MASCULINE SPECIFIC CASES
"""
# --- Nom/Voc Sg Exceptions (Fixed string mapping to prevent linear fragmentation) ---
nom_sg_ant = pn.cross("nt[ANT_STEM][Masc][Nom][Sg]", "n")  # bhāvant -> bhāvan
voc_sg_ant = pn.cross("nt[ANT_STEM][Masc][Voc][Sg]", "n")  # bhāvant -> bhāvan

# FIXED: Consumes 'ant' + tags sequentially so FST pointer doesn't decouple
nom_sg_mvant = pn.cross("ant[MANT_STEM][Masc][Nom][Sg]", "ān") | pn.cross(
    "ant[VANT_STEM][Masc][Nom][Sg]", "ān"
)
voc_sg_mvant = pn.cross("nt[MANT_STEM][Masc][Voc][Sg]", "n") | pn.cross(
    "nt[VANT_STEM][Masc][Voc][Sg]", "n"
)

# --- Strong Cases (Stem stays 'nt') --- Verified OK
acc_sg_m = strong_m + pn.cross("[Acc][Sg]", "am")  # bhāvant -> bhāvantam
nom_du_m = strong_m + pn.cross("[Nom][Du]", "au")
acc_du_m = strong_m + pn.cross("[Acc][Du]", "au")
voc_du_m = strong_m + pn.cross("[Voc][Du]", "au")
nom_pl_m = strong_m + pn.cross("[Nom][Pl]", "as")
voc_pl_m = strong_m + pn.cross("[Voc][Pl]", "as")

# --- Weak Cases (Stem drops 'n') --- Verified OK
acc_pl_m = weak_m + pn.cross("[Acc][Pl]", "as")  # bhāvant -> bhāvatas


"""
4. NEUTER SPECIFIC CASES
"""
# --- Weak Cases (Nom/Acc/Voc Sg & Du) --- Verified OK
nom_sg_n = weak_n + pn.cross("[Nom][Sg]", "")  # bhāvant -> bhāvat
acc_sg_n = weak_n + pn.cross("[Acc][Sg]", "")
voc_sg_n = weak_n + pn.cross("[Voc][Sg]", "")

# Note: Pure participles ([ANT_STEM]) can optionally form bhāvanti here,
# but bhāvantī is universally accepted for all three. Verified.
nom_du_n = strong_n + pn.cross("[Nom][Du]", "ī")  # bhāvant -> bhāvantī
acc_du_n = strong_n + pn.cross("[Acc][Du]", "ī")
voc_du_n = strong_n + pn.cross("[Voc][Du]", "ī")

# --- Strong Cases (Nom/Acc/Voc Pl) ---
# Penultimate vowel remains short for general mat/vat/ant adjectives (except mahat)
nom_pl_n = strong_n + pn.cross("[Nom][Pl]", "i")  # bhāvant -> bhāvanti
acc_pl_n = strong_n + pn.cross("[Acc][Pl]", "i")
voc_pl_n = strong_n + pn.cross("[Voc][Pl]", "i")


"""
5. GENDER-BLIND WEAK CASES (Ins, Dat, Abl, Gen, Loc)
"""
# Verified perfectly. Your downstream Sandhi engine (which you mentioned keeping unapplied
# for now) will correctly transform 'tbhyām' -> 'dbhyām' and 'tbhis' -> 'dbhis' later.
ins_sg = weak_blind + pn.cross("[Ins][Sg]", "ā")  # bhāvant -> bhāvatā
dat_sg = weak_blind + pn.cross("[Dat][Sg]", "e")
abl_sg = weak_blind + pn.cross("[Abl][Sg]", "as")
gen_sg = weak_blind + pn.cross("[Gen][Sg]", "as")
loc_sg = weak_blind + pn.cross("[Loc][Sg]", "i")

ins_du = weak_blind_pada + pn.cross("[Ins][Du]", "bhyām")  # bhāvant -> bhāvat#bhyām (-> bhāvadbhyām)
dat_du = weak_blind_pada + pn.cross("[Dat][Du]", "bhyām")
abl_du = weak_blind_pada + pn.cross("[Abl][Du]", "bhyām")
gen_du = weak_blind + pn.cross("[Gen][Du]", "os")
loc_du = weak_blind + pn.cross("[Loc][Du]", "os")

ins_pl = weak_blind_pada + pn.cross("[Ins][Pl]", "bhis")  # bhāvant -> bhāvat#bhis (-> bhāvadbhiḥ)
dat_pl = weak_blind_pada + pn.cross("[Dat][Pl]", "bhyas")
abl_pl = weak_blind_pada + pn.cross("[Abl][Pl]", "bhyas")
gen_pl = weak_blind + pn.cross("[Gen][Pl]", "ām")
loc_pl = weak_blind_pada + pn.cross("[Loc][Pl]", "su")  # bhāvant -> bhāvat#su (-> bhāvatsu)

"""
6. FEMININE SPECIFIC CASES (Nadī Declension)
"""
# --- Dynamic Feminine Bases ---
# Participles ([ANT_STEM]) keep the 'n' for thematic roots -> nt + ī
f_strong_base = pn.cross("[ANT_STEM]", "") + pn.cross("[Fem]", "")

# Possessives ([MANT_STEM], [VANT_STEM]) drop the 'n' -> t + ī
# (Note: If you add athematic participles later, add them to this weak base)
f_weak_base = pn.cross("nt", "t") + pn.cross(m_v_tags, "") + pn.cross("[Fem]", "")

f_base = pn.union(f_strong_base, f_weak_base)

# --- Nominative / Accusative / Vocative ---
nom_sg_f = f_base + pn.cross(
    "[Nom][Sg]", "ī"
)  # bhāvant -> bhāvantī / bhagavat -> bhagavatī
acc_sg_f = f_base + pn.cross("[Acc][Sg]", "īm")
voc_sg_f = f_base + pn.cross("[Voc][Sg]", "i")

nom_du_f = f_base + pn.cross("[Nom][Du]", "yau")
acc_du_f = f_base + pn.cross("[Acc][Du]", "yau")
voc_du_f = f_base + pn.cross("[Voc][Du]", "yau")

nom_pl_f = f_base + pn.cross("[Nom][Pl]", "yas")
acc_pl_f = f_base + pn.cross("[Acc][Pl]", "īs")  # Acc Pl uses īs, not yas!
voc_pl_f = f_base + pn.cross("[Voc][Pl]", "yas")

# --- Oblique Cases (yā, yai, yās, yām) ---
ins_sg_f = f_base + pn.cross("[Ins][Sg]", "yā")
dat_sg_f = f_base + pn.cross("[Dat][Sg]", "yai")
abl_sg_f = f_base + pn.cross("[Abl][Sg]", "yās")
gen_sg_f = f_base + pn.cross("[Gen][Sg]", "yās")
loc_sg_f = f_base + pn.cross("[Loc][Sg]", "yām")

ins_du_f = f_base + pn.cross("[Ins][Du]", "ībhyām")
dat_du_f = f_base + pn.cross("[Dat][Du]", "ībhyām")
abl_du_f = f_base + pn.cross("[Abl][Du]", "ībhyām")
gen_du_f = f_base + pn.cross("[Gen][Du]", "yos")
loc_du_f = f_base + pn.cross("[Loc][Du]", "yos")

ins_pl_f = f_base + pn.cross("[Ins][Pl]", "ībhis")
dat_pl_f = f_base + pn.cross("[Dat][Pl]", "ībhyas")
abl_pl_f = f_base + pn.cross("[Abl][Pl]", "ībhyas")
gen_pl_f = f_base + pn.cross("[Gen][Pl]", "īnām")
loc_pl_f = f_base + pn.cross("[Loc][Pl]", "īṣu")  # Retroflex ṣ triggered by ī


# Compile the Feminine Paradigm
ant_fem_paradigm = pn.union(
    nom_sg_f,
    acc_sg_f,
    voc_sg_f,
    nom_du_f,
    acc_du_f,
    voc_du_f,
    nom_pl_f,
    acc_pl_f,
    voc_pl_f,
    ins_sg_f,
    dat_sg_f,
    abl_sg_f,
    gen_sg_f,
    loc_sg_f,
    ins_du_f,
    dat_du_f,
    abl_du_f,
    gen_du_f,
    loc_du_f,
    ins_pl_f,
    dat_pl_f,
    abl_pl_f,
    gen_pl_f,
    loc_pl_f,
).optimize()

ant_masc_paradigm = pn.union(
    nom_sg_ant,
    nom_sg_mvant,
    voc_sg_ant,
    voc_sg_mvant,
    acc_sg_m,
    nom_du_m,
    acc_du_m,
    voc_du_m,
    nom_pl_m,
    voc_pl_m,
    acc_pl_m,
    ins_sg,
    dat_sg,
    abl_sg,
    gen_sg,
    loc_sg,
    ins_du,
    dat_du,
    abl_du,
    gen_du,
    loc_du,
    ins_pl,
    dat_pl,
    abl_pl,
    gen_pl,
    loc_pl,
).optimize()

ant_neut_paradigm = pn.union(
    nom_sg_n,
    acc_sg_n,
    voc_sg_n,
    nom_du_n,
    acc_du_n,
    voc_du_n,
    nom_pl_n,
    acc_pl_n,
    voc_pl_n,
    ins_sg,
    dat_sg,
    abl_sg,
    gen_sg,
    loc_sg,
    ins_du,
    dat_du,
    abl_du,
    gen_du,
    loc_du,
    ins_pl,
    dat_pl,
    abl_pl,
    gen_pl,
    loc_pl,
).optimize()

# Combined active participle / possessive paradigm
ant_stem_paradigm = pn.union(
    ant_masc_paradigm, ant_neut_paradigm, ant_fem_paradigm
).optimize()
