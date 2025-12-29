import React, { useEffect, useState, useRef } from "react";
// Sanskrit Vibe — single-file React component app
// - Offline friendly (all data embedded)
// - Uses Tailwind utility classes for styling (no external network required)
// - Stores progress in localStorage
// - Supports noun declension and verb conjugation prompts
// export default function App() {
//   return (
//     <div className="min-h-screen flex items-center justify-center bg-gray-100">
//       <h1 className="text-4xl font-bold text-blue-500">
//         Tailwind is working! 🎉
//       </h1>
//     </div>
//   );
// }
export default function SanskritVibeApp() {
  // --- Sample dataset (expandable) ---
  // Each noun includes forms for cases x numbers. For verbs include conjugations.
  const TRANSLIT_MAP = {
  a: "अ", ā: "आ", i: "इ", ī: "ई", u: "उ", ū: "ऊ",
  e: "ए", o: "ओ", ai: "ऐ", au: "औ",
  k: "क", kh: "ख", g: "ग", gh: "घ", ṅ: "ङ",
  c: "च", ch: "छ", j: "ज", jh: "झ", ñ: "ञ",
  ṭ: "ट", ṭh: "ठ", ḍ: "ड", ḍh: "ढ", ṇ: "ण",
  t: "त", th: "थ", d: "द", dh: "ध", n: "न",
  p: "प", ph: "फ", b: "ब", bh: "भ", m: "म",
  y: "य", r: "र", l: "ल", v: "व",
  ś: "श", ṣ: "ष", s: "स", h: "ह",
  ṃ: "ं", ḥ: "ः", ṛ: "ऋ", ṝ: "ॠ",
  " ": " ", "-": ""
};
  const DATA = {
    nouns: [
      {
        id: "n1",
        lemma: "राम",
        translit: "rāma",
        gloss: "Rama (proper name)",
        gender: "m",
        // declensions: case -> [singular, dual, plural]
        declensions: {
          nominative: ["रामः", "रामौ", "रामा: / रामाः"],
          accusative: ["रामम्", "रामौ", "रामान्"],
          instrumental: ["रामेण", "रामाभ्याम्", "रामैः"],
          dative: ["रामाय", "रामाभ्याम्", "रामेभ्यः"],
          ablative: ["रामात्", "रामाभ्याम्", "रामेभ्यः"],
          genitive: ["रामस्य", "रामयोः", "रामाणाम्"],
          locative: ["रामे", "रामयोः", "रामेषु"],
          vocative: ["हे राम", "हे रामौ", "हे रामा: / हे रामाः"]
        }
      },
      {
        id: "n2",
        lemma: "फल",
        translit: "phala",
        gloss: "fruit",
        gender: "n",
        declensions: {
          nominative: ["फलम्", "फलौ", "फलानि"],
          accusative: ["फलम्", "फलौ", "फलानि"],
          instrumental: ["फलेन", "फलाभ्याम्", "फलैः"],
          dative: ["फलाय", "फलाभ्याम्", "फलेभ्यः"],
          ablative: ["फलात्", "फलाभ्याम्", "फलेभ्यः"],
          genitive: ["फलस्य", "फलयोः", "फलानाम्"],
          locative: ["फले", "फलयोः", "फलेषु"],
          vocative: ["हे फल", "हे फलौ", "हे फलानि"]
        }
      }
    ],
    verbs: [
      {
        id: "v1",
        lemma: "गम्",
        translit: "gam",
        gloss: "to go",
        // conjugations: tense -> person-number array (1s,2s,3s,1d,2d,3d,1p,2p,3p)
        conjugations: {
          present: [
            "गच्छामि", // 1s
            "गच्छसि",
            "गच्छति",
            "गच्छाव",
            "गच्छथः",
            "गच्छतः",
            "गच्छामः",
            "गच्छथ",
            "गच्छन्ति"
          ],
          past: [
            "अगच्छम्",
            "अगच्छः",
            "अगच्छत्",
            "अगच्छाव",
            "अगच्छतम्",
            "अगच्छत",
            "अगच्छाम",
            "अगच्छत",
            "अगच्छन्"
          ]
        }
      }
    ]
  };

  const CASES = [
    "nominative",
    "accusative",
    "instrumental",
    "dative",
    "ablative",
    "genitive",
    "locative",
    "vocative"
  ];

  const NUMBERS = ["singular", "dual", "plural"];

  const PERSON_NUMBER_LABELS = [
    "1st sing",
    "2nd sing",
    "3rd sing",
    "1st dual",
    "2nd dual",
    "3rd dual",
    "1st pl",
    "2nd pl",
    "3rd pl"
  ];

  // --- State ---
  const [mode, setMode] = useState(() => {
    return localStorage.getItem("sv_mode") || "auto"; // auto, noun, verb
  });
  const [current, setCurrent] = useState(null);
  const [promptText, setPromptText] = useState("");
  const [userInput, setUserInput] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [score, setScore] = useState(() => {
    const s = localStorage.getItem("sv_score");
    return s ? JSON.parse(s) : { correct: 0, total: 0 };
  });
  const inputRef = useRef(null);

  // --- Utilities ---
  const normalize = (s) =>
    s
      .trim()
      .replace(/\s+/g, " ")
      .replace(/-/g, "")
      .toLowerCase();

  const pickRandom = (arr) => arr[Math.floor(Math.random() * arr.length)];

  // generate a new prompt
  const newPrompt = (forceMode = null) => {
    const m = forceMode || mode;
    if (m === "noun") {
      const noun = pickRandom(DATA.nouns);
      const cas = pickRandom(CASES);
      const numIndex = Math.floor(Math.random() * NUMBERS.length);
      setCurrent({ type: "noun", noun, case: cas, number: numIndex });
      setPromptText(
        `Decline the noun \"${noun.lemma}\" (${noun.translit}) in the ${cas} (${NUMBERS[numIndex]})`
      );
    } else if (m === "verb") {
      const verb = pickRandom(DATA.verbs);
      const tense = pickRandom(Object.keys(verb.conjugations));
      const pnIdx = Math.floor(Math.random() * 9);
      setCurrent({ type: "verb", verb, tense, pnIdx });
      setPromptText(
        `Conjugate the verb \"${verb.lemma}\" (${verb.translit}) — ${tense}, ${PERSON_NUMBER_LABELS[pnIdx]}`
      );
    } else {
      // auto: choose random between noun and verb
      if (Math.random() < 0.6) newPrompt("noun");
      else newPrompt("verb");
      return;
    }
    setUserInput("");
    setFeedback(null);
    setTimeout(() => inputRef.current && inputRef.current.focus(), 50);
  };

  useEffect(() => {
    // first prompt on load
    newPrompt();
  }, []);

  useEffect(() => {
    localStorage.setItem("sv_score", JSON.stringify(score));
  }, [score]);

  useEffect(() => localStorage.setItem("sv_mode", mode), [mode]);

  const checkAnswer = () => {
  if (!current) return;
  let correctForms = [];

  if (current.type === "noun") {
    const { noun, case: cas, number } = current;
    const forms = noun.declensions[cas];
    if (!forms) {
      setFeedback({ ok: false, msg: "No forms available for this case" });
      return;
    }
    // allow multiple alternatives separated by '/'
    correctForms = forms[number].split("/").map((s) => s.trim());
  } else if (current.type === "verb") {
    const { verb, tense, pnIdx } = current;
    const conj = verb.conjugations[tense];
    correctForms = [conj[pnIdx].trim()];
  }

  // ---- NEW LOGIC ----
  const userDeva = hkToDevanagari(userInput.trim());
  const normalizeDeva = (s) => s.replace(/\s+/g, "").trim();

  const matched = correctForms.some(
    (f) => normalizeDeva(f) === normalizeDeva(userDeva)
  );

  setFeedback({
    ok: matched,
    correct: correctForms[0],
    all: correctForms,
  });

  setScore((s) => ({
    correct: s.correct + (matched ? 1 : 0),
    total: s.total + 1,
  }));
};


  const revealAnswer = () => {
    if (!current) return;
    if (current.type === "noun") {
      const forms = current.noun.declensions[current.case];
      setFeedback({ ok: false, reveal: forms[ current.number ] });
    } else if (current.type === "verb") {
      const conj = current.verb.conjugations[current.tense];
      setFeedback({ ok: false, reveal: conj[current.pnIdx] });
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter") {
      checkAnswer();
    }
    if (e.ctrlKey && e.key === "k") {
      newPrompt();
    }
  };
  
  function hkToDevanagari(input) {
  const vowels = {
    a: "अ", A: "आ", i: "इ", I: "ई", u: "उ", U: "ऊ",
    R: "ऋ", e: "ए", ai: "ऐ", o: "ओ", au: "औ",
  };

  const matras = {
    a: "", A: "ा", i: "ि", I: "ी", u: "ु", U: "ू",
    R: "ृ", e: "े", ai: "ै", o: "ो", au: "ौ",
  };

  const consonants = {
    kh: "ख", k: "क", gh: "घ", g: "ग", G: "ङ",
    ch: "छ", c: "च", jh: "झ", j: "ज", J: "ञ",
    Th: "ठ", T: "ट", Dh: "ढ", D: "ड", N: "ण",
    th: "थ", t: "त", dh: "ध", d: "द", n: "न",
    ph: "फ", p: "प", bh: "भ", b: "ब", m: "म",
    y: "य", r: "र", l: "ल", v: "व",
    z: "श", S: "ष", s: "स", h: "ह",
  };

  const specials = { M: "ं", H: "ः", "~": "ँ", "'": "ऽ", ".": "।", "|": "॥" };

  let result = "";
  let i = 0;

  function match(map) {
    const two = input.slice(i, i + 2);
    const one = input[i];
    if (map[two]) return [map[two], 2];
    if (map[one]) return [map[one], 1];
    return [null, 0];
  }

  while (i < input.length) {
    // Try consonant
    let [cons, lenC] = match(consonants);
    if (cons) {
      i += lenC;
      let [vowel, lenV] = match(vowels);

      if (vowel) {
        // Consonant + vowel matra
        result += cons + matras[input.slice(i, i + lenV)];
        i += lenV;
      } else if (i < input.length) {
        // Check if next is another consonant (cluster)
        let [nextCons, lenNext] = (function () {
          const two = input.slice(i, i + 2);
          const one = input[i];
          if (consonants[two]) return [consonants[two], 2];
          if (consonants[one]) return [consonants[one], 1];
          return [null, 0];
        })();

        if (nextCons) {
          result += cons + "्"; // join cluster with halant
        } else {
          // End or special character → default inherent 'a'
          result += cons;
        }
      } else {
        // End of word, implicit 'a'
        result += cons;
      }
      continue;
    }

    // Vowels (standalone)
    let [vowel, lenV] = match(vowels);
    if (vowel) {
      result += vowel;
      i += lenV;
      continue;
    }

    // Specials (anusvāra, visarga, etc.)
    if (specials[input[i]]) {
      result += specials[input[i]];
      i++;
      continue;
    }

    // Fallback (punctuation, etc.)
    result += input[i];
    i++;
  }

  return result;
}




    function fromDevanagariToKyoto(input) {
  if (!input) return "";

  // base mapping for independent vowels, consonants, matras and signs
  const base = {
    // Independent vowels
    "अ": "a", "आ": "A", "इ": "i", "ई": "I",
    "उ": "u", "ऊ": "U", "ऋ": "R", "ॠ": "RR",
    "ऌ": "lR", "ॡ": "lRR", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au",
    // Consonants
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "G",
    "च": "c", "छ": "ch", "ज": "j", "झ": "jh", "ञ": "J",
    "ट": "T", "ठ": "Th", "ड": "D", "ढ": "Dh", "ण": "N",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v",
    "श": "z", "ष": "S", "स": "s", "ह": "h",
    // Nukta variants (basic coverage)
    "क़": "k", "ख़": "kh", "ग़": "g", "ज़": "z", "फ़": "ph", "ऱ": "r",
    // Signs (independent handling below)
    "ं": "M", "ँ": "M", "ः": "H", "ऽ": "'",
    "।": ".", "॥": ".."
  };

  const matra = {
    "ा": "A", "ि": "i", "ी": "I", "ु": "u", "ू": "U",
    "ृ": "R", "ॄ": "RR", "ॢ": "lR", "ॣ": "lRR",
    "े": "e", "ै": "ai", "ो": "o", "ौ": "au", "्": "" // virama handled separately
  };

  // helper to test whether char is a consonant
  const consonants = new Set(Object.keys(base).filter(c => /[क-हक़-फ़]/.test(c)));

  // We'll iterate through input chars and build romanized output
  const chars = Array.from(input);
  let out = "";

  for (let i = 0; i < chars.length; i++) {
    const ch = chars[i];
    const next = chars[i + 1];

    // If ch is a consonant
    if (consonants.has(ch)) {
      // If next is virama, explicit halant: no inherent vowel
      if (next === "्") {
        out += base[ch]; // just consonant
        i += 1; // skip the virama
        continue;
      }

      // If next is a matra — combine consonant + matra
      if (next && matra[next] !== undefined) {
        // consonant mapping + matra mapping
        out += base[ch] + matra[next];
        i += 1; // skip matra
        continue;
      }

      // If next is another consonant or nothing, use inherent 'a'
      out += base[ch] + "a";
      continue;
    }

    // If ch is an independent vowel
    if (base[ch] !== undefined && !consonants.has(ch)) {
      out += base[ch];
      continue;
    }

    // If ch is a matra (should only occur after consonant normally) — map directly
    if (matra[ch] !== undefined) {
      out += matra[ch];
      continue;
    }

    // other signs: anusvara/visarga/candrabindu etc.
    if (ch === "ं" || ch === "ँ") {
      out += "M";
      continue;
    }
    if (ch === "ः") {
      out += "H";
      continue;
    }
    if (ch === "ऽ") {
      out += "'";
      continue;
    }

    // punctuation, whitespace, digits, fallback: keep as-is
    if (/\s/.test(ch)) {
      out += ch;
      continue;
    }
    const digitMap = { "०":"0","१":"1","२":"2","३":"3","४":"4","५":"5","६":"6","७":"7","८":"8","९":"9" };
    if (digitMap[ch]) { out += digitMap[ch]; continue; }

    // fallback: append the character itself (useful for unknown chars)
    out += ch;
  }

  return out;
}

  // --- UI ---
  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-6 flex flex-col items-center">
      <div className="w-full max-w-3xl bg-gray-800 rounded-2xl p-6 shadow-lg">
        <header className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-semibold">Sanskrit Vibe — Decline & Conjugate</h1>
          <div className="text-sm text-gray-300">Offline • Local-only</div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <div className="bg-gray-900 p-6 rounded-lg text-center">
              <div className="text-5xl font-serif mb-2">{current?.type === "noun" ? current.noun.lemma : current?.verb?.lemma}</div>
              <div className="text-sm text-gray-400 mb-2">
                {current?.type === "noun" ? current?.noun?.translit : current?.verb?.translit}
              </div>
              <div className="text-gray-300 italic mb-4">{current?.type === "noun" ? current?.noun?.gloss : current?.verb?.gloss}</div>

              <div className="bg-gray-700 rounded px-4 py-3 text-left">
                <div className="font-medium text-sm text-gray-200 mb-2">Prompt</div>
                <div className="text-lg">{promptText}</div>
              </div>

              <div className="mt-4 flex gap-2">
                <input
                  ref={inputRef}
                  value={userInput}
                  onChange={(e) => {
                    setUserInput(e.target.value)
                    // const devanagari = hkToDevanagari(val);
                    // setUserInput(devanagari);
                  }}
                  onKeyDown={handleKey}
                    placeholder="Type in Harvard–Kyoto (e.g., rAmaH)"

                  className="w-full rounded-full px-4 py-3 bg-gray-100 text-gray-900 placeholder-gray-500 focus:outline-none"
                />
                <div className="mt-2 text-xl font-serif text-yellow-400">
                  {hkToDevanagari(userInput)}
                </div>
                <button
                  onClick={checkAnswer}
                  className="px-4 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-full text-white"
                >
                  Check
                </button>
                <button
                  onClick={() => newPrompt()}
                  className="px-4 py-3 bg-gray-600 hover:bg-gray-500 rounded-full text-white"
                >
                  Next
                </button>
              </div>

              <div className="mt-4">
                {feedback && (
                  <div className={`p-3 rounded ${feedback.ok ? 'bg-green-800 text-green-200' : 'bg-red-800 text-red-200'}`}>
                    {feedback.ok ? (
                      <div>✅ Correct — answer saved.</div>
                    ) : (
                      <div>
                        ❌ Not quite.
                        {feedback.reveal ? (
                          <div className="mt-2 text-sm">
                            <strong>Correct:</strong>{" "}
                            {feedback.reveal}{" "}
                            <span className="text-gray-400">
                              ({fromDevanagariToKyoto(feedback.reveal)})
                            </span>
                          </div>
                        ) : (
                          <div className="mt-2 text-sm">
                            <strong>Correct:</strong>{" "}
                            {feedback.correct}{" "}
                            <span className="text-gray-400">
                              ({fromDevanagariToKyoto(feedback.correct)})
                            </span>
                            {feedback.all && feedback.all.length > 1 && (
                              <div className="mt-1 text-xs text-gray-500">
                                Alternatives:{" "}
                                {feedback.all
                                  .map(
                                    (alt) =>
                                      `${alt} (${fromDevanagariToKyoto(alt)})`
                                  )
                                  .join(", ")}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                <div className="mt-2 flex gap-2">
                  <button onClick={revealAnswer} className="text-sm px-3 py-1 bg-yellow-700 rounded">Reveal</button>
                  <button onClick={() => { setUserInput(''); setFeedback(null); }} className="text-sm px-3 py-1 bg-gray-600 rounded">Clear</button>
                </div>
              </div>

            </div>
          </div>

          <aside className="bg-gray-800 p-4 rounded-lg">
            <div className="mb-4">
              <div className="text-xs text-gray-400">Score</div>
              <div className="text-xl font-semibold">{score.correct} / {score.total}</div>
            </div>

            <div className="mb-4">
              <div className="text-xs text-gray-400">Mode</div>
              <div className="flex gap-2 mt-2">
                <button onClick={() => { setMode('auto'); newPrompt('auto'); }} className={`px-3 py-1 rounded ${mode==='auto' ? 'bg-indigo-600' : 'bg-gray-700'}`}>Auto</button>
                <button onClick={() => { setMode('noun'); newPrompt('noun'); }} className={`px-3 py-1 rounded ${mode==='noun' ? 'bg-indigo-600' : 'bg-gray-700'}`}>Noun</button>
                <button onClick={() => { setMode('verb'); newPrompt('verb'); }} className={`px-3 py-1 rounded ${mode==='verb' ? 'bg-indigo-600' : 'bg-gray-700'}`}>Verb</button>
              </div>
            </div>

            <div className="mb-4">
              <div className="text-xs text-gray-400">Controls</div>
              <div className="text-sm mt-2">Press <kbd className="px-2 py-1 bg-gray-700 rounded">Enter</kbd> to check, <kbd className="px-2 py-1 bg-gray-700 rounded">Ctrl+K</kbd> for next.</div>
            </div>

            <div className="mb-4">
              <div className="text-xs text-gray-400">Data</div>
              <div className="mt-2 text-sm text-gray-300">Built-in examples: {DATA.nouns.length} nouns, {DATA.verbs.length} verbs.</div>
            </div>

            <div className="mt-2">
              <button onClick={() => { localStorage.clear(); setScore({correct:0,total:0}); }} className="w-full px-3 py-2 bg-red-600 rounded">Reset Progress</button>
            </div>
          </aside>
        </div>

        <footer className="mt-6 text-xs text-gray-500">
          This app is offline-capable (all data embedded). To make it installable you may add a service worker & manifest.
        </footer>
      </div>
    </div>
  );
}

/*
Notes / next steps you can perform locally:
- Expand DATA with more nouns/verbs and full declension tables.
- Add transliteration normalization for user input (IAST vs. diacritics stripping).
- Add audio or stroke animations for script learning.
- To enable PWA installability, add a manifest.json and a small service worker that caches this bundle and assets.
*/