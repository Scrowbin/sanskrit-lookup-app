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
