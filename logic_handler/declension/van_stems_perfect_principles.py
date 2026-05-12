import pynini as pn

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


"""
3. MASCULINE SPECIFIC CASES
"""
# --- Sg Exceptions ---
nom_sg_m = pn.cross("vāṅs[VAS_STEM][Masc][Nom][Sg]", "vān")  # vidvāṅs -> vidvān
voc_sg_m = pn.cross(
    "vāṅs[VAS_STEM][Masc][Voc][Sg]", "van"
)  # vidvāṅs -> vidvan (Short 'a'!)

# --- Strong Cases (Stem stays 'vāṅs') ---
acc_sg_m = strong_m + pn.cross("[Acc][Sg]", "am")  # vidvāṅs -> vidvāṅsam
nom_du_m = strong_m + pn.cross("[Nom][Du]", "au")  # vidvāṅs -> vidvāṅsau
acc_du_m = strong_m + pn.cross("[Acc][Du]", "au")
voc_du_m = strong_m + pn.cross("[Voc][Du]", "au")
nom_pl_m = strong_m + pn.cross("[Nom][Pl]", "as")  # vidvāṅs -> vidvāṅsas
voc_pl_m = strong_m + pn.cross("[Voc][Pl]", "as")

# --- Weakest Cases (Stem becomes 'uṣ') ---
acc_pl_m = weak_m + pn.cross("[Acc][Pl]", "as")  # vidvāṅs -> viduṣas


"""
4. NEUTER SPECIFIC CASES
"""
# --- Middle Cases (Nom/Acc/Voc Sg) ---
nom_sg_n = middle_n + pn.cross("[Nom][Sg]", "")  # vidvāṅs -> vidvat
acc_sg_n = middle_n + pn.cross("[Acc][Sg]", "")
voc_sg_n = middle_n + pn.cross("[Voc][Sg]", "")

# --- Weakest Cases (Nom/Acc/Voc Du) ---
nom_du_n = weak_n + pn.cross("[Nom][Du]", "ī")  # vidvāṅs -> viduṣī
acc_du_n = weak_n + pn.cross("[Acc][Du]", "ī")
voc_du_n = weak_n + pn.cross("[Voc][Du]", "ī")

# --- Strong Cases (Nom/Acc/Voc Pl) ---
nom_pl_n = strong_n + pn.cross("[Nom][Pl]", "i")  # vidvāṅs -> vidvāṅsi
acc_pl_n = strong_n + pn.cross("[Acc][Pl]", "i")
voc_pl_n = strong_n + pn.cross("[Voc][Pl]", "i")


"""
5. GENDER-BLIND MIDDLE CASES (Consonant Endings)
The stem behaves exactly like a t-stem here!
"""
ins_du = middle_blind + pn.cross(
    "[Ins][Du]", "bhyām"
)  # vidvāṅs -> vidvatbhyām (Sandhi -> dbhyām)
dat_du = middle_blind + pn.cross("[Dat][Du]", "bhyām")
abl_du = middle_blind + pn.cross("[Abl][Du]", "bhyām")
ins_pl = middle_blind + pn.cross(
    "[Ins][Pl]", "bhis"
)  # vidvāṅs -> vidvatbhis (Sandhi -> dbhis)
dat_pl = middle_blind + pn.cross("[Dat][Pl]", "bhyas")
abl_pl = middle_blind + pn.cross("[Abl][Pl]", "bhyas")
loc_pl = middle_blind + pn.cross("[Loc][Pl]", "su")  # vidvāṅs -> vidvatsu


"""
6. GENDER-BLIND WEAKEST CASES (Vowel Endings)
The stem collapses to 'uṣ'
"""
ins_sg = weak_blind + pn.cross("[Ins][Sg]", "ā")  # vidvāṅs -> viduṣā
dat_sg = weak_blind + pn.cross("[Dat][Sg]", "e")  # vidvāṅs -> viduṣe
abl_sg = weak_blind + pn.cross("[Abl][Sg]", "as")
gen_sg = weak_blind + pn.cross("[Gen][Sg]", "as")
loc_sg = weak_blind + pn.cross("[Loc][Sg]", "i")  # vidvāṅs -> viduṣi
gen_du = weak_blind + pn.cross("[Gen][Du]", "os")  # vidvāṅs -> viduṣos
loc_du = weak_blind + pn.cross("[Loc][Du]", "os")
gen_pl = weak_blind + pn.cross("[Gen][Pl]", "ām")  # vidvāṅs -> viduṣām

"""
7. FEMININE -VĀṄS STEMS (e.g., viduṣī)
"""

# Feminine Base: Unconditionally collapses 'vāṅs' to the weakest grade 'uṣ'
fem_base_vas = pn.cross("vāṅs[VAS_STEM]", "uṣ") + pn.cross("[Fem]", "")

# Singular
nom_sg_f = fem_base_vas + pn.cross("[Nom][Sg]", "ī")  # vidvāṅs -> viduṣī
acc_sg_f = fem_base_vas + pn.cross("[Acc][Sg]", "īm")  # vidvāṅs -> viduṣīm
ins_sg_f = fem_base_vas + pn.cross("[Ins][Sg]", "yā")  # vidvāṅs -> viduṣyā
dat_sg_f = fem_base_vas + pn.cross("[Dat][Sg]", "yai")  # vidvāṅs -> viduṣyai
abl_sg_f = fem_base_vas + pn.cross("[Abl][Sg]", "yās")
gen_sg_f = fem_base_vas + pn.cross("[Gen][Sg]", "yās")
loc_sg_f = fem_base_vas + pn.cross("[Loc][Sg]", "yām")
voc_sg_f = fem_base_vas + pn.cross("[Voc][Sg]", "i")  # vidvāṅs -> viduṣi (short i!)

# Dual
nom_du_f = fem_base_vas + pn.cross("[Nom][Du]", "yau")  # vidvāṅs -> viduṣyau
acc_du_f = fem_base_vas + pn.cross("[Acc][Du]", "yau")
voc_du_f = fem_base_vas + pn.cross("[Voc][Du]", "yau")
ins_du_f = fem_base_vas + pn.cross("[Ins][Du]", "ībhyām")  # vidvāṅs -> viduṣībhyām
dat_du_f = fem_base_vas + pn.cross("[Dat][Du]", "ībhyām")
abl_du_f = fem_base_vas + pn.cross("[Abl][Du]", "ībhyām")
gen_du_f = fem_base_vas + pn.cross("[Gen][Du]", "yos")  # vidvāṅs -> viduṣyos
loc_du_f = fem_base_vas + pn.cross("[Loc][Du]", "yos")

# Plural
nom_pl_f = fem_base_vas + pn.cross("[Nom][Pl]", "yas")  # vidvāṅs -> viduṣyas
acc_pl_f = fem_base_vas + pn.cross("[Acc][Pl]", "īs")  # vidvāṅs -> viduṣīs
voc_pl_f = fem_base_vas + pn.cross("[Voc][Pl]", "yas")
ins_pl_f = fem_base_vas + pn.cross("[Ins][Pl]", "ībhis")
dat_pl_f = fem_base_vas + pn.cross("[Dat][Pl]", "ībhyas")
abl_pl_f = fem_base_vas + pn.cross("[Abl][Pl]", "ībhyas")
gen_pl_f = fem_base_vas + pn.cross("[Gen][Pl]", "īnām")
loc_pl_f = fem_base_vas + pn.cross(
    "[Loc][Pl]", "īsu"
)  # Underlying 'su' (Sandhi will Ruki it to īṣu)

# 8. FINAL PARADIGM COMPILATIONS FOR -VĀṄS STEMS

# Masculine -vāṅs paradigm (e.g., vidvāṅs)
vas_masc_paradigm = pn.union(
    nom_sg_m,
    acc_sg_m,
    ins_sg,
    dat_sg,
    abl_sg,
    gen_sg,
    loc_sg,
    voc_sg_m,
    nom_du_m,
    acc_du_m,
    ins_du,
    dat_du,
    abl_du,
    gen_du,
    loc_du,
    voc_du_m,
    nom_pl_m,
    acc_pl_m,
    ins_pl,
    dat_pl,
    abl_pl,
    gen_pl,
    loc_pl,
    voc_pl_m,
).optimize()

vas_fem_paradigm = pn.union(
    nom_sg_f,
    acc_sg_f,
    ins_sg_f,
    dat_sg_f,
    abl_sg_f,
    gen_sg_f,
    loc_sg_f,
    voc_sg_f,
    nom_du_f,
    acc_du_f,
    voc_du_f,
    ins_du_f,
    dat_du_f,
    abl_du_f,
    gen_du_f,
    loc_du_f,
    nom_pl_f,
    acc_pl_f,
    voc_pl_f,
    ins_pl_f,
    dat_pl_f,
    abl_pl_f,
    gen_pl_f,
    loc_pl_f,
).optimize()
# Neuter -vāṅs paradigm (e.g., vidvāṅs)
vas_neut_paradigm = pn.union(
    nom_sg_n,
    acc_sg_n,
    ins_sg,
    dat_sg,
    abl_sg,
    gen_sg,
    loc_sg,
    voc_sg_n,
    nom_du_n,
    acc_du_n,
    ins_du,
    dat_du,
    abl_du,
    gen_du,
    loc_du,
    voc_du_n,
    nom_pl_n,
    acc_pl_n,
    ins_pl,
    dat_pl,
    abl_pl,
    gen_pl,
    loc_pl,
    voc_pl_n,
).optimize()

# Master -vāṅs Transducer
vas_stem_paradigm = pn.union(
    vas_masc_paradigm, vas_neut_paradigm, vas_fem_paradigm
).optimize()
