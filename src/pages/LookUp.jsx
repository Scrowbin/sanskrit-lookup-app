import { useState, useEffect } from "react";
import { t } from "@indic-transliteration/sanscript";
import { INPUT_SCHEMES } from "../constants/transliterationSchemes";
import useSanskritAPI from "../hook/useSanskritAPI";

// ── Declension table layout ──────────────────────────────────────────────────
const DECL_CASES = ["Nom", "Acc", "Ins", "Dat", "Abl", "Gen", "Loc", "Voc"];
const DECL_NUMBERS = ["Sg", "Du", "Pl"];
const DECL_CASE_LABELS = {
  Nom: "Nominative", Acc: "Accusative", Ins: "Instrumental",
  Dat: "Dative", Abl: "Ablative", Gen: "Genitive",
  Loc: "Locative", Voc: "Vocative",
};

// ── Conjugation table layout ─────────────────────────────────────────────────
const CONJ_PERSONS = ["1", "2", "3"];
const CONJ_NUMBERS = ["sg", "du", "pl"];
const PERSON_LABELS = { "1": "First", "2": "Second", "3": "Third" };
const NUMBER_LABELS = { sg: "Singular", du: "Dual", pl: "Plural" };

// ── Tense / mood options ─────────────────────────────────────────────────────
const TENSES = [
  { value: "present", label: "Present" },
  { value: "imperfect", label: "Imperfect" },
  { value: "optative", label: "Optative" },
  { value: "imperative", label: "Imperative" },
  { value: "future", label: "Future" },
  { value: "periphrastic_future", label: "Future2" },
  { value: "injunctive", label: "Injunctive" },
  { value: "perfect", label: "Perfect" },
  { value: "aorist", label: "Aorist" },
  { value: "benedictive", label: "Benedictive" },
  { value: "subjunctive", label: "Subjunctive" },
  { value: "conditional", label: "Conditional" },
  { value: "pluperfect", label: "Pluperfect" },
];

const VOICES = [
  { value: "active", label: "Active" },
  { value: "middle", label: "Middle" },
  { value: "passive", label: "Passive" },
];

const GENDER_MAP = { mas: "m", fem: "f", neu: "n" };

export default function LookUp() {
  const { conjugateDerivative, declense, loading, error, serverReady, clearError } =
    useSanskritAPI();

  const [mode, setMode] = useState("Declension");

  // Shared input state
  const [inputType, setInputType] = useState("Roman");
  const [inputValue, setInputValue] = useState("");
  const [inputScheme, setInputScheme] = useState("iast");
  const [outputScript, setOutputScript] = useState("Roman");

  // Conjugation-specific state
  const [gana, setGana] = useState(1);

  // Declension-specific state
  const [gender, setGender] = useState("mas");

  // Results
  const [conjResults, setConjResults] = useState(null); // { primary, causative, desiderative, intensive }
  const [declResult, setDeclResult] = useState(null);
  const [activeTab, setActiveTab] = useState("primary");
  const [showScroll, setShowScroll] = useState(false);

  const devanagariDisplay = t(inputValue, inputScheme, "devanagari");

  useEffect(() => {
    const checkScrollTop = () => {
      if (!showScroll && window.pageYOffset > 400) {
        setShowScroll(true);
      } else if (showScroll && window.pageYOffset <= 400) {
        setShowScroll(false);
      }
    };
    window.addEventListener('scroll', checkScrollTop);
    return () => window.removeEventListener('scroll', checkScrollTop);
  }, [showScroll]);

  const scrollTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // ── Helpers ────────────────────────────────────────────────────────────────

  /** Convert IAST to chosen output script */
  function toOutput(forms) {
    if (!forms || forms.length === 0) return "—";
    const mapped = forms.map((f) =>
      outputScript === "Devanagari" ? t(f, "iast", "devanagari") : f
    );
    return mapped.join(", ");
  }

  /** Normalise user input to IAST for the API */
  function toIAST(val) {
    if (inputType === "Devanagari") {
      return t(val, "devanagari", "iast");
    }
    return t(val, inputScheme, "iast");
  }

  // ── Submit handlers ────────────────────────────────────────────────────────

  async function handleConjugation(e) {
    e.preventDefault();
    clearError();
    const root = toIAST(inputValue).trim();
    if (!root) return;

    // Reset results to initial loading state
    setConjResults({
      primary: null,
      causative: null,
      desiderative: null,
      intensive: null,
    });

    // We fetch them concurrently, but update the state as each one completes
    // to give the user immediate feedback (incremental rendering).
    const fetchAndUpdate = async (derivative, key) => {
      try {
        const res = await conjugateDerivative({ root, class_num: Number(gana), derivative });
        setConjResults(prev => ({ ...prev, [key]: res }));
      } catch (err) {
        // Errors are handled by the hook, just set empty to stop loading skeleton
        setConjResults(prev => ({ ...prev, [key]: {} }));
      }
    };

    await Promise.all([
      fetchAndUpdate(null, "primary"),
      fetchAndUpdate("causative", "causative"),
      fetchAndUpdate("desiderative", "desiderative"),
      fetchAndUpdate("intensive", "intensive")
    ]);
  }

  async function handleDeclension(e) {
    e.preventDefault();
    clearError();
    const stem = toIAST(inputValue).trim();
    if (!stem) return;

    const paradigm = await declense({
      stem,
      gender: GENDER_MAP[gender],
    });
    setDeclResult(paradigm);
  }

  // ── Rendering Helpers ──────────────────────────────────────────────────────

  function renderKrdantaForm(formString) {
    if (outputScript !== "Devanagari") {
      // Still apply styling to the m. n. f. tags even in Roman script
      return formString.split(" ").map((word, i) => {
        if (word === "m." || word === "n." || word === "f.") {
          return <span key={i} className="text-neutral-500 font-sans text-[10px] uppercase tracking-wider mx-1">{word.replace('.', '')}</span>;
        }
        return <span key={i}>{word} </span>;
      });
    }
    
    return formString.split(" ").map((word, i) => {
      if (word === "m." || word === "n." || word === "f.") {
        return <span key={i} className="text-neutral-500 font-sans text-[10px] uppercase tracking-wider mx-1">{word.replace('.', '')}</span>;
      }
      return <span key={i}>{t(word, "iast", "devanagari")} </span>;
    });
  }

  function renderDerivativeResult(title, data) {
    if (!data || (!data.tenses && !data.krdantas) || (Object.keys(data.tenses || {}).length === 0 && !data.krdantas)) {
      return null;
    }

    return (
      <div className="mt-12 space-y-8">
        <h2 className="text-2xl font-bold text-indigo-400 border-b border-neutral-700 pb-2">{title}</h2>

        {data.tenses && TENSES.map(({ value, label }) => {
          const tenseData = data.tenses[value];
          if (!tenseData) return null;

          return (
            <div key={value} className="space-y-6 bg-neutral-900/40 p-6 rounded-xl border border-neutral-800 shadow-sm relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500/50"></div>
              <h3 className="text-xl font-bold text-neutral-100 border-b border-neutral-700/50 pb-3 mb-4">{label}</h3>
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                {VOICES.map(({ value: voiceValue, label: voiceLabel }) => {
                  const paradigm = tenseData[voiceValue];
                  if (!paradigm || Object.keys(paradigm).length === 0) return null;

                  return (
                    <div key={voiceValue} className="space-y-3">
                      <div className="overflow-x-auto">
                        <table className="w-full border-collapse text-sm bg-neutral-900 rounded-lg overflow-hidden shadow">
                          <thead>
                            <tr className="border-b border-neutral-700 bg-neutral-800">
                              <th className="px-4 py-2 text-left text-neutral-300 font-medium w-32">{voiceLabel}</th>
                              {CONJ_NUMBERS.map(n => (
                                <th key={n} className="px-4 py-2 text-left text-neutral-300 font-medium">{NUMBER_LABELS[n]}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {CONJ_PERSONS.map((p) => (
                              <tr key={p} className="border-b border-neutral-800 hover:bg-neutral-800/80 transition-colors">
                                <td className="px-4 py-3 font-medium text-neutral-400">
                                  {PERSON_LABELS[p]}
                                </td>
                                {CONJ_NUMBERS.map((n) => (
                                  <td key={n} className="px-4 py-3 font-mono text-base text-neutral-200">
                                    {toOutput(paradigm[`${p}${n}`])}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}

        {data.krdantas && (data.krdantas.participles?.length > 0 || data.krdantas.indeclinables?.length > 0) && (
          <div className="space-y-8 pt-4">

            {data.krdantas.participles?.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-xl font-medium text-neutral-200">Participles</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {data.krdantas.participles.map((p, idx) => (
                    <div key={idx} className="bg-neutral-900 p-4 rounded-lg shadow border border-neutral-800">
                      <div className="text-xs uppercase tracking-wide text-neutral-500 mb-1">{p.name}</div>
                      <div className="font-mono text-base text-neutral-200 whitespace-pre-wrap">
                        {renderKrdantaForm(p.form)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {data.krdantas.indeclinables?.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-xl font-medium text-neutral-200">Indeclinable forms</h3>
                <div className="flex flex-wrap gap-4">
                  {data.krdantas.indeclinables.map((item, idx) => (
                    <div key={idx} className="bg-neutral-900 px-5 py-4 rounded-lg shadow border border-neutral-800 flex-1 min-w-[200px]">
                      <div className="text-xs uppercase tracking-wide text-neutral-500 mb-1">{item.name}</div>
                      <div className="font-mono text-base text-neutral-200 whitespace-pre-wrap">
                        {renderKrdantaForm(item.form)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        )}
      </div>
    );
  }

  // ── Shared styles ─────────────────────────────────────────────────────────
  const labelStyles = "text-[11px] uppercase tracking-wide text-neutral-400";

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 flex justify-center">
      <div className="w-full max-w-[1600px] px-6 md:px-12 lg:px-16 py-10 space-y-12">

        {/* ── Server status indicator ──────────────────────────────────────── */}
        <div className="flex justify-center">
          <span
            className={`inline-flex items-center gap-2 text-xs px-3 py-1 rounded-full ${serverReady
              ? "bg-emerald-900/40 text-emerald-400"
              : "bg-amber-900/40 text-amber-400"
              }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${serverReady ? "bg-emerald-400 animate-pulse" : "bg-amber-400"
                }`}
            />
            {serverReady ? "Engine ready" : "Engine starting…"}
          </span>
        </div>

        {/* ── Mode toggle ──────────────────────────────────────────────────── */}
        <div className="flex justify-center">
          <div className="flex w-fit rounded-lg bg-neutral-800 p-1">
            <button
              onClick={() => { setMode("Declension"); setConjResults(null); }}
              className={`px-4 py-2 text-sm rounded-md transition-colors ${mode === "Declension"
                ? "bg-neutral-100 text-neutral-900 shadow"
                : "text-neutral-300 hover:text-white"
                }`}
            >
              Noun Declension
            </button>

            <button
              onClick={() => { setMode("Conjugation"); setDeclResult(null); }}
              className={`px-4 py-2 text-sm rounded-md transition-colors ${mode === "Conjugation"
                ? "bg-neutral-100 text-neutral-900 shadow"
                : "text-neutral-300 hover:text-white"
                }`}
            >
              Verb Conjugation
            </button>
          </div>
        </div>

        {/* ── Error banner ──────────────────────────────────────────────────── */}
        {error && (
          <div className="bg-red-900/30 border border-red-700 text-red-300 rounded-lg px-4 py-3 text-sm flex justify-between items-center">
            <span>⚠ {error}</span>
            <button onClick={clearError} className="text-red-400 hover:text-red-200 ml-4 font-bold">✕</button>
          </div>
        )}

        {/* ================================================================= */}
        {/* CONJUGATION MODE                                                  */}
        {/* ================================================================= */}
        {mode === "Conjugation" && (
          <section className="space-y-8">
            <div>
              <h1 className="text-3xl font-semibold text-center text-white mb-2">
                Verb Conjugation
              </h1>
              <p className="text-center text-neutral-400">
                Enter a root to generate all primary and derivative paradigms
              </p>
            </div>

            <form className="space-y-8 bg-neutral-900/50 p-6 rounded-xl border border-neutral-800" onSubmit={handleConjugation}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* INPUT */}
                <div className={`space-y-1 ${inputType === "Devanagari" ? "md:col-span-2" : ""}`}>
                  <div className={labelStyles}>Input ({inputType})</div>
                  <input
                    id="verb-text-input"
                    type="text"
                    autoComplete="off"
                    className="input inset-0 flex items-center text-neutral-100 whitespace-pre"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder={inputType === "Roman" ? "e.g. bhū" : "e.g. भू"}
                  />
                </div>

                {inputType === "Roman" && (
                  <div className="space-y-1">
                    <div className={labelStyles}>Preview (Devanagari)</div>
                    <input
                      type="text"
                      className="input bg-neutral-900 text-neutral-300 border-neutral-700"
                      readOnly
                      value={devanagariDisplay}
                    />
                  </div>
                )}

                {/* INPUT SCHEME */}
                <div className="space-y-1">
                  <div className={labelStyles}>Input Script</div>
                  <select className="input" value={inputType} onChange={(e) => setInputType(e.target.value)}>
                    <option value="Roman">Roman</option>
                    <option value="Devanagari">Devanagari</option>
                  </select>
                </div>

                {inputType === "Roman" && (
                  <div className="space-y-1">
                    <div className={labelStyles}>Transliteration Scheme</div>
                    <select className="input" value={inputScheme} onChange={(e) => setInputScheme(e.target.value)}>
                      {Object.entries(INPUT_SCHEMES).map(([value, label]) => (
                        <option key={value} value={value}>{label}</option>
                      ))}
                    </select>
                  </div>
                )}

                {/* CLASS (GAṆA) */}
                <div className="space-y-1">
                  <div className={labelStyles}>Class (Gaṇa)</div>
                  <select className="input" value={gana} onChange={(e) => setGana(e.target.value)}>
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0].map((num) => (
                      <option key={num} value={num}>Class {num} {num === 0 ? "(No Present forms)" : ""}</option>
                    ))}
                  </select>
                </div>

                {/* OUTPUT FORMAT */}
                <div className="space-y-1">
                  <div className={labelStyles}>Output Script</div>
                  <select className="input" value={outputScript} onChange={(e) => setOutputScript(e.target.value)}>
                    <option value="Roman">Roman (IAST)</option>
                    <option value="Devanagari">Devanagari</option>
                  </select>
                </div>
              </div>

              {/* BUTTONS */}
              <div className="flex gap-4 justify-center pt-2">
                <button type="submit" className="btn-primary min-w-[120px]" disabled={loading}>
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <span className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                      Loading...
                    </span>
                  ) : "Generate"}
                </button>
                <button
                  type="reset"
                  className="btn-secondary min-w-[120px]"
                  disabled={loading}
                  onClick={() => {
                    setInputType("Roman");
                    setInputValue("");
                    setInputScheme("iast");
                    setGana(1);
                    setConjResults(null);
                    clearError();
                  }}
                >
                  Reset
                </button>
              </div>
            </form>

            {/* ── Conjugation results ──────────────────────────────── */}
            {conjResults && (
              <div className="space-y-8 animate-in fade-in duration-500 pb-16">

                <div className="flex flex-wrap gap-2 border-b border-neutral-800 pb-2">
                  {["primary", "causative", "desiderative", "intensive"].map(tab => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${activeTab === tab
                        ? "bg-neutral-800 text-white"
                        : "text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/50"
                        }`}
                    >
                      {tab.charAt(0).toUpperCase() + tab.slice(1)} Conjugation
                    </button>
                  ))}
                </div>

                <div className="min-h-[400px]">
                  {activeTab === "primary" && (conjResults.primary ? renderDerivativeResult("Primary Conjugation", conjResults.primary) : (loading && <div className="animate-pulse text-neutral-500">Generating Primary Conjugation...</div>))}
                  {activeTab === "causative" && (conjResults.causative ? renderDerivativeResult("Causative Conjugation", conjResults.causative) : (loading && <div className="animate-pulse text-neutral-500">Generating Causative Conjugation...</div>))}
                  {activeTab === "desiderative" && (conjResults.desiderative ? renderDerivativeResult("Desiderative Conjugation", conjResults.desiderative) : (loading && <div className="animate-pulse text-neutral-500">Generating Desiderative Conjugation...</div>))}
                  {activeTab === "intensive" && (conjResults.intensive ? renderDerivativeResult("Intensive Conjugation", conjResults.intensive) : (loading && <div className="animate-pulse text-neutral-500">Generating Intensive Conjugation...</div>))}
                </div>

                {!loading && Object.values(conjResults).every(res => !res || (!res.tenses && !res.krdantas)) && (
                  <div className="text-center text-neutral-500 py-12">
                    No results found for this root and class.
                  </div>
                )}
              </div>
            )}
          </section>
        )}

        {/* ================================================================= */}
        {/* DECLENSION MODE                                                   */}
        {/* ================================================================= */}
        {mode === "Declension" && (
          <section className="space-y-8">
            <div>
              <h1 className="text-3xl font-semibold text-center text-white mb-2">Declension</h1>
              <p className="text-center text-neutral-400">
                Enter a stem and select gender to generate the full paradigm
              </p>
            </div>

            <form className="space-y-8 bg-neutral-900/50 p-6 rounded-xl border border-neutral-800" onSubmit={handleDeclension}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* INPUT */}
                <div className={`space-y-1 ${inputType === "Devanagari" ? "md:col-span-2" : ""}`}>
                  <div className={labelStyles}>Input ({inputType})</div>
                  <input
                    id="main-text-input"
                    type="text"
                    autoComplete="off"
                    className="input inset-0 flex items-center text-neutral-100 whitespace-pre"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder={inputType === "Roman" ? "e.g. rāma" : "e.g. राम"}
                  />
                </div>

                {inputType === "Roman" && (
                  <div className="space-y-1">
                    <div className={labelStyles}>Preview (Devanagari)</div>
                    <input
                      type="text"
                      className="input bg-neutral-900 text-neutral-300 border-neutral-700"
                      readOnly
                      value={devanagariDisplay}
                    />
                  </div>
                )}

                {/* INPUT SCHEME */}
                <div className="space-y-1">
                  <div className={labelStyles}>Input Script</div>
                  <select className="input" value={inputType} onChange={(e) => setInputType(e.target.value)}>
                    <option value="Roman">Roman</option>
                    <option value="Devanagari">Devanagari</option>
                  </select>
                </div>

                {inputType === "Roman" && (
                  <div className="space-y-1">
                    <div className={labelStyles}>Transliteration Scheme</div>
                    <select className="input" value={inputScheme} onChange={(e) => setInputScheme(e.target.value)}>
                      {Object.entries(INPUT_SCHEMES).map(([value, label]) => (
                        <option key={value} value={value}>{label}</option>
                      ))}
                    </select>
                  </div>
                )}

                {/* GENDER */}
                <div className="space-y-1">
                  <div className={labelStyles}>Gender</div>
                  <select className="input" value={gender} onChange={(e) => setGender(e.target.value)}>
                    <option value="mas">Masculine</option>
                    <option value="fem">Feminine</option>
                    <option value="neu">Neuter</option>
                  </select>
                </div>

                {/* OUTPUT FORMAT */}
                <div className="space-y-1">
                  <div className={labelStyles}>Output Script</div>
                  <select className="input" value={outputScript} onChange={(e) => setOutputScript(e.target.value)}>
                    <option value="Roman">Roman (IAST)</option>
                    <option value="Devanagari">Devanagari</option>
                  </select>
                </div>
              </div>

              {/* BUTTONS */}
              <div className="flex gap-4 justify-center pt-2">
                <button type="submit" className="btn-primary min-w-[120px]" disabled={loading}>
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <span className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                      Loading...
                    </span>
                  ) : "Generate"}
                </button>
                <button
                  type="reset"
                  className="btn-secondary min-w-[120px]"
                  disabled={loading}
                  onClick={() => {
                    setInputType("Roman");
                    setInputValue("");
                    setInputScheme("iast");
                    setGender("mas");
                    setDeclResult(null);
                    clearError();
                  }}
                >
                  Reset
                </button>
              </div>
            </form>

            {/* ── Declension results table ───────────────────────────────── */}
            {loading && (
              <div className="text-center text-neutral-400 py-12 animate-pulse">
                Generating declension paradigm...
              </div>
            )}

            {!loading && declResult && Object.keys(declResult).length > 0 && (
              <div className="overflow-x-auto mt-12 animate-in fade-in duration-500 pb-16">
                <h2 className="text-2xl font-bold text-indigo-400 border-b border-neutral-700 pb-2 mb-6">Declension Paradigm</h2>
                <table className="w-full border-collapse text-sm bg-neutral-900 rounded-lg overflow-hidden shadow">
                  <thead>
                    <tr className="border-b border-neutral-700 bg-neutral-800">
                      <th className="px-4 py-3 text-left text-neutral-300 font-medium w-32">Case</th>
                      {DECL_NUMBERS.map((n) => (
                        <th key={n} className="px-4 py-3 text-left text-neutral-300 font-medium">{n}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {DECL_CASES.map((c) => (
                      <tr key={c} className="border-b border-neutral-800 hover:bg-neutral-800/80 transition-colors">
                        <td className="px-4 py-3 font-medium text-neutral-400">
                          {DECL_CASE_LABELS[c]}
                        </td>
                        {DECL_NUMBERS.map((n) => (
                          <td key={n} className="px-4 py-3 font-mono text-base text-neutral-200">
                            {toOutput(declResult[`${c}_${n}`])}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        )}
      </div>

      {/* Scroll to top button */}
      <button
        onClick={scrollTop}
        className={`fixed bottom-8 right-8 p-3 rounded-full bg-indigo-600 text-white shadow-lg transition-all duration-300 hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-2 focus:ring-offset-neutral-950 z-50 ${
          showScroll ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10 pointer-events-none'
        }`}
        aria-label="Scroll to top"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
        </svg>
      </button>
    </div>
  );
}
