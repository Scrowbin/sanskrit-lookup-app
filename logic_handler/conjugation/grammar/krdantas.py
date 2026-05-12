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

    def _build_and_format(self, name: str, root_str: str, class_num: int, type_key: str, suffix_m: str, suffix_f: str = "", preverb_str: str = "", stem_fst=None) -> list[str]:
        output = []
        
        # Check override
        if root_str in krdanta_overrides and type_key in krdanta_overrides[root_str]:
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
            return []
            
        if preverb_str:
            # Apply preverb sandhi
            p_m = pn.accep(preverb_str) + pn.accep(m_form)
            m_form = self.get_forms(p_m)[0] if self.get_forms(p_m) else preverb_str + m_form
            if f_form:
                p_f = pn.accep(preverb_str) + pn.accep(f_form)
                f_form = self.get_forms(p_f)[0] if self.get_forms(p_f) else preverb_str + f_form

        output.append(name)
        if f_form:
            output.append(f"{m_form} m. n. {f_form} f.")
        else:
            output.append(f"{m_form}")
            
        return output

    def generate_block(
        self,
        root_str: str,
        class_num: int,
        preverb_str: str = "",
        derivative: str | None = None,
    ) -> str:
        out = ["Participles"]
        
        # 1. Past Passive Participle (-ta / -tā)
        # Samprasāraṇa roots (vac, yaj, svap etc.) are handled via krdanta_overrides.
        out.extend(self._build_and_format(
            "Past Passive Participle", root_str, class_num, "ppp", "ta", "tā", preverb_str
        ))
        
        # 2. Past Active Participle (-tavat / -tavatī)
        out.extend(self._build_and_format(
            "Past Active Participle", root_str, class_num, "pp_act", "tavat", "tavatī", preverb_str
        ))
        
        # 3. Present Active Participle
        # Stem is Present Stem. For thematic stems ending in 'a', 'a' + 'ant' -> 'ant' (pararūpa)
        pres_stem = self.c._get_stem(root_str, class_num, "[WEAK]", "present", None, None, None)
        
        # We strip the final thematic '+a' from the stem.
        # This prevents 'bho+a' + '+ant' -> 'bho+a+ant' (which yields bhavānt).
        # Stripping '+a' leaves 'bho', which when combined with '+ant' yields 'bhavant'.
        pres_stem_for_ant = pres_stem @ pn.cdrewrite(pn.cross("+a", ""), "", "[WORD_END]", self.c.stems.sig)
        
        out.extend(self._build_and_format(
            "Present Active Participle", root_str, class_num, "prp_act", "ant", "antī", preverb_str, pres_stem_for_ant
        ))
        
        # 4. Present Middle Participle
        out.extend(self._build_and_format(
            "Present Middle Participle", root_str, class_num, "prp_mid", "māna", "mānā", preverb_str, pres_stem
        ))
        
        # 5. Present Passive Participle
        pass_stem = self.c.stems._build_passive(root_str, class_num)
        out.extend(self._build_and_format(
            "Present Passive Participle", root_str, class_num, "prp_pass", "māna", "mānā", preverb_str, pass_stem
        ))
        
        # Future stem
        fut_stem = self.c._get_stem(root_str, class_num, "[STRONG]", "future", None, None, None)
        # Note: future stem ends in 'sya' or 'iṣya', we need to strip 'a'
        fut_stem = (fut_stem + pn.accep("+")) @ pn.cdrewrite(pn.cross("a+", ""), "", "", self.c.stems.sig)
        
        # 6. Future Active Participle
        out.extend(self._build_and_format(
            "Future Active Participle", root_str, class_num, "futp_act", "at", "antī", preverb_str, fut_stem
        ))
        
        # 7. Future Middle Participle
        out.extend(self._build_and_format(
            "Future Middle Participle", root_str, class_num, "futp_mid", "amāṇa", "amāṇā", preverb_str, fut_stem
        ))
        
        # 8. Future Passive Participle (Gerundives) - tavya, anīya, ya
        # tavya uses the periphrastic future base
        peri_base = self.c.stems._build_periphrastic_future_system(root_str, class_num, "[STRONG]", "periphrastic_future")
        strong_root = self.c.stems._apply_guna(root_str, "[STRONG]")
        
        out.extend(self._build_and_format(
            "Future Passive Participle", root_str, class_num, "fpp_tavya", "tavya", "tavyā", preverb_str, peri_base
        ))
        out.extend(self._build_and_format(
            "Future Passive Participle", root_str, class_num, "fpp_ya", "ya", "yā", preverb_str, strong_root
        ))
        out.extend(self._build_and_format(
            "Future Passive Participle", root_str, class_num, "fpp_aniya", "anīya", "anīyā", preverb_str, strong_root
        ))
        
        # 9. Perfect Participles
        perf_act_base = self.c.stems._build_perfect_krdanta_base(root_str, class_num, "active")
        perf_mid_base = self.c.stems._build_perfect_krdanta_base(root_str, class_num, "middle")
        
        phonemes = ALPHABET.parse_phonemes(root_str)
        if root_str == "bhū":
            act_suffix = "as"
        elif phonemes and phonemes[-1] in ('u', 'ū', 'ṛ', 'ṝ'):
            act_suffix = "vas"
        else:
            act_suffix = "ivas"
            
        out.extend(self._build_and_format(
            "Perfect Active Participle", root_str, class_num, "perf_act", act_suffix, "uṣī", preverb_str, perf_act_base
        ))
        out.extend(self._build_and_format(
            "Perfect Middle Participle", root_str, class_num, "perf_mid", "āna", "ānā", preverb_str, perf_mid_base
        ))
        
        out.append("Indeclinable forms")
        
        # Infinitive (uses periphrastic base)
        out.extend(self._build_and_format(
            "Infinitive", root_str, class_num, "inf", "tum", "", preverb_str, peri_base
        ))
        
        # Absolutive
        out.extend(self._build_and_format(
            "Absolutive", root_str, class_num, "abs_tva", "tvā", "", preverb_str, pn.accep(root_str)
        ))
        out.extend(self._build_and_format(
            "Absolutive", root_str, class_num, "abs_ya", "ya", "", preverb_str, pn.accep(root_str)
        ))

        return "\n".join(out)
