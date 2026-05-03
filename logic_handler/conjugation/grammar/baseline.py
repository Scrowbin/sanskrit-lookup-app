"""baseline.py — Run all INRIA HTML files through the parser and report failures."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from inria_parser import parse_inria_html, extract_root_from_html, INRIA_TO_ENGINE_TENSE, INRIA_TO_ENGINE_VOICE
from pathlib import Path

try:
    from conjugate import SanskritConjugator
    engine = SanskritConjugator()
except ImportError:
    engine = None

GRAMMAR_DIR = os.path.dirname(os.path.abspath(__file__))
INRIA_DIR   = os.path.join(os.path.dirname(GRAMMAR_DIR), 'inria')

files = {
    'bhu': (os.path.join(GRAMMAR_DIR, 'Sanskrit Grammarian Conjugation Engine.html'), 1),
    'da':  (os.path.join(INRIA_DIR,   'da.html'),  3),
    'gam': (os.path.join(INRIA_DIR,   'gam.html'), 1),
    'han': (os.path.join(INRIA_DIR,   'han.html'), 2),
    'kr':  (os.path.join(INRIA_DIR,   'kr.html'),  8),
    'ni':  (os.path.join(INRIA_DIR,   'ni.html'),  1),
    'vac': (os.path.join(INRIA_DIR,   'vac.html'), 2),
    'yaj': (os.path.join(INRIA_DIR,   'yaj.html'), 1),
}

OUT = []

def p(s=''):
    OUT.append(s)

grand_pass = grand_fail = 0

for key, (fpath, cls_hint) in files.items():
    if not os.path.exists(fpath):
        p(f'MISSING: {fpath}')
        continue
    html = Path(fpath).read_text(encoding='utf-8', errors='replace')
    root, cls_str = extract_root_from_html(html)
    cls = int(cls_str) if cls_str.isdigit() else cls_hint

    data = parse_inria_html(html, 'Primary Conjugation')

    p(f'\n=== {root} cl.{cls} ===')
    r_pass = r_fail = 0

    # Finite forms
    for (tense_raw, voice_raw), forms_dict in sorted(data['finite'].items()):
        et = INRIA_TO_ENGINE_TENSE.get(tense_raw)
        ev = INRIA_TO_ENGINE_VOICE.get(voice_raw)
        if not et or not ev:
            continue
        for (person, number), inria_forms in sorted(forms_dict.items()):
            if engine:
                try:
                    result = engine.conjugate(root, cls, person, number, ev, et, use_db=False)
                    engine_forms = {f.strip() for f in result.split(' OR ')}
                    ok = any(f in engine_forms for f in inria_forms)
                    if ok:
                        r_pass += 1
                    else:
                        r_fail += 1
                        p(f'  FAIL [{tense_raw} {voice_raw} {person}{number}]  engine={result!r}  inria={"/".join(inria_forms)!r}')
                except Exception as e:
                    r_fail += 1
                    p(f'  ERR  [{tense_raw} {voice_raw} {person}{number}]  {e}')

    # Participles
    if engine:
        try:
            block = engine.conjugate(root, cls, '3', 'sg', 'active', 'krdantas', use_db=False)
        except Exception:
            block = ''
        for type_key, forms in sorted(data['participles'].items()):
            ok = any(f in block for f in forms)
            if ok:
                r_pass += 1
            else:
                r_fail += 1
                p(f'  FAIL [participle/{type_key}]  engine_block has={any(f in block for f in forms)}  inria={forms!r}')
        for type_key, forms in sorted(data['indeclinables'].items()):
            ok = any(f.lstrip('-') in block for f in forms)
            if ok:
                r_pass += 1
            else:
                r_fail += 1
                p(f'  FAIL [indecl/{type_key}]  inria={forms!r}')

    total = r_pass + r_fail
    rate = 100*r_pass/total if total else 0
    p(f'  --- {root}: pass={r_pass} fail={r_fail} ({rate:.0f}%)')
    grand_pass += r_pass
    grand_fail += r_fail

grand_total = grand_pass + grand_fail
grand_rate = 100*grand_pass/grand_total if grand_total else 0
p(f'\n=== GRAND TOTAL: pass={grand_pass} fail={grand_fail} ({grand_rate:.1f}%) ===')

out_text = '\n'.join(OUT)
out_path = os.path.join(GRAMMAR_DIR, 'baseline_report.txt')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(out_text)
print(f'Report written to {out_path}')
print(out_text)
