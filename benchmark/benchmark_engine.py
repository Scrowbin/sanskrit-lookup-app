import time
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os

# Add logic_handler and grammar to path so we can import the engine directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logic_handler")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logic_handler", "conjugation", "grammar")))

def run_benchmarks():
    print("=" * 50)
    print(" SANSKRIT ENGINE BENCHMARK ".center(50))
    print("=" * 50)

    # 1. Warm-up / Load Time
    print("\n[1] Measuring Engine FST Warm-up Time...")
    start_time = time.time()
    
    # Importing and instantiating the conjugator forces Pynini to compile the FSTs
    from conjugation.grammar.conjugate import SanskritConjugator
    conjugator = SanskritConjugator()
    
    warmup_time = time.time() - start_time
    print(f" -> Engine Loaded & FSTs Compiled in: {warmup_time:.4f} seconds")

    # 2. Single Conjugation Time
    print("\n[2] Measuring Single Cell Conjugation Time...")
    test_cases_single = [
        ("bhū", 1, "present", "active", "3", "sg", "primary"),
        ("edh", 1, "present", "middle", "3", "sg", "primary"),
        ("yuj", 7, "imperfect", "active", "3", "pl", "primary"),
        ("kṛ", 8, "perfect", "active", "3", "sg", "primary"),
        ("han", 2, "aorist", "active", "3", "sg", "primary"),
    ]
    
    total_single_time = 0
    print(f"    Testing {len(test_cases_single)} unique single-cell requests:")
    for (root, cls, tense, voice, person, num, deriv) in test_cases_single:
        t0 = time.time()
        conjugator.conjugate(root, cls, person, num, voice, tense, deriv)
        t1 = time.time()
        duration = t1 - t0
        total_single_time += duration
        print(f"      - {root} ({tense} {voice}): {duration:.4f}s")
    
    print(f" -> Average single cell time: {(total_single_time / len(test_cases_single)):.4f} seconds")

    # 3. Full Paradigm Time (includes Krdantas)
    print("\n[3] Measuring Full Paradigm Generation Time...")
    test_cases_full = [
        ("bhū", 1, "primary"),
        ("gam", 1, "primary"),
        ("kṛ", 8, "primary"),
        ("dṛś", 1, "primary"),
        ("kṛ", 8, "causative"),
    ]

    total_full_time = 0
    print(f"    Testing {len(test_cases_full)} full roots (All tenses + Krdantas):")
    for (root, cls, deriv) in test_cases_full:
        t0 = time.time()
        conjugator.get_all_tenses(root, cls, deriv)
        t1 = time.time()
        duration = t1 - t0
        total_full_time += duration
        print(f"      - {root} (class {cls}, {deriv}): {duration:.4f}s")

    print(f" -> Average full paradigm time: {(total_full_time / len(test_cases_full)):.4f} seconds")

    print("\n" + "=" * 50)
    print(f" Total Benchmark Time: {(time.time() - start_time):.4f} seconds")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    run_benchmarks()
