import csv
import os
from alphabet import ALPHABET

# Transliteration mapping for IAST to SLP1
IAST_TO_SLP1 = {
    'ā':'A', 'ī':'I', 'ū':'U', 'ṛ':'f', 'ṝ':'F', 'ḷ':'x', 'ḹ':'X',
    'ai':'E', 'au':'O', 'kh':'K', 'gh':'G', 'ṅ':'N', 'ch':'C', 'jh':'J', 'ñ':'Y',
    'ṭh':'W', 'ṭ':'w', 'ḍh':'Q', 'ḍ':'q', 'ṇ':'R', 'th':'T', 'dh':'D', 'ph':'P', 'bh':'B',
    'ś':'S', 'ṣ':'z', 'ḥ':'H', 'ṃ':'M'
}

def to_slp1(iast_str):
    s = iast_str
    # Replace longer matches first
    for k, v in sorted(IAST_TO_SLP1.items(), key=lambda x: -len(x[0])):
        s = s.replace(k, v)
    return s

class DhatupathaAnalyzer:
    def __init__(self):
        self.roots = []
        self._load()

    def _load(self):
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dhatupatha.csv')
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 3 and not row[0].startswith('#'):
                        self.roots.append({
                            'class_num': int(row[0]),
                            'raw': row[2]
                        })
        except Exception as e:
            print(f"Error loading dhatupatha.csv: {e}")

    def get_root_entry(self, root_str, class_num):
        """Find the matching Dhatupatha entry for an IAST root in a specific class."""
        slp1_base = to_slp1(root_str)
        # Some roots in Dhatupatha are stored with initial z/R instead of s/n (e.g. su -> zu)
        # For simplicity in this small benchmark, if slp1_base starts with 's', try 'z' too.
        candidates = [slp1_base]
        if slp1_base.startswith('s'):
            candidates.append('z' + slp1_base[1:])
        if slp1_base.startswith('n'):
            candidates.append('R' + slp1_base[1:])

        # Some roots in Dhatupatha have 'qu', 'wu', 'o~' as anubandha prefixes.
        # e.g. krī -> qukrI\Y, kṛ -> qukf\Y, nuj -> wunadi~
        prefixes_to_strip = ['qu', 'wu', 'o~', 'Y']
        
        for entry in self.roots:
            if entry['class_num'] == class_num:
                raw = entry['raw']
                clean = raw.replace('\\', '').replace('^', '').replace('~', '')
                for pfx in prefixes_to_strip:
                    if clean.startswith(pfx):
                        clean = clean[len(pfx):]
                for cand in candidates:
                    if clean.startswith(cand):
                        return raw
                    # Special case: some H (visarga) roots are used instead of h
                    # e.g. duH -> duh
                    if cand.endswith('h') and clean.startswith(cand[:-1] + 'H'):
                        return raw
        return None

    def is_anit(self, root_str, class_num):
        """A root is Aniṭ if it has an anudātta accent (\) in the Dhatupatha."""
        entry = self.get_root_entry(root_str, class_num)
        if not entry:
            return False
        # \ is the marker for anudatta, meaning anit
        return '\\' in entry

    def get_aorist_type(self, root_str, class_num):
        """Determine Aorist type from Paninian anubandhas and phonology.
        Returns: 'root', 'a', 's', 'is', 'sa' (or None if unhandled fallback)
        """
        entry = self.get_root_entry(root_str, class_num)
        if not entry:
            return "is" # Fallback to default Seṭ aorist

        # 1. Anubandhas that trigger a-aorist (puṣādi-dyutādi-lṛdit)
        # x (ḷ), ir, and f (ṛ, but only as a suffix marker, not the root vowel)
        # Typical entries end with these followed by ~ or \ or ^
        cleaned_entry = entry.replace('\\','').replace('^','').replace('~','')
        # We need to strip the root part to check suffixes.
        # But for simplicity, we can just check if it ends with x or ir or f (ignoring Y or N markers)
        suffix_part = cleaned_entry
        for it in ['Y', 'N', 'p']:
            if suffix_part.endswith(it):
                suffix_part = suffix_part[:-1]
                
        phonemes = ALPHABET.parse_phonemes(root_str)
        
        if suffix_part.endswith("f") or suffix_part.endswith("x"):
            # kṛ is qukf\Y. After stripping Y, it's qukf. Ends in f.
            # But f is the root vowel. Anubandha f only occurs on consonant-ending roots like kfIqf.
            # So if it ends in f, it's anubandha ONLY if length is > root length, or simply:
            if suffix_part.endswith("f") and len(phonemes) > 0 and phonemes[-1] != 'ṛ':
                return "a"
            if suffix_part.endswith("x"):
                return "a"

        # Special root aorist overrides (e.g., bhū)
        if root_str in ("bhū",):
            return "root"

        is_anit = self.is_anit(root_str, class_num)
        
        # 2. sa-aorist (Panini 3.1.45): ends in ś,ṣ,s,h + penultimate i,u,ṛ + Aniṭ
        if is_anit and phonemes:
            if phonemes[-1] in ('ś', 'ṣ', 's', 'h'):
                if len(phonemes) >= 2 and phonemes[-2] in ('i', 'u', 'ṛ'):
                    return "sa"

        # 3. Default Aniṭ -> s-aorist
        if is_anit:
            return "s"

        # 4. Default Seṭ -> is-aorist
        return "is"

# Singleton instance
DHATUPATHA_ANALYZER = DhatupathaAnalyzer()
