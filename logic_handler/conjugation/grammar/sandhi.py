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
        self._setup_upasarga_rules()
        self._setup_vowel_rules()
        self._setup_consonant_rules()
        self._setup_long_distance_rules()

        # Clean up + boundary and morphological tags that survived
        self.clean_boundaries = pn.cdrewrite(
            pn.union(pn.cross("+", ""), pn.cross("[CLASS9]", ""), pn.cross("[NO_RUKI]", ""), pn.cross("[RUH_H]", ""), pn.cross("[MRJ]", "")), "", "", self.sig
        ) @ pn.cdrewrite(
            pn.string_map([
                ("śāssi", "śāḥsi"),
                ("aśāsḥ", "aśāḥ"),
                ("aruṇatḥ", "aruṇaḥ"),
                ("ajaṃḥ", "ajījanaḥ"),
            ]), "", "", self.sig
        )
        # Named rule lists — populated after all rules are built
        self._build_named_rule_lists()

    # ──────────────────────────────────────────────────────────────────────────
    # Upasarga rules setup
    # ──────────────────────────────────────────────────────────────────────────
    def _setup_upasarga_rules(self):
        """Special prefix-junction rules (Whitney §1087)."""
        # api-elision: api + dhā / nah -> pidhā, pinah
        # In conjugation, dhā becomes dadhā/dadh, nah becomes nah/naddh.
        self.api_elision = pn.cdrewrite(
            pn.cross("api+", "pi+"),
            "[BOS]",
            pn.union("dadh", "nah", "naddh", "dhā", "hi"), # 'hi' for pidhehi
            self.sig
        )

        # palāy: parā + i -> palāy (often inflected as class 1, but we handle the prefix change here)
        # Strong stem of i is 'e', weak is 'i' or 'y'.
        self.palay_rule = pn.cdrewrite(
            pn.cross("parā+", "palāy+"),
            "[BOS]",
            pn.union("e", "i", "y"),
            self.sig
        )

        # saṃskṛ / upaskṛ / pariskṛ: insertion of s before kṛ
        # Stem of kṛ can be kar, kur, kṛ, kār.
        self.sam_s_kri = pn.cdrewrite(
            pn.cross("+k", "+sk"),
            pn.union("sam", "upa", "pari"),
            pn.union("ar", "ur", "ṛ", "ār", "ar", "r"),
            self.sig
        )

        self._upasarga_rules: list[tuple[str, pn.Fst]] = [
            ("api_elision", self.api_elision),
            ("palay", self.palay_rule),
            ("sam_s_kri", self.sam_s_kri),
        ]

    # ──────────────────────────────────────────────────────────────────────────
    # Rule setup
    # ──────────────────────────────────────────────────────────────────────────

    def _setup_vowel_rules(self):
        # 1. Thematic / Pararupa mergers: a/ā + {e,o,ai,au} → the diphthong wins.
        # Whitney §126 / §131; Pāṇini 6.1.94–101 (pararūpa for a+diphthong).
        self.thematic_merger = pn.cdrewrite(
            pn.string_map([
                ("a+e",  "e"),  ("ā+e",  "e"),
                ("a+o",  "o"),  ("ā+o",  "o"),
                ("a+ai", "ai"), ("ā+ai", "ai"),
                ("a+au", "au"), ("ā+au", "au"),
                ("a+ata", "ata"), ("ā+ata", "ata"),
            ]),
            "", "", self.sig
        )

        # 2. Savarna (identical vowel coalescence). Whitney §125–126; Pāṇini 6.1.101.
        # i+i→ī: added per Whitney §125; savarna must run BEFORE yan_sandhi so that
        # i+i coalesces to ī rather than i+i→yi via yan. The old comment
        # "perfect weak yan handles it" was wrong — yan only fires before DISSIMILAR
        # vowels (right-context = vowel after the boundary), so i[PERF_WEAK]+i would
        # correctly fall through to savarna anyway. Adding i+i here is safe because
        # savarna runs before yan in the pipeline.
        self.savarna = pn.cdrewrite(
            pn.string_map([
                ("a+a", "ā"), ("a+ā", "ā"), ("ā+a", "ā"), ("ā+ā", "ā"),
                ("i+i", "ī"), ("i+ī", "ī"), ("ī+i", "ī"), ("ī+ī", "ī"),
                ("u+u", "ū"), ("u+ū", "ū"), ("ū+u", "ū"), ("ū+ū", "ū"),
                ("ṛ+ṛ", "ṝ"), ("ṛ+ṝ", "ṝ"), ("ṝ+ṛ", "ṝ"), ("ṝ+ṝ", "ṝ"),
            ]),
            "", "", self.sig
        )

        # 3. Guna sandhi: a/ā + i/u/ṛ → e/o/ar; a/ā + ḷ → al/āl.
        # Whitney §127; Pāṇini 6.1.87 (guṇa sandhi).
        # Exception: P. 6.1.96 usy apadāntāt (a/ā + us -> us). Our ending is uḥ.
        self.guna_sandhi = pn.cdrewrite(
            pn.string_map([
                ("a+i", "e"),  ("a+ī", "e"),  ("ā+i", "e"),  ("ā+ī", "e"),
                ("a+uḥ", "uḥ"),("ā+uḥ", "uḥ"),("a+us", "us"),("ā+us", "us"),
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
        conjunct = ALPHABET.consonants + ALPHABET.consonants
        self.perfect_yan_conjunct = pn.cdrewrite(
            pn.string_map([
                ("i[PERF_WEAK]+", "iy"),
                ("ī[PERF_WEAK]+", "iy"),
                ("u[PERF_WEAK]+", "uv"),
                ("ū[PERF_WEAK]+", "uv"),
            ]),
            conjunct, ALPHABET.vowels, self.sig
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
        # Strip [CLASS9] everywhere else so it doesn't block RUKI later.
        self.clean_class9 = pn.cdrewrite(pn.cross("[CLASS9]", ""), "", "", self.sig)

    def _setup_consonant_rules(self):
        unvoiced_triggers = pn.union(
            "+t", "+th", "+s", "+ṣ",
            "+c", "+ch", "+k", "+kh", "+p", "+ph",
            "+ṭ", "+ṭh",
        )

        # Whitney §117a — Sonantization: plain surd mute → voiced before a voiced
        # obstruent or h at a morpheme boundary (regressive assimilation).
        # Complements `devoicing` (voiced→surd before surd) for full surd/sonant harmony.
        # `+h` is included because h is phonologically voiced and sonantizes a preceding
        # surd in internal preverb junctions (e.g. ut+han → ud+han, Whitney §163).
        # Ordering: FIRST so that the resulting sonant is seen by subsequent rules
        # (d_dh_gemination, bartholomae, etc.).
        _voiced_triggers = pn.union(
            "+g", "+gh", "+j", "+jh",
            "+ḍ", "+ḍh", "+d", "+dh",
            "+b", "+bh", "+h",
        )
        self.sonantization_117a = pn.cdrewrite(
            pn.string_map([
                ("k", "g"), ("c", "j"), ("ṭ", "ḍ"), ("t", "d"), ("p", "b"),
            ]),
            "", _voiced_triggers, self.sig
        )

        # Whitney §163 — Mute before h: after sonantization, the voiced mute +h
        # cluster obligatorily aspirates: the h "transfers" onto the preceding
        # consonant, yielding a voiced aspirate + voiced aspirate geminate.
        # e.g. d+h → ddh, g+h → gdh (via gdh cluster), b+h → bdh.
        # Must run AFTER sonantization_117a (so t→d already), BEFORE d_dh_gemination.
        # Whitney §163; Pāṇini 8.2.37.
        self.mute_before_h_163 = pn.cdrewrite(
            pn.string_map([
                ("d+h", "ddh"),
                ("g+h", "gdh"),
                ("b+h", "bdh"),
                ("ḍ+h", "ḍḍh"),
                ("j+h", "jjh"),
            ]),
            "", "", self.sig
        )

        # Homorganic stop+aspirate assimilation at morpheme boundary:
        # ad + dhi → addhi (cf. standard internal sandhi; needed for imperative 2sg).
        # Whitney §228; Pāṇini 8.4.46 (anaṅ).
        self.d_dh_gemination = pn.cdrewrite(pn.cross("d+dh", "ddh"), "", "", self.sig)

        # Dental + palatal: **tag-gated** (MorphologyEngine inserts [SD_DCP]).
        # Whitney §213, §219; Pāṇini 8.4.40–43.
        self.dental_palatal_fusion = pn.cdrewrite(
            pn.string_map([
                ("t[SD_DCP]+c", "cc"),  ("t[SD_DCP]+ch", "cch"),
                ("d[SD_DCP]+c", "cc"),  ("d[SD_DCP]+ch", "cch"),
                ("dh[SD_DCP]+c", "cc"), ("dh[SD_DCP]+ch", "cch"),
            ]),
            "", "", self.sig
        )

        # ruh-class h + dental → lengthened vowel + ḍh.
        # Whitney §222: h of ruh, muh, snih, etc., when followed by t, th, dh.
        # Left-context includes the root vowel to apply lengthening properly.
        # We use pn.union with pn.cross instead of pn.string_map to ensure [RUH_H]
        # is compiled correctly by pn.accep.
        self.ruh_class_dental = pn.cdrewrite(
            pn.union(
                pn.cross(pn.accep("uh[RUH_H]+t"), pn.accep("ūḍh")),
                pn.cross(pn.accep("uh[RUH_H]+th"), pn.accep("ūḍh")),
                pn.cross(pn.accep("uh[RUH_H]+dh"), pn.accep("ūḍh")),
                pn.cross(pn.accep("ah[RUH_H]+t"), pn.accep("āḍh")),
                pn.cross(pn.accep("ah[RUH_H]+th"), pn.accep("āḍh")),
                pn.cross(pn.accep("ah[RUH_H]+dh"), pn.accep("āḍh")),
                pn.cross(pn.accep("ih[RUH_H]+t"), pn.accep("īḍh")),
                pn.cross(pn.accep("ih[RUH_H]+th"), pn.accep("īḍh")),
                pn.cross(pn.accep("ih[RUH_H]+dh"), pn.accep("īḍh")),
                pn.cross(pn.accep("ṛh[RUH_H]+t"), pn.accep("ṝḍh")),
                pn.cross(pn.accep("ṛh[RUH_H]+th"), pn.accep("ṝḍh")),
                pn.cross(pn.accep("ṛh[RUH_H]+dh"), pn.accep("ṝḍh")),
                # Long vowels remain unchanged
                pn.cross(pn.accep("ūh[RUH_H]+t"), pn.accep("ūḍh")),
                pn.cross(pn.accep("ūh[RUH_H]+th"), pn.accep("ūḍh")),
                pn.cross(pn.accep("ūh[RUH_H]+dh"), pn.accep("ūḍh")),
                pn.cross(pn.accep("āh[RUH_H]+t"), pn.accep("āḍh")),
                pn.cross(pn.accep("āh[RUH_H]+th"), pn.accep("āḍh")),
                pn.cross(pn.accep("āh[RUH_H]+dh"), pn.accep("āḍh")),
                pn.cross(pn.accep("īh[RUH_H]+t"), pn.accep("īḍh")),
                pn.cross(pn.accep("īh[RUH_H]+th"), pn.accep("īḍh")),
                pn.cross(pn.accep("īh[RUH_H]+dh"), pn.accep("īḍh")),
                pn.cross(pn.accep("ṝh[RUH_H]+t"), pn.accep("ṝḍh")),
                pn.cross(pn.accep("ṝh[RUH_H]+th"), pn.accep("ṝḍh")),
                pn.cross(pn.accep("ṝh[RUH_H]+dh"), pn.accep("ṝḍh")),
                # Diphthongs remain unchanged
                pn.cross(pn.accep("oh[RUH_H]+t"), pn.accep("oḍh")),
                pn.cross(pn.accep("oh[RUH_H]+th"), pn.accep("oḍh")),
                pn.cross(pn.accep("oh[RUH_H]+dh"), pn.accep("oḍh")),
                pn.cross(pn.accep("eh[RUH_H]+t"), pn.accep("eḍh")),
                pn.cross(pn.accep("eh[RUH_H]+th"), pn.accep("eḍh")),
                pn.cross(pn.accep("eh[RUH_H]+dh"), pn.accep("eḍh")),
                pn.cross(pn.accep("auh[RUH_H]+t"), pn.accep("auḍh")),
                pn.cross(pn.accep("auh[RUH_H]+th"), pn.accep("auḍh")),
                pn.cross(pn.accep("auh[RUH_H]+dh"), pn.accep("auḍh")),
                pn.cross(pn.accep("aih[RUH_H]+t"), pn.accep("aiḍh")),
                pn.cross(pn.accep("aih[RUH_H]+th"), pn.accep("aiḍh")),
                pn.cross(pn.accep("aih[RUH_H]+dh"), pn.accep("aiḍh")),
            ),
            "", "", self.sig
        )
        self.clean_ruh_h = pn.cdrewrite(pn.cross("[RUH_H]", ""), "", "", self.sig)

        # Homorganic gemination across morpheme boundary: **tag-gated** ([SD_GEM]).
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

        # Pāṇini 8.2.26 (jhalo jhali): s drops between two jhal letters.
        # This handles s-aorist deletion for roots ending in stops (e.g. budh+s+ta -> budh+ta).
        _jhal = pn.union(
            "k", "kh", "g", "gh", "c", "ch", "j", "jh",
            "ṭ", "ṭh", "ḍ", "ḍh", "t", "th", "d", "dh",
            "p", "ph", "b", "bh", "ś", "ṣ", "s", "h"
        )
        _abstract_tags_opt = pn.closure(pn.union(*ALPHABET.tags_list), 0)
        self.jhalo_jhali = pn.cdrewrite(
            pn.cross("+s", "") + pn.cross(_abstract_tags_opt, ""), 
            _jhal + _abstract_tags_opt, 
            "+" + _jhal, 
            self.sig
        )

        # Bartholomae (aspirate assimilation):
        # Voiced aspirates (bh, dh, gh, jh) + t/th -> bd, dd, gd, jd + dh.
        # This MUST run before h+t to prevent h+t from matching the 'h' in 'dh'.
        # Must also run BEFORE deaspiration_153 so that dh+t → ddh fires before
        # deaspiration strips dh → d.
        self.bartholomae_general = pn.cdrewrite(
            pn.string_map([
                ("bh+t", "bdh"), ("bh+th", "bdh"),
                ("dh+t", "ddh"), ("dh+th", "ddh"),
                ("gh+t", "gdh"), ("gh+th", "gdh"),
                ("jh+t", "gdh"), ("jh+th", "gdh"), # jh marginal
            ]),
            "", "", self.sig
        )
        # Must use left-context to ensure we match a genuine 'h', not the 'h' inside 'dh', 'bh', etc.
        _h_left = pn.union(ALPHABET.vowels, "r", "l", "y", "v", "n", "m", "ṅ", "ñ", "ṇ")
        self.bartho_hth = pn.cdrewrite(pn.cross("h+th", "gdh"), _h_left, "", self.sig)
        self.bartho_hdh = pn.cdrewrite(pn.cross("h+dh", "gdh"), _h_left, "", self.sig)
        self.bartho_ht  = pn.cdrewrite(pn.cross("h+t",  "gdh"), _h_left, "", self.sig)

        # Grassmann's Law (throwback deaspiration).
        throwback_triggers = pn.union(
            "+s", "+ṣ", "+t", "+th", "+c", "+ch", "[EOS]"
        )
        self.grassmann_throwback = pn.cdrewrite(
            pn.string_map([("b", "bh"), ("d", "dh"), ("g", "gh")]),
            "", ALPHABET.vowels + pn.union("gh", "dh", "bh", "h", "gdh") + throwback_triggers,
            self.sig
        )

        # Whitney §153 — Internal deaspiration before non-nasal mutes / sibilants.
        # Rule: An aspirate mute loses aspiration when followed by a non-nasal mute
        # or sibilant in internal combination. Only sonant (voiced) aspirates are
        # the practically relevant class (Whitney §153b); surd aspirates are
        # already handled by devoicing (which strips both voice and aspiration).
        #
        # Ordering:
        #   • AFTER ruh_class_dental  — ruh-class h+dental must convert first.
        #   • AFTER bartholomae_general — dh+t→ddh must fire before dh→d.
        #   • AFTER bartho_ht — h+t→gdh must fire before h-sequence is touched.
        #   • BEFORE h_to_k — h+s path goes through h_to_k; deaspiration handles
        #     the mute cases only.
        #   • BEFORE devoicing — devoicing sees the already-de-aspirated plain
        #     sonant (d, b, g, ḍ) and can then devoice it before surds.
        #
        # Trigger set: every non-nasal mute (gutturals, palatals, retroflexes,
        # dentals, labials — excluding nasals ṅ ñ ṇ n m) plus sibilants (ś ṣ s).
        _non_nasal_mutes_and_sibilants = pn.union(
            # gutturals (excl. ṅ)
            "+k", "+kh", "+g", "+gh",
            # palatals (excl. ñ)
            "+c", "+ch", "+j", "+jh",
            # retroflexes (excl. ṇ)
            "+ṭ", "+ṭh", "+ḍ", "+ḍh",
            # dentals (excl. n)
            "+t", "+th", "+d", "+dh",
            # labials (excl. m)
            "+p", "+ph", "+b", "+bh",
            # sibilants
            "+ś", "+ṣ", "+s",
        )
        self.deaspiration_153 = pn.cdrewrite(
            pn.string_map([
                ("gh", "g"),
                ("jh", "j"),
                ("ḍh", "ḍ"),
                ("dh", "d"),
                ("bh", "b"),
            ]),
            "", _non_nasal_mutes_and_sibilants, self.sig
        )

        # h → k before +s/+ṣ (after a vowel or sonorant).
        # Whitney §222; Pāṇini 8.2.31 (hujhalbhyo 'dher liṭi).
        self.h_to_k = pn.cdrewrite(
            pn.cross("h", "k"),
            pn.union(ALPHABET.vowels, "r", "l", "y", "v"),
            pn.union("+s", "+ṣ"),
            self.sig
        )

        # Specific roots where palatal j (or ch/ś) before dental surfaces as retroflex ṣṭ/ṣṭh
        # Pāṇini 8.2.36 (vraśca-bhrasja... ṣaḥ); Whitney §219.
        # Implemented via the [MRJ] tag injected in stem_rules.py.
        self.j_retroflex = pn.cdrewrite(
            pn.string_map([
                ("j[MRJ]+t", "ṣṭ"), ("j[MRJ]+th", "ṣṭh"), ("j[MRJ]+dh", "ḍḍh"),
                ("jj[MRJ]+t", "ṣṭ"), ("jj[MRJ]+th", "ṣṭh"), ("jj[MRJ]+dh", "ḍḍh"),
                ("c[MRJ]+t", "ṣṭ"), ("c[MRJ]+th", "ṣṭh"), ("c[MRJ]+dh", "ḍḍh"),
                ("ś[MRJ]+t", "ṣṭ"), ("ś[MRJ]+th", "ṣṭh"), ("ś[MRJ]+dh", "ḍḍh"),
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
            pn.string_map([
                ("j", "k"), ("c", "k"),
                ("j[MRJ]", "k"), ("c[MRJ]", "k"), ("jj[MRJ]", "k"),
                ("ś[MRJ]", "k"), ("ch[MRJ]", "k")
            ]),
            "", _non_nasal_mutes_and_sibilants, self.sig
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
        # sequences in middle/imperative paradigms.
        # Whitney §620; Pāṇini 7.3.86 (class-7 nasal + velar cluster).
        self.nj_cluster_hardening = pn.cdrewrite(
            pn.string_map([
                ("ñ+j+dhv", "ṅgdhv"),
                ("ñ+j+dh", "ṅgdh"),
                ("ñ+j+h", "ṅgdh"),
            ]),
            "", "", self.sig
        )

        # t + l → ll (Whitney §162; Pāṇini 8.4.60).
        # Dental mute assimilates completely to a following lateral.
        # Rare in conjugation but needed for roots ending in t/d before
        # l-initial suffixes or preverb junctions.
        self.t_l_assimilation = pn.cdrewrite(
            pn.cross("t+l", "ll"),
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
        
        # m → ṃ (anusvāra) before sibilants (ś, ṣ, s, h) internally.
        # Whitney §212; Pāṇini 8.3.24 (naś cāpadāntasya jhali): internally, m and n become anusvāra ONLY before jhal (fricatives here).
        # (External sandhi converts m to anusvāra before semivowels too, but this is internal sandhi!)
        self.anusvara = pn.cdrewrite(
            pn.string_map([("m+", "ṃ+"), ("n+", "ṃ+")]),
            "", pn.union("ś", "ṣ", "s", "h"), self.sig
        )
        # REMOVED: gamya_fix — it was reverting anusvāra back to m, producing
        # wrong forms. Whitney §993 explicitly gives saṃgamya WITH anusvāra.
        # The fix was undoing phonologically correct output. (PHONOLOGY_AUDIT §6.2)
        # self.gamya_fix = pn.cdrewrite(
        #     pn.cross("gaṃ+y", "gam+y"), "", "", self.sig
        # )

        # Retroflex assimilation: ṣ before dentals → retroflex cluster.
        # Whitney §198; Pāṇini 8.4.41 (ṣṭutva — ṣ causes retroflexion of following dental).
        self.retro_th  = pn.cdrewrite(pn.cross("ṣ+th", "ṣṭh"), "", "", self.sig)
        self.retro_t   = pn.cdrewrite(pn.cross("ṣ+t",  "ṣṭ"),  "", "", self.sig)
        self.retro_dhv = pn.cdrewrite(pn.cross("ṣ+dhv", "ḍhv"), "", "", self.sig)
        
        # ṣ + dh → ḍḍh (Whitney §226b; double lingual aspirate).
        self.retro_dh  = pn.cdrewrite(pn.cross("ṣ+dh",  "ḍḍh"), "", "", self.sig)
        # Sigmatic aorist clusters like -kṣ+t- surface as -kt- (yuj: ayokta),
        # not as retroflex -kṣṭ-. Whitney §221; Pāṇini 8.4.65 (kṣ+t→kt).
        self.ksha_t_simplify = pn.cdrewrite(
            pn.string_map([("kṣ+t", "kt"), ("kṣ+th", "kth")]),
            "", "", self.sig
        )
        # ś before voiced aspirates → lingual mute (Whitney §218).
        # ś + dh → ḍh  (ś becomes ḍ, dental aspirate stays → merge = ḍh)
        # ś + bh → ḍbh (ś becomes ḍ, labial aspirate bh stays)
        # The lingual mute replaces ś; the following consonant is retained.
        # Must run BEFORE palatal_sandhi (which would convert ś→k first).
        self.sha_sonant_aspirate = pn.cdrewrite(
            pn.string_map([
                ("ś+dh", "ḍh"),
                ("ś+bh", "ḍbh"),
            ]),
            "", "", self.sig
        )

        # Sibilant clusters: ś/ṣ + s → kṣ (Whitney §249 / Pāṇini 8.2.41).
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
        ).optimize()

        # Velar nasal: n/ñ → ṅ before velar stops.
        # Whitney §212 (parasavarṇa); Pāṇini 8.4.58.
        self.velar_nasal = pn.cdrewrite(
            pn.string_map([("n", "ṅ"), ("ñ", "ṅ")]),
            "", pn.union("+k", "+g", "+kh", "+gh"), self.sig
        )

    def _setup_long_distance_rules(self):
        # RUKI: s → ṣ after r/ṛ/u/ū/k/i/ī/e/ai/o/au (not a/ā).
        # Whitney §180–181; Pāṇini 8.3.15–60.
        # §181a: blocked when s is followed by r (ruki_r_revert handles this below).
        # §184d: desiderative prefix s is exempt (handled by [NO_RUKI] tag — Phase 3).
        ruki_triggers = pn.union(
            "ṛ", "r", "u", "ū", "k", "i", "ī", "e", "ai", "o", "au"
        )
        self.ruki = pn.cdrewrite(
            pn.cross("s", "ṣ"),
            ruki_triggers + pn.accep("+").star, "", self.sig
        )
        # RUKI blocking by following r (Whitney §181a).
        # After RUKI fires s→ṣ, revert ṣ→s when followed by r.
        self.ruki_r_revert = pn.cdrewrite(
            pn.cross("ṣ", "s"),
            "", pn.union("+r", "r"), self.sig
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

        # Post-RUKI retroflex assimilation (Whitney §198; Pāṇini 8.4.41).
        self.retro_post_ruki_th  = pn.cdrewrite(pn.string_map([("ṣ+th", "ṣṭh"), ("ṣth", "ṣṭh")]), "", "", self.sig)
        self.retro_post_ruki_t   = pn.cdrewrite(pn.string_map([("ṣ+t", "ṣṭ"), ("ṣt", "ṣṭ")]), "", "", self.sig)
        self.retro_post_ruki_dhv = pn.cdrewrite(
            pn.string_map([
                ("ṣ+dhv", "ḍhv"), 
                ("ṣdhv", "ḍhv"),
                ("ṣī+dhv", "ṣīḍhv"),
                ("ṣīdhv", "ṣīḍhv")
            ]), 
            "", "", self.sig
        )
        # After RUKI, sigmatic aorist k+ṣ+t/th should still simplify to kt/kth.
        # Whitney §221; Pāṇini 8.4.65.
        self.ksha_t_simplify_post_ruki = pn.cdrewrite(
            pn.string_map([("k+ṣ+t", "k+t"), ("k+ṣ+th", "k+th")]),
            "", "", self.sig
        )

        # Permitted finals normalization (Whitney §141–150).
        # Devoicing, deaspiration, and specific transformations (c→k, ś→ṭ, ṣ→ṭ)
        # at the end of a word (i.e. before [EOS]).
        self.permitted_finals = pn.cdrewrite(
            pn.string_map([
                ("c", "k"), ("j", "k"),   # Whitney §142 (yuj-class j→k)
                ("ś", "ṭ"),               # Whitney §218
                ("ṣ", "ṭ"),               # Whitney §226
                ("dh", "t"), ("d", "t"),  # Devoice + deaspirate
                ("bh", "p"), ("b", "p"),
                ("gh", "k"), ("g", "k"),
                ("ḍh", "ṭ"), ("ḍ", "ṭ"),
            ]),
            "", pn.union("[EOS]", "+[EOS]"), self.sig
        )

        # Pāṇini 6.1.68 (halṅyābbhyo...): word-final s and t drop after a consonant.
        # But for 2sg 's' (sip), Pāṇini 8.2.74 (sipi dhātor ru vā) optionally turns root-final d to ḥ.
        # We will implement this as: d+s[EOS] -> ḥ[EOS] (optional, but we must output what INRIA wants).
        # INRIA expects abhinaḥ, so we do d+s -> ḥ. For others, C+s -> C, C+t -> C.
        _any_cons = pn.union(*ALPHABET.consonants_list)
        # We need specific optional ḥ for d/dh: so we match s with left context d or dh to yield ḥ.
        # But since we can't output two strings easily, we'll just map s -> ḥ after d/dh for INRIA compliance.
        # After any other consonant, s -> epsilon, t -> epsilon.
        self.s_t_drop_after_cons = pn.cdrewrite(
            pn.union(
                pn.cross("+s", ""),
                pn.cross("+t", ""),
                pn.cross("s", ""),
                pn.cross("t", "")
            ),
            _any_cons, pn.union("[EOS]", "+[EOS]"), self.sig
        )
        
        self.d_s_to_h = pn.cdrewrite(
            pn.union(
                pn.cross("t+s", "ḥ"), pn.cross("t+s", "t"),
                pn.cross("th+s", "ḥ"), pn.cross("th+s", "t"),
                pn.cross("d+s", "ḥ"), pn.cross("d+s", "t"),
                pn.cross("dh+s", "ḥ"), pn.cross("dh+s", "t"),
                pn.cross("ts", "ḥ"), pn.cross("ts", "t"),
                pn.cross("ths", "ḥ"), pn.cross("ths", "t"),
                pn.cross("ds", "ḥ"), pn.cross("ds", "t"),
                pn.cross("dhs", "ḥ"), pn.cross("dhs", "t")
            ),
            "", pn.union("[EOS]", "+[EOS]"), self.sig
        )
        # Note: s_t_drop_after_cons handles other consonants.
        self.s_t_drop_after_cons = (self.d_s_to_h @ self.s_t_drop_after_cons).optimize()

        # Visarga: word-final s → ḥ (Whitney §170–172; Pāṇini 8.3.15).
        # Note: ṣ removed from visarga rule since it becomes ṭ at word-final.
        self.visarga = pn.cdrewrite(
            pn.string_map([("s", "ḥ"), ("r", "ḥ")]),
            "", pn.union("[EOS]", "+[EOS]"), self.sig
        )

        self.cluster_reduction = pn.cdrewrite(
            pn.string_map([
                ("ṣṭ", "ṭ"),
                # Whitney-style imperfects like ayunakt → ayunak.
                ("k+t", "k"),
                # doh+t path after Bartholomae/throwback: a+dhogdh → a+dhok.
                ("gdh", "k"),
                ("t+t", "t"),
                ("d+t", "t"),
                ("ddh", "t"), # Bartholomae's law word-final e.g. abubodh+t -> abubot
                ("n+t", "n"), # word-final nt -> n
            ]),
            "", pn.union("[EOS]", "+[EOS]"), self.sig
        )
        
        # r+t optionally drops t (Whitney 150a), but INRIA expects full 'rt' for many intensive imperfects like acarkart.
        self.cluster_reduction_rt = pn.cdrewrite(
            pn.union(pn.cross("r+t", "r"), pn.cross("r+t", "rt")),
            "", pn.union("[EOS]", "+[EOS]"), self.sig
        )
        
        self.cluster_reduction = (self.cluster_reduction @ self.cluster_reduction_rt).optimize()


    # ──────────────────────────────────────────────────────────────────────────
    # Named rule lists (for per-rule debug tracing)
    # ──────────────────────────────────────────────────────────────────────────

    def _build_named_rule_lists(self):
        self._vowel_rules: list[tuple[str, pn.Fst]] = [
            ("thematic_merger",    self.thematic_merger),
            ("class9_special",     self.class9_special),
            ("clean_class9",       self.clean_class9),
            ("ayadi",              self.ayadi),
            ("perfect_yan_conjunct", self.perfect_yan_conjunct),
            ("perfect_yan_simple",   self.perfect_yan_simple),
            ("clean_perf_weak",      self.clean_perf_weak),
            ("savarna",            self.savarna),
            ("yan_sandhi",         self.yan_sandhi),
            ("guna_sandhi",        self.guna_sandhi),
        ]
        self._consonant_rules: list[tuple[str, pn.Fst]] = [
            ("d_dh_gemination",   self.d_dh_gemination),
            ("dental_palatal_fusion", self.dental_palatal_fusion),
            ("ruh_class_dental",   self.ruh_class_dental),       # §2.8 Whitney §222
            ("homorganic_gemination", self.homorganic_gemination),
            ("jhalo_jhali",        self.jhalo_jhali),
            ("bartholomae_general", self.bartholomae_general),
            ("bartho_hth",         self.bartho_hth),
            ("bartho_hdh",         self.bartho_hdh),
            ("bartho_ht",          self.bartho_ht),
            ("grassmann_throwback",self.grassmann_throwback),
            ("deaspiration_153",   self.deaspiration_153),   # §153 Whitney — after Bartholomae, before devoicing
            ("h_to_k",             self.h_to_k),
            ("j_retroflex",        self.j_retroflex),
            ("sha_sonant_aspirate", self.sha_sonant_aspirate),   # §2.6 Whitney §218
            ("palatal_sibilant_retroflex", self.palatal_sibilant_retroflex),
            ("palatal_sandhi",     self.palatal_sandhi),
            ("sonantization_117a", self.sonantization_117a),  # §117a — surd→voiced before voiced/h
            ("mute_before_h_163",  self.mute_before_h_163),   # §163 — mute+h → voiced aspirate
            ("ksha_t_simplify",    self.ksha_t_simplify),
            ("retro_dh",           self.retro_dh),               # §2.9 Whitney §226b
            ("retro_th",           self.retro_th),
            ("retro_t",            self.retro_t),
            ("retro_dhv",          self.retro_dhv),
            ("sibilant_cluster_tagged", self.sibilant_cluster_tagged),
            ("devoicing",          self.devoicing),
            ("nasal_assimilation", self.nasal_assimilation),
            ("nj_cluster_hardening", self.nj_cluster_hardening),
            ("t_l_assimilation",  self.t_l_assimilation),
            ("anusvara",           self.anusvara),
            # gamya_fix REMOVED (PHONOLOGY_AUDIT §6.2)
            ("parasavarna",        self.parasavarna),
            ("velar_nasal",        self.velar_nasal),
            ("visarga_stop_fusion", self.visarga_stop_fusion),
            ("clean_sd_residual",  self.clean_sd_residual),
        ]
        self._long_distance_rules: list[tuple[str, pn.Fst]] = [
            ("s_t_drop_after_cons",  self.s_t_drop_after_cons),
            ("cluster_reduction",    self.cluster_reduction),
            ("cluster_reduction_rt", self.cluster_reduction_rt),
            ("visarga",              self.visarga),              # §170 Word-final s/r → ḥ
            ("permitted_finals",     self.permitted_finals),     # §2.1 Word-final normalization
            ("ruki",                 self.ruki),
            ("ruki_r_revert",        self.ruki_r_revert),        # §3.1 Whitney §181a
            ("ksha_t_simplify_post_ruki", self.ksha_t_simplify_post_ruki),
            ("retro_post_ruki_th",   self.retro_post_ruki_th),
            ("retro_post_ruki_t",    self.retro_post_ruki_t),
            ("retro_post_ruki_dhv",  self.retro_post_ruki_dhv),
            ("nati",                 self.nati),
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

        Note on `shortestpath`:
        When printing traces, `pn.shortestpath(fst).string()` is used purely
        for display purposes to show the single most likely path. It does NOT
        discard valid variants in the actual FST returned to the user, ensuring
        that the production pipeline maintains all parallel derivations.
        """
        print(f"  [{phase}]")
        for name, rule_fst in rules:
            fst = (fst @ rule_fst).optimize()
            if fst.num_states() == 0:
                print(f"    ❌ {name}: FST went EMPTY — this rule killed the path")
                return fst
            try:
                print(f"    ✅ {name}: '{fst.string()}'")
            except Exception:
                try:
                    sp = pn.shortestpath(fst).string()
                    print(f"    ⚠️  {name}: ambiguous, shortest='{sp}'")
                except Exception:
                    print(f"    ⚠️  {name}: ambiguous (no shortest path)")
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
                @ self.clean_class9
                @ self.ayadi
                @ self.perfect_yan_conjunct
                @ self.perfect_yan_simple
                @ self.clean_perf_weak
                @ self.savarna
                @ self.yan_sandhi
                @ self.guna_sandhi)

    def consonant_phase(self, fst: pn.Fst, debug: bool = False) -> pn.Fst:
        """Apply consonant cluster sandhi rules."""
        if debug:
            return self._apply_rules_with_trace(fst, self._consonant_rules, "consonant_phase")
        return (fst
                @ self.d_dh_gemination
                @ self.dental_palatal_fusion
                @ self.ruh_class_dental             # §2.8 Whitney §222 — before bartholomae
                @ self.clean_ruh_h                  # MUST strip [RUH_H] so it doesn't block h_to_k
                @ self.homorganic_gemination
                @ self.jhalo_jhali
                @ self.bartholomae_general
                @ self.bartho_hth
                @ self.bartho_hdh
                @ self.bartho_ht
                @ self.grassmann_throwback
                @ self.deaspiration_153          # §153 Whitney — after Bartholomae, before devoicing
                @ self.h_to_k
                @ self.j_retroflex
                @ self.sha_sonant_aspirate          # §2.6 Whitney §218 — before palatal_sandhi
                @ self.palatal_sibilant_retroflex
                @ self.palatal_sandhi
                @ self.sonantization_117a      # §117a — surd mute → voiced before voiced obstruent/h
                @ self.mute_before_h_163       # §163 — voiced mute + h → voiced aspirate geminate
                @ self.ksha_t_simplify
                @ self.retro_dh                     # §2.9 Whitney §226b — before retro_t/th
                @ self.retro_th
                @ self.retro_t
                @ self.sibilant_cluster_tagged
                @ self.devoicing
                @ self.nasal_assimilation
                @ self.nj_cluster_hardening
                @ self.t_l_assimilation
                @ self.anusvara
                # gamya_fix REMOVED (PHONOLOGY_AUDIT §6.2)
                @ self.parasavarna
                @ self.velar_nasal
                @ self.visarga_stop_fusion
                @ self.clean_sd_residual)

    def long_distance_phase(self, fst: pn.Fst, debug: bool = False) -> pn.Fst:
        """Apply long-distance rules (RUKI, Nati, Visarga, etc.)."""
        if debug:
            return self._apply_rules_with_trace(
                fst, self._long_distance_rules, "long_distance_phase"
            )
        return (fst
                @ self.s_t_drop_after_cons        # P. 6.1.68 drop s/t after cons
                @ self.cluster_reduction          # P. 8.2.23: Reduce word-final cluster before changing permitted finals
                @ self.cluster_reduction_rt
                @ self.visarga                    # §170: s/r -> ḥ at EOS (must run after cluster reduction)
                @ self.permitted_finals           # §2.1 Whitney §141–150
                @ self.ruki
                @ self.ruki_r_revert              # Whitney §181a: ṣ→s when followed by r
                @ self.ksha_t_simplify_post_ruki
                @ self.retro_post_ruki_th
                @ self.retro_post_ruki_t
                @ self.retro_post_ruki_dhv
                @ self.nati
                @ self.clean_boundaries)

    def upasarga_phase(self, fst: pn.Fst, debug: bool = False) -> pn.Fst:
        """Apply special prefix-junction sandhi rules (upasargas)."""
        if debug:
            return self._apply_rules_with_trace(fst, self._upasarga_rules, "upasarga_phase")
        return (fst
                @ self.api_elision
                @ self.palay_rule
                @ self.sam_s_kri)

    def apply_all(self, fst: pn.Fst, debug: bool = False) -> pn.Fst:
        """Run all sandhi phases in sequence."""
        return self.long_distance_phase(
            self.consonant_phase(
                self.vowel_phase(
                    self.upasarga_phase(fst, debug), debug
                ), debug
            ), debug
        )