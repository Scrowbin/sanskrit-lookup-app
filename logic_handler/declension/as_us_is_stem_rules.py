import pynini as pn

# 1. Define our dynamic gender matchers
any_g = pn.union("[Masc]", "[Fem]", "[Neut]")
mf_g = pn.union("[Masc]", "[Fem]")  # For Masc/Fem shared cases

"""
1. Consonant t-stem (e.g., marut, trivṛt)
"""
# --- Gender-Specific Cases (Nom, Acc, Voc) ---
# Masc/Fem
nom_sg_t_mf = pn.cross("[DENTAL_T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Nom][Sg]", "")
acc_sg_t_mf = (
    pn.cross("[DENTAL_T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Acc][Sg]", "am")
)
voc_sg_t_mf = pn.cross("[DENTAL_T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Voc][Sg]", "")

nom_du_t_mf = (
    pn.cross("[DENTAL_T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Nom][Du]", "au")
)
acc_du_t_mf = (
    pn.cross("[DENTAL_T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Acc][Du]", "au")
)
voc_du_t_mf = (
    pn.cross("[DENTAL_T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Voc][Du]", "au")
)

nom_pl_t_mf = (
    pn.cross("[DENTAL_T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Nom][Pl]", "as")
)
acc_pl_t_mf = (
    pn.cross("[DENTAL_T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Acc][Pl]", "as")
)
voc_pl_t_mf = (
    pn.cross("[DENTAL_T_STEM]", "") + pn.cross(mf_g, "") + pn.cross("[Voc][Pl]", "as")
)

# Neuter
nom_sg_t_n = pn.cross("[DENTAL_T_STEM][Neut][Nom][Sg]", "")
acc_sg_t_n = pn.cross("[DENTAL_T_STEM][Neut][Acc][Sg]", "")
voc_sg_t_n = pn.cross("[DENTAL_T_STEM][Neut][Voc][Sg]", "")

nom_du_t_n = pn.cross("[DENTAL_T_STEM][Neut][Nom][Du]", "ī")
acc_du_t_n = pn.cross("[DENTAL_T_STEM][Neut][Acc][Du]", "ī")
voc_du_t_n = pn.cross("[DENTAL_T_STEM][Neut][Voc][Du]", "ī")

# Neuter Plural consumes the 't' for nasal insertion
nom_pl_t_n = pn.cross("t[DENTAL_T_STEM][Neut][Nom][Pl]", "nti")
acc_pl_t_n = pn.cross("t[DENTAL_T_STEM][Neut][Acc][Pl]", "nti")
voc_pl_t_n = pn.cross("t[DENTAL_T_STEM][Neut][Voc][Pl]", "nti")


# --- Gender-Blind Cases (Ins, Dat, Abl, Gen, Loc) ---
# We create a base that drops the stem tag and ANY gender tag
t_base = pn.cross("[DENTAL_T_STEM]", "") + pn.cross(any_g, "")
t_base_pada = pn.cross("[DENTAL_T_STEM]", "#") + pn.cross(any_g, "")

ins_sg_t = t_base + pn.cross("[Ins][Sg]", "ā")
dat_sg_t = t_base + pn.cross("[Dat][Sg]", "e")
abl_sg_t = t_base + pn.cross("[Abl][Sg]", "as")
gen_sg_t = t_base + pn.cross("[Gen][Sg]", "as")
loc_sg_t = t_base + pn.cross("[Loc][Sg]", "i")

ins_du_t = t_base_pada + pn.cross("[Ins][Du]", "bhyām")
dat_du_t = t_base_pada + pn.cross("[Dat][Du]", "bhyām")
abl_du_t = t_base_pada + pn.cross("[Abl][Du]", "bhyām")
gen_du_t = t_base + pn.cross("[Gen][Du]", "os")
loc_du_t = t_base + pn.cross("[Loc][Du]", "os")

ins_pl_t = t_base_pada + pn.cross("[Ins][Pl]", "bhis")
dat_pl_t = t_base_pada + pn.cross("[Dat][Pl]", "bhyas")
abl_pl_t = t_base_pada + pn.cross("[Abl][Pl]", "bhyas")
gen_pl_t = t_base + pn.cross("[Gen][Pl]", "ām")
loc_pl_t = t_base_pada + pn.cross("[Loc][Pl]", "su")

"""
2. Consonant s-stem & yas-stem (e.g., manas, havis, cakṣus, śreyas)
Assumes downstream engine handles Ruki (s -> ṣ), but forces morphological 
sandhi (as -> o, is -> ir, us -> ur) directly within the FST.
Comparatives use [YAS_STEM] to prevent collisions with as-stems like 'pravayas'.
"""

# --- Dynamic Bases ---
s_base_vowel = pn.union(
    pn.cross("[S_STEM]", ""), pn.cross("[YAS_STEM]", "")
) + pn.cross(any_g, "")

# Base that performs s->ṣ retroflexion for is/us stems
s_base_vowel_ruki = pn.union(
    pn.cross("is[S_STEM]", "iṣ"),
    pn.cross("us[S_STEM]", "uṣ"),
    pn.cross("as[S_STEM]", "as"),
    pn.cross("yas[YAS_STEM]", "yas"),
) + pn.cross(any_g, "")

s_base_vowel_ruki_mf = pn.union(
    pn.cross("is[S_STEM]", "iṣ"),
    pn.cross("us[S_STEM]", "uṣ"),
    pn.cross("as[S_STEM]", "as"),
) + pn.cross(mf_g, "")

s_base_bh = pn.union(
    pn.cross("as[S_STEM]", "o"),  # manas -> mano
    pn.cross("is[S_STEM]", "ir"),  # havis -> havir
    pn.cross("us[S_STEM]", "ur"),  # cakṣus -> cakṣur
    pn.cross("yas[YAS_STEM]", "yo"),  # śreyas -> śreyo
) + pn.cross(any_g, "")

# Strong bases for comparatives
yas_strong_mf = pn.cross("yas[YAS_STEM]", "yāṃs") + pn.cross(mf_g, "")
yas_strong_n = pn.cross("yas[YAS_STEM]", "yāṃs") + pn.cross("[Neut]", "")

# --- Masculine/Feminine Specific Cases ---
# Nom Sg lengthens the vowel for normal stems, infixes nasal for comparatives
nom_sg_s_mf = (
    pn.union(
        pn.cross("as[S_STEM]", "ās"),
        pn.cross("is[S_STEM]", "īs"),
        pn.cross("us[S_STEM]", "ūs"),
        pn.cross("yas[YAS_STEM]", "yān"),
    )
    + pn.cross(mf_g, "")
    + pn.cross("[Nom][Sg]", "")
)

voc_sg_s_mf = pn.union(
    pn.cross("[S_STEM]", "") + pn.cross(mf_g, ""),
    pn.cross("yas[YAS_STEM]", "yan") + pn.cross(mf_g, ""),
) + pn.cross("[Voc][Sg]", "")

acc_sg_s_mf = pn.union(
    s_base_vowel_ruki_mf, yas_strong_mf
) + pn.cross("[Acc][Sg]", "am")

nom_du_s_mf = pn.union(
    s_base_vowel_ruki_mf, yas_strong_mf
) + pn.cross("[Nom][Du]", "au")
acc_du_s_mf = pn.union(
    s_base_vowel_ruki_mf, yas_strong_mf
) + pn.cross("[Acc][Du]", "au")
voc_du_s_mf = pn.union(
    s_base_vowel_ruki_mf, yas_strong_mf
) + pn.cross("[Voc][Du]", "au")

nom_pl_s_mf = pn.union(
    s_base_vowel_ruki_mf, yas_strong_mf
) + pn.cross("[Nom][Pl]", "as")
voc_pl_s_mf = pn.union(
    s_base_vowel_ruki_mf, yas_strong_mf
) + pn.cross("[Voc][Pl]", "as")

# Acc Pl is universally weak
acc_pl_s_mf = s_base_vowel_ruki + pn.cross("[Acc][Pl]", "as")


# --- Neuter Specific Cases ---
nom_sg_s_n = s_base_vowel + pn.cross("[Nom][Sg]", "")
acc_sg_s_n = s_base_vowel + pn.cross("[Acc][Sg]", "")
voc_sg_s_n = s_base_vowel + pn.cross("[Voc][Sg]", "")

nom_du_s_n = s_base_vowel_ruki + pn.cross("[Nom][Du]", "ī")
acc_du_s_n = s_base_vowel_ruki + pn.cross("[Acc][Du]", "ī")
voc_du_s_n = s_base_vowel_ruki + pn.cross("[Voc][Du]", "ī")

# Plural base triggers nasal infixation and lengthening
n_pl_base = pn.union(
    pn.cross("as[S_STEM]", "āṃs") + pn.cross("[Neut]", ""),
    pn.cross("is[S_STEM]", "īṃṣ") + pn.cross("[Neut]", ""),
    pn.cross("us[S_STEM]", "ūṃṣ") + pn.cross("[Neut]", ""),
    yas_strong_n,
)
nom_pl_s_n = n_pl_base + pn.cross("[Nom][Pl]", "i")
acc_pl_s_n = n_pl_base + pn.cross("[Acc][Pl]", "i")
voc_pl_s_n = n_pl_base + pn.cross("[Voc][Pl]", "i")


# --- Gender-Blind Oblique Cases (Ins, Dat, Abl, Gen, Loc) ---
ins_sg_s = s_base_vowel_ruki + pn.cross("[Ins][Sg]", "ā")
dat_sg_s = s_base_vowel_ruki + pn.cross("[Dat][Sg]", "e")
abl_sg_s = s_base_vowel_ruki + pn.cross("[Abl][Sg]", "as")
gen_sg_s = s_base_vowel_ruki + pn.cross("[Gen][Sg]", "as")
loc_sg_s = s_base_vowel_ruki + pn.cross("[Loc][Sg]", "i")

# These use the modified 'bh' base
ins_du_s = s_base_bh + pn.cross("[Ins][Du]", "bhyām")
dat_du_s = s_base_bh + pn.cross("[Dat][Du]", "bhyām")
abl_du_s = s_base_bh + pn.cross("[Abl][Du]", "bhyām")

gen_du_s = s_base_vowel_ruki + pn.cross("[Gen][Du]", "os")
loc_du_s = s_base_vowel_ruki + pn.cross("[Loc][Du]", "os")

# These use the modified 'bh' base
ins_pl_s = s_base_bh + pn.cross("[Ins][Pl]", "bhis")
dat_pl_s = s_base_bh + pn.cross("[Dat][Pl]", "bhyas")
abl_pl_s = s_base_bh + pn.cross("[Abl][Pl]", "bhyas")

gen_pl_s = s_base_vowel_ruki + pn.cross("[Gen][Pl]", "ām")

# Locative plural can have visarga (aḥsu/iḥṣu/uḥṣu) or sibilant doubling (assu/iṣṣu/uṣṣu).
# We generate both options!
loc_pl_s = pn.union(
    s_base_vowel + pn.cross("[Loc][Pl]", "su"),
    pn.union(
        pn.cross("as[S_STEM]", "aḥ") + pn.cross(any_g, "") + pn.cross("[Loc][Pl]", "su"),
        pn.cross("is[S_STEM]", "iḥ") + pn.cross(any_g, "") + pn.cross("[Loc][Pl]", "su"),
        pn.cross("us[S_STEM]", "uḥ") + pn.cross(any_g, "") + pn.cross("[Loc][Pl]", "su"),
        pn.cross("yas[YAS_STEM]", "yaḥ") + pn.cross(any_g, "") + pn.cross("[Loc][Pl]", "su"),
    )
)

# Master Union
s_stem_paradigm = pn.union(
    nom_sg_s_mf,
    voc_sg_s_mf,
    acc_sg_s_mf,
    nom_du_s_mf,
    acc_du_s_mf,
    voc_du_s_mf,
    nom_pl_s_mf,
    voc_pl_s_mf,
    acc_pl_s_mf,
    nom_sg_s_n,
    acc_sg_s_n,
    voc_sg_s_n,
    nom_du_s_n,
    acc_du_s_n,
    voc_du_s_n,
    nom_pl_s_n,
    acc_pl_s_n,
    voc_pl_s_n,
    ins_sg_s,
    dat_sg_s,
    abl_sg_s,
    gen_sg_s,
    loc_sg_s,
    ins_du_s,
    dat_du_s,
    abl_du_s,
    gen_du_s,
    loc_du_s,
    ins_pl_s,
    dat_pl_s,
    abl_pl_s,
    gen_pl_s,
    loc_pl_s,
).optimize()

t_mf_specific = pn.union(
    nom_sg_t_mf,
    acc_sg_t_mf,
    voc_sg_t_mf,
    nom_du_t_mf,
    acc_du_t_mf,
    voc_du_t_mf,
    nom_pl_t_mf,
    acc_pl_t_mf,
    voc_pl_t_mf,
)

# 2. Neuter Specific
t_n_specific = pn.union(
    nom_sg_t_n,
    acc_sg_t_n,
    voc_sg_t_n,
    nom_du_t_n,
    acc_du_t_n,
    voc_du_t_n,
    nom_pl_t_n,
    acc_pl_t_n,
    voc_pl_t_n,
)

# 3. Gender-Blind Oblique Cases
# (Ins, Dat, Abl, Gen, Loc - Shared by all genders)
t_oblique = pn.union(
    ins_sg_t,
    dat_sg_t,
    abl_sg_t,
    gen_sg_t,
    loc_sg_t,
    ins_du_t,
    dat_du_t,
    abl_du_t,
    gen_du_t,
    loc_du_t,
    ins_pl_t,
    dat_pl_t,
    abl_pl_t,
    gen_pl_t,
    loc_pl_t,
)

# 4. Master T-Stem Union
# Combines all M/F cases, N cases, and oblique cases into one FST
t_stem_paradigm = pn.union(t_mf_specific, t_n_specific, t_oblique).optimize()
