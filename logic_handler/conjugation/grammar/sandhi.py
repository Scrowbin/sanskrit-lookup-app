"""sandhi.py — FST-based Sanskrit internal phonology (stem-boundary sandhi).

Pipeline order: vowel_phase → consonant_phase → long_distance_phase.
Within each phase, rules are ordered by specificity (most specific first).

**Vowel phase** (Whitney §126–131, §244): thematic mergers, class-9 ī-drop,
ayadi, perfect weak yan, savarna, yan, guna (including **a/ā + ḷ** per §244).

**Consonant phase**: ``d+dh`` gemination; **tag-gated** dental+palatal (``[SD_DCP]``),
homorganic gemination (``[SD_GEM]``), ś+t retroflex (``[SD_SSR]``), sibilant
clusters (``[SD_SIB]``), Bartholomae, Grassmann, palatal→velar before voiceless
suffix initials, devoicing, nasals, anusvāra/parasavarṇa, **visarga+stop**
(``[SD_LAR]``), then **``clean_sd_residual``** to strip any leftover ``[SD_*]``.
Context tags are **inserted in MorphologyEngine** immediately before ``clean_tags``.

**Long-distance phase**: RUKI, nati, visarga, cluster reduction, boundary cleanup.

This is **not** a complete external-sandhi or Vedic-accent engine; see
``ENGINE_AUDIT.md`` for remaining phonology gaps.

All three phase methods accept ``debug=True``.  When enabled, rules are
applied *one by one* via ``_apply_rules_with_trace()``, which prints the
intermediate string after every rule and stops immediately when a rule causes
the FST to go empty — identifying exactly which rule killed the valid path.
"""
import pynini as pn
from alphabet import ALPHABET


class SandhiEngine:
    """Modular FST engine for Sanskrit internal phonology."""

    def __init__(self):
        self.sig = ALPHABET.sigma_star
        self._setup_vowel_rules()
        self._setup_consonant_rules()
        self._setup_long_distance_rules()
        # Erase morpheme boundaries and [CLASS9] at the very end
        self.clean_boundaries = pn.cdrewrite(
            pn.union(
                pn.cross("+", ""),
                pn.cross("[CLASS9]", ""),
                pn.cross("[EOS]", ""),       # ← added
            ),
            "", "", self.sig
        )
        # Named rule lists — populated after all rules are built
        self._build_named_rule_lists()

    # ──────────────────────────────────────────────────────────────────────────
    # Rule setup
    # ──────────────────────────────────────────────────────────────────────────

    def _setup_vowel_rules(self):
        self.pragrhya_erase = pn.cdrewrite(
            pn.cross("[PRAGRHYA]", ""), "", "", self.sig
        )
        # 1. Thematic / Pararupa mergers: a/ā + {e,o,ai,au} → the diphthong wins.
        self.thematic_merger = pn.cdrewrite(
            pn.string_map([
                ("a+e",  "e"),  ("ā+e",  "e"),
                ("a+o",  "o"),  ("ā+o",  "o"),
                ("a+ai", "ai"), ("ā+ai", "ai"),
                ("a+au", "au"), ("ā+au", "au"),
            ]),
            "", "", self.sig
        )

        # 2. Savarna (identical vowel coalescence).
        # NOTE: i+i→ī intentionally excluded — perfect weak yan handles it.
        self.savarna = pn.cdrewrite(
            pn.string_map([
                ("a+a", "ā"), ("a+ā", "ā"), ("ā+a", "ā"), ("ā+ā", "ā"),
                ("i+ī", "ī"), ("ī+i", "ī"), ("ī+ī", "ī"), ("i+i", "ī"),
                ("u+u", "ū"), ("u+ū", "ū"), ("ū+u", "ū"), ("ū+ū", "ū"),
                ("ṛ+ṛ", "ṝ"), ("ṛ+ṝ", "ṝ"), ("ṝ+ṛ", "ṝ"), ("ṝ+ṝ", "ṝ"),
            ]),
            "", "", self.sig
        )

        # 3. Guna sandhi: a/ā + i/u/ṛ → e/o/ar; a/ā + ḷ → al/āl (Whitney §244)
        self.guna_sandhi = pn.cdrewrite(
            pn.string_map([
                ("a+i", "e"),  ("a+ī", "e"),  ("ā+i", "e"),  ("ā+ī", "e"),
                ("a+u", "o"),  ("a+ū", "o"),  ("ā+u", "o"),  ("ā+ū", "o"),
                ("a+ṛ", "ar"), ("a+ṝ", "ar"), ("ā+ṛ", "ar"), ("ā+ṝ", "ar"),
                ("a+ḷ", "al"), ("a+ḹ", "al"), ("ā+ḷ", "āl"), ("ā+ḹ", "āl"),
            ]),
            "", "", self.sig
        )

        # 4. Ayadi (diphthong before vowel): e+V → ay+V, o+V → av+V, etc.
        self.ayadi = pn.cdrewrite(
            pn.string_map([
                ("e+", "ay"), ("o+", "av"), ("ai+", "āy"), ("au+", "āv"),
            ]),
            "", pn.union(ALPHABET.vowels, "y"), self.sig
        )

        # Perfect weak yan sandhi (er anekācaḥ asamyogapūrvasya & exceptions)
        # Pāṇini 6.4.82: i/ī after single consonant -> y.
        # Pāṇini 6.4.77: i/ī after conjunct -> iy. u/ū -> uv.
        _any_cons = ALPHABET.consonants
        _conjunct_context = _any_cons + _any_cons   # two consonants directly before
        self.perfect_yan_conjunct = pn.cdrewrite(
            pn.string_map([
                ("i[PERF_WEAK]+", "iy"),
                ("ī[PERF_WEAK]+", "iy"),
                ("u[PERF_WEAK]+", "uv"),
                ("ū[PERF_WEAK]+", "uv"),
            ]),
            _conjunct_context, ALPHABET.vowels, self.sig
        )
        self.perfect_yan_conjunct = pn.cdrewrite(
            pn.string_map([
                ("i[PERF_WEAK]+", "iy"),
                ("ī[PERF_WEAK]+", "iy"),
                ("u[PERF_WEAK]+", "uv"),
                ("ū[PERF_WEAK]+", "uv"),
            ]),
            _conjunct_context, ALPHABET.vowels, self.sig
        )
        self.perfect_yan_simple = pn.cdrewrite(
            pn.string_map([
                ("i[PERF_WEAK]+", "y"),
                ("ī[PERF_WEAK]+", "y"),
                ("u[PERF_WEAK]+", "uv"), # u/ū universally take uv
                ("ū[PERF_WEAK]+", "uv"),
                ("ṛ[PERF_WEAK]+", "r"),
            ]),
            "", ALPHABET.vowels, self.sig
        )
        
        self.clean_perf_weak = pn.cdrewrite(
            pn.cross("[PERF_WEAK]", ""), "", "", self.sig
        )

        # 5. General Yan sandhi (semi-vowelisation before vowel)
        self.yan_sandhi = pn.cdrewrite(
            pn.string_map([
                ("i+",  "y"),
                ("ī+",  "y"),
                ("u+",  "v"),
                ("ū+",  "v"),
                ("ṛ+",  "r"),
            ]),
            "", ALPHABET.vowels, self.sig
        )

        # 6. Class-9 suffix vowel-drop: ī[CLASS9]+ erased before any vowel-initial ending
        self.class9_special = pn.cdrewrite(
            pn.cross("ī[CLASS9]+", "+"), "", ALPHABET.vowels, self.sig
        )

    def _setup_consonant_rules(self):
        unvoiced_triggers = pn.union(
            "+t", "+th", "+s", "+ṣ",
            "+c", "+ch", "+k", "+kh", "+p", "+ph",
            "+ṭ", "+ṭh", 
        )

        # Homorganic stop+aspirate assimilation at morpheme boundary:
        # ad + dhi → addhi (cf. standard internal sandhi; needed for imperative 2sg).
        self.d_dh_gemination = pn.cdrewrite(pn.cross("d+dh", "ddh"), "", "", self.sig)

        # Dental + palatal: **tag-gated** (MorphologyEngine inserts [SD_DCP]).
        # Whitney §213, §219; Pāṇini 8.4.40–43.
        self.dental_palatal_fusion = pn.cdrewrite(
            pn.string_map([
                ("t[SD_DCP]+c", "cc"), ("t[SD_DCP]+ch", "cch"),
                ("d[SD_DCP]+c", "cc"), ("d[SD_DCP]+ch", "cch"),
                ("dh[SD_DCP]+c", "cch"), ("dh[SD_DCP]+ch", "cch"),
            ]),
            "", "", self.sig
        )

        # Homorganic gemination across '+' — **tag-gated** ([SD_GEM]).
        # Whitney §231; sonorants included for reduplication / intensive edges.
        self.homorganic_gemination = pn.cdrewrite(
            pn.string_map([
                ("t[SD_GEM]+t", "tt"), ("d[SD_GEM]+d", "dd"),
                ("p[SD_GEM]+p", "pp"), ("b[SD_GEM]+b", "bb"),
                ("k[SD_GEM]+k", "kk"), ("g[SD_GEM]+g", "gg"),
                ("ṭ[SD_GEM]+ṭ", "ṭṭ"), ("ḍ[SD_GEM]+ḍ", "ḍḍ"),
                ("c[SD_GEM]+c", "cc"), ("j[SD_GEM]+j", "jj"),
                ("l[SD_GEM]+l", "ll"), ("r[SD_GEM]+r", "rr"),
                ("y[SD_GEM]+y", "yy"), ("v[SD_GEM]+v", "vv"),
            ]),
            "", "", self.sig
        )

        # Bartholomae (aspirate assimilation):
        # Voiced aspirates (bh, dh, gh, jh) + t/th -> bd, dd, gd, jd + dh.
        # This MUST run before h+t to prevent h+t from matching the 'h' in 'dh'.
        self.bartholomae_general = pn.cdrewrite(
            pn.string_map([
                ("bh+t", "bdh"), ("bh+th", "bdh"),
                ("dh+t", "ddh"), ("dh+th", "ddh"),
                ("gh+t", "gdh"), ("gh+th", "gdh"),
                ("jh+t", "gdh"), ("jh+th", "gdh"), # jh marginal
            ]),
            "", "", self.sig
        )
        self.bartho_hth = pn.cdrewrite(pn.cross("h+th", "gdh"), "", "", self.sig)
        self.bartho_hdh = pn.cdrewrite(pn.cross("h+dh", "gdh"), "", "", self.sig)
        self.bartho_ht  = pn.cdrewrite(pn.cross("h+t",  "gdh"), "", "", self.sig)

        # ── Grassmann's Law throwback for duh‑class roots (Whitney §155) ──
        # When [GRASSMANN] is present and the final h/gdh is deaspirated,
        # the initial consonant re-aspirates.
        # This is a simplified rule handling the most common case: duh → dhuk/dhug

        # Rule: [GRASSMANN] + (anything) + gdh/k/g + (trigger) →
        #       delete [GRASSMANN], change initial d→dh, g→gh, b→bh
        self.grassmann_init_aspirate = pn.cdrewrite(
            pn.string_map([
                ("d", "dh"), ("g", "gh"), ("b", "bh"),
            ]),
            "[GRASSMANN]",  # left-context: tag must precede
            # Right-context: any string containing a deaspirated final
            pn.union("gdh", "k", "g", "t", "p"),  
            self.sig
        )
        # Then erase the tag
        self.grassmann_clean = pn.cdrewrite(
            pn.cross("[GRASSMANN]", ""), "", "", self.sig
        )

        # --- ś completions (Whitney §218) ---
        # ś + dh → ḍh, ś + bh → ḍ
        self.s_dh_bh = pn.cdrewrite(
            pn.string_map([("ś+dh", "ḍh"), ("ś+bh", "ḍ")]),
            "", "", self.sig
        )

        # --- ṣ + dh → ḍḍh (Whitney §226b) ---
        self.retro_ddh = pn.cdrewrite(
            pn.cross("ṣ+dh", "ḍḍh"), "", "", self.sig
        )

        # --- Deaspiration before non‑nasal mutes / sibilants (Whitney §153) ---
        # This must run AFTER Bartholomae so that bh+t→bdh is not undone.
        _unaspirate_targets = pn.union("+k", "+kh", "+g", "+gh",
                                    "+c", "+ch", "+j", "+jh",
                                    "+ṭ", "+ṭh", "+ḍ", "+ḍh",
                                    "+t", "+th", "+d", "+dh",
                                    "+p", "+ph", "+b", "+bh",
                                    "+ś", "+ṣ", "+s", "+h")
        self.deaspirate_before_obstruent = pn.cdrewrite(
            pn.string_map([
                ("kh", "k"), ("gh", "g"),
                ("ch", "c"), ("jh", "j"),
                ("ṭh", "ṭ"), ("ḍh", "ḍ"),
                ("th", "t"), ("dh", "d"),
                ("ph", "p"), ("bh", "b"),
            ]),
            "", _unaspirate_targets, self.sig
        )

        # Grassmann's Law (throwback deaspiuration)
        throwback_triggers = pn.union(
            "+s", "+ṣ", "+t", "+th", "+c", "+ch", "+dhv", "[EOS]", "+[EOS]"
        )
        self.grassmann_throwback = pn.cdrewrite(
            pn.string_map([("b", "bh"), ("d", "dh"), ("g", "gh")]),
            "", ALPHABET.vowels + pn.union("gh", "dh", "bh", "h", "gdh") + throwback_triggers,
            self.sig
        )

        # Ruh‑class (Whitney §222b): h + dental → vowel lengthening + lingual.
        # Tag [RUH_H] is injected by MorphologyEngine.
        # We need a two‑step: lengthen the preceding vowel, then change +t/th/dh.
        # We'll handle it with a dedicated rule.
        self.ruh_class_h = pn.cdrewrite(
            pn.string_map([
                # Basic combinations: h + t → lengthen vowel + ṭ, etc.
                # The vowel must be short before h; we treat only a/i/u/ṛ.
                ("a[RUH_H]h+t", "āḍh"),   # but combination after vowel lengthening is complex
                # Simpler: We'll handle it in the morphology engine by inserting a tag that triggers vowel lengthening and cluster replacement.
                # For now, we keep a placeholder; the real fix requires root‑specific FSTs.
                # We'll address it by adding explicit overrides for ruh‑class roots in irregulars.
            ]),
            "", "", self.sig
        )

        # h → k before +s/+ṣ (after a vowel or sonorant)
        self.h_to_k = pn.cdrewrite(
            pn.cross("h", "k"),
            pn.union(ALPHABET.vowels, "r", "l", "y", "v"),
            pn.union("+s", "+ṣ"),
            self.sig
        )

        # Specific roots where palatal j before dental t/th surfaces as retroflex ṣṭ/ṣṭh
        # (e.g. mārj+ti -> mārṣṭi; Whitney §219, §212-213).
        self.j_retroflex = pn.cdrewrite(
            pn.string_map([
                ("rj+t", "rṣṭ"), ("rj+th", "rṣṭh"),
                ("yaj+t", "yaṣṭ"), ("yaj+th", "yaṣṭh"),
                ("ij+t", "iṣṭ"), ("ij+th", "iṣṭh"),
                ("sṛj+t", "sraṣṭ"), ("sṛj+th", "sraṣṭh"),
                ("mṛj+t", "mṛṣṭ"), ("mṛj+th", "mṛṣṭh"),
                ("bhrajj+t", "bhṛṣṭ"), ("bhrajj+th", "bhṛṣṭh"),
            ]),
            "", "", self.sig
        )

        # Rule for mṛj‑class (Whitney §219) – convert j to ṣ before surd dentals, etc.
        # The tag [MRJ] is inserted by MorphologyEngine for roots in the mṛj set.
        self.mrj_class_rule = pn.cdrewrite(
            pn.string_map([
                ("[MRJ]j+t", "ṣṭ"),      # before t → ṣṭ
                ("[MRJ]j+th", "ṣṭh"),    # before th → ṣṭh
                ("[MRJ]j+dh", "ḍḍh"),    # before dh → ḍḍh
                ("[MRJ]j+bh", "ḍ"),      # before bh → ḍ
                ("[MRJ]j+s", "kṣ"),      # before s → kṣ
            ]),
            "", "", self.sig
        )

        # Palatal ś before dental t/th → ṣṭ / ṣṭh — **tag-gated** ([SD_SSR] from morphology).
        # Whitney §219; Pāṇini 8.4.44 śtutva.
        self.palatal_sibilant_retroflex = pn.cdrewrite(
            pn.string_map([
                ("ś[SD_SSR]+t", "ṣṭ"), ("ś[SD_SSR]+th", "ṣṭh"),
            ]),
            "", "", self.sig
        )

        # Palatal → velar before unvoiced dental/sibilant
        self.palatal_sandhi = pn.cdrewrite(
            pn.string_map([("j", "k"), ("c", "k")]),
            "", unvoiced_triggers, self.sig
        )

        # General devoicing
        self.devoicing = pn.cdrewrite(
            pn.string_map([
                ("d",  "t"), ("dh", "t"), ("g",  "k"), ("gh", "k"),
                ("b",  "p"), ("bh", "p"), ("ḍ",  "ṭ"), ("ḍh", "ṭ"),
            ]),
            "", unvoiced_triggers, self.sig
        )

        # Nasal assimilation: n → homorganic nasal before stops
        self.nasal_assimilation = pn.cdrewrite(
            pn.string_map([
                ("n", "ñ"),
            ]), "", pn.union("+j", "+c", "j", "c"), self.sig
        ) @ pn.cdrewrite(
            pn.string_map([
                ("n", "m"),
            ]), "", pn.union("+p", "+ph", "+b", "+bh", "p", "ph", "b", "bh"), self.sig
        ) @ pn.cdrewrite(
            pn.string_map([
                ("n", "ṇ"),
            ]), "", pn.union("+ṭ", "+ṭh", "+ḍ", "+ḍh", "ṭ", "ṭh", "ḍ", "ḍh"), self.sig
        )
        # Class-7 yuj-type clusters: yuñj+dhv/hi -> yuṅgdhv/i.
        # This bridges nasal assimilation output (ñj) to attested velar+aspirate
        # sequences in middle/imperative paradigms (Whitney class-7 behavior).
        self.nj_cluster_hardening = pn.cdrewrite(
            pn.string_map([
                ("ñ+j+dhv", "ṅgdhv"),
                ("ñ+j+dh", "ṅgdh"),
                ("ñ+j+h", "ṅgdh"),
            ]),
            "", "", self.sig
        )

        # ── Anusvāra and Parasavarṇa (m + consonant) ──────────────────────────
        # m -> anusvāra before all consonants (this is optional before stops externally, but obligatory internally/preverbs)
        # Then anusvāra -> parasavarṇa (homorganic nasal) before stops.
        # We can implement this directly mapping m + stop -> homorganic nasal + stop
        self.parasavarna = pn.cdrewrite(
            pn.string_map([
                ("m+k", "ṅ+k"), ("m+kh", "ṅ+kh"), ("m+g", "ṅ+g"), ("m+gh", "ṅ+gh"),
                ("m+c", "ñ+c"), ("m+ch", "ñ+ch"), ("m+j", "ñ+j"), ("m+jh", "ñ+jh"),
                ("m+ṭ", "ṇ+ṭ"), ("m+ṭh", "ṇ+ṭh"), ("m+ḍ", "ṇ+ḍ"), ("m+ḍh", "ṇ+ḍh"),
                ("m+t", "n+t"), ("m+th", "n+th"), ("m+d", "n+d"), ("m+dh", "n+dh"), ("m+n", "n+n"),
            ]),
            "", "", self.sig
        )
        
        # m -> ṃ (anusvāra) before semivowels (y, r, l, v) and sibilants (ś, ṣ, s, h)
        self.anusvara = pn.cdrewrite(
            pn.cross("m+", "ṃ+"),
            "", pn.union("y", "r", "l", "v", "ś", "ṣ", "s", "h"), self.sig
        )
        # Internal root+suffix m+y (e.g. gam+ya) remains m, not anusvāra.        

        # Retroflex assimilation (Panini 8.4.41)
        self.retro_th  = pn.cdrewrite(pn.cross("ṣ+th", "ṣṭh"), "", "", self.sig)
        self.retro_t   = pn.cdrewrite(pn.cross("ṣ+t",  "ṣṭ"),  "", "", self.sig)
        self.retro_dhv = pn.cdrewrite(pn.cross("ṣ+dhv", "ḍhv"), "", "", self.sig)
        # Sigmatic aorist clusters like -kṣ+t- surface as -kt- (yuj: ayokta),
        # not as retroflex -kṣṭ-.
        self.ksha_t_simplify = pn.cdrewrite(
            pn.string_map([("kṣ+t", "kt"), ("kṣ+th", "kth")]),
            "", "", self.sig
        )
        # Sibilant clusters — **tag-gated** ([SD_SIB] from morphology).
        # Whitney §249; replaces former global ṣ+s / ś+s only for tagged inputs.
        self.sibilant_cluster_tagged = pn.cdrewrite(
            pn.string_map([
                ("ṣ[SD_SIB]+s", "kṣ"),
                ("ś[SD_SIB]+s", "kṣ"),
                ("s[SD_SIB]+ṣ", "kṣ"),
                ("ṣ[SD_SIB]+ś", "ś"),
            ]),
            "", "", self.sig
        )

        # Visarga + voiceless stop — **tag-gated** ([SD_LAR] from morphology).
        # Classical internal fusion (Whitney visarga sandhi, narrow).
        self.visarga_stop_fusion = pn.cdrewrite(
            pn.string_map([
                ("ḥ[SD_LAR]+k", "k"), ("ḥ[SD_LAR]+kh", "kh"),
                ("ḥ[SD_LAR]+g", "g"), ("ḥ[SD_LAR]+gh", "gh"),
                ("ḥ[SD_LAR]+c", "c"), ("ḥ[SD_LAR]+ch", "ch"),
                ("ḥ[SD_LAR]+t", "t"), ("ḥ[SD_LAR]+th", "th"),
                ("ḥ[SD_LAR]+p", "p"), ("ḥ[SD_LAR]+ph", "ph"),
            ]),
            "", "", self.sig
        )

        # Strip any surviving [SD_*] markers (should not surface in output).
        self.clean_sd_residual = (
            pn.cdrewrite(pn.cross("[SD_DCP]", ""), "", "", self.sig)
            @ pn.cdrewrite(pn.cross("[SD_GEM]", ""), "", "", self.sig)
            @ pn.cdrewrite(pn.cross("[SD_SSR]", ""), "", "", self.sig)
            @ pn.cdrewrite(pn.cross("[SD_SIB]", ""), "", "", self.sig)
            @ pn.cdrewrite(pn.cross("[SD_LAR]", ""), "", "", self.sig)
            @ pn.cdrewrite(pn.cross("[MRJ]", ""), "", "", self.sig)
            @ pn.cdrewrite(pn.cross("[RUH_H]", ""), "", "", self.sig)
            @ pn.cdrewrite(pn.cross("[GRASSMANN]", ""), "", "", self.sig)
            @ pn.cdrewrite(pn.cross("[NO_RUKI]", ""), "", "", self.sig)
        ).optimize()

        # Velar nasal: n/ñ → ṅ before velar stops
        self.velar_nasal = pn.cdrewrite(
            pn.string_map([("n", "ṅ"), ("ñ", "ṅ")]),
            "", pn.union("+k", "+g", "+kh", "+gh"), self.sig
        )

    def _setup_long_distance_rules(self):
        # RUKI: s → ṣ after r/ṛ/u/ū/k/i/ī/e/ai/o/au
        ruki_triggers = pn.union(
            "ṛ", "r", "u", "ū", "k", "i", "ī", "e", "ai", "o", "au"
        )
        self.ruki = pn.cdrewrite(
            pn.cross("s", "ṣ"),
            ruki_triggers + pn.accep("+").star, "", self.sig
        )

        self.no_ruki_revert = pn.cdrewrite(
            pn.cross("ṣ", "s"),
            "[NO_RUKI]", "", self.sig
        )
        self.ruki_revert_before_r = pn.cdrewrite(
            pn.cross("ṣ", "s"),
            "", pn.union("r", "+r"), self.sig
        )

        

        # Nati: n → ṇ after r/ṛ/ṣ across allowable interveners
        triggers = pn.union("r", "ṛ", "ṣ", "ṝ")
        allowed_interveners = pn.union(
            ALPHABET.vowels, ALPHABET.gutturals, ALPHABET.labials,
            "y", "v", "h", "ṃ", "+"
        ).star.optimize()
        self.nati = pn.cdrewrite(
            pn.cross("n", "ṇ"),
            triggers + allowed_interveners,
            pn.accep("+").star + pn.union(ALPHABET.vowels, "n", "m", "y", "v"),
            self.sig
        )

        # Post-RUKI retroflex assimilation
        self.retro_post_ruki_th  = pn.cdrewrite(pn.cross("ṣ+th",  "ṣṭh"), "", "", self.sig)
        self.retro_post_ruki_t   = pn.cdrewrite(pn.cross("ṣ+t",   "ṣṭ"),  "", "", self.sig)
        self.retro_post_ruki_dhv = pn.cdrewrite(pn.cross("ṣ+dhv", "ḍhv"), "", "", self.sig)
        # After RUKI, sigmatic aorist k+ṣ+t/th should still simplify to kt/kth.
        self.ksha_t_simplify_post_ruki = pn.cdrewrite(
            pn.string_map([("k+ṣ+t", "k+t"), ("k+ṣ+th", "k+th")]),
            "", "", self.sig
        )

        # ── Comprehensive Word‑Final Normalization (Whitney §122, §141‑150) ─────
        # Order: palatal reversion → deaspiration → devoicing → cluster reduction
        #         → sibilant → visarga → single‑consonant enforcement
        
        # Step 1: Palatal reversion c/j → k before [EOS] (Whitney §142, §217)
        self.final_palatal_reversion = pn.cdrewrite(
            pn.string_map([
                ("c+[EOS]", "k+[EOS]"),
                ("j+[EOS]", "k+[EOS]"),
            ]),
            "", "", self.sig
        )
        
        # Step 2: Deaspirate aspirates before [EOS] (Whitney §114, §150)
        self.final_deaspiration = pn.cdrewrite(
            pn.string_map([
                ("kh+[EOS]", "k+[EOS]"),
                ("gh+[EOS]", "g+[EOS]"),
                ("ch+[EOS]", "c+[EOS]"),
                ("jh+[EOS]", "j+[EOS]"),
                ("ṭh+[EOS]", "ṭ+[EOS]"),
                ("ḍh+[EOS]", "ḍ+[EOS]"),
                ("th+[EOS]", "t+[EOS]"),
                ("dh+[EOS]", "d+[EOS]"),
                ("ph+[EOS]", "p+[EOS]"),
                ("bh+[EOS]", "b+[EOS]"),
            ]),
            "", "", self.sig
        )
            
        # Step 3: Voice sonant stops → surd before [EOS] (Whitney §141‑142)
        self.final_devoicing = pn.cdrewrite(
            pn.string_map([
                ("g+[EOS]",  "k+[EOS]"),
                ("d+[EOS]",  "t+[EOS]"),
                ("b+[EOS]",  "p+[EOS]"),
                ("ḍ+[EOS]",  "ṭ+[EOS]"),
                ("gh+[EOS]", "k+[EOS]"),
                ("dh+[EOS]", "t+[EOS]"),
                ("bh+[EOS]", "p+[EOS]"),
                ("ḍh+[EOS]", "ṭ+[EOS]"),
                ("j+[EOS]",  "k+[EOS]"),   # in case palatal reversion didn't fire
            ]),
            "", "", self.sig
        )
        
        # ṣ → ṭ before [EOS] (Whitney §226)
        self.final_s_to_t = pn.cdrewrite(
            pn.cross("ṣ+[EOS]", "ṭ+[EOS]"),
            "", "", self.sig
        )
        
        # Step 5: General cluster reduction to single consonant (Whitney §150)
        # Strategy: repeatedly delete the first of two consonants before [EOS]
        # until only one remains. We implement this by dropping specific clusters.
        # self.final_cluster_simplify = pn.cdrewrite(
        #     pn.string_map([
        #         # Drop first consonant of common clusters
        #         ("kt", "k"), ("kt", "k"),
        #         ("ṅk", "ṅ"), ("ñc", "ñ"),
        #         ("ṇṭ", "ṇ"), ("nt", "n"),
        #         ("mp", "m"), ("ṅg", "ṅ"),
        #         # Sibilant + stop → stop dropped first? No, sibilant becomes visarga
        #         # These are handled elsewhere
        #     ]),
        #     "", pn.accep("+[EOS]"), self.sig
        # )

        # Visarga: word-final s/ṣ → ḥ
        self.visarga = pn.cdrewrite(
            pn.string_map([
                ("s+[EOS]",  "ḥ"),
                ("ṣ+[EOS]",  "ḥ"),
                # keep the old patterns for safety (if EOS appears without +)
                ("s[EOS]",   "ḥ[EOS]"),
                ("ṣ[EOS]",   "ḥ[EOS]"),
            ]),
            "", "", self.sig
        )

        # Word-final cluster reduction: ṣṭ → ṭ
        self.cluster_reduction = pn.cdrewrite(
            pn.string_map([
                ("ṣṭ+[EOS]", "ṭ"),
                ("k+t+[EOS]", "k"),
                ("gdh+[EOS]", "k"),
            ]),
            "", "", self.sig
        )


    # ──────────────────────────────────────────────────────────────────────────
    # Named rule lists (for per-rule debug tracing)
    # ──────────────────────────────────────────────────────────────────────────

    def _build_named_rule_lists(self):
        self._vowel_rules: list[tuple[str, pn.Fst]] = [
            ("thematic_merger",    self.thematic_merger),
            ("class9_special",     self.class9_special),
            ("ayadi",              self.ayadi),
            ("perfect_yan_conjunct", self.perfect_yan_conjunct),
            ("perfect_yan_simple",   self.perfect_yan_simple),
            ("clean_perf_weak",      self.clean_perf_weak),
            ("savarna",            self.savarna),
            ("yan_sandhi",         self.yan_sandhi),
            ("guna_sandhi",        self.guna_sandhi),
            ("pragrhya_erase",      self.pragrhya_erase),
        ]
        self._consonant_rules: list[tuple[str, pn.Fst]] = [
            ("d_dh_gemination",   self.d_dh_gemination),
            ("dental_palatal_fusion", self.dental_palatal_fusion),
            ("homorganic_gemination", self.homorganic_gemination),
            ("bartholomae_general", self.bartholomae_general),
            ("bartho_hth",         self.bartho_hth),
            ("bartho_hdh",         self.bartho_hdh),
            ("bartho_ht",          self.bartho_ht),
            ("deaspirate_before_obstruent", self.deaspirate_before_obstruent),
            ("grassmann_throwback",self.grassmann_throwback),
            ("h_to_k",             self.h_to_k),
            ("s_dh_bh",             self.s_dh_bh),
            ("j_retroflex",        self.j_retroflex),
            ("palatal_sibilant_retroflex", self.palatal_sibilant_retroflex),
            ("palatal_sandhi",     self.palatal_sandhi),
            ("ksha_t_simplify",    self.ksha_t_simplify),
            ("retro_th",           self.retro_th),
            ("retro_t",            self.retro_t),
            ("retro_ddh",           self.retro_ddh),
            ("retro_dhv",          self.retro_dhv),
            ("sibilant_cluster_tagged", self.sibilant_cluster_tagged),
            ("devoicing",          self.devoicing),
            ("nasal_assimilation", self.nasal_assimilation),
            ("nj_cluster_hardening", self.nj_cluster_hardening),
            ("anusvara",           self.anusvara),
            ("parasavarna",        self.parasavarna),
            ("velar_nasal",        self.velar_nasal),
            ("visarga_stop_fusion", self.visarga_stop_fusion),
            ("grassmann_init_aspirate", self.grassmann_init_aspirate),
            ("grassmann_clean", self.grassmann_clean),
            ("clean_sd_residual",  self.clean_sd_residual),
        ]
        self._long_distance_rules: list[tuple[str, pn.Fst]] = [
            ("ruki",                 self.ruki),
            ("no_ruki_revert",            self.no_ruki_revert),      # after RUKI
            ("ruki_revert_before_r",      self.ruki_revert_before_r), # after RUKI
            ("ksha_t_simplify_post_ruki", self.ksha_t_simplify_post_ruki),
            ("retro_post_ruki_th",   self.retro_post_ruki_th),
            ("retro_post_ruki_t",    self.retro_post_ruki_t),
            ("retro_post_ruki_dhv",  self.retro_post_ruki_dhv),
            ("nati",                 self.nati),
            # ── Final normalization (must run before visarga) ──
            ("final_palatal_reversion",   self.final_palatal_reversion),
            ("final_deaspiration",        self.final_deaspiration),
            ("final_devoicing",           self.final_devoicing),
            ("final_s_to_t",              self.final_s_to_t),
            # --- Visarga & cluster reduction ---
            ("visarga",              self.visarga),
            ("cluster_reduction",    self.cluster_reduction),
            ("clean_boundaries",     self.clean_boundaries),
        ]

    # ──────────────────────────────────────────────────────────────────────────
    # Debug helper
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _apply_rules_with_trace(
        fst: pn.Fst,
        rules: list[tuple[str, pn.Fst]],
        phase: str,
    ) -> pn.Fst:
        """Apply rules one by one, printing each result.

        Stops immediately when a rule causes the FST to go empty, identifying
        exactly which rule killed the valid path.
        """
        print(f"  [{phase}]")
        for name, rule_fst in rules:
            fst = (fst @ rule_fst).optimize()
            try:
                fst = fst.determinize().optimize()
            except pn.FstOpError:
                pass
            if fst.num_states() == 0:
                print(f"    ❌ {name}: FST went EMPTY — this rule killed the path")
                return fst
            try:
                print(f"    ✅ {name}: '{fst.string()}'")
            except Exception:
                print(f"    ⚠️  {name}: ambiguous (no unique string)")
        return fst

    # ──────────────────────────────────────────────────────────────────────────
    # Phase entry points
    # ──────────────────────────────────────────────────────────────────────────

    def vowel_phase(self, fst: pn.Fst, debug: bool = False) -> pn.Fst:
        """Apply vowel sandhi rules.

        Order is critical — see inline comments in _setup_vowel_rules.
        """
        if debug:
            return self._apply_rules_with_trace(fst, self._vowel_rules, "vowel_phase")
        return (fst
                @ self.thematic_merger
                @ self.class9_special
                @ self.ayadi
                @ self.perfect_yan_conjunct
                @ self.perfect_yan_simple
                @ self.clean_perf_weak
                @ self.savarna
                @ self.yan_sandhi
                @ self.guna_sandhi
                @ self.pragrhya_erase)

    def consonant_phase(self, fst: pn.Fst, debug: bool = False) -> pn.Fst:
        """Apply consonant cluster sandhi rules."""
        if debug:
            return self._apply_rules_with_trace(fst, self._consonant_rules, "consonant_phase")
        return (fst
                @ self.d_dh_gemination
                @ self.mrj_class_rule
                @ self.dental_palatal_fusion
                @ self.homorganic_gemination
                @ self.bartholomae_general
                @ self.bartho_hth
                @ self.bartho_hdh
                @ self.bartho_ht
                @ self.deaspirate_before_obstruent
                @ self.grassmann_throwback
                @ self.h_to_k
                @ self.s_dh_bh
                @ self.j_retroflex
                @ self.palatal_sibilant_retroflex
                @ self.palatal_sandhi
                @ self.ksha_t_simplify
                @ self.retro_th
                @ self.retro_t
                @ self.retro_ddh
                @ self.retro_dhv
                @ self.sibilant_cluster_tagged
                @ self.devoicing
                @ self.nasal_assimilation
                @ self.nj_cluster_hardening
                @ self.anusvara
                @ self.parasavarna
                @ self.velar_nasal
                @ self.visarga_stop_fusion
                @ self.grassmann_init_aspirate  # Grassmann initial aspiration
                @ self.grassmann_clean          # clean up Grassmann tag
                @ self.clean_sd_residual)

    def long_distance_phase(self, fst: pn.Fst, debug: bool = False) -> pn.Fst:
        """Apply long-distance rules (RUKI, Nati, Visarga, etc.)."""
        if debug:
            return self._apply_rules_with_trace(
                fst, self._long_distance_rules, "long_distance_phase"
            )
        for name, rule_fst in self._long_distance_rules:
            fst = (fst @ rule_fst).optimize()
            try:
                fst = pn.determinize(fst).optimize()
            except pn.FstOpError:
                pass   # already deterministic or non‑determinizable – ignore
        return fst

    def apply_all(self, fst: pn.Fst, debug: bool = False) -> pn.Fst:
        """Run all three sandhi phases in sequence."""
        return self.long_distance_phase(
            self.consonant_phase(
                self.vowel_phase(fst, debug), debug
            ), debug
        )