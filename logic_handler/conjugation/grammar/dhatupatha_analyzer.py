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
    aorist_type: str
    takes_periphrastic_perfect: bool

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
        if raw is None:
            obj = RootObject(
                iast=root_str,
                class_num=class_num,
                is_anit=False,
                is_vet=False,
                aorist_type='is',
                takes_periphrastic_perfect=self._check_periphrastic(root_str),
            )
        else:
            is_anit = self._raw_is_anit(raw)
            is_vet = self._raw_is_vet(raw)
            obj = RootObject(
                iast=root_str,
                class_num=class_num,
                is_anit=is_anit,
                is_vet=is_vet,
                aorist_type=self._raw_aorist_type(root_str, raw),
                takes_periphrastic_perfect=self._check_periphrastic(root_str),
            )
        self._cache[key] = obj
        return obj

    @staticmethod
    def _check_periphrastic(root_str: str) -> bool:
        """True if the root's first phoneme is a long vowel (→ periphrastic perfect)."""
        phonemes = ALPHABET.parse_phonemes(root_str)
        return bool(phonemes) and phonemes[0] in _PERIPHRASTIC_LONG_VOWELS

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
