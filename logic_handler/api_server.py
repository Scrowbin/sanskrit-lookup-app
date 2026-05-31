"""api_server.py — Lightweight Flask HTTP API wrapping the Sanskrit engines.

Exposes two POST endpoints consumed by the Electron renderer via IPC:

    POST /api/conjugate   → SanskritConjugator.conjugate()
    POST /api/declense    → DeclensionEngine.declense()
    GET  /api/health      → {"status": "ok"}

The Electron main process spawns this server as a child process and
proxies requests through IPC handlers, keeping the renderer sandboxed.

Usage (standalone testing)::

    cd logic_handler
    python api_server.py            # starts on http://127.0.0.1:5199
"""
from __future__ import annotations

import os
import sys
import json
import traceback

# ── Path bootstrapping ────────────────────────────────────────────────────────
# Ensure both engine directories are importable regardless of cwd.
_HERE = os.path.dirname(os.path.abspath(__file__))
_CONJ_DIR = os.path.join(_HERE, "conjugation", "grammar")
_DECL_DIR = os.path.join(_HERE, "declension")

for _p in (_HERE, _CONJ_DIR, _DECL_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flask import Flask, request, jsonify
from flask_cors import CORS

# ── Lazy engine singletons ────────────────────────────────────────────────────
# Engines are expensive to compile (pynini FST construction).  We instantiate
# them once on first request so the server starts up fast but the first actual
# call pays the compilation cost.

_conjugator = None
_declension_engine = None

# Packaged app uses generative FST only (verbs_clean.csv is ~12 MB and omitted).
_USE_INRIA_DB = os.environ.get("SANSKRIT_USE_INRIA_DB", "").lower() in ("1", "true", "yes")


def _get_conjugator():
    global _conjugator
    if _conjugator is None:
        # Import from conjugation/grammar/conjugate.py
        from conjugate import SanskritConjugator
        _conjugator = SanskritConjugator()
    return _conjugator


def _get_declension_engine():
    global _declension_engine
    if _declension_engine is None:
        # Import from declension/engine.py
        from engine import DeclensionEngine
        _declension_engine = DeclensionEngine()
    return _declension_engine


# ── Flask app ─────────────────────────────────────────────────────────────────

app = Flask(__name__)
CORS(app)  # allow requests from the Vite dev server (localhost:5173)


@app.route("/api/health", methods=["GET"])
def health():
    """Simple liveness probe."""
    return jsonify({"status": "ok"})


@app.route("/api/conjugate", methods=["POST"])
def conjugate():
    """Conjugate a Sanskrit verb root.

    Expected JSON body::

        {
            "root":       "bhū",        // IAST root string
            "class_num":  1,             // Gaṇa 1-10 (0 for no present)
            "person":     "3",           // "1", "2", "3"
            "number":     "sg",          // "sg", "du", "pl"
            "voice":      "active",      // "active" | "middle" | "passive"
            "tense":      "present",     // tense/mood name
            "derivative": null           // null | "causative" | "desiderative" | ...
        }

    Returns::

        { "forms": ["bhavati"], "error": null }
    """
    try:
        data = request.get_json(force=True)
        engine = _get_conjugator()
        result = engine.conjugate(
            root_str=data["root"],
            class_num=int(data.get("class_num", 1)),
            person=str(data.get("person", "3")),
            number=data.get("number", "sg"),
            voice=data.get("voice", "active"),
            tense=data.get("tense", "present"),
            derivative=data.get("derivative", None),
            use_db=_USE_INRIA_DB,
        )
        # result can be list[str] or str (krdantas block)
        if isinstance(result, str):
            forms = [result]
        else:
            forms = result
        return jsonify({"forms": forms, "error": None})
    except Exception as exc:
        traceback.print_exc()
        return jsonify({"forms": [], "error": str(exc)}), 400


@app.route("/api/conjugate/full", methods=["POST"])
def conjugate_full():
    """Generate a full conjugation paradigm for all person/number combinations.

    Expected JSON body::

        {
            "root":       "bhū",
            "class_num":  1,
            "voice":      "active",
            "tense":      "present",
            "derivative": null
        }

    Returns a dict keyed by "{person}{number}" with form lists::

        {
            "paradigm": {
                "1sg": ["bhavāmi"], "1du": ["bhavāvaḥ"], "1pl": ["bhavāmaḥ"],
                "2sg": ["bhavasi"], ...
            },
            "error": null
        }
    """
    try:
        data = request.get_json(force=True)
        engine = _get_conjugator()
        root = data["root"]
        class_num = int(data.get("class_num", 1))
        voice = data.get("voice", "active")
        tense = data.get("tense", "present")
        derivative = data.get("derivative", None)

        paradigm = engine.conjugate_paradigm(
            root_str=root,
            class_num=class_num,
            voice=voice,
            tense=tense,
            derivative=derivative,
            use_db=_USE_INRIA_DB,
        )

        return jsonify({"paradigm": paradigm, "error": None})
    except Exception as exc:
        traceback.print_exc()
        return jsonify({"paradigm": {}, "error": str(exc)}), 400

# Voices to attempt per tense (passive aliases to middle for non-present-system)
_TENSES_VOICES = {
    "present":              ["active", "middle", "passive"],
    "imperfect":            ["active", "middle", "passive"],
    "imperative":           ["active", "middle", "passive"],
    "optative":             ["active", "middle", "passive"],
    "perfect":              ["active", "middle"],
    "aorist":               ["active", "middle", "passive"],
    "future":               ["active", "middle"],
    "conditional":          ["active", "middle"],
    "periphrastic_future":  ["active"],
    "benedictive":          ["active", "middle"],
    "subjunctive":          ["active", "middle"],
    "pluperfect":           ["active", "middle"],
    "injunctive":           ["active", "middle", "passive"],
}

# Whitney §1002-1012: Intensives only conjugate in the present-system
# (present, imperfect, optative, imperative) and only in active + middle.
# The yaṅluganta active is athematic (cl3); the yaṅanta is middle-only.
_INTENSIVE_TENSES_VOICES = {
    "present":   ["active", "middle"],
    "imperfect": ["active", "middle"],
    "optative":  ["active", "middle"],
    "imperative":["active", "middle"],
}


@app.route("/api/conjugate/derivative", methods=["POST"])
def conjugate_derivative():
    """Generate all tense paradigms + kṛdantas for one derivative of a root.

    Expected JSON body::

        {
            "root":       "bhū",
            "class_num":  1,
            "derivative": null   // null | "causative" | "desiderative" | "intensive"
        }

    Returns::

        {
            "result": {
                "tenses": {
                    "present": {
                        "active":  {"1sg": [...], ...},
                        "middle":  {"1sg": [...], ...}
                    },
                    ...
                },
                "krdantas": "..."
            },
            "error": null
        }
    """
    try:
        data = request.get_json(force=True)
        engine = _get_conjugator()
        root = data["root"]
        class_num = int(data.get("class_num", 1))
        derivative = data.get("derivative", None)

        result = {"tenses": {}}

        # Intensives use a restricted tense set (Whitney §1002-1012)
        tenses_voices = _INTENSIVE_TENSES_VOICES if derivative == "intensive" else _TENSES_VOICES

        for tense, voices in tenses_voices.items():
            tense_data = {}
            for voice in voices:
                paradigm = {}
                has_any = False
                for person in ("1", "2", "3"):
                    for number in ("sg", "du", "pl"):
                        try:
                            forms = engine.conjugate(
                                root_str=root,
                                class_num=class_num,
                                person=person,
                                number=number,
                                voice=voice,
                                tense=tense,
                                derivative=derivative,
                                use_db=_USE_INRIA_DB,
                            )
                            if isinstance(forms, str):
                                forms = [forms]
                            paradigm[f"{person}{number}"] = forms
                            if forms:
                                has_any = True
                        except Exception:
                            paradigm[f"{person}{number}"] = []
                if has_any:
                    tense_data[voice] = paradigm
            if tense_data:
                result["tenses"][tense] = tense_data

        # Kṛdantas (participles & indeclinables)
        try:
            krd = engine.conjugate(
                root_str=root,
                class_num=class_num,
                person="3",
                number="sg",
                tense="krdantas",
                derivative=derivative,
                use_db=_USE_INRIA_DB,
            )
            result["krdantas"] = krd
        except Exception:
            result["krdantas"] = {"participles": [], "indeclinables": []}

        return jsonify({"result": result, "error": None})
    except Exception as exc:
        traceback.print_exc()
        return jsonify({"result": {"tenses": {}, "krdantas": ""}, "error": str(exc)}), 400


@app.route("/api/declense", methods=["POST"])
def declense():
    """Decline a Sanskrit nominal stem.

    Expected JSON body::

        {
            "stem":      "rāma",   // IAST nominal stem
            "gender":    "m",      // "m" | "f" | "n"
            "stem_type": "auto",   // optional override
            "r_subtype": "agt"     // optional for ṛ-stems
        }

    Returns::

        {
            "paradigm": {
                "Nom_Sg": ["rāmaḥ"], "Nom_Du": ["rāmau"], ...
            },
            "error": null
        }
    """
    try:
        data = request.get_json(force=True)
        engine = _get_declension_engine()
        raw = engine.declense(
            stem=data["stem"],
            gender=data["gender"],
            stem_type=data.get("stem_type", "auto"),
            r_subtype=data.get("r_subtype", "agt"),
        )
        # raw is dict[(case, number), list[str]] — convert to JSON-safe keys
        paradigm = {}
        for (case, number), forms in raw.items():
            paradigm[f"{case}_{number}"] = forms
        return jsonify({"paradigm": paradigm, "error": None})
    except Exception as exc:
        traceback.print_exc()
        return jsonify({"paradigm": {}, "error": str(exc)}), 400


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Sanskrit API Server")
    parser.add_argument("--port", type=int, default=5199,
                        help="Port to listen on (default: 5199)")
    args = parser.parse_args()

    print("[Sanskrit API] Warming up Paninian engine FSTs (this takes a few seconds)...")
    _get_conjugator() # Force compilation during boot
    
    print(f"[Sanskrit API] Starting on http://127.0.0.1:{args.port}")
    # Use threaded=False for pynini thread-safety; Flask dev server is fine
    # for a single-user desktop app.
    app.run(host="127.0.0.1", port=args.port, debug=False, threaded=False)
