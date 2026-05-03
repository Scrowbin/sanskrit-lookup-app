import csv
import os

class InriaLookup:
    """Singleton index of verbs_clean.csv for fallback lookups.

    Used by VerifyWithDB post-pass to supplement FST output with true
    irregular or suppletive forms that the FST cannot algorithmically derive.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._index = {}
            cls._instance._load()
        return cls._instance

    def _load(self):
        csv_path = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'verbs_clean.csv'
        )
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = (
                        row['stem_iast'],
                        row['tense'],
                        row['voice'],
                        row['person'],
                        row['number'],
                        row['derivation'],
                    )
                    form = self._normalize(row['form_iast'])
                    if key not in self._index:
                        self._index[key] = []
                    if form not in self._index[key]:
                        self._index[key].append(form)
        except Exception as e:
            print(f"InriaLookup: error loading CSV — {e}")

    @staticmethod
    def _normalize(word: str) -> str:
        """Fixes INRIA's underlying 's' and 'r' to surface 'ḥ'."""
        if not word: return word
        if word.endswith('s') or word.endswith('r'):
            return word[:-1] + 'ḥ'
        return word

    def lookup(
        self,
        root_str: str,
        tense: str,
        voice: str,
        person: str,
        number: str,
        derivation: str | None
    ) -> list[str]:
        """Return a list of valid forms from the INRIA DB."""
        if derivation is None or derivation == "primary":
            derivation = "primary"
        
        # Reverse map engine roots back to INRIA stems
        engine_to_inria = {
            "div": "dīv",
        }
        inria_root = engine_to_inria.get(root_str, root_str)

        # In INRIA, causative/desiderative/intensive rows have the root_str in stem_iast,
        # and derivation field marks them.
        key = (inria_root, tense, voice, person, number, derivation)
        return self._index.get(key, [])

INRIA_LOOKUP = InriaLookup()
