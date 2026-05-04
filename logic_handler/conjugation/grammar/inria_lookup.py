import csv
import os

class InriaLookup:
    """Singleton index of roots.csv for fallback lookups.

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
        # roots.csv matches the benchmark harness’ mappings/columns.
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'roots.csv')
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    mode = row.get("mode") or ""
                    voice = row.get("voice") or ""
                    number = row.get("number") or ""

                    mode_map = {
                        "pres":  "present",
                        "ipft":  "imperfect",
                        "impv":  "imperative",
                        "opt":   "optative",
                        "ben":   "benedictive",
                        "sfut":  "future",
                        "cond":  "conditional",
                        "perf":  "perfect",
                        "pfut":  "periphrastic_future",
                        "aor":   "aorist",
                        "inj":   "injunctive",
                    }
                    voice_map = {"para": "active", "atma": "middle", "pass": "passive"}
                    number_map = {"s": "sg", "d": "du", "p": "pl"}
                    deriv_map = {"": "primary", "caus": "causative", "desid": "desiderative", "intens": "intensive"}

                    tense = mode_map.get(mode, mode)
                    voice = voice_map.get(voice, voice)
                    number = number_map.get(number, number)

                    if row.get("class") == "denom":
                        derivation = "denominative"
                    else:
                        derivation = deriv_map.get(row.get("modification", ""), "primary")

                    root_iast = (row.get("root_IAST", "") or "").split("#")[0]
                    key = (
                        root_iast,
                        tense,
                        voice,
                        row.get("person", ""),
                        number,
                        derivation,
                    )
                    form = self._normalize(row.get("form_IAST", ""))
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
        inria_root = engine_to_inria.get(root_str, root_str).split("#")[0]

        # Index keys follow roots.csv: root_IAST + derivation label.
        key = (inria_root, tense, voice, person, number, derivation)
        return self._index.get(key, [])

INRIA_LOOKUP = InriaLookup()
