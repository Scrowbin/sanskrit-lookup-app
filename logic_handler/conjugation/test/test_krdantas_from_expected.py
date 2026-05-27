import os
import re
import urllib.request
import json

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "grammar")))
from conjugate import SanskritConjugator

EXPECTED_DIR = r"f:\sanskrit-lookup-app\expected output"
c = SanskritConjugator()

DERIVATIVES = {
    "Primary": None,
    "Causative": "causative",
    "Desiderative": "desiderative",
    "Intensive": "intensive",
}

def get_class(root_str):
    import csv, os
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "verbs_clean.csv"))
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["stem_iast"].strip() == root_str:
                    return int(row["class"].strip())
    except Exception:
        pass
    return 1 # fallback

def parse_txt(file_path):
    import re
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    blocks = re.split(r"(?=(?:Primary|Causative|Desiderative|Intensive) Conjugation)", text)
    expected_data = {}
    for block in blocks:
        if not block.strip(): continue
        m_deriv = re.match(r"(Primary|Causative|Desiderative|Intensive) Conjugation", block)
        if not m_deriv: continue
        deriv_name = m_deriv.group(1)
        participles = []
        indeclinables = []
        m_part = re.search(r"Participles\n(.*?)(?=Indeclinable forms|\Z)", block, re.DOTALL)
        if m_part:
            lines = [line.strip() for line in m_part.group(1).strip().split("\n") if line.strip()]
            i = 0
            while i < len(lines):
                name = lines[i]
                if i + 1 < len(lines):
                    form = lines[i+1]
                    participles.append({"name": name, "form": form})
                    i += 2
                else: break
        m_ind = re.search(r"Indeclinable forms\n(.*?)(?=\Z)", block, re.DOTALL)
        if m_ind:
            lines = [line.strip() for line in m_ind.group(1).strip().split("\n") if line.strip()]
            i = 0
            while i < len(lines):
                name = lines[i]
                if i + 1 < len(lines):
                    form = lines[i+1]
                    indeclinables.append({"name": name, "form": form})
                    i += 2
                else: break
        if participles or indeclinables:
            expected_data[deriv_name] = {"participles": participles, "indeclinables": indeclinables}
    return expected_data

def get_api_data(root, class_num, derivative):
    try:
        res = c.get_krdantas_block(root, class_num, derivative, use_db=False)
        return res if res else {}
    except Exception as e:
        print(f"Error generating {root} {derivative}: {e}")
    return {}

def normalize(s):
    return s.strip().replace(" m. n. ", " ").replace(" f.", "")

def main():
    total = 0
    passed = 0
    failed = 0
    
    results_csv = ["Root,Derivative,Category,Name,Expected,Actual,Status"]
    
    for filename in os.listdir(EXPECTED_DIR):
        if not filename.endswith(".txt"):
            continue
        
        root = filename.replace(".txt", "")
        
        class_num = get_class(root)
        expected_krd = parse_txt(os.path.join(EXPECTED_DIR, filename))
        
        for deriv_name, exp_data in expected_krd.items():
            deriv_api = DERIVATIVES.get(deriv_name)
            act_data = get_api_data(root, class_num, deriv_api)
            
            act_participles = act_data.get("participles", [])
            act_indeclinables = act_data.get("indeclinables", [])
            
            # Helper to find form
            def get_act_form(act_list, name, expected_form):
                norm_exp = normalize(expected_form)
                matches_by_name = []
                for item in act_list:
                    if item.get("name") == name:
                        matches_by_name.append(item.get("form"))
                
                for f in matches_by_name:
                    if norm_exp == normalize(f) or expected_form in f:
                        return f
                        
                return matches_by_name[0] if matches_by_name else None
                
            for cat, exp_list, act_list in [("Participle", exp_data["participles"], act_participles), 
                                            ("Indeclinable", exp_data["indeclinables"], act_indeclinables)]:
                for exp_item in exp_list:
                    name = exp_item["name"]
                    exp_form = exp_item["form"]
                    act_form = get_act_form(act_list, name, exp_form)
                    
                    total += 1
                    status = "PASS"
                    
                    if not act_form:
                        status = "FAIL (Missing)"
                        failed += 1
                    elif normalize(exp_form) != normalize(act_form) and exp_form not in act_form:
                        status = "FAIL (Mismatch)"
                        failed += 1
                    else:
                        passed += 1
                        
                    results_csv.append(f"{root},{deriv_name},{cat},{name},{exp_form},{act_form},{status}")
                    
    with open("krdanta_results.csv", "w", encoding="utf-8") as f:
        f.write("\n".join(results_csv))
        
    print(f"Total: {total}, Passed: {passed}, Failed: {failed}")
    print("Results written to krdanta_results.csv")

if __name__ == "__main__":
    main()
