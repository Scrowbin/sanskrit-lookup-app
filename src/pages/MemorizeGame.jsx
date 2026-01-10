// !! This page is secondary for now, dont need to touch it, focus on the LookUp page


export function MemorizeGame () {
    // -    -- Sample dataset (expandable) ---
  // Each noun includes forms for cases x numbers. For verbs include conjugations.
  
  const DATA = {
    
  };

  

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

export default MemorizeGame