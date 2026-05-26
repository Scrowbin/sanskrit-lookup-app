import pynini as pn
from conjugate import SanskritConjugator
from irregulars import krdanta_overrides
from alphabet import ALPHABET

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

    def _build_and_format(self, name: str, root_str: str, class_num: int, type_key: str, suffix_m: str, suffix_f: str = "", preverb_str: str = "", stem_fst=None, derivative=None) -> dict | None:
        # Avoid overrides for derivatives, as overrides are for primary roots.
        if derivative is None and root_str in krdanta_overrides and type_key in krdanta_overrides[root_str]:
            override = krdanta_overrides[root_str][type_key]
            m_form = override.get("m", "")
            f_form = override.get("f", "")
        else:
            # Generate algorithmic
            if stem_fst is None:
                # Fallback to bare root if no stem provided
                stem_fst = pn.accep(root_str)
                
            combined_m = stem_fst + pn.accep("+") + pn.accep(suffix_m)
            m_forms = self.get_forms(combined_m)
            m_form = m_forms[0] if m_forms else ""
            
            f_form = ""
            if suffix_f:
                combined_f = stem_fst + pn.accep("+") + pn.accep(suffix_f)
                f_forms = self.get_forms(combined_f)
                f_form = f_forms[0] if f_forms else ""

        if not m_form:
            return None
            
        if preverb_str:
            # Strip conventional '-' prefix from override values (e.g. "-gamya" → "gamya")
            # before FST processing — the dash is a display convention, not an FST character.
            clean_m = m_form.lstrip('-')
            p_m = pn.accep(preverb_str) + pn.accep(clean_m)
            m_form = self.get_forms(p_m)[0] if self.get_forms(p_m) else preverb_str + clean_m
            if f_form:
                clean_f = f_form.lstrip('-')
                p_f = pn.accep(preverb_str) + pn.accep(clean_f)
                f_form = self.get_forms(p_f)[0] if self.get_forms(p_f) else preverb_str + clean_f

        if f_form:
            return {"name": name, "form": f"{m_form} m. n. {f_form} f."}
        else:
            return {"name": name, "form": m_form}

    def generate_block(self, root_str: str, class_num: int, preverb_str: str = "", derivative: str | None = None) -> dict:
        if derivative == "causative":
            class_num = 10
        
        participles = []
        indeclinables = []
        
        def add_p(item):
            if item:
                participles.append(item)
                
        def add_i(item):
            if item:
                indeclinables.append(item)
                
        if derivative in ("intensive", "intensive_luganta", "intensive_anta"):
            # 1. Present Active Participle (Luganta)
            luganta_stem = self.c._get_stem(root_str, class_num, "[WEAK]", "present", "intensive_luganta", None, None)
            add_p(self._build_and_format(
                "Present Active Participle", root_str, class_num, "prp_act", "at", "atī", preverb_str, luganta_stem, "intensive_luganta"
            ))
            
            # 2. Present Middle Participle (Anta)
            anta_stem = self.c._get_stem(root_str, class_num, "[WEAK]", "present", "intensive_anta", None, None)
            add_p(self._build_and_format(
                "Present Middle Participle", root_str, class_num, "prp_mid", "māna", "mānā", preverb_str, anta_stem, "intensive_anta"
            ))
            
            # 3. Periphrastic Perfect (ām)
            luganta_strong = self.c._get_stem(root_str, class_num, "[STRONG]", "present", "intensive_luganta", None, None)
            add_i(self._build_and_format(
                "Periphrastic Perfect", root_str, class_num, "peri_perf_anta", "ām", "", preverb_str, anta_stem, "intensive_anta"
            ))
            add_i(self._build_and_format(
                "Periphrastic Perfect", root_str, class_num, "peri_perf_luganta", "ām", "", preverb_str, luganta_strong, "intensive_luganta"
            ))
            
            return {
                "participles": participles,
                "indeclinables": indeclinables
            }
        
        
        # 1. Past Passive Participle (-ta / -tā)
        ppp_stem = None
        if derivative == "causative":
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
        
        add_p(self._build_and_format(
            "Present Active Participle", root_str, class_num, "prp_act", "at", "antī", preverb_str, pres_stem_for_ant, derivative
        ))
        
        # 4. Present Middle Participle
        is_thematic = (class_num in {1, 4, 6, 10}) or (derivative is not None)
        mid_suf_m = "māna" if is_thematic else "āna"
        mid_suf_f = "mānā" if is_thematic else "ānā"
        
        add_p(self._build_and_format(
            "Present Middle Participle", root_str, class_num, "prp_mid", mid_suf_m, mid_suf_f, preverb_str, pres_stem, derivative
        ))
        
        # 5. Present Passive Participle
        if derivative == "causative":
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
        if not derivative:
            add_p(self._build_and_format(
                "Future Middle Participle", root_str, class_num, "futp_mid", "māna", "mānā", preverb_str, raw_fut_stem, derivative
            ))
        
        # 8. Future Passive Participle (Gerundives) - tavya, anīya, ya
        peri_base = self.c.stems._build_periphrastic_future_system(root_str, class_num, "[STRONG]", "periphrastic_future", derivative=derivative)
        
        # for aniya/ya, strong_root for primary is guna. For derivative, it's just the base stem (e.g. causative base, or desiderative base)
        if derivative == "causative":
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
        if derivative == "causative":
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
                act_suffix = "vān"
            else:
                act_suffix = "ivān"
                
            add_p(self._build_and_format(
                "Perfect Active Participle", root_str, class_num, "perf_act", act_suffix, "uṣī", preverb_str, perf_act_base, derivative
            ))
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
            tva_stem = peri_base if derivative else pn.accep(root_str)
            add_i(self._build_and_format(
                "Absolutive", root_str, class_num, "abs_tva", "tvā", "", preverb_str, tva_stem, derivative
            ))

        # -ya / -tya absolutive
        # For unprefixed queries, we still want to generate the -ya absolutive with a hyphen to indicate it requires a preverb.
        abs_ya_suffix = "ya" if root_ends_in_vowel else "tya"
        abs_ya_stem = ya_base if derivative else pn.accep(root_str)
        
        # If there's no preverb in the query, prepend a hyphen to the output format inside _build_and_format?
        # Alternatively, we just add it to the final string. But _build_and_format returns a dict.
        # Let's intercept the form after generation.
        ya_form_dict = self._build_and_format("Absolutive", root_str, class_num, "abs_ya", abs_ya_suffix, "", preverb_str, abs_ya_stem, derivative)
        if not is_prefixed and ya_form_dict:
            ya_form_dict["form"] = "-" + ya_form_dict["form"]
        add_i(ya_form_dict)
        
        # Periphrastic Perfect (for derivatives)
        if derivative:
            peri_perf_base = self.c.stems._build_periphrastic_base(root_str, class_num, derivative)
            add_i(self._build_and_format(
                "Periphrastic Perfect", root_str, class_num, "peri_perf", "", "", preverb_str, peri_perf_base, derivative
            ))
        
        return {
            "participles": participles,
            "indeclinables": indeclinables
        }
