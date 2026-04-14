from conjugate import SanskritConjugator

def test_1():
    api = SanskritConjugator()
    test_suite = [
        ("bhū", 1, "Thematic Guṇa"),
        ("ad",  2, "Consonant Devoicing"),
        ("hu",  3, "Reduplication/Yan"),
        ("su",  5, "nu/no Vikaraṇa"),
        ("yuj", 7, "Nasal Infix")
    ]

    for root, cls, desc in test_suite:
        print(f"\n--- CLASS {cls}: √{root} ---")
        for p in ['1', '2', '3']:
            row = [api.conjugate(root, cls, p, n) for n in ['sg', 'd', 'pl']]
            print(f"{p}: {row[0]:<12} {row[1]:<12} {row[2]:<12}")

def run_hu_stress_test():
    api = SanskritConjugator()
    root = "hu"
    cls = 3
    
    # We test the three tenses currently supported by your logic
    tenses = [
        ("present", "Present (Laṭ)"),
        ("imperfect", "Imperfect (Laṅ)"),
        ("imperative", "Imperative (Loṭ)")
    ]

    for tense_key, tense_name in tenses:
        print(f"\n=== ROOT: √{root} | {tense_name} ===")
        print("-" * 65)
        print(f"{'':<12} | {'Singular':<15} | {'Dual':<15} | {'Plural':<15}")
        print("-" * 65)
        
        for p in ['1', '2', '3']:
            row = []
            for n in ['sg', 'd', 'pl']:
                try:
                    res = api.conjugate(root, cls, p, n, tense=tense_key)
                    row.append(res)
                except Exception as e:
                    row.append("ERROR")
            
            p_label = {"1": "First", "2": "Second", "3": "Third"}[p]
            print(f"{p_label:<12} | {row[0]:<15} | {row[1]:<15} | {row[2]:<15}")
        print("-" * 65)

def test_op():
    api = SanskritConjugator()
    root= "ad"
    class_num=2
    tense="optative"
    for p in ['1', '2', '3']:
            row = []
            for n in ['sg', 'd', 'pl']:
                try:
                    res = api.conjugate(root, class_num=class_num, person=p, number=n, tense=tense)
                    row.append(res)
                except Exception as e:
                    row.append("ERROR")
            p_label = {"1": "First", "2": "Second", "3": "Third"}[p]
            print(f"{p_label:<12} | {row[0]:<15} | {row[1]:<15} | {row[2]:<15}")

def test_class_5():
    api = SanskritConjugator()
    root= "kṛ"
    class_num=5
    tense="present"
    for p in ['1', '2', '3']:
            row = []
            for n in ['sg', 'd', 'pl']:
                # try:
                res = api.conjugate(root, class_num=class_num, person=p, number=n, tense=tense)
                row.append(res)
                # except Exception as e:
                #     row.append("ERROR")
            p_label = {"1": "First", "2": "Second", "3": "Third"}[p]
            print(f"{p_label:<12} | {row[0]:<15} | {row[1]:<15} | {row[2]:<15}")
    
def run_comprehensive_test(filename="res2.txt"):
    api = SanskritConjugator()
    
    # Root, Class, Description of what it tests
    test_suite = [
        ("bhū", 1, "Guna + Thematic"),
        ("ad", 2, "Athematic + Devoicing (atti)"),
        ("hu", 3, "Reduplication + Special 3pl (juhvati)"),
        ("div", 4, "Internal Lengthening (dīvyati)"),
        ("su", 5, "Athematic Sign (-nu/-no-)"),
        ("tud", 6, "Thematic + No Guna"),
        ("yuj", 7, "Infix + Palatal Sandhi (yunakti)"),
        ("tan", 8, "Athematic Sign (-u/-o-)"),
        ("krī", 9, "Athematic Sign (-nā/-nī-) + Nati (krīṇāti)"),
        ("cur", 10, "Causative-style (-aya-)")
    ]

    tenses = ["present", "imperfect", "imperative", "optative", "future"]
    
    # ... (test_suite and tenses definitions as before) ...

    # Open the file in write mode ('w')
    with open(filename, "w+", encoding="utf-8") as f:
        for root, cls, desc in test_suite:
            # Create a header string
            header = f"\n{'='*80}\nTESTING: √{root} (Class {cls}) | {desc}\n{'='*80}\n"
            
            # Print to terminal AND write to file
            print(header)
            f.write(header)

            for tense in tenses:
                f.write(f"\n--- Tense: {tense.upper()} ---\n")
                f.write(f"{'Person':<10} | {'Singular':<15} | {'Dual':<15} | {'Plural':<15}\n")
                f.write("-" * 65 + "\n")
                
                for p in ["3", "2", "1"]:
                    row = []
                    for n in ["sg", "d", "pl"]:
                        try:
                            res = api.conjugate(root, cls, p, n, tense=tense)
                            row.append(res)
                        except:
                            row.append("ERR")
                    
                    line = f"{p + 'rd':<10} | {row[0]:<15} | {row[1]:<15} | {row[2]:<15}\n"
                    f.write(line)
            f.write("\n" + "*"*80 + "\n")

    print(f"\nDone! Results exported to {filename}")

def test_future_tense():
    api = SanskritConjugator()
    
    # Root, Class, Expected 3sg, Notes
    future_cases = [
        ("bhū", 1, "bhaviṣyati", "Tests: Guna + 'i' augment + Ruki (s -> ṣ)"),
        ("ad",  2, "atsyati",    "Tests: Guna + No 'i' + Devoicing (d -> t)"),
        ("su",  5, "soṣyati",    "Tests: Guna + Ruki (o + sya -> oṣya)"),
        ("yuj", 7, "yokṣyati",   "Tests: Guna + Palatal Sandhi (j -> k) + Devoicing"),
        ("krī", 9, "kreṣyati",   "Tests: Guna (ī -> ē) + Ruki"),
    ]

    print(f"\n{'='*85}")
    print(f"{'Root':<6} | {'Class':<6} | {'Result':<15} | {'Expected':<15} | {'Status'}")
    print(f"{'='*85}")

    for root, cls, expected, notes in future_cases:
        try:
            # We only need 3rd person singular for the logic check
            res = api.conjugate(root, cls, "3", "sg", tense="future")
            status = "✅ PASS" if res == expected else "❌ FAIL"
            print(f"{root:<6} | {cls:<6} | {res:<15} | {expected:<15} | {status}")
            if res != expected:
                print(f"       └─ Logic Note: {notes}")
        except Exception as e:
            print(f"{root:<6} | {cls:<6} | {'ERR':<15} | {expected:<15} | ❌ CRASH")
            print(f"       └─ Error: {e}")

    print("="*85)

if __name__ == "__main__":
    # test_future_tense()
    # test_1()
    # run_hu_stress_test()
    # test_op()
    # test_class_5()
    run_comprehensive_test()
