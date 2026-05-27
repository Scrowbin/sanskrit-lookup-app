import os
import re
import csv
import sys
import logging

# Ensure stdout and stderr handle utf-8 to prevent cp932 crashes on Windows
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr:
    sys.stderr.reconfigure(encoding='utf-8')

# Append paths so we can import modules properly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "grammar")))
from conjugate import SanskritConjugator
from dhatupatha_analyzer import DHATUPATHA_ANALYZER

EXPECTED_DIR = r"f:\sanskrit-lookup-app\expected output"
c = SanskritConjugator()

ROOT_CLASSES = {
    "bhū": 1, "ad": 2, "hu": 3, "div": 4, "dīv": 4, "su": 5, "tud": 6, "yuj": 7, "tan": 8, "krī": 9, "cur": 10,
    "kṛ": 8, "budh": 1, "duh": 2, "gam": 1, "dviṣ": 2, "muc": 6, "vac": 2, "han": 2, "pā": 1, "nī": 1, 
    "śru": 5, "dā": 3, "sthā": 1, "bhid": 7, "kṣip": 6, "vṛ": 9, "yaj": 1, "labh": 1, "smṛ": 1, "man": 4, 
    "vid": 2, "ruh": 1, "viś": 6, "nind": 1, "sṛj": 6, "stu": 2, "jan": 4, "mṛj": 2, "svap": 2, "śās": 2, "rudh": 7
}

def get_class(root_str):
    return ROOT_CLASSES.get(root_str, 1)

def normalize(s):
    # Same normalization as test.py (convert trailing s/r to visarga)
    if not s:
        return s
    # Split " OR " if multiple
    forms = [f.strip() for f in s.split(" OR ")]
    norm_forms = []
    for f in forms:
        if f.endswith("s") or f.endswith("r"):
            f = f[:-1] + "ḥ"
        norm_forms.append(f)
    return " OR ".join(norm_forms)

def parse_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    expected_data = [] # List of dicts
    current_deriv = "primary"
    current_tense = None
    current_voice = None
    
    tenses_map = {
        "Present": "present",
        "Imperfect": "imperfect",
        "Optative": "optative",
        "Imperative": "imperative",
        "Future": "future",
        "Future2": "periphrastic_future",
        "Aorist": "aorist",
        "Perfect": "perfect",
        "Periphrastic Future": "periphrastic_future",
        "Benedictive": "benedictive",
        "Injunctive": "injunctive",
        "Conditional": "conditional"
    }
    
    persons_map = {
        "First": "1",
        "Second": "2",
        "Third": "3"
    }
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Check derivation
        m_deriv = re.match(r"(Primary|Causative|Desiderative|Intensive) Conjugation", line)
        if m_deriv:
            raw = m_deriv.group(1).lower()
            current_deriv = raw if raw != "primary" else None
            continue
            
        # Check tense
        if line in tenses_map:
            current_tense = tenses_map[line]
            continue
            
        # Check voice
        if line.startswith("Active") or line.startswith("Middle") or line.startswith("Passive"):
            current_voice = line.split()[0].lower()
            continue
            
        # Check person
        parts = line.split("\t")
        if len(parts) >= 4 and parts[0] in persons_map:
            person = persons_map[parts[0]]
            sg, du, pl = parts[1].strip(), parts[2].strip(), parts[3].strip()
            
            for num_idx, num in enumerate(["sg", "du", "pl"]):
                val = [sg, du, pl][num_idx]
                if val and val != "-":
                    expected_data.append({
                        "derivative": current_deriv,
                        "tense": current_tense,
                        "voice": current_voice,
                        "person": person,
                        "number": num,
                        "expected": val
                    })
                    
    return expected_data

def main():
    total = 0
    full_passed = 0
    partial_passed = 0
    failed = 0
    
    results_csv = ["Root,Derivative,Tense,Voice,Person,Number,Expected,Actual,Status"]
    
    # We will test all 41 files
    files = [f for f in os.listdir(EXPECTED_DIR) if f.endswith(".txt")]
    
    for filename in files:
        root = filename.replace(".txt", "")
        class_num = get_class(root)
        
        expected_list = parse_txt(os.path.join(EXPECTED_DIR, filename))
        
        for exp in expected_list:
            drv = exp["derivative"]
            tense = exp["tense"]
            voice = exp["voice"]
            person = exp["person"]
            number = exp["number"]
            expected_form = exp["expected"]
            
            # Skip if missing basic data
            if not tense or not voice:
                continue
                
            total += 1
            
            try:
                actual = c.conjugate(
                    root_str=root,
                    class_num=class_num,
                    person=person,
                    number=number,
                    voice=voice,
                    tense=tense,
                    derivative=drv,
                    use_db=False
                )
                
                # actual could be list
                if isinstance(actual, list):
                    actual_str = " OR ".join(actual)
                else:
                    actual_str = actual
                    
                norm_exp = normalize(expected_form)
                norm_act = normalize(actual_str)
                
                # INRIA expected text separates multiple forms by space or comma (e.g. 'abhinaḥ abhinat' or 'abhet, abhidat')
                # Engine separates by ' OR ' (e.g. 'abhinat OR abhinaḥ')
                raw_exp_forms = re.split(r'[, ]+', norm_exp)
                exp_set = set(f.strip() for f in raw_exp_forms if f.strip())
                act_set = set(f.strip() for f in norm_act.split(" OR ") if f.strip())
                
                if exp_set == act_set:
                    status = "FULL PASS"
                    full_passed += 1
                elif exp_set & act_set: 
                    status = "PARTIAL PASS"
                    partial_passed += 1
                else:
                    # Substring match fallback just in case
                    if any(e in norm_act for e in exp_set):
                        status = "PARTIAL PASS"
                        partial_passed += 1
                    else:
                        status = "FAIL"
                        failed += 1
                
                if status != "FULL PASS":
                    results_csv.append(f"{root},{drv},{tense},{voice},{person},{number},{norm_exp},{norm_act},{status}")
                    
            except Exception as e:
                failed += 1
                results_csv.append(f"{root},{drv},{tense},{voice},{person},{number},{expected_form},ERROR: {e},FAIL")
                
    with open("conjugation_results.csv", "w", encoding="utf-8") as f:
        f.write("\n".join(results_csv))
        
    print(f"Total Conjugations: {total}")
    print(f"  Full Pass:    {full_passed}")
    print(f"  Partial Pass: {partial_passed}")
    print(f"  Failed:       {failed}")
    if total > 0:
        total_pass = full_passed + partial_passed
        print(f"Combined Pass Rate: {total_pass/total*100:.1f}%")
    print("Results (Failed & Partial) written to conjugation_results.csv")

if __name__ == "__main__":
    main()
