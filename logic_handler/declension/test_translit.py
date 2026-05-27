#!/usr/bin/env python3
"""
test_translit.py
----------------
Test script to verify that the SLP1 -> IAST transliterator in benchmark.py
correctly maps Sanskrit phonemes using the indic-transliteration library.
"""

import sys
import os

# Add parent directory to path to import benchmark
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from benchmark import slp1_to_iast, _is_clean_iast
except ImportError as e:
    print(f"Error importing from benchmark.py: {e}")
    sys.exit(1)

def run_tests():
    # Test cases: (slp1_input, expected_iast, should_be_clean)
    test_cases = [
        # 1. Basic Vowels & Prosody
        ("a", "a", True),
        ("A", "ā", True),
        ("i", "i", True),
        ("I", "ī", True),
        ("u", "u", True),
        ("U", "ū", True),
        ("f", "ṛ", True),
        ("F", "ṝ", True),
        ("x", "ḷ", True),
        ("X", "ḹ", True),
        ("e", "e", True),
        ("E", "ai", True),
        ("o", "o", True),
        ("O", "au", True),
        ("M", "ṃ", True),
        ("H", "ḥ", True),
        
        # 2. Sibilants
        ("S", "ś", True),
        ("z", "ṣ", True),  # standard SLP1 z maps to ṣ
        ("s", "s", True),
        
        # 3. Gutturals & Palatals
        ("k K g G N", "k kh g gh ṅ", True),
        ("c C j J Y", "c ch j jh ñ", True),
        
        # 4. Retroflexes (Standard SLP1: w W q Q R)
        ("w W q Q R", "ṭ ṭh ḍ ḍh ṇ", True),
        
        # 5. Dentals (Standard SLP1: t T d D n)
        ("t T d D n", "t th d dh n", True),
        
        # 6. Word-final s/r sandhi conversion to visarga (ḥ)
        ("aMSakas", "aṃśakaḥ", True),
        ("pitur", "pituḥ", True),
        
        # 7. Liquid L and palatal nasal Y
        ("yajYiya", "yajñiya", True),
        ("agnimiLe", "agnimiḻe", True),  # L maps to ḻ
    ]

    failed = 0
    passed = 0

    print("=== Running Transliteration Tests (Standard SLP1) ===")
    for i, (slp1, expected, expected_clean) in enumerate(test_cases, 1):
        actual = slp1_to_iast(slp1)
        actual_clean = _is_clean_iast(actual)
        
        status = "PASSED"
        err_msg = ""
        
        if actual != expected or actual_clean != expected_clean:
            status = "FAILED"
            failed += 1
            err_msg = f" -> Got '{actual}' (clean: {actual_clean}), expected '{expected}' (clean: {expected_clean})"
        else:
            passed += 1
            
        print(f"Test {i:02d}: '{slp1}' -> '{actual}' [{status}]{err_msg}")

    print("\n=== Summary ===")
    print(f"Passed: {passed}/{len(test_cases)}")
    print(f"Failed: {failed}/{len(test_cases)}")
    
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
