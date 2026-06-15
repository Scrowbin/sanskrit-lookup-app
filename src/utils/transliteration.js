import { t } from "@indic-transliteration/sanscript";
import { INPUT_SCHEMES } from "../constants/transliterationSchemes";

/** Single code points that may appear in IAST (engine alphabet). */
const IAST_CHARS = new Set(
  "aāiīuūṛṝḷḹeēoōṃḥ" +
    "kgṅcjñṭḍṇtdnpbmyrlvśṣsh" +
    "+~!. "
);

/** Per-scheme Roman/Devanagari input alphabets (punctuation: space, +, ~, !, .). */
const SCHEME_INPUT_PATTERNS = {
  devanagari: /^[\u0900-\u097F\uA8E0-\uA8FF\s+~!.]+$/u,
  iast: /^[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF\s+~!.]+$/u,
  hk: /^[a-zA-Z0-9\s+~!.]+$/u,
  iso: /^[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF\s+~!.]+$/u,
  itrans: /^[a-zA-Z0-9.|'\\\s+~!.]+$/u,
  itrans_dravidian: /^[a-zA-Z0-9.|'\\\s+~!.]+$/u,
  kolkata: /^[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF\s+~!.]+$/u,
  slp1: /^[a-zA-Z0-9\s+~!.]+$/u,
  velthuis: /^[a-zA-Z".\s+~!.]+$/u,
  wx: /^[a-zA-Z0-9\s+~!.]+$/u,
  cyrillic: /^[\u0400-\u04FF\s+~!.]+$/u,
};

export function resolveInputScheme(inputType, inputScheme) {
  return inputType === "Devanagari" ? "devanagari" : inputScheme;
}

export function schemeLabel(scheme) {
  if (scheme === "devanagari") return "Devanagari";
  return INPUT_SCHEMES[scheme] ?? scheme;
}

function isLegalIAST(text) {
  const normalized = text.normalize("NFC");
  for (const ch of normalized) {
    if (!IAST_CHARS.has(ch)) return false;
  }
  try {
    const dev = t(normalized, "iast", "devanagari");
    return /[\u0900-\u097F]/u.test(dev);
  } catch {
    return false;
  }
}

function hasLatinLetters(text) {
  return /[A-Za-z]/.test(text);
}

function hasDevanagari(text) {
  return /[\u0900-\u097F\uA8E0-\uA8FF]/u.test(text);
}

/**
 * Normalise user input to IAST for the conjugation/declension API.
 * Devanagari and all Roman schemes are converted via Sanscript.
 */
export function toIAST(value, inputType, inputScheme) {
  const trimmed = value.trim();
  if (!trimmed) return "";
  const scheme = resolveInputScheme(inputType, inputScheme);
  return t(trimmed, scheme, "iast").trim();
}

/**
 * Validate input for the active script/scheme before calling the engine.
 * @returns {{ valid: boolean, message: string, iast: string }}
 */
export function validateInput(value, inputType, inputScheme) {
  const trimmed = value.trim();
  if (!trimmed) {
    return { valid: false, message: "Enter a root or stem.", iast: "" };
  }

  const scheme = resolveInputScheme(inputType, inputScheme);
  const pattern = SCHEME_INPUT_PATTERNS[scheme];

  if (inputType === "Devanagari" && hasLatinLetters(trimmed)) {
    return {
      valid: false,
      message: "Devanagari input cannot contain Roman letters.",
      iast: "",
    };
  }

  if (inputType === "Roman" && hasDevanagari(trimmed)) {
    return {
      valid: false,
      message: "Roman input cannot contain Devanagari characters.",
      iast: "",
    };
  }

  if (pattern && !pattern.test(trimmed)) {
    return {
      valid: false,
      message: `Contains characters not allowed in ${schemeLabel(scheme)}.`,
      iast: "",
    };
  }

  let iast;
  try {
    iast = t(trimmed, scheme, "iast").trim();
  } catch {
    return {
      valid: false,
      message: "Could not transliterate this input.",
      iast: "",
    };
  }

  if (!iast) {
    return {
      valid: false,
      message: "Transliteration produced an empty result.",
      iast: "",
    };
  }

  if (!isLegalIAST(iast)) {
    return {
      valid: false,
      message:
        "Input is not valid Sanskrit transliteration for the selected scheme.",
      iast: "",
    };
  }

  return { valid: true, message: "", iast };
}

/** Preview in another scheme (for read-only fields). */
export function transliteratePreview(value, inputType, inputScheme, targetScheme) {
  const trimmed = value.trim();
  if (!trimmed) return "";
  const from = resolveInputScheme(inputType, inputScheme);
  try {
    return t(trimmed, from, targetScheme);
  } catch {
    return "";
  }
}
