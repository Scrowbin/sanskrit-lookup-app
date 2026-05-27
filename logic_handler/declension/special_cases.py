import pynini as pn

# --- Core Tag Drop Transducers ---
masc_tag = pn.cross("[Masc]", "")
fem_tag = pn.cross("[Fem]", "")
neut_tag = pn.cross("[Neut]", "")
mf_blind = pn.cross(pn.union("[Masc]", "[Fem]"), "")

# =============================================================================
# 1. SAKHI PARADIGM (Friend)
# =============================================================================
sakhi_paradigm = pn.union(
    pn.cross("sakhi", "sakhā") + masc_tag + pn.cross("[Nom][Sg]", ""),
    pn.cross("sakhi", "sakhāyam") + masc_tag + pn.cross("[Acc][Sg]", ""),
    pn.cross("sakhi", "sakhyā") + masc_tag + pn.cross("[Ins][Sg]", ""),
    pn.cross("sakhi", "sakhye") + masc_tag + pn.cross("[Dat][Sg]", ""),
    pn.cross("sakhi", "sakhyuḥ") + masc_tag + pn.cross("[Abl][Sg]", ""),
    pn.cross("sakhi", "sakhyuḥ") + masc_tag + pn.cross("[Gen][Sg]", ""),
    pn.cross("sakhi", "sakhyau") + masc_tag + pn.cross("[Loc][Sg]", ""),
    pn.cross("sakhi", "sakhe") + masc_tag + pn.cross("[Voc][Sg]", ""),
    pn.cross("sakhi", "sakhāyau") + masc_tag + pn.cross("[Nom][Du]", ""),
    pn.cross("sakhi", "sakhāyau") + masc_tag + pn.cross("[Acc][Du]", ""),
    pn.cross("sakhi", "sakhāyau") + masc_tag + pn.cross("[Voc][Du]", ""),
    pn.cross("sakhi", "sakhibhyām") + masc_tag + pn.cross("[Ins][Du]", ""),
    pn.cross("sakhi", "sakhibhyām") + masc_tag + pn.cross("[Dat][Du]", ""),
    pn.cross("sakhi", "sakhibhyām") + masc_tag + pn.cross("[Abl][Du]", ""),
    pn.cross("sakhi", "sakhyos") + masc_tag + pn.cross("[Gen][Du]", ""),
    pn.cross("sakhi", "sakhyos") + masc_tag + pn.cross("[Loc][Du]", ""),
    pn.cross("sakhi", "sakhāyas") + masc_tag + pn.cross("[Nom][Pl]", ""),
    pn.cross("sakhi", "sakhīn") + masc_tag + pn.cross("[Acc][Pl]", ""),
    pn.cross("sakhi", "sakhāyas") + masc_tag + pn.cross("[Voc][Pl]", ""),
    pn.cross("sakhi", "sakhibhis") + masc_tag + pn.cross("[Ins][Pl]", ""),
    pn.cross("sakhi", "sakhibhyas") + masc_tag + pn.cross("[Dat][Pl]", ""),
    pn.cross("sakhi", "sakhibhyas") + masc_tag + pn.cross("[Abl][Pl]", ""),
    pn.cross("sakhi", "sakhīnām") + masc_tag + pn.cross("[Gen][Pl]", ""),
    pn.cross("sakhi", "sakhibhiṣu") + masc_tag + pn.cross("[Loc][Pl]", ""),
).optimize()

# =============================================================================
# 2. RAI PARADIGM (Wealth)
# =============================================================================
rai_paradigm = pn.union(
    pn.cross("rai", "rāḥ") + masc_tag + pn.cross("[Nom][Sg]", ""),
    pn.cross("rai", "rāyam") + masc_tag + pn.cross("[Acc][Sg]", ""),
    pn.cross("rai", "rāyā") + masc_tag + pn.cross("[Ins][Sg]", ""),
    pn.cross("rai", "rāye") + masc_tag + pn.cross("[Dat][Sg]", ""),
    pn.cross("rai", "rāyaḥ") + masc_tag + pn.cross("[Abl][Sg]", ""),
    pn.cross("rai", "rāyaḥ") + masc_tag + pn.cross("[Gen][Sg]", ""),
    pn.cross("rai", "rāyi") + masc_tag + pn.cross("[Loc][Sg]", ""),
    pn.cross("rai", "rāḥ") + masc_tag + pn.cross("[Voc][Sg]", ""),
    pn.cross("rai", "rāyau") + masc_tag + pn.cross("[Nom][Du]", ""),
    pn.cross("rai", "rāyau") + masc_tag + pn.cross("[Acc][Du]", ""),
    pn.cross("rai", "rāyau") + masc_tag + pn.cross("[Voc][Du]", ""),
    pn.cross("rai", "rābhyām") + masc_tag + pn.cross("[Ins][Du]", ""),
    pn.cross("rai", "rābhyām") + masc_tag + pn.cross("[Dat][Du]", ""),
    pn.cross("rai", "rābhyām") + masc_tag + pn.cross("[Abl][Du]", ""),
    pn.cross("rai", "rāyos") + masc_tag + pn.cross("[Gen][Du]", ""),
    pn.cross("rai", "rāyos") + masc_tag + pn.cross("[Loc][Du]", ""),
    pn.cross("rai", "rāyas") + masc_tag + pn.cross("[Nom][Pl]", ""),
    pn.cross("rai", "rāyas") + masc_tag + pn.cross("[Acc][Pl]", ""),
    pn.cross("rai", "rāyas") + masc_tag + pn.cross("[Voc][Pl]", ""),
    pn.cross("rai", "rābhis") + masc_tag + pn.cross("[Ins][Pl]", ""),
    pn.cross("rai", "rābhyas") + masc_tag + pn.cross("[Dat][Pl]", ""),
    pn.cross("rai", "rābhyas") + masc_tag + pn.cross("[Abl][Pl]", ""),
    pn.cross("rai", "rāyām") + masc_tag + pn.cross("[Gen][Pl]", ""),
    pn.cross("rai", "rāsu") + masc_tag + pn.cross("[Loc][Pl]", ""),
).optimize()

# =============================================================================
# 3. PATI PARADIGM (Husband / Master split)
# =============================================================================
pati_paradigm = pn.union(
    pn.cross("pati", "patis") + masc_tag + pn.cross("[Nom][Sg]", ""),
    pn.cross("pati", "patim") + masc_tag + pn.cross("[Acc][Sg]", ""),
    pn.cross("pati", "pate") + masc_tag + pn.cross("[Voc][Sg]", ""),
    pn.cross("pati", "patyā") + masc_tag + pn.cross("[Ins][Sg]", ""),
    pn.cross("pati", "patinā") + masc_tag + pn.cross("[Ins][Sg]", ""),
    pn.cross("pati", "patye") + masc_tag + pn.cross("[Dat][Sg]", ""),
    pn.cross("pati", "pataye") + masc_tag + pn.cross("[Dat][Sg]", ""),
    pn.cross("pati", "patyuḥ") + masc_tag + pn.cross("[Abl][Sg]", ""),
    pn.cross("pati", "pates") + masc_tag + pn.cross("[Abl][Sg]", ""),
    pn.cross("pati", "patyuḥ") + masc_tag + pn.cross("[Gen][Sg]", ""),
    pn.cross("pati", "pates") + masc_tag + pn.cross("[Gen][Sg]", ""),
    pn.cross("pati", "patyau") + masc_tag + pn.cross("[Loc][Sg]", ""),
    pn.cross("pati", "patau") + masc_tag + pn.cross("[Loc][Sg]", ""),
    pn.cross("pati", "patī") + masc_tag + pn.cross("[Nom][Du]", ""),
    pn.cross("pati", "patī") + masc_tag + pn.cross("[Acc][Du]", ""),
    pn.cross("pati", "patī") + masc_tag + pn.cross("[Voc][Du]", ""),
    pn.cross("pati", "patibhyām") + masc_tag + pn.cross("[Ins][Du]", ""),
    pn.cross("pati", "patibhyām") + masc_tag + pn.cross("[Dat][Du]", ""),
    pn.cross("pati", "patibhyām") + masc_tag + pn.cross("[Abl][Du]", ""),
    pn.cross("pati", "patyos") + masc_tag + pn.cross("[Gen][Du]", ""),
    pn.cross("pati", "patyos") + masc_tag + pn.cross("[Loc][Du]", ""),
    pn.cross("pati", "patayas") + masc_tag + pn.cross("[Nom][Pl]", ""),
    pn.cross("pati", "patīn") + masc_tag + pn.cross("[Acc][Pl]", ""),
    pn.cross("pati", "patayas") + masc_tag + pn.cross("[Voc][Pl]", ""),
    pn.cross("pati", "patibhis") + masc_tag + pn.cross("[Ins][Pl]", ""),
    pn.cross("pati", "patibhyas") + masc_tag + pn.cross("[Dat][Pl]", ""),
    pn.cross("pati", "patibhyas") + masc_tag + pn.cross("[Abl][Pl]", ""),
    pn.cross("pati", "patīnām") + masc_tag + pn.cross("[Gen][Pl]", ""),
    pn.cross("pati", "patisu") + masc_tag + pn.cross("[Loc][Pl]", ""),
).optimize()

# =============================================================================
# 4. GO PARADIGM (Cow / Ox)
# =============================================================================
go_paradigm = pn.union(
    pn.cross("go", "gauh") + mf_blind + pn.cross("[Nom][Sg]", ""),
    pn.cross("go", "gām") + mf_blind + pn.cross("[Acc][Sg]", ""),
    pn.cross("go", "gavā") + mf_blind + pn.cross("[Ins][Sg]", ""),
    pn.cross("go", "gave") + mf_blind + pn.cross("[Dat][Sg]", ""),
    pn.cross("go", "goh") + mf_blind + pn.cross("[Abl][Sg]", ""),
    pn.cross("go", "goh") + mf_blind + pn.cross("[Gen][Sg]", ""),
    pn.cross("go", "gavi") + mf_blind + pn.cross("[Loc][Sg]", ""),
    pn.cross("go", "gauh") + mf_blind + pn.cross("[Voc][Sg]", ""),
    pn.cross("go", "gāvau") + mf_blind + pn.cross("[Nom][Du]", ""),
    pn.cross("go", "gāvau") + mf_blind + pn.cross("[Acc][Du]", ""),
    pn.cross("go", "gāvau") + mf_blind + pn.cross("[Voc][Du]", ""),
    pn.cross("go", "gॉbhyām") + mf_blind + pn.cross("[Ins][Du]", ""),  # gobhyām
    pn.cross("go", "gॉbhyām") + mf_blind + pn.cross("[Dat][Du]", ""),
    pn.cross("go", "gॉbhyām") + mf_blind + pn.cross("[Abl][Du]", ""),
    pn.cross("go", "gavos") + mf_blind + pn.cross("[Gen][Du]", ""),
    pn.cross("go", "gavos") + mf_blind + pn.cross("[Loc][Du]", ""),
    pn.cross("go", "gāvaḥ") + mf_blind + pn.cross("[Nom][Pl]", ""),
    pn.cross("go", "gāḥ") + mf_blind + pn.cross("[Acc][Pl]", ""),
    pn.cross("go", "gāvaḥ") + mf_blind + pn.cross("[Voc][Pl]", ""),
    pn.cross("go", "gॉbhiḥ") + mf_blind + pn.cross("[Ins][Pl]", ""),
    pn.cross("go", "gॉbhyas") + mf_blind + pn.cross("[Dat][Pl]", ""),
    pn.cross("go", "gॉbhyas") + mf_blind + pn.cross("[Abl][Pl]", ""),
    pn.cross("go", "gavām") + mf_blind + pn.cross("[Gen][Pl]", ""),
    pn.cross("go", "goṣu") + mf_blind + pn.cross("[Loc][Pl]", ""),
).optimize()

# =============================================================================
# 5. MONSTER MONOPHONEMICS (Nau & Div)
# =============================================================================
nau_paradigm = pn.union(
    pn.cross("nau", "nauḥ") + fem_tag + pn.cross("[Nom][Sg]", ""),
    pn.cross("nau", "nāvam") + fem_tag + pn.cross("[Acc][Sg]", ""),
    pn.cross("nau", "nāvā") + fem_tag + pn.cross("[Ins][Sg]", ""),
    pn.cross("nau", "nāve") + fem_tag + pn.cross("[Dat][Sg]", ""),
    pn.cross("nau", "nāvaḥ") + fem_tag + pn.cross("[Abl][Sg]", ""),
    pn.cross("nau", "nāvaḥ") + fem_tag + pn.cross("[Gen][Sg]", ""),
    pn.cross("nau", "nāvi") + fem_tag + pn.cross("[Loc][Sg]", ""),
    pn.cross("nau", "nāvau") + fem_tag + pn.cross("[Nom][Du]", ""),
    pn.cross("nau", "nāvau") + fem_tag + pn.cross("[Acc][Du]", ""),
    pn.cross("nau", "naubhyām") + fem_tag + pn.cross("[Ins][Du]", ""),
    pn.cross("nau", "nāvaḥ") + fem_tag + pn.cross("[Nom][Pl]", ""),
    pn.cross("nau", "nāvaḥ") + fem_tag + pn.cross("[Acc][Pl]", ""),
    pn.cross("nau", "naubhiḥ") + fem_tag + pn.cross("[Ins][Pl]", ""),
    pn.cross("nau", "nāvām") + fem_tag + pn.cross("[Gen][Pl]", ""),
    pn.cross("nau", "nauṣu") + fem_tag + pn.cross("[Loc][Pl]", ""),
).optimize()

div_paradigm = pn.union(
    pn.cross("div", "dyauḥ") + fem_tag + pn.cross("[Nom][Sg]", ""),
    pn.cross("div", "divam") + fem_tag + pn.cross("[Acc][Sg]", ""),
    pn.cross("div", "divā") + fem_tag + pn.cross("[Ins][Sg]", ""),
    pn.cross("div", "divaḥ") + fem_tag + pn.cross("[Abl][Sg]", ""),
    pn.cross("div", "divaḥ") + fem_tag + pn.cross("[Gen][Sg]", ""),
    pn.cross("div", "divi") + fem_tag + pn.cross("[Loc][Sg]", ""),
    pn.cross("div", "divau") + fem_tag + pn.cross("[Nom][Du]", ""),
    pn.cross("div", "dyubhyām") + fem_tag + pn.cross("[Ins][Du]", ""),
    pn.cross("div", "divaḥ") + fem_tag + pn.cross("[Nom][Pl]", ""),
    pn.cross("div", "divaḥ") + fem_tag + pn.cross("[Acc][Pl]", ""),
    pn.cross("div", "dyubhiḥ") + fem_tag + pn.cross("[Ins][Pl]", ""),
    pn.cross("div", "dyuṣu") + fem_tag + pn.cross("[Loc][Pl]", ""),
).optimize()

# =============================================================================
# 6. THE FOUR SHIFTING NEUTERS (asthi, dadhi, sakthi, akṣi)
# =============================================================================
irreg_neuter_bases = pn.union("asthi", "dadhi", "sakthi", "akṣi")

# Target the final 'i' explicitly relative to the known base vocabulary lengths
strip_stem_i = pn.cdrewrite(pn.cross("i", ""), "", "[EOS]", irreg_neuter_bases + "i")

weak_neuter_overrides = pn.union(
    (irreg_neuter_bases + pn.cross("i", "nā")) + neut_tag + pn.cross("[Ins][Sg]", ""),
    (irreg_neuter_bases + pn.cross("i", "ne")) + neut_tag + pn.cross("[Dat][Sg]", ""),
    (irreg_neuter_bases + pn.cross("i", "nas")) + neut_tag + pn.cross("[Abl][Sg]", ""),
    (irreg_neuter_bases + pn.cross("i", "nas")) + neut_tag + pn.cross("[Gen][Sg]", ""),
    (irreg_neuter_bases + pn.cross("i", "ni")) + neut_tag + pn.cross("[Loc][Sg]", ""),
    (irreg_neuter_bases + pn.cross("i", "nos")) + neut_tag + pn.cross("[Gen][Du]", ""),
    (irreg_neuter_bases + pn.cross("i", "nos")) + neut_tag + pn.cross("[Loc][Du]", ""),
)

four_neuters_paradigm = pn.union(
    weak_neuter_overrides,
    (irreg_neuter_bases + neut_tag + pn.cross("[Nom][Sg]", "")),
    (irreg_neuter_bases + neut_tag + pn.cross("[Acc][Sg]", "")),
    (irreg_neuter_bases + pn.cross("i", "e") + neut_tag + pn.cross("[Voc][Sg]", "")),
    (irreg_neuter_bases + pn.cross("i", "") + neut_tag + pn.cross("[Voc][Sg]", "")),
    (irreg_neuter_bases + pn.cross("i", "nī") + neut_tag + pn.cross("[Nom][Du]", "")),
    (irreg_neuter_bases + pn.cross("i", "nī") + neut_tag + pn.cross("[Acc][Du]", "")),
    (irreg_neuter_bases + pn.cross("i", "nī") + neut_tag + pn.cross("[Voc][Du]", "")),
    (irreg_neuter_bases + neut_tag + pn.cross("[Ins][Du]", "bhyām")),
    (irreg_neuter_bases + neut_tag + pn.cross("[Dat][Du]", "bhyām")),
    (irreg_neuter_bases + neut_tag + pn.cross("[Abl][Du]", "bhyām")),
    (irreg_neuter_bases + pn.cross("i", "īni") + neut_tag + pn.cross("[Nom][Pl]", "")),
    (irreg_neuter_bases + pn.cross("i", "īni") + neut_tag + pn.cross("[Acc][Pl]", "")),
    (irreg_neuter_bases + pn.cross("i", "īni") + neut_tag + pn.cross("[Voc][Pl]", "")),
    (irreg_neuter_bases + neut_tag + pn.cross("[Ins][Pl]", "bhis")),
    (irreg_neuter_bases + neut_tag + pn.cross("[Dat][Pl]", "bhyas")),
    (irreg_neuter_bases + neut_tag + pn.cross("[Abl][Pl]", "bhyas")),
    (irreg_neuter_bases + pn.cross("i", "īnām") + neut_tag + pn.cross("[Gen][Pl]", "")),
    (irreg_neuter_bases + neut_tag + pn.cross("[Loc][Pl]", "su")),
).optimize()

# =============================================================================
# 7. STRĪ PARADIGM (Complete paradigm mapping)
# =============================================================================
stri_paradigm = pn.union(
    pn.cross("strī", "strī") + fem_tag + pn.cross("[Nom][Sg]", ""),
    (pn.cross("strī", "strīm") | pn.cross("strī", "striyam"))
    + fem_tag
    + pn.cross("[Acc][Sg]", ""),
    pn.cross("strī", "striyā") + fem_tag + pn.cross("[Ins][Sg]", ""),
    pn.cross("strī", "striyai") + fem_tag + pn.cross("[Dat][Sg]", ""),
    pn.cross("strī", "striyās") + fem_tag + pn.cross("[Abl][Sg]", ""),
    pn.cross("strī", "striyās") + fem_tag + pn.cross("[Gen][Sg]", ""),
    pn.cross("strī", "striyām") + fem_tag + pn.cross("[Loc][Sg]", ""),
    pn.cross("strī", "stri") + fem_tag + pn.cross("[Voc][Sg]", ""),
    pn.cross("strī", "striyau") + fem_tag + pn.cross("[Nom][Du]", ""),
    pn.cross("strī", "striyau") + fem_tag + pn.cross("[Acc][Du]", ""),
    pn.cross("strī", "striyau") + fem_tag + pn.cross("[Voc][Du]", ""),
    pn.cross("strī", "strībhyām") + fem_tag + pn.cross("[Ins][Du]", ""),
    pn.cross("strī", "strībhyām") + fem_tag + pn.cross("[Dat][Du]", ""),
    pn.cross("strī", "strībhyām") + fem_tag + pn.cross("[Abl][Du]", ""),
    pn.cross("strī", "striyos") + fem_tag + pn.cross("[Gen][Du]", ""),
    pn.cross("strī", "striyos") + fem_tag + pn.cross("[Loc][Du]", ""),
    pn.cross("strī", "striyas") + fem_tag + pn.cross("[Nom][Pl]", ""),
    pn.cross("strī", "strīs") + fem_tag + pn.cross("[Acc][Pl]", ""),
    pn.cross("strī", "striyas") + fem_tag + pn.cross("[Voc][Pl]", ""),
    pn.cross("strī", "strībhis") + fem_tag + pn.cross("[Ins][Pl]", ""),
    pn.cross("strī", "strībhyas") + fem_tag + pn.cross("[Dat][Pl]", ""),
    pn.cross("strī", "strībhyas") + fem_tag + pn.cross("[Abl][Pl]", ""),
    pn.cross("strī", "strīṇām") + fem_tag + pn.cross("[Gen][Pl]", ""),
    pn.cross("strī", "strīṣu") + fem_tag + pn.cross("[Loc][Pl]", ""),
).optimize()

# =============================================================================
# 8. PANTHAN PARADIGM (Path)
# =============================================================================
panthan_paradigm = pn.union(
    pn.cross("panthan", "panthāḥ") + masc_tag + pn.cross("[Nom][Sg]", ""),
    pn.cross("panthan", "panthānam") + masc_tag + pn.cross("[Acc][Sg]", ""),
    pn.cross("panthan", "pathā") + masc_tag + pn.cross("[Ins][Sg]", ""),
    pn.cross("panthan", "pathe") + masc_tag + pn.cross("[Dat][Sg]", ""),
    pn.cross("panthan", "pathaḥ") + masc_tag + pn.cross("[Abl][Sg]", ""),
    pn.cross("panthan", "pathaḥ") + masc_tag + pn.cross("[Gen][Sg]", ""),
    pn.cross("panthan", "pathi") + masc_tag + pn.cross("[Loc][Sg]", ""),
    pn.cross("panthan", "panthāḥ") + masc_tag + pn.cross("[Voc][Sg]", ""),
    pn.cross("panthan", "panthānau") + masc_tag + pn.cross("[Nom][Du]", ""),
    pn.cross("panthan", "panthānau") + masc_tag + pn.cross("[Acc][Du]", ""),
    pn.cross("panthan", "panthibhyām") + masc_tag + pn.cross("[Ins][Du]", ""),
    pn.cross("panthan", "panthānaḥ") + masc_tag + pn.cross("[Nom][Pl]", ""),
    pn.cross("panthan", "pathaḥ") + masc_tag + pn.cross("[Acc][Pl]", ""),
    pn.cross("panthan", "panthibhiḥ") + masc_tag + pn.cross("[Ins][Pl]", ""),
    pn.cross("panthan", "panthiṣu") + masc_tag + pn.cross("[Loc][Pl]", ""),
).optimize()

# =============================================================================
# 9. KROṢṬU PARADIGM (Jackal)
# =============================================================================
krostu_paradigm = pn.union(
    pn.cross("kroṣṭu", "kroṣṭā") + masc_tag + pn.cross("[Nom][Sg]", ""),
    pn.cross("kroṣṭu", "kroṣṭāram") + masc_tag + pn.cross("[Acc][Sg]", ""),
    pn.cross("kroṣṭu", "kroṣṭunā") + masc_tag + pn.cross("[Ins][Sg]", ""),
    pn.cross("kroṣṭu", "kroṣṭave") + masc_tag + pn.cross("[Dat][Sg]", ""),
    pn.cross("kroṣṭu", "kroṣṭoḥ") + masc_tag + pn.cross("[Abl][Sg]", ""),
    pn.cross("kroṣṭu", "kroṣṭoḥ") + masc_tag + pn.cross("[Gen][Sg]", ""),
    pn.cross("kroṣṭu", "kroṣṭau") + masc_tag + pn.cross("[Loc][Sg]", ""),
    pn.cross("kroṣṭu", "kroṣṭo") + masc_tag + pn.cross("[Voc][Sg]", ""),
    pn.cross("kroṣṭu", "kroṣṭārau") + masc_tag + pn.cross("[Nom][Du]", ""),
    pn.cross("kroṣṭu", "kroṣṭārau") + masc_tag + pn.cross("[Acc][Du]", ""),
    pn.cross("kroṣṭu", "kroṣṭubhyām") + masc_tag + pn.cross("[Ins][Du]", ""),
    pn.cross("kroṣṭu", "kroṣṭāraḥ") + masc_tag + pn.cross("[Nom][Pl]", ""),
    pn.cross("kroṣṭu", "kroṣṭūn") + masc_tag + pn.cross("[Acc][Pl]", ""),
    pn.cross("kroṣṭu", "kroṣṭubhiḥ") + masc_tag + pn.cross("[Ins][Pl]", ""),
    pn.cross("kroṣṭu", "kroṣṭūnām") + masc_tag + pn.cross("[Gen][Pl]", ""),
    pn.cross("kroṣṭu", "kroṣṭuṣu") + masc_tag + pn.cross("[Loc][Pl]", ""),
).optimize()

# =============================================================================
# 10. LAKṢMĪ NOMINATIVE OVERRIDE
# =============================================================================
laksmi_paradigm = (
    pn.cross("lakṣmī", "lakṣmīs") + fem_tag + pn.cross("[Nom][Sg]", "")
).optimize()

# =============================================================================
# 11. MAHAT PARADIGM (Great - Shifting Consonant Stem)
# =============================================================================
# Vowel long-lengthening occurs strictly in masculine strong cases.
mahat_paradigm = pn.union(
    pn.cross("mahat", "mahān") + masc_tag + pn.cross("[Nom][Sg]", ""),
    pn.cross("mahat", "mahāntam") + masc_tag + pn.cross("[Acc][Sg]", ""),
    pn.cross("mahat", "mahān") + masc_tag + pn.cross("[Voc][Sg]", ""),
    pn.cross("mahat", "mahāntau") + masc_tag + pn.cross("[Nom][Du]", ""),
    pn.cross("mahat", "mahāntau") + masc_tag + pn.cross("[Acc][Du]", ""),
    pn.cross("mahat", "mahāntau") + masc_tag + pn.cross("[Voc][Du]", ""),
    pn.cross("mahat", "mahāntaḥ") + masc_tag + pn.cross("[Nom][Pl]", ""),
    # Weak cases drop nasal and remain short
    pn.cross("mahat", "mahatā") + masc_tag + pn.cross("[Ins][Sg]", ""),
    pn.cross("mahat", "mahataḥ") + masc_tag + pn.cross("[Acc][Pl]", ""),
    pn.cross("mahat", "mahadbhyām") + masc_tag + pn.cross("[Ins][Du]", ""),
    pn.cross("mahat", "mahadbhis") + masc_tag + pn.cross("[Ins][Pl]", ""),

    # --- Feminine (declines like nadī on stem mahatī) ---
    pn.cross("mahat", "mahatī") + fem_tag + pn.cross("[Nom][Sg]", ""),
    pn.cross("mahat", "mahatīm") + fem_tag + pn.cross("[Acc][Sg]", ""),
    pn.cross("mahat", "mahatyā") + fem_tag + pn.cross("[Ins][Sg]", ""),
    pn.cross("mahat", "mahatyai") + fem_tag + pn.cross("[Dat][Sg]", ""),
    pn.cross("mahat", "mahatyās") + fem_tag + pn.cross("[Abl][Sg]", ""),
    pn.cross("mahat", "mahatyās") + fem_tag + pn.cross("[Gen][Sg]", ""),
    pn.cross("mahat", "mahatyām") + fem_tag + pn.cross("[Loc][Sg]", ""),
    pn.cross("mahat", "mahati") + fem_tag + pn.cross("[Voc][Sg]", ""),
    pn.cross("mahat", "mahatyau") + fem_tag + pn.cross("[Nom][Du]", ""),
    pn.cross("mahat", "mahatyau") + fem_tag + pn.cross("[Acc][Du]", ""),
    pn.cross("mahat", "mahatyau") + fem_tag + pn.cross("[Voc][Du]", ""),
    pn.cross("mahat", "mahatībhyām") + fem_tag + pn.cross("[Ins][Du]", ""),
    pn.cross("mahat", "mahatībhyām") + fem_tag + pn.cross("[Dat][Du]", ""),
    pn.cross("mahat", "mahatībhyām") + fem_tag + pn.cross("[Abl][Du]", ""),
    pn.cross("mahat", "mahatyos") + fem_tag + pn.cross("[Gen][Du]", ""),
    pn.cross("mahat", "mahatyos") + fem_tag + pn.cross("[Loc][Du]", ""),
    pn.cross("mahat", "mahatyaḥ") + fem_tag + pn.cross("[Nom][Pl]", ""),
    pn.cross("mahat", "mahatīs") + fem_tag + pn.cross("[Acc][Pl]", ""),
    pn.cross("mahat", "mahatyaḥ") + fem_tag + pn.cross("[Voc][Pl]", ""),
    pn.cross("mahat", "mahatībhis") + fem_tag + pn.cross("[Ins][Pl]", ""),
    pn.cross("mahat", "mahatībhyas") + fem_tag + pn.cross("[Dat][Pl]", ""),
    pn.cross("mahat", "mahatībhyas") + fem_tag + pn.cross("[Abl][Pl]", ""),
    pn.cross("mahat", "mahatīnām") + fem_tag + pn.cross("[Gen][Pl]", ""),
    pn.cross("mahat", "mahatīṣu") + fem_tag + pn.cross("[Loc][Pl]", ""),
).optimize()

# =============================================================================
# 12. ŚVAN & YUVAN PARADIGMS (Dog / Youth - Samprasāraṇa Weak Stems)
# =============================================================================
# These undergo internal vowel collapse (va -> u) exclusively in weak cases.
svan_paradigm = pn.union(
    pn.cross("śvan", "śvā") + masc_tag + pn.cross("[Nom][Sg]", ""),
    pn.cross("śvan", "śvānam") + masc_tag + pn.cross("[Acc][Sg]", ""),
    pn.cross("śvan", "śvānau") + masc_tag + pn.cross("[Nom][Du]", ""),
    pn.cross("śvan", "śvānaḥ") + masc_tag + pn.cross("[Nom][Pl]", ""),
    # Samprasāraṇa weak mutations (śvan -> śun)
    pn.cross("śvan", "śunā") + masc_tag + pn.cross("[Ins][Sg]", ""),
    pn.cross("śvan", "śunaḥ") + masc_tag + pn.cross("[Gen][Sg]", ""),
    pn.cross("śvan", "śunaḥ") + masc_tag + pn.cross("[Acc][Pl]", ""),
    # Middle cases act like normal consonant stems (drop n)
    pn.cross("śvan", "śvabhyām") + masc_tag + pn.cross("[Ins][Du]", ""),
    pn.cross("śvan", "śvabhis") + masc_tag + pn.cross("[Ins][Pl]", ""),
).optimize()

yuvan_paradigm = pn.union(
    pn.cross("yuvan", "yuvā") + masc_tag + pn.cross("[Nom][Sg]", ""),
    pn.cross("yuvan", "yuvānam") + masc_tag + pn.cross("[Acc][Sg]", ""),
    pn.cross("yuvan", "yuvānau") + masc_tag + pn.cross("[Nom][Du]", ""),
    pn.cross("yuvan", "yuvānaḥ") + masc_tag + pn.cross("[Nom][Pl]", ""),
    # Samprasāraṇa weak mutations (yuvan -> yūn)
    pn.cross("yuvan", "yūnā") + masc_tag + pn.cross("[Ins][Sg]", ""),
    pn.cross("yuvan", "yūnaḥ") + masc_tag + pn.cross("[Gen][Sg]", ""),
    pn.cross("yuvan", "yūnaḥ") + masc_tag + pn.cross("[Acc][Pl]", ""),
    # Middle
    pn.cross("yuvan", "yuvabhyām") + masc_tag + pn.cross("[Ins][Du]", ""),
    pn.cross("yuvan", "yuvabhis") + masc_tag + pn.cross("[Ins][Pl]", ""),
).optimize()

# =============================================================================
# 13. MAGHAVAN PARADIGM (Indra - Dual Paradigm Base)
# =============================================================================
# Panini permits this to inflect either with full Samprasāraṇa (maghaun-)
# OR completely parallel to regular matup suffix stems (maghavat-).
maghavan_paradigm = pn.union(
    pn.cross("maghavan", "maghavā") + masc_tag + pn.cross("[Nom][Sg]", ""),
    # Weak Branch 1: Samprasāraṇa Collapse
    pn.cross("maghavan", "maghonaḥ") + masc_tag + pn.cross("[Acc][Pl]", ""),
    pn.cross("maghavan", "maghonā") + masc_tag + pn.cross("[Ins][Sg]", ""),
    # Weak Branch 2: Suffixal T-Stem Transition
    pn.cross("maghavan", "maghavataḥ") + masc_tag + pn.cross("[Acc][Pl]", ""),
    pn.cross("maghavan", "maghavatā") + masc_tag + pn.cross("[Ins][Sg]", ""),
    # Middle Cases
    pn.cross("maghavan", "maghavabhyām") + masc_tag + pn.cross("[Ins][Du]", ""),
    pn.cross("maghavan", "maghavadbhyām") + masc_tag + pn.cross("[Ins][Du]", ""),
).optimize()

# =============================================================================
# 14. AHAN PARADIGM (Day - Irregular Neuter an-stem)
# =============================================================================
# Mutates completely into alternating word endings 'ahaḥ', 'aha', and 'aho'
ahan_paradigm = pn.union(
    pn.cross("ahan", "ahaḥ") + neut_tag + pn.cross("[Nom][Sg]", ""),
    pn.cross("ahan", "ahaḥ") + neut_tag + pn.cross("[Acc][Sg]", ""),
    pn.cross("ahan", "ahan") + neut_tag + pn.cross("[Voc][Sg]", ""),
    pn.cross("ahan", "ahne") + neut_tag + pn.cross("[Dat][Sg]", ""),
    pn.cross("ahan", "ahnaḥ") + neut_tag + pn.cross("[Gen][Sg]", ""),
    # Dual / Plural Strong
    pn.cross("ahan", "ahnī") + neut_tag + pn.cross("[Nom][Du]", ""),
    pn.cross("ahan", "ahāni") + neut_tag + pn.cross("[Nom][Pl]", ""),
    # Middle cases transform base final to r/s variations before bh entries
    pn.cross("ahan", "ahobhyām") + neut_tag + pn.cross("[Ins][Du]", ""),
    pn.cross("ahan", "ahobhiḥ") + neut_tag + pn.cross("[Ins][Pl]", ""),
    pn.cross("ahan", "ahaḥsu") + neut_tag + pn.cross("[Loc][Pl]", ""),
).optimize()

# =============================================================================
# UPDATED MASTER PIPELINE COMPILATION
# =============================================================================
all_irregular_nouns_paradigm = pn.union(
    sakhi_paradigm,
    rai_paradigm,
    pati_paradigm,
    go_paradigm,
    nau_paradigm,
    div_paradigm,
    four_neuters_paradigm,
    stri_paradigm,
    panthan_paradigm,
    krostu_paradigm,
    laksmi_paradigm,
    mahat_paradigm,
    svan_paradigm,
    yuvan_paradigm,
    maghavan_paradigm,
    ahan_paradigm,
).optimize()

