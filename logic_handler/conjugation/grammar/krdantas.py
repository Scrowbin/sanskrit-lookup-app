import csv
import os
import pynini as pn
from conjugate import SanskritConjugator
from irregulars import krdanta_overrides
from alphabet import ALPHABET


# ---------------------------------------------------------------------------
# CSV fallback for krdanta indeclinables (inria_indeclinables.csv)
# ---------------------------------------------------------------------------

_SUBTYPE_TO_KEY = {
    "absolutive/gerund": "abs",
    "infinitive":        "inf",
}
# conjugation column → derivative label used by the engine
_CONJ_TO_DERIV = {
    "causative":   "causative",
    "desiderative": "desiderative",
    "intensive":   "intensive",
    "primary":     None,
    "":            None,
}


class _InriaIndeclinables:
    """Singleton lookup table backed by inria_indeclinables.csv.

    Indexed as:  (stem_iast, type_key, derivative) -> [form_iast, ...]
    where type_key is 'inf' or 'abs', and derivative is None/'causative'/etc.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._index: dict = {}
            cls._instance._load()
        return cls._instance

    def _load(self):
        import sys
        if getattr(sys, 'frozen', False):
            data_dir = os.path.join(sys._MEIPASS, 'data')
        else:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        csv_path = os.path.join(data_dir, 'inria_indeclinables.csv')
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as fh:
                for row in csv.DictReader(fh):
                    subtype    = (row.get('subtype',     '') or '').strip()
                    type_key   = _SUBTYPE_TO_KEY.get(subtype)
                    if type_key is None:
                        continue   # skip particles / adverbs-in-tas

                    stem_iast  = (row.get('stem_iast',   '') or '').strip()
                    form_iast  = (row.get('form_iast',   '') or '').strip()
                    conj_raw   = (row.get('conjugation', '') or '').strip().lower()
                    derivative = _CONJ_TO_DERIV.get(conj_raw)

                    if not stem_iast or not form_iast:
                        continue

                    key = (stem_iast, type_key, derivative)
                    bucket = self._index.setdefault(key, [])
                    if form_iast not in bucket:
                        bucket.append(form_iast)
        except Exception as exc:
            print(f"InriaIndeclinables: failed to load CSV - {exc}")

    def lookup(self, stem_iast: str, type_key: str, derivative=None) -> list[str]:
        """Return matching IAST forms (empty list if not found)."""
        return self._index.get((stem_iast, type_key, derivative), [])


INRIA_INDECLINABLES = _InriaIndeclinables()

class KrdantaEngine:
    """Generates the Krdanta block for a root."""

    def __init__(self, conjugator: SanskritConjugator):
        self.c = conjugator

    def get_forms(self, fst: pn.Fst) -> list[str]:
        morph_fst = self.c.morphology.apply_all(fst)
        sandhi_fst = self.c.sandhi.apply_all(morph_fst)
        try:
            opt = sandhi_fst.optimize()
            if opt.num_states() == 0:
                return []
            return sorted(list(opt.paths().ostrings()))
        except Exception:
            return []

    def _build_and_format(self, name: str, root_str: str, class_num: int, type_key: str, suffix_m: str, suffix_f: str = "", preverb_str: str = "", stem_fst=None, derivative=None) -> list[dict]:
        override_key = f"{derivative}_{type_key}" if derivative else type_key
        
        override = None
        if root_str in krdanta_overrides:
            if override_key in krdanta_overrides[root_str]:
                override = krdanta_overrides[root_str][override_key]
            elif derivative is None and type_key in krdanta_overrides[root_str]:
                override = krdanta_overrides[root_str][type_key]
                
        if override is not None:
            m_forms = override.get("m", "").split("\n") if override.get("m") else []
            f_forms = override.get("f", "").split("\n") if override.get("f") else []
        else:
            # Generate algorithmic
            if stem_fst is None:
                # Fallback to bare root if no stem provided
                stem_fst = pn.accep(root_str)

            combined_m = stem_fst + pn.accep("+") + pn.accep(suffix_m)
            m_forms = self.get_forms(combined_m)

            f_forms = []
            if suffix_f:
                combined_f = stem_fst + pn.accep("+") + pn.accep(suffix_f)
                f_forms = self.get_forms(combined_f)

            # ── CSV fallback for verbal indeclinables (inf / abs) ────────────
            if not m_forms and type_key in ("inf", "abs_tva", "abs_ya"):
                csv_key = "inf" if type_key == "inf" else "abs"
                db_deriv = derivative if derivative in (
                    "causative", "desiderative", "intensive"
                ) else None
                db_forms = INRIA_INDECLINABLES.lookup(root_str, csv_key, db_deriv)
                if db_forms:
                    m_forms = db_forms

        if not m_forms:
            return []

        results = []
        max_len = max(len(m_forms), len(f_forms) if f_forms else 0)
        for i in range(max_len):
            m_form = m_forms[i] if i < len(m_forms) else m_forms[-1]
            f_form = f_forms[i] if f_forms and i < len(f_forms) else (f_forms[-1] if f_forms else "")

            if preverb_str:
                clean_m = m_form.lstrip('-')
                p_m = pn.accep(preverb_str) + pn.accep(clean_m)
                gen_m = self.get_forms(p_m)
                m_form = gen_m[0] if gen_m else preverb_str + clean_m
                if f_form:
                    clean_f = f_form.lstrip('-')
                    p_f = pn.accep(preverb_str) + pn.accep(clean_f)
                    gen_f = self.get_forms(p_f)
                    f_form = gen_f[0] if gen_f else preverb_str + clean_f

            if f_form:
                results.append({"name": name, "form": f"{m_form} m. n. {f_form} f."})
            else:
                results.append({"name": name, "form": m_form})
                
        return results

    def generate_block(self, root_str: str, class_num: int, preverb_str: str = "", derivative: str | None = None) -> dict:
        if derivative == "causative":
            class_num = 10
        
        participles = []
        indeclinables = []
        
        def add_p(items):
            if items:
                participles.extend(items)
                
        def add_i(items):
            if items:
                indeclinables.extend(items)
                
        if derivative in ("intensive", "intensive_luganta", "intensive_anta", "intensive_active_luganta"):
            # 1. Present Active Participle (Luganta)
            luganta_stem = self.c._get_stem(root_str, class_num, "[WEAK]", "present", "intensive_active_luganta", None, None)
            add_p(self._build_and_format(
                "Present Active Participle", root_str, class_num, "prp_act", "at", "atī", preverb_str, luganta_stem, "intensive_active_luganta"
            ))
            
            # 2. Present Middle Participle (Anta)
            anta_stem = self.c._get_stem(root_str, class_num, "[WEAK]", "present", "intensive_middle", None, None)
            add_p(self._build_and_format(
                "Present Middle Participle", root_str, class_num, "prp_mid", "māna", "mānā", preverb_str, anta_stem, "intensive_middle"
            ))
            
            # 3. Periphrastic Perfect (ām)
            luganta_strong = self.c._get_stem(root_str, class_num, "[STRONG]", "present", "intensive_active_luganta", None, None)
            add_i(self._build_and_format(
                "Periphrastic Perfect", root_str, class_num, "peri_perf_anta", "ām", "", preverb_str, anta_stem, "intensive_middle"
            ))
            add_i(self._build_and_format(
                "Periphrastic Perfect", root_str, class_num, "peri_perf_luganta", "ām", "", preverb_str, luganta_strong, "intensive_active_luganta"
            ))
            
            return {
                "participles": participles,
                "indeclinables": indeclinables
            }
        
        
        # 1. Past Passive Participle (-ta / -tā)
        ppp_stem = None
        if derivative == "causative" or (class_num == 10 and not derivative):
            ppp_stem = self.c.stems._build_causative_base(root_str) + pn.accep("i")
        elif derivative == "desiderative":
            ppp_stem = (self.c.stems._build_desiderative(root_str, "[WEAK]") + pn.accep("+")) @ pn.cdrewrite(pn.cross("a+", ""), "", "", self.c.stems.sig) + pn.accep("i")
            
        add_p(self._build_and_format(
            "Past Passive Participle", root_str, class_num, "ppp", "ta", "tā", preverb_str, ppp_stem, derivative
        ))
        
        # 2. Past Active Participle (-tavat / -tavatī)
        add_p(self._build_and_format(
            "Past Active Participle", root_str, class_num, "pp_act", "tavat", "tavatī", preverb_str, ppp_stem, derivative
        ))
        
        # 3. Present Active Participle
        pres_stem = self.c._get_stem(root_str, class_num, "[WEAK]", "present", derivative, "active", None, None)
        
        pres_stem_for_ant = (
            (pres_stem + pn.accep("[WORD_END]"))
            @ pn.cdrewrite(pn.cross("+a[WORD_END]", ""), "", "", self.c.stems.sig)
            @ pn.cdrewrite(pn.cross("a[WORD_END]", ""), "", "", self.c.stems.sig)
            @ pn.cdrewrite(pn.cross("[WORD_END]", ""), "", "", self.c.stems.sig)
        )
        
        # Thematic roots (1, 4, 6, 10, desiderative, causative) use antī. Athematic (2, 3, 5, 7, 8, 9, intensive luganta) use atī.
        is_thematic = (class_num in {1, 4, 6, 10}) or (derivative in ("causative", "desiderative"))
        # Note: root_str "bhū" intensive_active_luganta is athematic, so atī
        act_f = "antī" if is_thematic else "atī"
        
        add_p(self._build_and_format(
            "Present Active Participle", root_str, class_num, "prp_act", "at", act_f, preverb_str, pres_stem_for_ant, derivative
        ))
        
        # 4. Present Middle Participle
        is_thematic = (class_num in {1, 4, 6, 10}) or (derivative is not None)
        mid_suf_m = "māna" if is_thematic else "āna"
        mid_suf_f = "mānā" if is_thematic else "ānā"
        
        add_p(self._build_and_format(
            "Present Middle Participle", root_str, class_num, "prp_mid", mid_suf_m, mid_suf_f, preverb_str, pres_stem, derivative
        ))
        
        # 5. Present Passive Participle
        if derivative == "causative" or (class_num == 10 and not derivative):
            pass_stem = self.c.stems._build_causative_base(root_str) + pn.accep("ya")
        elif derivative == "desiderative":
            pass_stem = self.c.stems._build_desiderative_passive(root_str, "[WEAK]")
        else:
            pass_stem = self.c.stems._build_passive(root_str, class_num)
            
        add_p(self._build_and_format(
            "Present Passive Participle", root_str, class_num, "prp_pass", "māna", "mānā", preverb_str, pass_stem, derivative
        ))
        
        # Future stem
        raw_fut_stem = self.c._get_stem(root_str, class_num, "[STRONG]", "future", derivative, "active", None, None)
        fut_stem_for_ant = (raw_fut_stem + pn.accep("+")) @ pn.cdrewrite(pn.cross("a+", ""), "", "", self.c.stems.sig)
        
        # 6. Future Active Participle
        add_p(self._build_and_format(
            "Future Active Participle", root_str, class_num, "futp_act", "at", "antī", preverb_str, fut_stem_for_ant, derivative
        ))
        
        # 7. Future Middle Participle
        add_p(self._build_and_format(
            "Future Middle Participle", root_str, class_num, "futp_mid", "māna", "mānā", preverb_str, raw_fut_stem, derivative
        ))
        
        # 8. Future Passive Participle (Gerundives) - tavya, anīya, ya
        peri_base = self.c.stems._build_periphrastic_future_system(root_str, class_num, "[STRONG]", "periphrastic_future", derivative=derivative)
        
        # for aniya/ya, strong_root for primary is guna. For derivative, it's just the base stem (e.g. causative base, or desiderative base)
        if derivative == "causative" or (class_num == 10 and not derivative):
            strong_root = self.c.stems._build_causative_base(root_str)
        elif derivative == "desiderative":
            strong_root = self.c.stems._build_desiderative(root_str, "[STRONG]")
        else:
            strong_root = self.c.stems._apply_guna(root_str, "[STRONG]")
        
        add_p(self._build_and_format(
            "Future Passive Participle", root_str, class_num, "fpp_tavya", "tavya", "tavyā", preverb_str, peri_base, derivative
        ))
        
        # Strip final 'a' from causative/desiderative bases before vowel-initial affixes like anīya and ya
        # (Though causative 'ya' drops the 'aya' completely in Pāṇini. 'bhāvya', not 'bhāvayaya').
        # Actually for causative 'ya', the suffix is 'ya' and the base is just 'bhāv'.
        if derivative == "causative" or (class_num == 10 and not derivative):
            ya_base = (self.c.stems._build_causative_base(root_str) + pn.accep("[WORD_END]")) @ pn.cdrewrite(pn.cross("+[WORD_END]", ""), "", "", self.c.stems.sig) @ pn.cdrewrite(pn.cross("[WORD_END]", ""), "", "", self.c.stems.sig)
            aniya_base = ya_base # bhāv + anīya -> bhāvanīya
        elif derivative == "desiderative":
            ya_base = (strong_root + pn.accep("+")) @ pn.cdrewrite(pn.cross("a+", ""), "", "", self.c.stems.sig)
            aniya_base = ya_base
        else:
            ya_base = strong_root
            aniya_base = strong_root
            
        add_p(self._build_and_format(
            "Future Passive Participle", root_str, class_num, "fpp_aniya", "anīya", "anīyā", preverb_str, aniya_base, derivative
        ))
        add_p(self._build_and_format(
            "Future Passive Participle", root_str, class_num, "fpp_ya", "ya", "yā", preverb_str, ya_base, derivative
        ))
        
        # 9. Perfect Participles
        phonemes = ALPHABET.parse_phonemes(root_str)
        if not derivative:
            perf_act_base = self.c.stems._build_perfect_krdanta_base(root_str, class_num, "active")
            perf_mid_base = self.c.stems._build_perfect_krdanta_base(root_str, class_num, "middle")
            
            if root_str == "bhū" or (phonemes and phonemes[-1] in ('u', 'ū', 'ṛ', 'ṝ')):
                act_suffix = "vas"
            else:
                act_suffix = "ivas"
                
            m_dicts = self._build_and_format(
                "Perfect Active Participle", root_str, class_num, "perf_act", act_suffix, "uṣī", preverb_str, perf_act_base, derivative
            )
            for m_dict in m_dicts:
                if m_dict and m_dict.get("form"):
                    m_dict["form"] = m_dict["form"].replace("vaḥ m.", "vas m.").replace("ivaḥ m.", "ivas m.")
            add_p(m_dicts)
            
            add_p(self._build_and_format(
                "Perfect Middle Participle", root_str, class_num, "perf_mid", "āna", "ānā", preverb_str, perf_mid_base, derivative
            ))
        
        # Indeclinable forms
        
        # Infinitive (uses periphrastic base)
        add_i(self._build_and_format(
            "Infinitive", root_str, class_num, "inf", "tum", "", preverb_str, peri_base, derivative
        ))
        
        # Absolutive selection (Whitney §990):
        # • Unprefixed roots → -tvā only
        # • Prefixed (preverb present): consonant-final root → -tya; vowel-final → -ya
        is_prefixed = bool(preverb_str)
        short_vowels = {'a', 'i', 'u', 'ṛ', 'ḷ'}
        root_final = phonemes[-1] if phonemes else ''
        root_ends_in_vowel = root_final in set(ALPHABET.vowels_list)

        # -tvā absolutive: only for unprefixed roots
        if not is_prefixed:
            tva_stem = peri_base if derivative or class_num == 10 else pn.accep(root_str)
            add_i(self._build_and_format(
                "Absolutive", root_str, class_num, "abs_tva", "tvā", "", preverb_str, tva_stem, derivative
            ))

        # -ya / -tya absolutive
        # For unprefixed queries, we still want to generate the -ya absolutive with a hyphen to indicate it requires a preverb.
        if derivative:
            abs_ya_suffix = "ya"
        elif class_num == 10:
            abs_ya_suffix = "ya"
        else:
            abs_ya_suffix = "tya" if root_final in short_vowels else "ya"
        abs_ya_stem = ya_base if derivative or class_num == 10 else pn.accep(root_str)
        
        # If there's no preverb in the query, prepend a hyphen to the output format inside _build_and_format?
        # Alternatively, we just add it to the final string. But _build_and_format returns a dict.
        # Let's intercept the form after generation.
        ya_form_dicts = self._build_and_format("Absolutive", root_str, class_num, "abs_ya", abs_ya_suffix, "", preverb_str, abs_ya_stem, derivative)
        if not is_prefixed:
            for ya_form_dict in ya_form_dicts:
                if ya_form_dict and ya_form_dict.get("form"):
                    ya_form_dict["form"] = "-" + ya_form_dict["form"]
        add_i(ya_form_dicts)
        
        # Periphrastic Perfect (for derivatives and class 10, plus explicit overrides like hu)
        has_peri_override = derivative is None and root_str in krdanta_overrides and "peri_perf" in krdanta_overrides[root_str]
        if derivative or class_num == 10 or has_peri_override:
            if has_peri_override:
                peri_perf_base = pn.accep("") # unused, rely on override
            else:
                peri_perf_base = self.c.stems._build_periphrastic_base(root_str, class_num, derivative)
            add_i(self._build_and_format(
                "Periphrastic Perfect", root_str, class_num, "peri_perf", "", "", preverb_str, peri_perf_base, derivative
            ))
        
        return {
            "participles": participles,
            "indeclinables": indeclinables
        }
