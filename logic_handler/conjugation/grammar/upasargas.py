# grammar/upasargas.py

"""Verbal prefixes (Upasargas) for Sanskrit conjugation.
Whitney §1076 lists the standard prepositions. Pāṇini 1.4.58 (prādayaḥ) lists the upasargas.
"""

# The 22 traditional upasargas (nis/nir and dus/dur are grouped together, often counted as 20)
UPASARGAS = {
    "pra": "forward, forth",
    "parā": "away, forth",
    "apa": "away, off",
    "sam": "together",
    "anu": "after, along",
    "ava": "down, off",
    "nis": "out, forth",
    "nir": "out, forth",
    "dus": "bad, hard",
    "dur": "bad, hard",
    "vi": "apart, away",
    "ā": "to, unto, at",
    "ni": "down, into",
    "adhi": "above, over",
    "api": "unto, close upon",
    "ati": "across, beyond",
    "su": "well, good",
    "ud": "up, out",
    "abhi": "to, towards",
    "prati": "back, against",
    "pari": "around, about",
    "upa": "towards, near",
}

def is_valid_upasarga(prefix: str) -> bool:
    """Check if the given prefix is a valid single upasarga."""
    return prefix in UPASARGAS

def validate_preverb_string(preverbs: str) -> bool:
    """Validate a '+'-separated string of preverbs (e.g., 'sam+ud')."""
    if not preverbs:
        return True
    
    parts = preverbs.split('+')
    return all(is_valid_upasarga(p) for p in parts)
