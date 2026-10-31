import { numberToWords, wordsToNumber } from "./convert.js";

const EXAMPLES = [
  { number: "0", words: "bial" },
  { number: "42", words: "sawmli pahnih" },
  { number: "115", words: "za sawmpanga" },
  { number: "1000", words: "sangkhat" },
  { number: "1000000", words: "maktaduai" },
];

const numberInput = document.getElementById("number-input");
const wordsInput = document.getElementById("words-input");
const wordsResult = document.getElementById("words-result");
const wordsError = document.getElementById("words-error");
const numberResult = document.getElementById("number-result");
const numberError = document.getElementById("number-error");
const examplesEl = document.getElementById("examples");

function updateNumberToWords() {
  const raw = numberInput.value;
  if (!raw.trim()) {
    wordsResult.textContent = "";
    wordsError.hidden = true;
    return;
  }
  try {
    wordsResult.textContent = numberToWords(raw);
    wordsError.hidden = true;
  } catch (err) {
    wordsResult.textContent = "";
    wordsError.textContent = err.message;
    wordsError.hidden = false;
  }
}

function updateWordsToNumber() {
  const raw = wordsInput.value;
  if (!raw.trim()) {
    numberResult.textContent = "";
    numberError.hidden = true;
    return;
  }
  try {
    numberResult.textContent = String(wordsToNumber(raw));
    numberError.hidden = true;
  } catch (err) {
    numberResult.textContent = "";
    numberError.textContent = err.message;
    numberError.hidden = false;
  }
}

numberInput.addEventListener("input", updateNumberToWords);
wordsInput.addEventListener("input", updateWordsToNumber);

for (const ex of EXAMPLES) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.textContent = ex.number;
  btn.addEventListener("click", () => {
    numberInput.value = ex.number;
    wordsInput.value = ex.words;
    updateNumberToWords();
    updateWordsToNumber();
  });
  examplesEl.appendChild(btn);
}

updateNumberToWords();
updateWordsToNumber();
