import csv
import os

class InriaLookup:
    """Singleton index of verbs_clean.csv for fallback lookups.

    Used by the conjugation engine as a post-pass supplement: the FST
    generates forms algorithmically; for roots whose irregular or suppletive
    forms the FST cannot derive, the DB provides the authoritative surface.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._index = None
        return cls._instance

    def _ensure_loaded(self) -> None:
        if self._index is not None:
            return
        self._index = {}
        self._load()

    def _load(self):
        # verbs_clean.csv columns:
        #   form_slp1, form_iast, stem_slp1, stem_iast,
        #   tense, voice, person, number, class, derivation
        import sys
        if getattr(sys, 'frozen', False):
            data_dir = os.path.join(sys._MEIPASS, 'data')
        else:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        csv_path = os.path.join(data_dir, 'verbs_clean.csv')
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    root_iast  = (row.get('stem_iast',   '') or '').split('#')[0].strip()
                    tense      = (row.get('tense',       '') or '').strip()
                    voice      = (row.get('voice',       '') or '').strip()
                    person     = (row.get('person',      '') or '').strip()
                    number     = (row.get('number',      '') or '').strip()
                    derivation = (row.get('derivation',  '') or 'primary').strip() or 'primary'

                    if not root_iast:
                        continue

                    key  = (root_iast, tense, voice, person, number, derivation)
                    form = (row.get('form_iast', '') or '').strip()
                    if not form:
                        continue

                    if key not in self._index:
                        self._index[key] = []
                    if form not in self._index[key]:
                        self._index[key].append(form)

        except Exception as e:
            print(f"InriaLookup: error loading verbs_clean.csv - {e}")

    @staticmethod
    def _normalize(word: str) -> str:
        """Fixes INRIA's underlying 's' and 'r' to surface 'ḥ'."""
        if not word:
            return word
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
        derivation: str | None,
    ) -> list[str]:
        """Return a list of valid IAST forms from verbs_clean.csv."""
        self._ensure_loaded()
        if not derivation or derivation == "primary":
            derivation = "primary"

        # Engine-internal root aliases → canonical IAST stems in the DB
        engine_to_db = {
            "div": "dīv",
        }
        db_root = engine_to_db.get(root_str, root_str).split('#')[0]

        key = (db_root, tense, voice, person, number, derivation)
        return self._index.get(key, [])


INRIA_LOOKUP = InriaLookup()
