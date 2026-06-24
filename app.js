// app.js - lógica para cargar train.csv, parsear, filtrar y mostrar una palabra por ronda
"use strict";

const STATE = {
  entries: [],
  score: 0,
  currentWord: null,
  attempts: 0,
  maxAttempts: 0,
  loadAttempted: false,
  revealCount: 0,
  roundResolved: false,
  timerId: null,
  currentEntry: null,
  timerIntervalId: null,
  revealedLetters: ''
};

const SELECTORS = {
  btnBuyLetter: '#btn-buy-letter',
  word: '#word',
  definition: '#definition',
  guessInput: '#guess-input',
  guessSubmit: '#guess-submit',
  guessFeedback: '#guess-feedback',
  attemptsInfo: '#attempts-info',
  count: '#count',
  score: '#score',
  fileInput: '#file-input',
  fallback: '.fallback'
};

function $(sel) { return document.querySelector(sel); }

function updateCount() {
  const n = STATE.entries.length;
  $(SELECTORS.count).textContent = '';
}

function updateFallbackVisibility() {
  const fallback = $(SELECTORS.fallback);
  if (!fallback) return;
  fallback.style.display = (STATE.loadAttempted && !STATE.entries.length) ? 'block' : 'none';
}

function updateScore(announce = false) {
  $(SELECTORS.score).textContent = STATE.score;
  if (announce) {
    speak(`Puntuación ${STATE.score}`);
  }
}

function updateWordDisplay() {
  const wordEl = $(SELECTORS.word);
  if (!wordEl) return;
  if (!STATE.currentWord) {
    wordEl.textContent = '—';
    return;
  }
  const letters = Array.from(STATE.currentWord);
  const visible = letters.map((letter, index) => (index < STATE.revealCount ? letter : '_')).join(' ');
  wordEl.textContent = visible;
}

function clearRoundTimer() {
  if (STATE.timerId) {
    clearTimeout(STATE.timerId);
    STATE.timerId = null;
  }
  if (STATE.timerIntervalId) {
    clearInterval(STATE.timerIntervalId);
    STATE.timerIntervalId = null;
  }
}

function showEntry(entry) {
  if (!entry) return;
  const [w, d] = entry;
  clearRoundTimer();

  STATE.currentWord = w;
  STATE.currentEntry = entry;
  STATE.attempts = 0;
  STATE.revealCount = 0;
  STATE.roundResolved = false;
  STATE.revealedLetters = '';
  const lettersCount = Array.from(w).length;
  STATE.maxAttempts = lettersCount;

  updateWordDisplay();
  $(SELECTORS.definition).textContent = d;
  $(SELECTORS.guessFeedback).textContent = `Tiene ${lettersCount} letra(s). Definición: ${d}`;
  $(SELECTORS.attemptsInfo).textContent = `Tienes ${STATE.maxAttempts} intento(s)`;
  $(SELECTORS.guessInput).value = '';
  $(SELECTORS.guessInput).disabled = false;
  $(SELECTORS.guessSubmit).disabled = false;
  $(SELECTORS.btnBuyLetter).disabled = false;
  $(SELECTORS.guessInput).focus();
  speak(`La palabra tiene ${lettersCount} letras. Definición: ${d}`);

  let elapsedMinutes = 0;
  STATE.timerIntervalId = setInterval(() => {
    if (STATE.currentWord === w && !STATE.roundResolved) {
      elapsedMinutes += 1;
      STATE.score -= 1;
      speak('Pasó un minuto sin responder. Menos 1 punto.');
      setTimeout(() => updateScore(true), 400);
    }
  }, 60000);
}

function speak(text) {
  try {
    if ('speechSynthesis' in window) {
      const u = new SpeechSynthesisUtterance(text);
      u.lang = 'es-ES';
      u.rate = 1.0;
      window.speechSynthesis.speak(u);
    }
  } catch (e) {
    console.warn('TTS no disponible:', e);
  }
}

function pickRandom() {
  if (!STATE.entries.length) return null;
  const idx = Math.floor(Math.random() * STATE.entries.length);
  return STATE.entries[idx];
}

function filterRows(rows) {
  const re = /[\s\d\-]/u;
  const out = [];
  for (const r of rows) {
    const w = (r.word || r['word'] || '').trim();
    const d = (r.definition || r['definition'] || '').trim();
    if (!w || !d) continue;
    if (re.test(w)) continue;
    out.push([w, d]);
  }
  return out;
}

function loadCsvText(text) {
  const parsed = Papa.parse(text, { header: true, skipEmptyLines: true });
  if (parsed.errors && parsed.errors.length) {
    console.warn('Errores parseo CSV:', parsed.errors.slice(0, 5));
  }
  const rows = parsed.data;
  STATE.entries = filterRows(rows);
  STATE.loadAttempted = true;
  updateCount();
  updateFallbackVisibility();
  if (!STATE.entries.length) {
    $(SELECTORS.count).textContent = 'No hay entradas válidas en el CSV.';
    return;
  }
  const firstEntry = pickRandom();
  if (firstEntry) {
    showEntry(firstEntry);
  }
}

function fetchCsv(path = 'train.csv') {
  return fetch(path)
    .then(res => {
      if (!res.ok) throw new Error('No se pudo obtener ' + path + ' (status ' + res.status + ')');
      return res.text();
    })
    .then(text => {
      loadCsvText(text);
    })
    .catch(err => {
      STATE.loadAttempted = true;
      updateFallbackVisibility();
      throw err;
    });
}

function handleFileUpload(file) {
  const reader = new FileReader();
  reader.onload = () => {
    loadCsvText(reader.result);
  };
  reader.readAsText(file, 'utf-8');
}

function normalizeForCompare(s) {
  if (!s) return '';
  return s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
}

function buyLetter() {
  if (!STATE.currentWord || STATE.roundResolved) return;
  const letters = Array.from(STATE.currentWord);
  if (STATE.revealCount >= letters.length) {
    $(SELECTORS.guessFeedback).textContent = 'Ya se han mostrado todas las letras.';
    return;
  }

  STATE.score -= 2;
  STATE.revealCount += 1;
  STATE.revealedLetters += letters[STATE.revealCount - 1];
  updateScore(true);
  updateWordDisplay();
  const revealed = letters.slice(0, STATE.revealCount).join('');
  const input = $(SELECTORS.guessInput);
  input.value = STATE.revealedLetters;
  const cursorPos = input.value.length;
  input.focus();
  input.setSelectionRange(cursorPos, cursorPos);
  $(SELECTORS.guessFeedback).textContent = `Letras reveladas: ${revealed} (-2 puntos)`;
  $(SELECTORS.attemptsInfo).textContent = `Letras reveladas: ${STATE.revealCount}/${letters.length}`;
  speak(`Se revela la letra ${revealed.slice(-1)}`);
}

function handleGuess() {
  if (!STATE.currentWord) return;
  const answer = normalizeForCompare(STATE.currentWord);
  const guess = normalizeForCompare($(SELECTORS.guessInput).value);
  if (!guess) return;

  STATE.attempts++;
  const lettersCount = Array.from(STATE.currentWord).length;
  const feedback = $(SELECTORS.guessFeedback);
  const input = $(SELECTORS.guessInput);
  const btn = $(SELECTORS.guessSubmit);
  const buyBtn = $(SELECTORS.btnBuyLetter);

  if (guess === answer) {
    const pointsEarned = lettersCount - (STATE.attempts - 1);
    STATE.score += pointsEarned;
    $(SELECTORS.word).textContent = STATE.currentWord;
    feedback.textContent = `Correcto — la palabra es "${STATE.currentWord}". +${pointsEarned} puntos`;
    speak(`Correcto. La palabra es ${STATE.currentWord}. Has ganado ${pointsEarned} puntos`);
    setTimeout(() => updateScore(true), 400);
    input.disabled = true;
    btn.disabled = true;
    buyBtn.disabled = true;
    STATE.roundResolved = true;
    clearRoundTimer();
    $(SELECTORS.attemptsInfo).textContent = '';
    setTimeout(() => {
      const nextEntry = pickRandom();
      if (nextEntry) {
        showEntry(nextEntry);
      }
    }, 2000);
  } else {
    STATE.score -= 1;
    speak('Incorrecto, menos 1 punto');
    setTimeout(() => updateScore(true), 400);
    const remainingAttempts = STATE.maxAttempts - STATE.attempts;
    if (remainingAttempts > 0) {
      feedback.textContent = `No es correcto. Inténtalo otra vez. -1 punto`;
      $(SELECTORS.attemptsInfo).textContent = `Te quedan ${remainingAttempts} intento(s)`;
      input.value = '';
      input.focus();
    } else {
      feedback.textContent = `Fallaste. La palabra era: ${STATE.currentWord}. -1 punto`;
      $(SELECTORS.word).textContent = STATE.currentWord;
      speak(`Fallaste. La palabra era ${STATE.currentWord}.`);
      input.disabled = true;
      btn.disabled = true;
      buyBtn.disabled = true;
      STATE.roundResolved = true;
      clearRoundTimer();
      $(SELECTORS.attemptsInfo).textContent = '';
      setTimeout(() => {
        const nextEntry = pickRandom();
        if (nextEntry) {
          showEntry(nextEntry);
        }
      }, 2000);
    }
  }
}

function init() {
  updateScore();
  updateFallbackVisibility();

  $(SELECTORS.guessInput).disabled = true;
  $(SELECTORS.guessSubmit).disabled = true;
  $(SELECTORS.btnBuyLetter).disabled = true;

  fetchCsv('train.csv').catch(err => {
    console.warn('No se pudo cargar train.csv por fetch:', err);
    $(SELECTORS.count).textContent = 'No se cargó train.csv automáticamente; por favor sube el archivo.';
    STATE.entries = [];
    updateFallbackVisibility();
  });

  $(SELECTORS.btnBuyLetter).addEventListener('click', buyLetter);

  $(SELECTORS.fileInput).addEventListener('change', (ev) => {
    const f = ev.target.files && ev.target.files[0];
    if (!f) return;
    handleFileUpload(f);
  });

  const guessBtn = $(SELECTORS.guessSubmit);
  const guessInput = $(SELECTORS.guessInput);

  if (guessBtn && guessInput) {
    guessBtn.addEventListener('click', handleGuess);
    guessInput.addEventListener('keydown', (ev) => {
      if (ev.key === 'Enter') {
        ev.preventDefault();
        handleGuess();
      }
    });
  }
}

document.addEventListener('DOMContentLoaded', init);
