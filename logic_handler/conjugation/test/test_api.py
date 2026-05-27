import urllib.request
import json
import os
import time

def main():
    test_suite = [
        # All 10 primary classes
        ("bhū", 1, "Class 1  – Guṇa + Thematic / Standard Seṭ Future"),
        ("ad", 2, "Class 2  – Athematic + Devoicing (atti / atsyati)"),
        ("hu", 3, "Class 3  – Reduplication / a-Aorist / ṣ+dhv→ḍhv Sandhi (ahoḍhvam)"),
        ("dīv", 4, "Class 4  – Internal Lengthening (dīvyati)"),
        ("su", 5, "Class 5  – Athematic Sign (-nu/-no-)"),
        ("tud", 6, "Class 6  – Thematic + No Guṇa / Aniṭ Luṭ (tottā)"),
        ("yuj", 7, "Class 7  – Nasal Infix + Palatal Sandhi (yunakti / yokṣyati)"),
        ("tan", 8, "Class 8  – Athematic Sign (-u/-o-)"),
        ("krī", 9, "Class 9  – Athematic Sign (-nā/-nī-) + Nati (krīṇāti)"),
        ("cur", 10, "Class 10 – Causative-style (-aya-)"),
        # Phonological edge cases
        ("kṛ", 8, "Guṇa of ṛ + Ruki / ṣṭ Sandhi (akārṣṭam)"),
        ("budh", 1, "Grassmann Throwback + Devoicing / iṣ-Aorist (abodhiṣam)"),
        ("duh", 2, "Grassmann Throwback + H-Sandhi + Ruki (dhokṣyati)"),
        ("gam", 1, "Suppletive Present (gaccha) / Root Aorist (agamat)"),
        ("dviṣ", 2, "Aniṭ S-Aorist / Palatal Sandhi (adviṣat)"),
        ("muc", 6, "Nasal Infix (muñca) / a-Aorist (amucat)"),
        # Expanded classical suite
        ("vac", 2, "Suppletive strong stem (vakti / ucyate)"),
        ("han", 2, "gh-deletion (hanti / jighāṃsati)"),
        ("pā", 1, "Long-vowel root + yan sandhi (pāti / pātum)"),
        ("nī", 1, "Long-vowel root + periphrastic perfect"),
        ("śru", 5, "u-final + Benedictive (śrūyāt)"),
        ("dā", 3, "Reduplicating class, long-ā (dadāti)"),
        ("sthā", 1, "Long-ā root, suppletive aorist (asthāt)"),
        ("bhid", 7, "Class 7 nasal infix, s-aorist (abhaiṭsīt)"),
        ("kṣip", 6, "Thematic no-guṇa, veṭ future"),
        ("vṛ", 9, "Veṭ root with both future forms (variṣyati / varīṣyati)"),
        # Additional coverage gaps
        ("yaj", 1, "Passive sandhi ya-infix + palatal (ijyate)"),
        ("labh", 1, "Ātmanepada-only root (labhate)"),
        ("smṛ", 1, "ṛ-final class 1, different aorist type from kṛ (asmart)"),
        ("man", 4, "Nasal-final root, non-suppletive (manyate)"),
        ("vid", 2, "Perfect-as-present anomaly (veda = he knows)"),
    ]

    out_dir = r"f:\sanskrit-lookup-app\actual_output"
    os.makedirs(out_dir, exist_ok=True)
    
    API_URL = "http://localhost:5199/api/conjugate/derivative"

    derivatives = [None, "causative", "desiderative", "intensive"]

    print(f"Testing {len(test_suite)} roots against API at {API_URL}")
    print("=" * 60)

    for root_str, class_num, desc in test_suite:
        t0 = time.perf_counter()
        results = {}
        for drv in derivatives:
            payload = {
                "root": root_str,
                "class_num": class_num,
                "derivative": drv
            }
            try:
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(API_URL, data=data, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        res_data = json.loads(response.read().decode("utf-8"))
                        results[drv if drv else "primary"] = res_data.get("paradigm", res_data)
                    else:
                        print(f"  [ERROR] {root_str} ({drv}) returned {response.status}")
                        results[drv if drv else "primary"] = {"error": f"HTTP {response.status}"}
            except Exception as e:
                safe_name_err = root_str.encode('ascii', 'ignore').decode('ascii')
                print(f"  [ERROR] {safe_name_err} ({drv}) failed: {e}")
                results[drv if drv else "primary"] = {"error": str(e)}
        
        t1 = time.perf_counter()
        
        out_file = os.path.join(out_dir, f"{root_str}_api_result.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        safe_name = root_str.encode('ascii', 'ignore').decode('ascii')
        print(f"Processed {safe_name} (Class {class_num}) in {t1 - t0:.2f}s")

    print("=" * 60)
    print("Done!")

if __name__ == "__main__":
    main()
