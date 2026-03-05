import { useState } from "react";
import { t } from "@indic-transliteration/sanscript";
import { INPUT_SCHEMES } from "../constants/transliterationSchemes";

export default function LookUp() {
  const isDebugging = true;

  const [mode, setMode] = useState("Declension"); //Declension or Verb Conjugation

  const [inputType, setInputType] = useState("Roman"); //whether the user wants to type in roman characters or devanagari
  const [inputValue, setInputValue] = useState("");
  const [inputScheme, setInputScheme] = useState("iast");

  const devanagariDisplay = t(inputValue, inputScheme, "devanagari");

  //css sh
  const labelStyles = "text-[11px] uppercase tracking-wide text-neutral-400";
  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 flex justify-center">
      <div className="w-full max-w-5xl px-6 py-10 space-y-12">
        <div className="flex justify-center">
          <div className="flex w-fit rounded-lg bg-neutral-800 p-1">
            <button
              onClick={() => setMode("Declension")}
              className={`px-4 py-2 text-sm rounded-md ${
                mode === "Declension"
                  ? "bg-neutral-100 text-neutral-900"
                  : "text-neutral-300 hover:text-white"
              }`}
            >
              Noun Declension
            </button>

            <button
              onClick={() => setMode("Conjugation")}
              className={`px-4 py-2 text-sm rounded-md ${
                mode === "Conjugation"
                  ? "bg-neutral-100 text-neutral-900"
                  : "text-neutral-300 hover:text-white"
              }`}
            >
              Verb Conjugation
            </button>
          </div>
        </div>

        {
          (mode === "Conjugation") &&
         (
          <section className="space-y-6">
            <h1 className="text-3xl font-semibold text-center">Verb Conjugation</h1>
            <p className="text-center text-neutral-400">
              Submit root and details for verb conjugation
            </p>

            <form className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* INPUT (Roman → Devanagari overlay) */}
                <div className={`space-y-1 ${ inputType === "Devanagari" ? "md:col-span-2" : ""}`} >
                  <div className={labelStyles}>
                    Input ({inputType})
                  </div>
                  
                  <div className="relative group">
                    <input
                      id="verb-text-input"
                      type="text"
                      name="stem"
                      autoComplete="off"
                      className="input inset-0 flex items-center text-neutral-100 whitespace-pre"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                    />
                  </div>
                </div>

                {(inputType === "Roman") && <div className="space-y-1">
                  <div className={labelStyles}>
                    Preview (Devanagari)
                  </div>
                  
                  <input
                    type="text"
                    className="input bg-neutral-900"
                    readOnly
                    value={devanagariDisplay}
                  />
                </div>}
              
                {/* INPUT i.e roman or devanagari */}
                <div className="space-y-1">
                  <div className={labelStyles}>
                    Input Scheme
                  </div>
                  
                  <select name="input" className="input" value={inputType} onChange={(e) => setInputType(e.target.value)}>
                    <option value="Roman">Roman</option>
                    <option value="Devanagari">Devanagari</option>
                  </select>
                </div>
                
                {/* TRANSLITERATION SCHEME */}
                {(inputType === "Roman") &&
                (<div className="space-y-1">
                  <div className={labelStyles}>
                    Transliteration Scheme
                  </div>
                  
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
                </div>)}

                {/* CLASS (GAṆA) */}
                <div className="space-y-1">
                  <div className={labelStyles}>
                    Class (Gaṇa) 
                  </div>

                  <div className={labelStyles}>
                    Use 0 for roots with no present forms
                  </div>
                  <select name="gana" className="input">
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0].map(num => (
                      <option key={num} value={num}>Class {num}</option>
                    ))}
                  </select>
                </div>

                {/* OUTPUT FORMAT */}
                <div className="space-y-1">
                  <div className={labelStyles}>
                    Output Script
                  </div>
                  
                  <select name="outputFont" className="input">
                    <option>Roman</option>
                    <option>Devanagari</option>
                  </select>
                </div>

              </div>

              <div className="flex gap-4 justify-center">
                <button type="submit" className="btn-primary">
                  Send
                </button>
                <button
                  type="reset"
                  className="btn-secondary"
                  onClick={() => {
                    setInputType("Roman");
                    setInputValue("");
                    setInputScheme("itrans");
                  }}
                >
                  Reset
                </button>
              </div>
            </form>
          </section>    
         )
        }

        {
          (mode === "Declension") &&
         (
         <section className="space-y-6">
            <h1 className="text-3xl font-semibold text-center">Declension</h1>
            <p className="text-center text-neutral-400">
              Submit stem and gender for declension
            </p>

            <form className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* INPUT (Roman → Devanagari overlay) */}
                <div className={`space-y-1 ${ inputType === "Devanagari" ? "md:col-span-2" : ""}`} >
                  <div className={labelStyles}>
                    Input ({inputType})
                  </div>
                  

                  <div className="relative group">
                    <input
                      id="main-text-input"
                      type="text"
                      name="stem"
                      autoComplete="off"
                      className="input inset-0 flex items-center text-neutral-100 whitespace-pre"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                    />
                  </div>
                </div>

        
                
                {(inputType === "Roman") && <div className="space-y-1">
                  <div className={labelStyles}>
                    Preview (Devanagari)
                  </div>
                  
                  <input
                    type="text"
                    className="input bg-neutral-900"
                    readOnly
                    value={devanagariDisplay}
                  />
                </div>}
              
                {/* INPUT i.e roman or devanagari */}
                <div className="space-y-1">
                  <div className={labelStyles}>
                    Input Scheme
                  </div>
                  
                  <select name="input" className="input" value={inputType} onChange={(e) => setInputType(e.target.value)}>
                    <option value="Roman">Roman</option>
                    <option value="Devanagari">Devanagari</option>
                  </select>
                </div>
                
                {/* TRANSLITERATION SCHEME */}
                {(inputType === "Roman")
                &&
                (<div className="space-y-1">
                  <div className={labelStyles}>
                    Transliteration Scheme
                  </div>
                  
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
                </div>)}

                {/* GENDER */}
                <div className="space-y-1">
                  <div className={labelStyles}>
                    Gender
                  </div>
                  
                  <select name="gender" className="input">
                    <option value="mas">Masculine</option>
                    <option value="fem">Feminine</option>
                    <option value="neu">Neuter</option>
                  </select>
                </div>

                {/* OUTPUT FORMAT */}
                <div className="space-y-1">
                  <div className={labelStyles}>
                    Output Script
                  </div>
                  
                  <select name="outputFont" className="input">
                    <option>Roman</option>
                    <option>Devanagari</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-4 justify-center">
                <button type="submit" className="btn-primary">
                  Send
                </button>
                <button
                  type="reset"
                  className="btn-secondary"
                  onClick={() => {
                    setInputType("Roman");
                    setInputValue("");
                    setInputScheme("itrans");
                  }}
                >
                  Reset
                </button>
              </div>
            </form>
          </section>
          )
        }
      </div>
    </div>
  );
}
