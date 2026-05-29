"""build_api.py — Freeze the Sanskrit API server into a standalone executable.

Bundles api_server.py, pynini/OpenFst, grammar modules, and only the CSV/TSV
files needed at runtime (not benchmark corpora or verbs_clean.csv).

Prerequisites:
    pip install pyinstaller   (in the conda 'sanskrit' env)

Usage:
    cd f:\\sanskrit-lookup-app
    C:\\Users\\hjiis\\miniconda3\\envs\\sanskrit\\python.exe scripts/build_api.py

Output:
    dist_python/api_server/   ← api_server.exe + DLLs + trimmed data
"""
from __future__ import annotations

import glob
import os
import sys

import PyInstaller.__main__
import pynini
import pywrapfst

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
LOGIC = os.path.join(PROJECT, "logic_handler")
CONJ_GRAMMAR = os.path.join(LOGIC, "conjugation", "grammar")
CONJ_DATA = os.path.join(LOGIC, "conjugation", "data")
DECL_DIR = os.path.join(LOGIC, "declension")

# CSV/TSV actually read by the engines at runtime (see dhatupatha_analyzer, krdantas).
RUNTIME_DATA_FILES = (
    "adverbs.csv",
    "dhatupatha.csv",
    "unprefixed-roots.csv",
    "vidyut_dhatupatha_5.tsv",
    "root_features.tsv",
    "lakara_voice_index.tsv",
    "inria_indeclinables.csv",
)

# Declension modules only — no benchmark scripts, tests, or grammar/data bench CSVs.
_DECL_SKIP_FILES = frozenset({"benchmark.py", "test.py", "test_translit.py"})
_DECL_SKIP_DIRS = frozenset({"__pycache__", "data"})

# PyInstaller modules not needed by Flask + pynini (reduces frozen folder size).
EXCLUDE_MODULES = (
    "tkinter",
    "_tkinter",
    "matplotlib",
    "numpy",
    "pandas",
    "scipy",
    "PIL",
    "IPython",
    "notebook",
    "jupyter",
    "pytest",
    "distutils",
    "setuptools",
    "pip",
    "wheel",
)


def _folder_size_mb(path: str) -> float:
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(root, name))
            except OSError:
                pass
    return total / (1024 * 1024)


def _collect_pynini_binaries() -> list[tuple[str, str]]:
    binaries: list[tuple[str, str]] = []
    pynini_dir = os.path.dirname(pynini.__file__)
    pywrap_dir = os.path.dirname(pywrapfst.__file__)
    for pkg_dir in (pynini_dir, pywrap_dir):
        for name in os.listdir(pkg_dir):
            if name.endswith((".pyd", ".dll", ".so")):
                binaries.append((os.path.join(pkg_dir, name), "."))

    try:
        import _pywrapfst

        binaries.append((_pywrapfst.__file__, "."))
    except ImportError:
        pass

    conda_lib_bin = os.path.join(sys.prefix, "Library", "bin")
    for pat in ("ffi*.dll", "dl.dll", "*fst*.dll"):
        for dll in glob.glob(os.path.join(conda_lib_bin, pat)):
            binaries.append((dll, "."))
    return binaries


def _runtime_data_entries() -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for name in RUNTIME_DATA_FILES:
        src = os.path.join(CONJ_DATA, name)
        if not os.path.isfile(src):
            print(f"  WARNING: missing runtime data file: {src}")
            continue
        kb = os.path.getsize(src) / 1024
        print(f"  data: {name} ({kb:.1f} KB)")
        entries.append((src, "data"))
    return entries


def _declension_entries() -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for root, dirs, files in os.walk(DECL_DIR):
        dirs[:] = [d for d in dirs if d not in _DECL_SKIP_DIRS]
        rel = os.path.relpath(root, DECL_DIR)
        dest_root = "declension" if rel == "." else os.path.join("declension", rel).replace("\\", "/")
        for name in files:
            if not name.endswith(".py") or name in _DECL_SKIP_FILES:
                continue
            entries.append((os.path.join(root, name), dest_root))
    return entries


def _hidden_imports() -> list[str]:
    return [
        "pynini",
        "pywrapfst",
        "_pywrapfst",
        "flask",
        "flask_cors",
        "flask.json",
        "werkzeug",
        "jinja2",
        "conjugate",
        "alphabet",
        "vowel_strength",
        "sandhi",
        "stem_rules",
        "endings",
        "morphology",
        "feature_resolver",
        "inria_lookup",
        "dhatupatha_analyzer",
        "reduplication",
        "irregulars",
        "krdantas",
        "upasargas",
        "corpus_lexical_hints",
        "engine",
        "a_stem_rules",
        "i_stem_rules",
        "u_stem_rules",
        "r_stems_rules",
        "an_in_stem_rules",
        "ant_mant_vant_stem_adj",
        "as_us_is_stem_rules",
        "dip_thong_rules",
        "general_term_rules",
        "van_stems_perfect_principles",
        "rules",
        "special_cases",
        "visarga",
        "grammar.grammar",
        "s_rules",
        "t_stems",
    ]


def main() -> None:
    out_dir = os.path.join(PROJECT, "dist_python", "api_server")
    binaries = _collect_pynini_binaries()
    datas = [(CONJ_GRAMMAR, "grammar"), *_runtime_data_entries(), *_declension_entries()]

    pyinstaller_args = [
        os.path.join(LOGIC, "api_server.py"),
        "--name",
        "api_server",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--noconsole",
        "--paths",
        CONJ_GRAMMAR,
        "--paths",
        DECL_DIR,
        "--paths",
        LOGIC,
        "--distpath",
        os.path.join(PROJECT, "dist_python"),
        "--workpath",
        os.path.join(PROJECT, "build_python"),
        "--specpath",
        os.path.join(PROJECT, "build_python"),
    ]

    for src, dest in datas:
        pyinstaller_args.extend(["--add-data", f"{src}{os.pathsep}{dest}"])

    for src, dest in binaries:
        pyinstaller_args.extend(["--add-binary", f"{src}{os.pathsep}{dest}"])

    for mod in _hidden_imports():
        pyinstaller_args.extend(["--hidden-import", mod])

    for mod in EXCLUDE_MODULES:
        pyinstaller_args.extend(["--exclude-module", mod])

    print("=" * 60)
    print("Building api_server.exe with PyInstaller (trimmed bundle)")
    print("=" * 60)
    print(f"  Source:  {os.path.join(LOGIC, 'api_server.py')}")
    print(f"  Output:  {out_dir}")
    print(f"  Runtime data files: {len(RUNTIME_DATA_FILES)}")
    print(f"  Declension .py modules: {len(_declension_entries())}")
    print()

    PyInstaller.__main__.run(pyinstaller_args)

    if os.path.isdir(out_dir):
        print()
        print("=" * 60)
        print(f"Done — frozen API folder: {_folder_size_mb(out_dir):.1f} MB")
        print(f"  {os.path.join(out_dir, 'api_server.exe')}")
        print("Next: npm run build:electron")
        print("=" * 60)
    else:
        print("Build finished but output folder not found:", out_dir)


if __name__ == "__main__":
    main()
