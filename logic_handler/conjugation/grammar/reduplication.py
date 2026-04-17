import pynini as pn
from alphabet import ALPHABET
from irregulars import perfect_redupe_overrides


class ReduplicationEngine:
    """Applies Abhyāsa (Reduplication) phonetic reductions to a verbal prefix.

    Architecture note
    -----------------
    The four Pāṇinian reduction rules (aspiration loss, velar→palatal,
    vowel shortening, ṛ→a) are each encoded as a ``pn.cdrewrite`` FST so that
    the reduction pipeline is fully transducer-based.  ``generate_prefix``
    composes these FSTs on a per-syllable acceptor and realises the result as a
    string — the string is used as a ``pn.accep(prefix)`` in the caller.

    Special-case overrides (e.g. √bhū → prefix "ba") are stored in
    ``irregulars.perfect_redupe_overrides`` so the FST rules remain generic.
    """

    def __init__(self):
        sig = ALPHABET.sigma_star

        # ── Rule 1: Aspiration loss ───────────────────────────────────────────
        self.deaspirate = pn.cdrewrite(
            pn.string_map([
                ("kh", "k"), ("gh", "g"),
                ("ch", "c"), ("jh", "j"),
                ("ṭh", "ṭ"), ("ḍh", "ḍ"),
                ("th", "t"), ("dh", "d"),
                ("ph", "p"), ("bh", "b"),
            ]),
            "", "", sig
        )

        # ── Rule 2: Velars & h → palatals ────────────────────────────────────
        self.palatalize = pn.cdrewrite(
            pn.string_map([("k", "c"), ("g", "j"), ("h", "j")]),
            "", "", sig
        )

        # ── Rule 3: Long vowel → short ────────────────────────────────────────
        self.shorten = pn.cdrewrite(
            pn.string_map([("ā", "a"), ("ī", "i"), ("ū", "u")]),
            "", "", sig
        )

        # ── Rule 4: Vocalic ṛ → a in the prefix ──────────────────────────────
        self.r_to_a = pn.cdrewrite(
            pn.cross("ṛ", "a"), "", "", sig
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _extract_initial_syllable(self, root_str: str) -> str:
        """Return the initial consonant-cluster + first vowel of *root_str*."""
        vowels = set(ALPHABET.vowels_list)
        syllable = ""
        for ch in root_str:
            syllable += ch
            if ch in vowels:
                break
        return syllable

    def _reduce_via_fst(self, syllable: str) -> str:
        """Apply the four reduction FSTs to *syllable* and return the string."""
        fst = pn.accep(syllable)
        fst = (fst @ self.deaspirate
                    @ self.palatalize
                    @ self.shorten
                    @ self.r_to_a).optimize()
        return fst.string()

    # ── Public API ────────────────────────────────────────────────────────────

    def generate_prefix(self, root_str: str) -> str:
        """Return the reduplication prefix for *root_str*.

        Checks ``irregulars.perfect_redupe_overrides`` first; falls back to the
        general FST reduction pipeline.
        """
        if root_str in perfect_redupe_overrides:
            return perfect_redupe_overrides[root_str]

        syllable = self._extract_initial_syllable(root_str)
        return self._reduce_via_fst(syllable)