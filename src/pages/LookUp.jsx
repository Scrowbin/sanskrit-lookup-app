import { useState } from "react";
import { t } from "@indic-transliteration/sanscript";
import { INPUT_SCHEMES } from "../constants/transliterationSchemes";

export default function LookUp() {
  const isDebugging = false;
  const [inputValue, setInputValue] = useState("");
  const [inputScheme, setInputScheme] = useState("hk");

  // This calculates the Devanagari version for display
  const devanagariDisplay = t(inputValue, inputScheme, "devanagari");

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 flex justify-center">
      <div className="w-full max-w-5xl px-6 py-10 space-y-16">
        
        {/* ================= DECLENSION ================= */}
        <section className="space-y-6">
          <h1 className="text-3xl font-semibold text-center">Declension</h1>
          <p className="text-center text-neutral-400">
            Submit stem and gender for declension
          </p>

          <form className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* STACKED INPUT CONTAINER */}
              <div className="relative group">
                {/* 1. The Visual Layer (Devanagari) */}
                <div className="input absolute inset-0 flex items-center pointer-events-none text-neutral-100 whitespace-pre">
                  {devanagariDisplay}
                  {/* Subtle blinking cursor simulation if empty */}
                  {inputValue === "" && <span className="text-neutral-500">Stem (e.g. rāma)</span>}
                </div>

                {/* 2. The Interaction Layer (Hidden Roman Text) */}
                <input
                  id="main-text-input"
                  type="text"
                  name="stem"
                  autoComplete="off"
                  className="input relative z-10 bg-transparent text-transparent caret-white focus:outline-none"
                  value={inputValue}           
                  onChange={(e) => setInputValue(e.target.value)}
                />
              </div>

              {isDebugging && (
                <input 
                  type="text" 
                  className="input bg-neutral-900" 
                  readOnly 
                  placeholder="Debug Preview" 
                  value={devanagariDisplay} 
                />
              )}

              <select name="gender" className="input">
                <option value="mas">Masculine</option>
                <option value="fem">Feminine</option>
                <option value="neu">Neuter</option>
              </select>

              <select 
                name="inputScheme" 
                className="input"
                value={inputScheme}
                onChange={(e) => setInputScheme(e.target.value)}
              >
                {Object.entries(INPUT_SCHEMES).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>

              <select name="outputFont" className="input">
                <option>Roman</option>
                <option>Devanagari</option>
              </select>
            </div>

            <div className="flex gap-4 justify-center">
              <button type="submit" className="btn-primary">Send</button>
              <button 
                type="reset" 
                className="btn-secondary"
                onClick={() => { setInputValue(""); setInputScheme("hk"); }}
              >
                Reset
              </button>
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}