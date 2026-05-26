"""build_api.py — Freeze the Sanskrit API server into a standalone executable.

Uses PyInstaller to bundle api_server.py + all Python dependencies (pynini,
flask, OpenFst libs, grammar data, CSV/DB files) into a single-folder
distribution that ships with the Electron installer.

Prerequisites:
    pip install pyinstaller   (in the conda 'sanskrit' env)

Usage:
    cd f:\\sanskrit-lookup-app
    C:\\Users\\hjiis\\miniconda3\\envs\\sanskrit\\python.exe scripts/build_api.py

Output:
    dist/api_server/           ← folder with api_server.exe + DLLs + data
    (Copy this into electron-builder's extraResources)
"""
import PyInstaller.__main__
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)  # project root
LOGIC = os.path.join(PROJECT, "logic_handler")
CONJ_GRAMMAR = os.path.join(LOGIC, "conjugation", "grammar")
CONJ_DATA = os.path.join(LOGIC, "conjugation", "data")
DECL_DIR = os.path.join(LOGIC, "declension")
DECL_GRAMMAR = os.path.join(DECL_DIR, "grammar")

# Locate the pynini / pywrapfst shared libraries from the conda env
import pynini
import pywrapfst
pynini_dir = os.path.dirname(pynini.__file__)
pywrap_dir = os.path.dirname(pywrapfst.__file__)

# Collect all .pyd / .dll files from pynini and pywrapfst packages
binaries = []
for pkg_dir in (pynini_dir, pywrap_dir):
    for f in os.listdir(pkg_dir):
        if f.endswith((".pyd", ".dll", ".so")):
            binaries.append((os.path.join(pkg_dir, f), "."))

# Also grab OpenFst shared libraries if they exist as separate packages
try:
    import _pywrapfst
    binaries.append((_pywrapfst.__file__, "."))
except ImportError:
    pass

# Data files to bundle alongside the executable
datas = [
    # Conjugation grammar modules (all .py files — imported at runtime)
    (CONJ_GRAMMAR, "grammar"),
    # Conjugation data (CSV, DB files)
    (CONJ_DATA, "data"),
    # Declension engine + submodules
    (DECL_DIR, "declension"),
]

# Hidden imports that PyInstaller can't auto-detect
hidden_imports = [
    "pynini",
    "pywrapfst",
    "_pywrapfst",
    "flask",
    "flask_cors",
    "flask.json",
    "werkzeug",
    "jinja2",
    # Conjugation grammar modules (imported dynamically)
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
    # Declension modules
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
]

# Build argument list
pyinstaller_args = [
    os.path.join(LOGIC, "api_server.py"),
    "--name", "api_server",
    "--noconfirm",
    "--clean",
    # Use one-folder mode (not one-file) — faster startup, easier to debug
    "--onedir",
    # Don't open a console window when the exe runs
    "--noconsole",
    # Add path so PyInstaller can find the grammar modules
    "--paths", CONJ_GRAMMAR,
    "--paths", DECL_DIR,
    "--paths", LOGIC,
    # Work/dist directories
    "--distpath", os.path.join(PROJECT, "dist_python"),
    "--workpath", os.path.join(PROJECT, "build_python"),
    "--specpath", os.path.join(PROJECT, "build_python"),
]

# Add all data directories
for src, dest in datas:
    pyinstaller_args.extend(["--add-data", f"{src}{os.pathsep}{dest}"])

# Add binary files
for src, dest in binaries:
    pyinstaller_args.extend(["--add-binary", f"{src}{os.pathsep}{dest}"])

# Add hidden imports
for mod in hidden_imports:
    pyinstaller_args.extend(["--hidden-import", mod])

print("=" * 60)
print("Building api_server.exe with PyInstaller")
print("=" * 60)
print(f"  Source:  {os.path.join(LOGIC, 'api_server.py')}")
print(f"  Output:  {os.path.join(PROJECT, 'dist_python', 'api_server')}")
print()

PyInstaller.__main__.run(pyinstaller_args)

print()
print("=" * 60)
print("Done!  The frozen API server is at:")
print(f"  {os.path.join(PROJECT, 'dist_python', 'api_server', 'api_server.exe')}")
print()
print("Next step: run electron-builder to package the full app.")
print("=" * 60)
