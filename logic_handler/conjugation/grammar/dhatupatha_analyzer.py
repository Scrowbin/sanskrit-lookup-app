import csv
import os
from dataclasses import dataclass, field
from alphabet import ALPHABET

# ── Transliteration ────────────────────────────────────────────────────────────
IAST_TO_SLP1 = {
    'ā':'A', 'ī':'I', 'ū':'U', 'ṛ':'f', 'ṝ':'F', 'ḷ':'x', 'ḹ':'X',
    'ai':'E', 'au':'O', 'kh':'K', 'gh':'G', 'ṅ':'N', 'ch':'C', 'jh':'J', 'ñ':'Y',
    'ṭh':'W', 'ṭ':'w', 'ḍh':'Q', 'ḍ':'q', 'ṇ':'R', 'th':'T', 'dh':'D',
    'ph':'P', 'bh':'B', 'ś':'S', 'ṣ':'z', 'ḥ':'H', 'ṃ':'M',
}

# Long vowels that force periphrastic perfect when root-initial
_PERIPHRASTIC_LONG_VOWELS = frozenset({"ī", "ū", "ṛ", "ṝ", "e", "ai", "o", "au"})

# Pāṇini 6.1.15-16: Roots that undergo Samprasāraṇa (y/v/r → i/u/ṛ) in weak forms.
_SAMPRASARANA_ROOTS = frozenset({
    # Yajādi / Vacādi group (6.1.15)
    "yaj", "vac", "vap", "svap", "vah", "vas", "vad", "ve", "vye", "hve", "śvi",
    # Grahādi group (6.1.16)
    "grah", "jyā", "vay", "vyadh", "vaś", "vyac", "vraśc", "prach", "bhrajj"
})

def to_slp1(iast_str: str) -> str:
    s = iast_str
    for k, v in sorted(IAST_TO_SLP1.items(), key=lambda x: -len(x[0])):
        s = s.replace(k, v)
    return s


# ── RootObject ─────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class RootObject:
    """Structured representation of a Dhatupatha root entry.

    All grammatical properties are derived once from the lexicon, eliminating
    phonetic heuristics scattered across stem_rules.py and conjugate.py.

    Attributes:
        iast: IAST string (e.g. "bhū")
        class_num: Gaṇa (verb class) as integer 1-10
        is_anit: True if root has anudātta accent (\\) — takes no connecting 'i'
        is_set: Inverse of is_anit (convenience property)
        aorist_type: Paninian aorist class: 'root'|'a'|'s'|'is'|'sa'
        takes_periphrastic_perfect: True for causatives, desideratives, intensives,
            class-10 roots, or roots whose *first* phoneme is a long vowel.
    """
    iast: str
    class_num: int
    is_anit: bool
    is_vet: bool
    is_idit: bool       # i-it: Triggers Nasal Insertion (Num)
    is_irit: bool       # ir-it: Optional a-aorist (Pāṇini 3.1.57)
    is_uuit: bool       # ū-it: Optional i (Veṭ) in Participles (Pāṇini 7.2.44)
    is_duit: bool       # du-it: Mandatory a-aorist (Pāṇini 3.1.55)
    is_s_opadesa: bool  # ṣ-opadeśa: Initial ṣ requires prefix-sandhi (ṣatva)
    is_n_opadesa: bool  # ṇ-opadeśa: Initial ṇ requires prefix-sandhi (natva)
    aorist_type: str
    takes_periphrastic_perfect: bool
    permitted_voices: set[str]
    takes_samprasarana: bool
    

    @property
    def is_set(self) -> bool:
        return not self.is_anit


# ── DhatupathaAnalyzer ─────────────────────────────────────────────────────────

class DhatupathaAnalyzer:
    """Loads dhatupatha.csv and answers grammatical queries about roots.

    CSV format (3 columns, no header):
        col 0 – gaṇa (class) number (1-based group index, NOT verb class)
        col 1 – serial within gaṇa
        col 2 – raw Dhatupatha entry in SLP1 with anubandhas

    The verb class is read from col 0 of the *group header* that precedes
    each gaṇa block.  This loader stores (class_num, raw) pairs.
    """

    def __init__(self):
        self._entries: list[dict] = []
        self._cache: dict[tuple[str, int], RootObject] = {}
        self._load()
        
    def _parse_paninian_flags(self, raw: str) -> dict:
        """Extracts Pāṇinian markers from the raw SLP1 string."""
        # Initial consonant checks (Initial mutation)
        is_s = raw.startswith('z')  # SLP1 'z' is 'ṣ'
        is_n = raw.startswith('R')  # SLP1 'R' is 'ṇ'

        # Helper to check for a vowel-marker combination
        # ir-it must be checked before id-it so 'ir' isn't mistaken for 'i'
        is_irit = "ir" in raw or "i~r" in raw
        is_idit = ("i" in raw or "i~" in raw) and not is_irit
        
        is_uuit = "U" in raw  # SLP1 'U' is long 'ū'
        is_duit = "du" in raw # SLP1 'du' is 'du' marker

        return {
            "is_idit": is_idit,
            "is_irit": is_irit,
            "is_uuit": is_uuit,
            "is_duit": is_duit,
            "is_s_opadesa": is_s,
            "is_n_opadesa": is_n
        }


    def _load(self):
        csv_path = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'dhatupatha.csv'
        )
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 3 and not row[0].startswith('#'):
                        try:
                            self._entries.append({
                                'class_num': int(row[0]),
                                'raw': row[2],
                            })
                        except ValueError:
                            pass
        except Exception as e:
            print(f"DhatupathaAnalyzer: error loading CSV — {e}")

    # ── Internal lookup ────────────────────────────────────────────────────────
    def _find_raw(self, root_str: str, class_num: int) -> str | None:
        """Return the raw Dhatupatha entry string, or None if not found."""
        slp1_base = to_slp1(root_str)
        candidates = [slp1_base]
        if slp1_base.startswith('s'):
            candidates.append('z' + slp1_base[1:])
        if slp1_base.startswith('n'):
            candidates.append('R' + slp1_base[1:])

        strip_prefixes = ['qu', 'wu', 'o~', 'Y']

        # Pass 1: exact class match
        for entry in self._entries:
            if entry['class_num'] != class_num:
                continue
            raw = entry['raw']
            clean = raw.replace('\\', '').replace('^', '').replace('~', '')
            for pfx in strip_prefixes:
                if clean.startswith(pfx):
                    clean = clean[len(pfx):]
            for cand in candidates:
                if clean.startswith(cand):
                    return raw
                if cand.endswith('h') and clean.startswith(cand[:-1] + 'H'):
                    return raw
                    
        # Pass 2: any class match (for roots like śru that are classified differently in Dhatupatha)
        for entry in self._entries:
            raw = entry['raw']
            clean = raw.replace('\\', '').replace('^', '').replace('~', '')
            for pfx in strip_prefixes:
                if clean.startswith(pfx):
                    clean = clean[len(pfx):]
            for cand in candidates:
                if clean.startswith(cand):
                    return raw
                if cand.endswith('h') and clean.startswith(cand[:-1] + 'H'):
                    return raw
                    
        return None

    def _raw_is_idit(self, raw: str) -> bool:
        """
        True if the root is marked with a short 'i' (Id-it).
        Pāṇini 7.1.58: 'idito num dhātoḥ' (Id-it roots get a nasal).
        """
        # Remove markers for nasalization (~), anudatta (\), and svarita (^)
        # Example: 'vadi~\' -> 'vadi'
        clean = raw.replace('~', '').replace('\\', '').replace('^', '')
        return clean.endswith('i')


    def _raw_permitted_voices(self, raw: str) -> set[str]:
        """Derive permitted voice (Pada) from Pāṇinian anubandhas and accents."""
        # 1. Check for explicit consonant anubandhas
        if raw.endswith('N'):
            return {"middle"}           # ṅ-it -> Ātmanepada
        if raw.endswith('Y'):
            return {"active", "middle"} # ñ-it -> Ubhayapada

        # 2. Check for Pāṇinian accent markers on the final anubandha.
        # We must peel away the '~' (nasalization) and other common 
        # consonant tags (like 'p', 'c', 'x') to expose the bare accent.
        suffix = raw
        while suffix and suffix[-1] in ('~', 'p', 'x', 'm', 'f', 'c'):
            suffix = suffix[:-1]
            
        # '\' = Anudāttet (Ātmanepada), '^' = Svaritet (Ubhayapada)
        if suffix.endswith('\\'):
            return {"middle"}
        elif suffix.endswith('^'):
            return {"active", "middle"}
            
        # 3. Default to Parasmaipada
        return {"active"}

    @staticmethod
    def _raw_is_anit(raw: str) -> bool:
        """Anudātta accent marker '\\' indicates Aniṭ."""
        return '\\' in raw

    @staticmethod
    def _raw_is_vet(raw: str) -> bool:
        """Svarita accent marker '~' typically indicates Veṭ (optionally Seṭ)."""
        return '~' in raw

    def _raw_aorist_type(self, root_str: str, raw: str) -> str:
        """Derive aorist class from anubandhas + phonology."""
        cleaned = raw.replace('\\', '').replace('^', '').replace('~', '')
        suffix_part = cleaned
        for it in ('Y', 'N', 'p'):
            if suffix_part.endswith(it):
                suffix_part = suffix_part[:-1]

        phonemes = ALPHABET.parse_phonemes(root_str)

        # ḷ-it (x) or f-suffix anubandha → a-aorist
        if suffix_part.endswith('x'):
            return 'a'
        if suffix_part.endswith('f') and phonemes and phonemes[-1] != 'ṛ':
            return 'a'
        # m-suffix anubandha → a-aorist (gam, muc)
        if suffix_part.endswith('m') and phonemes and phonemes[-1] != 'm':
            return 'a'

        is_anit = self._raw_is_anit(raw)

        # sa-aorist: aniṭ root ending in ś/ṣ/s/h with penultimate i/u/ṛ
        if is_anit and phonemes:
            if phonemes[-1] in ('ś', 'ṣ', 's', 'h'):
                if len(phonemes) >= 2 and phonemes[-2] in ('i', 'u', 'ṛ'):
                    return 'sa'

        return 's' if is_anit else 'is'

    # ── Public API ─────────────────────────────────────────────────────────────

    def get(self, root_str: str, class_num: int) -> RootObject:
        """Return a *cached* RootObject for the given root/class pair.

        Falls back to a safe default (Seṭ, is-aorist, no periphrastic)
        if the root is not found in the CSV.
        """
        key = (root_str, class_num)
        if key in self._cache:
            return self._cache[key]

        raw = self._find_raw(root_str, class_num)
        flags = self._parse_paninian_flags(raw) if raw else {
            k: False for k in ["is_idit", "is_irit", "is_uuit", "is_duit", "is_s_opadesa", "is_n_opadesa"]
        }

        if raw is None:
            obj = RootObject(
                iast=root_str,
                class_num=class_num,
                is_anit=False,
                is_vet=False,
                aorist_type="",
                takes_periphrastic_perfect=self._check_periphrastic(root_str),
                permitted_voices={"active", "middle"},
                takes_samprasarana=(root_str in _SAMPRASARANA_ROOTS),
                **flags
            )
        else:
            obj = RootObject(
                iast=root_str,
                class_num=class_num,
                is_anit=self._raw_is_anit(raw),
                is_vet=self._raw_is_vet(raw),
                aorist_type=self._raw_aorist_type(root_str, raw),
                takes_periphrastic_perfect=self._check_periphrastic(root_str),
                permitted_voices=self._raw_permitted_voices(raw),
                takes_samprasarana=(root_str in _SAMPRASARANA_ROOTS),
                **flags
            )
            
        self._cache[key] = obj
        return obj

    @staticmethod
    def _check_periphrastic(root_str: str) -> bool:
        """
        True if the root structurally requires the periphrastic perfect.
        1. Polysyllabic roots.
        2. Vowel-initial roots with a heavy syllable (except a/ā).
        3. Explicitly mandated Pāṇinian exceptions (uṣ, vid, jāgṛ, etc.).
        """
        # Pāṇini 3.1.35 - 3.1.38: Explicit overrides
        explicit_periphrastic = {"uṣ", "jāgṛ", "vid", "cakās", "daridrā", "ay", "day", "ās"}
        if root_str in explicit_periphrastic:
            return True

        phonemes = ALPHABET.parse_phonemes(root_str)
        if not phonemes:
            return False

        # 1. Polysyllabic roots (contains more than one vowel)
        vowel_count = sum(1 for p in phonemes if p in ALPHABET.vowels_list)
        if vowel_count > 1:
            return True

        # 2. Heavy vowel-initial roots (ijādeś ca gurumato 'nṛcḥ)
        # Starts with a vowel (excluding a/ā)
        first = phonemes[0]
        if first in ALPHABET.vowels_list and first not in ("a", "ā"):
            # Inherently long vowels are heavy
            if first in _PERIPHRASTIC_LONG_VOWELS:
                return True
            
            # Short vowels are heavy if followed by a consonant cluster (2+ consonants)
            cons_count = 0
            for p in phonemes[1:]:
                if p in ALPHABET.consonants_list:
                    cons_count += 1
                else:
                    break
            if cons_count >= 2:
                return True

        return False

    # ── Legacy helpers (kept for backwards compat) ─────────────────────────────

    def get_root_entry(self, root_str: str, class_num: int) -> str | None:
        """Return raw CSV entry string (legacy API)."""
        return self._find_raw(root_str, class_num)

    def is_anit(self, root_str: str, class_num: int) -> bool:
        """Return True if root is Aniṭ (legacy API)."""
        return self.get(root_str, class_num).is_anit

    def get_aorist_type(self, root_str: str, class_num: int) -> str:
        """Return aorist type string (legacy API)."""
        if class_num == 10:
            return "reduplicated"
        return self.get(root_str, class_num).aorist_type


# Singleton instance
DHATUPATHA_ANALYZER = DhatupathaAnalyzer()
