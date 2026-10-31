/** Mizo (Lushai) number ↔ words for integers 0 .. 9_999_999_999 */

export const MIN = 0;
export const MAX = 9_999_999_999;

const UNITS_FULL = {
  1: "pakhat",
  2: "pahnih",
  3: "pathum",
  4: "pali",
  5: "panga",
  6: "paruk",
  7: "pasarih",
  8: "pariat",
  9: "pakua",
};

const STEMS = {
  1: "khat",
  2: "hnih",
  3: "thum",
  4: "li",
  5: "nga",
  6: "ruk",
  7: "sarih",
  8: "riat",
  9: "kua",
};

const FULL_TO_DIGIT = Object.fromEntries(
  Object.entries(UNITS_FULL).map(([k, v]) => [v, Number(k)]),
);
const STEM_TO_DIGIT = Object.fromEntries(
  Object.entries(STEMS).map(([k, v]) => [v, Number(k)]),
);

const SCALES = [
  [1_000_000_000, "tluklehdingawn", false],
  [100_000_000, "vaibelchhetak", false],
  [10_000_000, "vaibelchhia", false],
  [1_000_000, "maktaduai", false],
  [100_000, "nuai", true],
  [10_000, "sing", true],
  [1_000, "sang", true],
  [100, "za", false],
  [10, "sawm", false],
];

const TONE_MAP = {
  á: "a",
  à: "a",
  â: "a",
  ä: "a",
  ǎ: "a",
  ȧ: "a",
  ạ: "a",
  ã: "a",
  é: "e",
  è: "e",
  ê: "e",
  ë: "e",
  ě: "e",
  ė: "e",
  ẹ: "e",
  í: "i",
  ì: "i",
  î: "i",
  ï: "i",
  ǐ: "i",
  ị: "i",
  ĩ: "i",
  ó: "o",
  ò: "o",
  ô: "o",
  ö: "o",
  ǒ: "o",
  ọ: "o",
  ú: "u",
  ù: "u",
  û: "u",
  ü: "u",
  ǔ: "u",
  ů: "u",
  ụ: "u",
  ũ: "u",
  ṅ: "n",
  ṭ: "t",
};

function stripDiacritics(s) {
  let out = "";
  for (const ch of s) out += TONE_MAP[ch] ?? ch;
  return out.normalize("NFKD").replace(/\p{M}/gu, "");
}

function coerceInt(n) {
  const s = String(n).trim().replace(/_/g, "").replace(/,/g, "");
  if (!s || !/^[+-]?\d+$/.test(s)) throw new Error(`not an integer: ${n}`);
  const value = Number(s);
  if (!Number.isInteger(value)) throw new Error(`not an integer: ${n}`);
  return value;
}

export function numberToWords(raw) {
  const value = coerceInt(raw);
  if (value < MIN || value > MAX) {
    throw new Error(`out of range (allowed ${MIN}..${MAX})`);
  }
  if (value === 0) return "bial";

  const parts = [];
  let remaining = value;

  for (const [scale, name, useKhat] of SCALES) {
    const digit = Math.floor(remaining / scale);
    remaining %= scale;
    if (digit === 0) continue;

    if (scale === 10) {
      if (digit === 1 && remaining > 0) {
        parts.push("sawm" + UNITS_FULL[remaining]);
        remaining = 0;
      } else if (digit === 1) {
        parts.push("sawm");
      } else {
        parts.push("sawm" + STEMS[digit]);
      }
      continue;
    }

    if (digit === 1) parts.push(useKhat ? name + "khat" : name);
    else parts.push(name + STEMS[digit]);
  }

  if (remaining > 0) parts.push(UNITS_FULL[remaining]);
  return parts.join(" ");
}

function matchScaleToken(tok) {
  const variants = [tok];
  if (tok.startsWith("nuaih")) variants.push("nuai" + tok.slice(5));
  if (tok.startsWith("maktaduaih")) variants.push("maktaduai" + tok.slice(10));

  for (const candidate of variants) {
    if (candidate.startsWith("sawm")) {
      const rest = candidate.slice(4);
      if (rest === "") return [10, 1];
      if (rest in FULL_TO_DIGIT) return [10, 10 + FULL_TO_DIGIT[rest]];
      if (rest in STEM_TO_DIGIT) return [10, STEM_TO_DIGIT[rest]];
      if (rest === "khat") return [10, 1];
    }

    for (const [scale, name] of SCALES) {
      if (scale === 10) continue;
      if (candidate === name || candidate === name + "khat") return [scale, 1];
      if (candidate.startsWith(name)) {
        const rest = candidate.slice(name.length);
        if (rest in STEM_TO_DIGIT) return [scale, STEM_TO_DIGIT[rest]];
        if (rest === "khat") return [scale, 1];
      }
    }
  }
  return null;
}

function tokenize(normalized) {
  const raw = normalized.split(/\s+/).filter(Boolean);
  const out = [];
  let i = 0;
  while (i < raw.length) {
    let a = raw[i];
    if (i + 1 < raw.length) {
      const b = raw[i + 1];
      const glued = a + b;
      if (b === "khat" && matchScaleToken(a + "khat") !== null) {
        out.push(a + "khat");
        i += 2;
        continue;
      }
      if (a === "sawm" && b in FULL_TO_DIGIT) {
        out.push("sawm" + b);
        i += 2;
        continue;
      }
      if (matchScaleToken(glued) !== null) {
        out.push(glued);
        i += 2;
        continue;
      }
      if ((a === "vaibelchhe" || a === "vaibelchhia") && b === "khat") {
        out.push(a === "vaibelchhe" ? "vaibelchhetak" : "vaibelchhiakhat");
        i += 2;
        continue;
      }
      if (a === "vaibelchhe" && b in STEM_TO_DIGIT) {
        out.push("vaibelchhetak" + b);
        i += 2;
        continue;
      }
    }
    if (a === "nuaih" || a === "maktaduaih") a = a.slice(0, -1);
    out.push(a);
    i += 1;
  }
  return out;
}

function normalizePhrase(text) {
  let s = stripDiacritics(text.trim().toLowerCase());
  s = s.replace(/\btluk\s+leh\s+dingawn\b/g, "tluklehdingawn");
  s = s.replace(/\bleh\b/g, " ");
  s = s.replace(/[‐‑‒–—―\-_/]+/g, " ");
  s = s.replace(/[^\w\s]/gu, " ");
  s = s.replace(/\s+/g, " ").trim();
  s = s.replace(/\bpalnih\b/g, "pahnih");
  return s;
}

export function wordsToNumber(text) {
  const normalized = normalizePhrase(text);
  if (!normalized) throw new Error("empty input");
  if (normalized === "bial" || normalized === "zero") return 0;

  const tokens = tokenize(normalized);
  if (!tokens.length) throw new Error("empty input after normalization");

  let total = 0;
  const usedScales = new Set();
  let i = 0;
  const n = tokens.length;

  while (i < n) {
    const tok = tokens[i];

    if (tok in FULL_TO_DIGIT) {
      if (i !== n - 1) throw new Error(`unexpected unit before end: ${tok}`);
      total += FULL_TO_DIGIT[tok];
      i += 1;
      break;
    }

    const matched = matchScaleToken(tok);
    if (matched === null) throw new Error(`unrecognized token: ${tok}`);

    const [scale, digit] = matched;
    if (usedScales.has(scale)) throw new Error(`duplicate scale for ${scale}`);
    if (usedScales.size > 0 && scale >= Math.min(...usedScales)) {
      throw new Error(`scales out of order near ${tok}`);
    }
    usedScales.add(scale);

    if (scale === 10 && digit >= 11) {
      total += digit;
      i += 1;
      if (i < n && tokens[i] in FULL_TO_DIGIT) {
        throw new Error("extra unit after teen form");
      }
      continue;
    }

    total += digit * scale;
    i += 1;

    if (scale === 10 && i < n && tokens[i] in FULL_TO_DIGIT) {
      total += FULL_TO_DIGIT[tokens[i]];
      i += 1;
      if (i < n) throw new Error("trailing tokens after units");
      break;
    }
  }

  if (i < n) throw new Error(`trailing tokens: ${tokens.slice(i).join(" ")}`);
  if (total < MIN || total > MAX) {
    throw new Error(`out of range (allowed ${MIN}..${MAX})`);
  }
  return total;
}
