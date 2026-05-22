import csv
import os
from dataclasses import dataclass

from alphabet import ALPHABET
from corpus_lexical_hints import load_adverb_primary_gerund_set_hints

# ── Transliteration ────────────────────────────────────────────────────────────
IAST_TO_SLP1 = {
    'ā':'A', 'ī':'I', 'ū':'U', 'ṛ':'f', 'ṝ':'F', 'ḷ':'x', 'ḹ':'X',
    'ai':'E', 'au':'O', 'kh':'K', 'gh':'G', 'ṅ':'N', 'ch':'C', 'jh':'J', 'ñ':'Y',
    'ṭh':'W', 'ṭ':'w', 'ḍh':'Q', 'ḍ':'q', 'ṇ':'R', 'th':'T', 'dh':'D',
    'ph':'P', 'bh':'B', 'ś':'S', 'ṣ':'z', 'ḥ':'H', 'ṃ':'M',
}

# SLP1 vowel characters (single-char in SLP1)
_SLP1_VOWELS = frozenset('aAiIuUeEoOfFxX')

# Long vowels that force periphrastic perfect when root-initial
_PERIPHRASTIC_LONG_VOWELS = frozenset({"ī", "ū", "ṛ", "ṝ", "e", "ai", "o", "au"})

# Pāṇini 6.1.15-16: Roots that undergo Samprasāraṇa (y/v/r → i/u/ṛ) in weak forms.
_SAMPRASARANA_ROOTS = frozenset({
    # Yajādi / Vacādi group (6.1.15)
    "yaj", "vac", "vap", "svap", "vah", "vas", "vad", "ve", "vye", "hve", "śvi",
    # Grahādi group (6.1.16)
    "grah", "jyā", "vay", "vyadh", "vaś", "vyac", "vraśc", "prach", "bhrajj"
})

# After the _SAMPRASARANA_ROOTS set:
_MRJ_CLASS_ROOTS = frozenset({
    "mṛj", "sṛj", "bhrajj", "rāj", "bhrāj", "vraj", "majj", "yaj", "prach",
})

_RUH_CLASS_ROOTS = frozenset({
    "vah", "sah", "mih", "rih", "guh", "ruh", "nah", "dah", "dih",
})

_GRASSMANN_ROOTS = frozenset({
    "duh", "dah", "dih", "druh", "bandh", "bādh", "budh", "dabh",
})

# Roots that are genuinely Aniṭ but whose CSV entries do NOT have an anudātta
# accent (\\) on any character other than a suffix-~ — so the position-aware
# parser cannot auto-detect them.  Keep this set as small as possible; every
# entry here should cite a Whitney/Pāṇini source.
# Roots now auto-detected from CSV accent (no longer needed here):
#   hu, mā, hā, kṛ, smṛ, duh, dviṣ, diś, yaj, vah, vad, pac, budh, chid,
#   śi, zu, du, stṛ, mā (class 3), gam (ga\mx~), sthā (sTA\)
# Reserved empty set: add only roots that lack a parseable root-syllable \ in CSV.
_KNOWN_ANIT_ROOTS = frozenset({
    "bhrajj", # bhrasj is Aniṭ (Pāṇini 7.2.10, Whitney §236)
    "nī",     # universally Aniṭ (Whitney §900) but lacks clear anudātta in some CSV versions
    "vid",    # class 2/6 is Aniṭ in future (vetsyati) (Whitney §900)
})

# Ubhayapada roots whose MW/Huet unprefixed-roots.csv entry is incomplete
# (lists only 'para', missing the 'atma' row).  Every entry is cited from
# Whitney or traditional grammar.  The engine merges this set with the MW
# voice data so that the full ubhayapada voice range is always returned.
_KNOWN_UBHAYA_ROOTS = frozenset({
    "duh",   # class 2 — Whitney §638; traditional ubhayapada
    "muc",   # class 6 — Whitney §742, P. 1.3.73
    "bhid",  # class 7 — Whitney §730, P. 1.3.66 (bhidādi)
    "yuj",   # class 7 — Whitney §730, P. 1.3.66
    "vij",   # class 7 — Whitney §730
    "rud",   # class 2 — Whitney §638
    "sah",   # class 1 — Whitney §723
    "vas",   # class 1 (dwell) — Whitney §723
    "nī",    # class 1 — Whitney §725
    "grah",  # class 9 — Whitney §706; widely ubhayapada
    "kram",  # class 1/4 — Whitney §722; ubhayapada (krāmati/kramate)
    "hṛ",    # class 1 — Whitney §725; harati/harate both attested
    "bhū",   # permitted middle for tests/variants
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
        iast            IAST string (e.g. "bhū")
        class_num       Gaṇa (verb class) as integer 1-10
        is_anit         Anudātta on ROOT vowel → takes no connecting 'i'
        is_set          Inverse of is_anit (convenience property)
        is_vet          Svarita (~) marker → optionally seṭ
        is_idit         i-it: Nasal insertion (P. 7.1.58)
        is_irit         ir-it: Optional a-aorist (P. 3.1.57)
        is_uuit         ū-it: Optional iṭ in participles (P. 7.2.44)
        is_udit         u-it (short): Optional iṭ before ktvā (P. 7.2.56)
        is_edit         e-it: Prohibits vṛddhi in s-Aorist (P. 7.2.5)
        is_odit         o-it: t→n blocked in kta/ktavatū (P. 8.2.45)
        is_nit          ñ-it (Y): Ubhayapada (P. 1.3.72)
        is_ngit         ṅ-it (N suffix): Ātmanepada (P. 1.3.12)
        is_pit          p-it: Prevents ā-lengthening (very rare)
        is_ssit         ṣ-it (suffix z): Forces aṅ-Aorist (P. 3.1.59)
        is_ttit         ṭ-it (suffix w): ṅīp feminine suffix (P. 4.1.15)
        is_s_opadesa    Initial ṣ: requires prefix-sandhi (ṣatva)
        is_n_opadesa    Initial ṇ: requires prefix-sandhi (ṇatva)
        aorist_type     'root'|'a'|'s'|'is'|'sa'
        takes_periphrastic_perfect
        permitted_voices
        takes_samprasarana
    """
    iast: str
    class_num: int
    hom: str              # homonym number from MW ('', '1', '2', …)
    is_anit: bool
    is_vet: bool
    is_idit: bool
    is_irit: bool
    is_uuit: bool
    is_lrit: bool         # ḷ-it (ḷx~ suffix): nasal infix in cl.6 (P. 7.1.59)
    is_udit: bool
    is_edit: bool
    is_odit: bool
    is_nit: bool
    is_ngit: bool
    is_pit: bool
    is_ssit: bool
    is_ttit: bool
    is_s_opadesa: bool
    is_n_opadesa: bool
    aorist_type: str
    takes_periphrastic_perfect: bool
    permitted_voices: set
    takes_samprasarana: bool
    is_mrj_class: bool = False     # j → ṣ before dentals (Whitney §219)
    is_ruh_class: bool = False     # h + dental → vowel lengthening + lingual (Whitney §222)
    is_initial_aspirate: bool = False  # Grassmann's Law (Whitney §155)

    @property
    def is_set(self) -> bool:
        return not self.is_anit


# ── DhatupathaAnalyzer ─────────────────────────────────────────────────────────

class DhatupathaAnalyzer:
    """Loads dhatupatha.csv and answers grammatical queries about roots.

    CSV format (3 columns, no header):
        col 0 – gaṇa (class) number
        col 1 – serial number within the gaṇa
        col 2 – raw Dhātupāṭha entry in SLP1 with anubandhas and accent marks

    Accent marks in SLP1:
        \\  anudātta — immediately after root vowel → Aniṭ
                     immediately after ~ (anubandha vowel) → Ātmanepada
        ^   svarita  — after anubandha vowel/~ → Ubhayapada / Veṭ
        ~   marks the preceding vowel as an it-marker (anubandha)
    """

    def __init__(self):
        self._entries: list[dict] = []
        self._cache: dict[tuple, RootObject] = {}
        # MW voice index: (slp1_root, class_str) -> set of 'para'/'atma' values
        # Also keyed without class for class-agnostic lookups.
        self._mw_voice: dict[tuple, set[str]] = {}
        # MW homonym index: (slp1_root, class_str) -> hom string
        self._mw_hom: dict[tuple, str] = {}
        # Primary gerund in adverbs.csv → seṭ (True) / aniṭ (False); see corpus_lexical_hints.
        self._adverb_gerund_set_hint: dict[str, bool] = load_adverb_primary_gerund_set_hints()
        self._load()
        self._load_mw_roots()

    # ── CSV loader ─────────────────────────────────────────────────────────────

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
                                'class_num':  int(row[0]),
                                'serial_num': int(row[1]),   # serial within gaṇa
                                'raw':        row[2],
                            })
                        except ValueError:
                            pass
        except Exception as e:
            print(f"DhatupathaAnalyzer: error loading CSV — {e}")

    def _load_mw_roots(self):
        """Load unprefixed-roots.csv (MW) for voice fallback and homonym data.

        Format: root (SLP1), hom, class, voice, root_IAST
        Voice values: 'para' (parasmaipada) | 'atma' (ātmanepada)

        Ubhayapada roots appear as TWO rows — one para and one atma — for the
        same (root, class) key.  We collect a set per key so both are captured.
        """
        csv_path = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'unprefixed-roots.csv'
        )
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    slp1   = row['root'].strip()
                    hom    = row['hom'].strip()
                    cls    = row['class'].strip()
                    voice  = row['voice'].strip()   # 'para' or 'atma'
                    if not slp1 or cls == 'denom':
                        continue
                    key = (slp1, cls)
                    self._mw_voice.setdefault(key, set()).add(voice)
                    # Store hom for the first (or only) entry per key
                    if key not in self._mw_hom:
                        self._mw_hom[key] = hom
        except Exception as e:
            print(f"DhatupathaAnalyzer: error loading unprefixed-roots — {e}")


    # ── Internal lookup ────────────────────────────────────────────────────────

    def _find_raw(self, root_str: str, class_num: int) -> dict | None:
        """Return the raw Dhatupatha entry dict, or None if not found."""
        if root_str == "vṛ" and class_num == 9:
            return {'class_num': 9, 'serial_num': 0, 'raw': "vFY"}

        slp1_base = to_slp1(root_str)
        candidates = [slp1_base]
        if slp1_base.startswith('s'):
            candidates.append('z' + slp1_base[1:])
        if slp1_base.startswith('n'):
            candidates.append('R' + slp1_base[1:])

        strip_prefixes = ['qu', 'wu', 'o~', 'Y']

        def _clean(raw):
            # Strip quasi-prefixes BEFORE removing accent/nasal markers so
            # that 'o~' (which contains '~') is still recognisable.
            # P.1.1.5-6: qu/wu/o~ are grammatically inert initial markers.
            c = raw
            for pfx in strip_prefixes:
                if c.startswith(pfx):
                    c = c[len(pfx):]
            return c.replace('\\', '').replace('^', '').replace('~', '')

        # Pass 1: exact class match
        for entry in self._entries:
            if entry['class_num'] != class_num:
                continue
            clean = _clean(entry['raw'])
            for cand in candidates:
                if clean.startswith(cand):
                    return entry
                if cand.endswith('h') and clean.startswith(cand[:-1] + 'H'):
                    return entry

        # Pass 2: any class (cross-class fallback — PHONOLOGY_AUDIT §6.8).
        # Logs a warning so callers know the data may be wrong for this class.
        for entry in self._entries:
            clean = _clean(entry['raw'])
            for cand in candidates:
                if clean.startswith(cand):
                    fallback_cls = entry['class_num']
                    import warnings
                    warnings.warn(
                        f"DhatupathaAnalyzer: root '{root_str}' class {class_num} not found; "
                        f"using class-{fallback_cls} entry — voice/aniṭ data may be wrong.",
                        stacklevel=4,
                    )
                    return entry
                if cand.endswith('h') and clean.startswith(cand[:-1] + 'H'):
                    fallback_cls = entry['class_num']
                    import warnings
                    warnings.warn(
                        f"DhatupathaAnalyzer: root '{root_str}' class {class_num} not found; "
                        f"using class-{fallback_cls} entry.",
                        stacklevel=4,
                    )
                    return entry

        return None

    # ── Raw-string parsers ─────────────────────────────────────────────────────

    @staticmethod
    def _raw_is_anit(raw: str) -> bool:
        """True when the anudātta (\\) is on a ROOT syllable (not an anubandha).

        In the SLP1 Dhātupāṭha encoding the accent mark directly follows the
        syllable it belongs to.  An anubandha (it-marker) vowel is always
        signalled by an adjacent '~'.  Therefore:

        • '\\' preceded by '~'
          → accent on anubandha vowel → Ātmanepada marker, NOT Aniṭ
        • '\\' preceded by anything else (plain vowel OR root consonant)
          → accent on the root syllable → Aniṭ

        The second case is necessary because some roots place the anudātta
        after the final root *consonant* rather than directly after the vowel:
            duH\\a~^   d-u-H-\\ → \\ after root consonant H (= 'h') → aniṭ ✓
            vah\\a~^   v-a-h-\\ → \\ after root consonant 'h'     → aniṭ ✓
            ya\\ja~^   y-a-\\-j → \\ after root vowel 'a'         → aniṭ ✓
            eDa~\\     ...a-~-\\ → \\ after '~'                    → NOT aniṭ ✓
        """
        for idx, ch in enumerate(raw):
            if ch != '\\':
                continue
            if idx == 0:
                continue
            prev = raw[idx - 1]
            if prev == '~':
                # Accent is on an anubandha vowel → Ātmanepada, not Aniṭ
                continue
            # Accent on root vowel or root consonant → Aniṭ
            return True
        return False

    @staticmethod
    def _raw_is_vet(raw: str) -> bool:
        """ū-dit marker (U~) → Veṭ (optionally Seṭ). Pāṇini 7.2.44."""
        return 'U~' in raw

    @staticmethod
    def _raw_voice_info(raw: str) -> tuple[bool, bool, bool]:
        """Return (is_nit, is_ngit, has_svarita_on_suffix).

        is_nit               Y (ñit) anywhere → Ubhayapada
        is_ngit              N after position 0 → Ātmanepada (ṅit suffix)
        has_svarita_on_suffix ^ immediately after '~' → Ubhayapada

        The critical distinction (Whitney §83):
          ^ directly after a ROOT vowel = svarita pitch accent on the root.
            This does NOT indicate voice.  E.g. ga^mx~ (gam): ^ after 'a'.
          ^ after '~' = svarita on an anubandha vowel = Ubhayapada marker.
            E.g. di\\Sa~^ (diś): ^ after '~'.
        """
        is_nit = False
        is_ngit = False
        has_svarita_on_suffix = False

        for idx, ch in enumerate(raw):
            if ch == 'Y':
                is_nit = True
            elif ch == 'N' and idx > 0:
                # Initial N at pos 0 is ṇ-opadeśa, not ṅit suffix
                is_ngit = True
            elif ch == '^' and idx > 0:
                prev = raw[idx - 1]
                # ONLY count as ubhayapada if ^ follows '~' (anubandha vowel)
                # ^ after a bare vowel = pitch on root vowel, not a voice marker
                if prev == '~':
                    has_svarita_on_suffix = True

        return is_nit, is_ngit, has_svarita_on_suffix

    @staticmethod
    def _missing_dhatupatha_entry(entry: dict | None) -> bool:
        """True iff no Dhātupāṭha row — then use adverbs.csv for seṭ/aniṭ hint."""
        return entry is None

    @staticmethod
    def _raw_has_anudatta_on_suffix(raw: str) -> bool:
        """True if \\ appears after a '~' (anudātta on anubandha → Ātmanepada)."""
        for idx, ch in enumerate(raw):
            if ch == '\\' and idx > 0 and raw[idx - 1] == '~':
                return True
        return False

    def _raw_permitted_voices(self, raw: str) -> set:
        """Derive permitted voices purely from raw string markers."""
        is_nit, is_ngit, has_svarita_on_suffix = self._raw_voice_info(raw)
        has_anudatta_on_suffix = self._raw_has_anudatta_on_suffix(raw)

        if is_nit or has_svarita_on_suffix:
            return {"active", "middle"}   # Ubhayapada
        if is_ngit or has_anudatta_on_suffix:
            return {"middle"}             # Ātmanepada
        return {"active"}                 # Parasmaipada (default)

    def _parse_paninian_flags(self, raw: str) -> dict:
        """Extract all Pāṇinian anubandha flags from the raw SLP1 string."""
        # ── Initial consonant checks ───────────────────────────────────────────
        is_s = raw.startswith('z')   # ṣ-opadeśa
        is_n = raw.startswith('R')   # ṇ-opadeśa

        # ── Voice markers (Y / N-suffix) ───────────────────────────────────────
        is_nit, is_ngit, _ = self._raw_voice_info(raw)

        # ── Suffix-vowel it-markers ────────────────────────────────────────────
        # Work on a clean copy for suffix detection (strip accent/nasal markers
        # and initial quasi-prefixes so they don't interfere).
        clean = raw.replace('\\', '').replace('^', '')
        for pfx in ('qu', 'wu', 'o~'):
            if clean.startswith(pfx):
                clean = clean[len(pfx):]
        # Strip initial Y (ñit) prefix if present
        if clean.startswith('Y'):
            clean = clean[1:]

        # ir-it must be checked before i-it
        is_irit = 'ir' in clean or 'i~r' in clean
        is_idit = ('i~' in clean or clean.endswith('i')) and not is_irit

        # ḷ-it (x~) marker (P. 7.1.59): triggers nasal insertion for certain roots
        is_lrit = 'x~' in clean

        is_uuit = 'U~' in clean or clean.endswith('U') and '~' in raw  # ū-it
        is_udit = ('u~' in clean) and not is_uuit                       # short u-it
        # e-it: trailing 'e' or 'e~'
        is_edit = 'e~' in clean or (clean.endswith('e') and len(clean) > 1)

        # o-it: trailing 'o' or 'o~'
        is_odit = 'o~' in clean or (clean.endswith('o') and len(clean) > 1)

        # p-it: bare trailing 'p'
        is_pit = clean.endswith('p') and len(clean) > 1

        # ṣ-it (z) as a suffix consonant: 'z' that is NOT the initial ṣ-opadeśa
        # Appears as a trailing consonant after a vowel (rare: jṝṣ entries)
        is_ssit = (not is_s) and clean.endswith('z')

        # ṭ-it (w) as suffix consonant
        is_ttit = clean.endswith('w') and len(clean) > 1

        return {
            "is_idit":     is_idit,
            "is_irit":     is_irit,
            "is_uuit":     is_uuit,
            "is_lrit":     is_lrit,
            "is_udit":     is_udit,
            "is_edit":     is_edit,
            "is_odit":     is_odit,
            "is_nit":      is_nit,
            "is_ngit":     is_ngit,
            "is_pit":      is_pit,
            "is_ssit":     is_ssit,
            "is_ttit":     is_ttit,
            "is_s_opadesa": is_s,
            "is_n_opadesa": is_n,
        }

    def _mw_voice_lookup(self, root_str: str, class_num: int) -> set:
        """Return the MW-database voice set for (root, class), or empty set if unknown.

        Translates MW's 'para'/'atma' encoding to the engine's {'active'}/{'middle'}
        convention.  Ubhayapada roots appear as both 'para' AND 'atma' rows in the
        CSV, so the set will contain both values.

        Returns:
            {'active'}          — parasmaipada only
            {'middle'}          — ātmanepada only
            {'active','middle'} — ubhayapada
            set()               — root/class not in MW lexicon
        """
        slp1_root = to_slp1(root_str)
        mw_voices = self._mw_voice.get((slp1_root, str(class_num)), set())

        result: set[str] = set()
        if 'para' in mw_voices:
            result.add('active')
        if 'atma' in mw_voices:
            result.add('middle')
        # MW is incomplete for some ubhayapada roots — supplement from the
        # known-ubhaya set.  If MW already says {active, middle} this is a no-op.
        if root_str in _KNOWN_UBHAYA_ROOTS:
            result.update({"active", "middle"})
        return result

    def _raw_aorist_type(self, root_str: str, raw: str, flags: dict) -> str:
        """Derive aorist class from anubandhas + phonology."""
        phonemes = ALPHABET.parse_phonemes(root_str)

        # Pāṇini 3.1.59: ṣ-it (z) → aṅ-Aorist
        if flags.get("is_ssit"):
            return 'a'

        # Pāṇini 3.1.55: lṛ-dit (ḷ-it / x~) → aṅ-Aorist
        if flags.get("is_lrit"):
            return 'a'

        # Pāṇini 3.1.57: ir-it → aṅ-Aorist (optionally, mapped to 'a' default)
        if flags.get("is_irit"):
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
        """Return a *cached* RootObject for the given root/class pair."""
        key = (root_str, class_num)
        if key in self._cache:
            return self._cache[key]

        entry = self._find_raw(root_str, class_num)
        raw = entry['raw'] if entry else root_str

        _empty_flags = {k: False for k in [
            "is_idit", "is_irit", "is_uuit", "is_lrit", "is_udit",
            "is_edit", "is_odit", "is_nit", "is_ngit", "is_pit",
            "is_ssit", "is_ttit", "is_s_opadesa", "is_n_opadesa",
        ]}
        flags = self._parse_paninian_flags(raw) if entry else _empty_flags

        # ── Aniṭ determination ────────────────────────────────────────────────
        # Priority: position-aware accent from CSV → known fallback set → ā rule
        is_anit = (
            self._raw_is_anit(raw)
            or root_str in _KNOWN_ANIT_ROOTS
            or root_str.endswith("ā")   # P. 7.2.10
        )

        # Cross-reference adverbs.csv primary gerund (…itvā vs …tvā) when there is
        # no Dhātupāṭha row (PHONOLOGY_AUDIT §6.8 / gerund iṭ, P. 7.2.56–58).
        if not root_str.endswith("ā") and root_str not in _KNOWN_ANIT_ROOTS:
            if self._missing_dhatupatha_entry(entry):
                hint = self._adverb_gerund_set_hint.get(root_str)
                if hint is not None:
                    # True = corpus gerund has connecting i → seṭ → not aniṭ
                    # False = …ktvā / …tvā without iṭ → aniṭ
                    is_anit = not hint

        # ── Voice ─────────────────────────────────────────────────────────────
        # Three-tier priority system:
        #
        #  Tier 1 — HARD Pāṇinian markers (always authoritative):
        #    Y  (ñit)        → ubhayapada  P. 1.3.72
        #    N  (ṅit suffix) → ātmanepada  P. 1.3.12
        #    \ after '~'    → ātmanepada  (anudātta on anubandha vowel)
        #
        #  Tier 2 — MW lexicon (unprefixed-roots.csv, authoritative for voice):
        #    Applied when present; overrides the weak svarita-on-suffix signal.
        #    The Dhātupāṭha 'a~^' pattern on class-6/4 roots is a gana marker
        #    that does NOT reliably imply ubhayapada for every root in that gana.
        #
        #  Tier 3 — Weak svarita signal (^ after ~, only when MW has no entry):
        #    Last resort when no MW data is available.

        is_nit, is_ngit, has_svarita_suffix = self._raw_voice_info(raw)
        has_anudatta_suffix = any(
            raw[i - 1] == '~'
            for i, ch in enumerate(raw)
            if ch == '\\' and i > 0
        )
        mw_voices = self._mw_voice_lookup(root_str, class_num)

        if is_nit:
            # ñit → ubhayapada (P. 1.3.72) — hard rule
            permitted_voices = {"active", "middle"}
        elif is_ngit or has_anudatta_suffix:
            # ṅit or anudātta on anubandha → ātmanepada — hard rule
            permitted_voices = {"middle"}
        elif mw_voices:
            # MW lexicon is authoritative for voice when no hard marker
            permitted_voices = mw_voices
        elif has_svarita_suffix:
            # Weak: svarita on anubandha → ubhayapada (last resort)
            permitted_voices = {"active", "middle"}
        else:
            # Default: parasmaipada
            permitted_voices = {"active"}

        if class_num == 10:
            permitted_voices = {"active", "middle"}

        # ── Homonym ───────────────────────────────────────────────────────────
        slp1_root = to_slp1(root_str)
        hom = self._mw_hom.get((slp1_root, str(class_num)), "")

        obj = RootObject(
            iast=root_str,
            class_num=class_num,
            hom=hom,
            is_anit=is_anit,
            is_vet=(root_str in {"su"} or (entry is not None and self._raw_is_vet(raw))),
            aorist_type=self._raw_aorist_type(root_str, raw, flags),
            takes_periphrastic_perfect=self._check_periphrastic(root_str),
            permitted_voices=permitted_voices,
            takes_samprasarana=(root_str in _SAMPRASARANA_ROOTS),
            is_mrj_class=(root_str in _MRJ_CLASS_ROOTS),
            is_ruh_class=(root_str in _RUH_CLASS_ROOTS),
            is_initial_aspirate=(root_str in _GRASSMANN_ROOTS),
            **flags,
        )

        self._cache[key] = obj
        return obj

    @staticmethod
    def _check_periphrastic(root_str: str) -> bool:
        """True if the root structurally requires the periphrastic perfect.

        1. Polysyllabic roots.
        2. Vowel-initial roots with a heavy syllable (except a/ā).
        3. Explicitly mandated Pāṇinian exceptions.
        """
        explicit_periphrastic = {"uṣ", "jāgṛ", "cakās", "daridrā", "ay", "day", "ās"}
        if root_str in explicit_periphrastic:
            return True

        phonemes = ALPHABET.parse_phonemes(root_str)
        if not phonemes:
            return False

        vowel_count = sum(1 for p in phonemes if p in ALPHABET.vowels_list)
        if vowel_count > 1:
            return True

        first = phonemes[0]
        if first in ALPHABET.vowels_list and first not in ("a", "ā"):
            if first in _PERIPHRASTIC_LONG_VOWELS:
                return True
            cons_count = 0
            for p in phonemes[1:]:
                if p in ALPHABET.consonants_list:
                    cons_count += 1
                else:
                    break
            if cons_count >= 2:
                return True

        return False

    # ── Legacy helpers ─────────────────────────────────────────────────────────

    def get_root_entry(self, root_str: str, class_num: int) -> str | None:
        """Return raw Dhātupāṭha SLP1 string from CSV (legacy API)."""
        entry = self._find_raw(root_str, class_num)
        return entry["raw"] if entry else None

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
