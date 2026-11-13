// app.js - Pecera de palabras
// Lógica del juego: carga del CSV (word, definition, level), niveles de
// dificultad con desplegable, partidas con puntuación propia y récord por nivel.
"use strict";

const LEVEL_NAMES = {
  1: "básico",
  2: "fácil",
  3: "intermedio",
  4: "difícil",
  5: "muy difícil",
};

const MIN_SCORE_END = -20; // la partida termina automáticamente al llegar a este puntaje
const ROUND_SECONDS = 60;  // duración del temporizador de ronda
const WARNING_SECONDS = 10; // últimos segundos: pitidos en escala ascendente

// notas aproximadas de la escala ascendente para los avisos sonoros
const SCALE_HZ = [523, 587, 659, 698, 784, 880, 988, 1046, 1108, 1174];

const STATE = {
  entries: [],           // [word, definition, level]
  level: 1,              // nivel del jugador (persistente)
  score: 0,              // puntuación de la partida en curso
  records: {},           // mejor puntuación por nivel (persistente)
  loadAttempted: false,
  gameActive: false,
  currentWord: null,
  currentEntry: null,
  attempts: 0,
  maxAttempts: 0,
  revealCount: 0,
  revealedLetters: "",
  roundResolved: true,
  timerIntervalId: null,
  secondsLeft: ROUND_SECONDS,
  pendingFirstEntry: null, // primera ronda en espera mientras entra la pecera
};

const PECERA_INTRO_MS = 5000; // duración de la animación de entrada de la pecera

const SELECTORS = {
  btnBuyLetter: "#btn-buy-letter",
  btnPass: "#btn-pass",
  btnFinish: "#btn-finish",
  btnInstructions: "#btn-instructions",
  levelSelect: "#level-select",
  word: "#word",
  definition: "#definition",
  guessInput: "#guess-input",
  guessSubmit: "#guess-submit",
  guessFeedback: "#guess-feedback",
  attemptsInfo: "#attempts-info",
  count: "#count",
  score: "#score",
  best: "#best",
  peceraSlot: "#pecera-slot",
  peceraScore: "#pecera-score",
  fileInput: "#file-input",
  fallback: ".fallback",
  overlayInstructions: "#overlay-instructions",
  overlayResult: "#overlay-result",
  btnCloseInstructions: "#btn-close-instructions",
  btnNewGame: "#btn-new-game",
  resultBody: "#result-body",
};

function $(sel) { return document.querySelector(sel); }

// ---------- pecera (marcador visual de acuario) ----------
// La API la publica pecera/integracion.js (módulo ES) con el evento
// 'aquarium-ready'. Hasta entonces, las llamadas quedan en cola y se aplican
// en el mismo orden en que se pidieron. Si no hay hueco de pecera, todo es no-op.
const PECERA = {
  api: null,
  pending: [],
  run(fn) {
    if (!document.getElementById("aquarium-root")) return;
    if (this.api) fn(this.api);
    else this.pending.push(fn);
  },
  receive() {
    this.api = window.aquarium;
    const queued = this.pending;
    this.pending = [];
    queued.forEach((fn) => fn(this.api));
  },
};
document.addEventListener("aquarium-ready", () => PECERA.receive());


// ---------- almacenamiento local ----------
const LS_LEVEL = "pecera.level";
const LS_RECORDS = "pecera.records";
const LS_NARRATION = "pecera.narracion"; // "voz" = TTS de la app | "lector" = TalkBack/VoiceOver vía aria-live

function lsGet(key, fallback) {
  try {
    const v = localStorage.getItem(key);
    return v === null ? fallback : v;
  } catch (e) {
    return fallback;
  }
}
function lsSet(key, value) {
  try { localStorage.setItem(key, value); } catch (e) { /* sin storage: no-op */ }
}

function loadRecords() {
  try { return JSON.parse(lsGet(LS_RECORDS, "{}")) || {}; }
  catch (e) { return {}; }
}
function bestForLevel(level) {
  return Number(STATE.records[level] || 0);
}
function saveRecords() {
  lsSet(LS_RECORDS, JSON.stringify(STATE.records));
}

// ---------- voz y sonido ----------
// Modo "voz": la app habla con speechSynthesis (normal sin lector de pantalla).
// Modo "lector": no se usa el TTS de la app (TalkBack lo tapa y lo mata al
// compartir el mismo motor de Android); los avisos van a una región aria-live
// y los pronuncia el lector de pantalla con su propia voz.
function narrationMode() {
  return lsGet(LS_NARRATION, "voz") === "lector" ? "lector" : "voz";
}

function announce(text) {
  const el = document.getElementById("sr-announcer");
  if (!el) return;
  // técnica estándar: vaciar y rellenar después para que TalkBack
  // registre el cambio de la región viva
  el.textContent = "";
  window.setTimeout(() => { el.textContent = text; }, 40);
}

function speak(text, interrupt = false) {
  try {
    if (narrationMode() === "lector") {
      announce(text);
      return;
    }
    if ("speechSynthesis" in window) {
      const synth = window.speechSynthesis;
      if (interrupt) synth.cancel();
      if (synth.paused) synth.resume(); // Chrome lo deja pausado al volver de segundo plano
      const u = new SpeechSynthesisUtterance(text);
      u.lang = "es-ES";
      u.rate = 1.0;
      synth.speak(u);
    }
  } catch (e) {
    console.warn("TTS no disponible:", e);
  }
}

// Chrome/Android exigen que la síntesis se «desbloquee» dentro del gesto del
// usuario; en la primera palabra tras cargar la página podía quedar muda.
function unlockTTS() {
  try {
    if (!("speechSynthesis" in window)) return;
    const synth = window.speechSynthesis;
    const u = new SpeechSynthesisUtterance(" ");
    u.volume = 0; // inaudible: solo activa el motor
    synth.cancel();
    synth.speak(u);
    synth.cancel();
    if (synth.paused) synth.resume();
  } catch (e) { /* sin TTS: sin efecto */ }
}

function beep(freq, duration = 0.14) {
  try {
    beep.ctx = beep.ctx || new (window.AudioContext || window.webkitAudioContext)();
    const osc = beep.ctx.createOscillator();
    const gain = beep.ctx.createGain();
    osc.type = "sine";
    osc.frequency.value = freq;
    gain.gain.value = 0.12;
    osc.connect(gain);
    gain.connect(beep.ctx.destination);
    osc.start();
    osc.stop(beep.ctx.currentTime + duration);
  } catch (e) {
    console.warn("Audio no disponible:", e);
  }
}

// ---------- interfaz: marcadores ----------
function updateScore(announce = false) {
  $(SELECTORS.score).textContent = STATE.score;
  const peceraScore = $(SELECTORS.peceraScore);
  if (peceraScore) peceraScore.textContent = STATE.score;
  // el agua, el pez y los hitos de la pecera siguen la puntuación del juego
  PECERA.run((aq) => aq.setScore(STATE.score));
  if (announce) speak(`Puntuación ${STATE.score}`);
  checkGameOver();
}

// tras cada variación de puntuación se dicta el total ("Tienes X", sin
// repetir "puntos": ya lo dijo el mensaje anterior); se encola después del
// mensaje que la provocó, sin interrumpirlo
function speakScore() {
  speak(`Tienes ${STATE.score}`);
}

function updateBest() {
  $(SELECTORS.best).textContent = bestForLevel(STATE.level);
}

function updateFallbackVisibility() {
  const fallback = $(SELECTORS.fallback);
  if (!fallback) return;
  fallback.style.display =
    (STATE.loadAttempted && !STATE.entries.length) ? "block" : "none";
}

// ---------- interfaz: palabra ----------
function updateWordDisplay() {
  const wordEl = $(SELECTORS.word);
  if (!wordEl) return;
  if (!STATE.currentWord) {
    wordEl.textContent = "—";
    return;
  }
  const letters = Array.from(STATE.currentWord);
  const visible = letters
    .map((letter, index) => (index < STATE.revealCount ? letter : "_"))
    .join(" ");
  wordEl.textContent = visible;
}

function setControlsEnabled(buy, guess, finish) {
  $(SELECTORS.btnBuyLetter).disabled = !buy;
  $(SELECTORS.btnPass).disabled = !buy;
  $(SELECTORS.guessInput).disabled = !guess;
  $(SELECTORS.guessSubmit).disabled = !guess;
  $(SELECTORS.btnFinish).disabled = !finish;
}

// ---------- temporizador de ronda ----------
// Cuenta atrás de ROUND_SECONDS segundos. En los últimos WARNING_SECONDS
// segundos suenan pitidos en escala ascendente; al llegar a 0 se resta un
// punto ("Menos 1 punto") y el ciclo vuelve a empezar. Comprar letra reinicia
// la cuenta.
function clearRoundTimer() {
  if (STATE.timerIntervalId) {
    clearInterval(STATE.timerIntervalId);
    STATE.timerIntervalId = null;
  }
}

function startCountdown() {
  clearRoundTimer();
  STATE.timerIntervalId = setInterval(() => {
    if (!STATE.currentWord || STATE.roundResolved || !STATE.gameActive) return;
    STATE.secondsLeft -= 1;
    if (STATE.secondsLeft > 0 && STATE.secondsLeft <= WARNING_SECONDS) {
      const idx = Math.min(SCALE_HZ.length - 1, WARNING_SECONDS - STATE.secondsLeft);
      beep(SCALE_HZ[idx]);
    }
    if (STATE.secondsLeft <= 0) {
      STATE.score -= 1;
      speak("Menos 1 punto", true);
      updateScore();
      speakScore();
      STATE.secondsLeft = ROUND_SECONDS;
    }
  }, 1000);
}

function pauseTimer() { clearRoundTimer(); }

function resumeTimer() {
  if (STATE.gameActive && !STATE.roundResolved && STATE.currentWord) {
    startCountdown();
  }
}

function resetCountdown() {
  STATE.secondsLeft = ROUND_SECONDS;
  resumeTimer(); // reinicia el ciclo completo del minuto
}

// ---------- animación de entrada de la pecera ----------
// Al empezar una partida nueva la pecera parte cubriendo toda la ventana
// (clase .intro, position fixed) y durante PECERA_INTRO_MS se redimensiona
// hasta su hueco en la rejilla, dejando ver poco a poco la ventana del juego.
// La primera pregunta solo arranca cuando la animación ha terminado.

function aquariumIntroAvailable() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return false; // sin animación si el usuario la evita
  return !!document.getElementById(SELECTORS.peceraSlot.slice(1));
}

function setSlotRect(slot, x, y, w, h) {
  slot.style.left = `${x}px`;
  slot.style.top = `${y}px`;
  slot.style.width = `${w}px`;
  slot.style.height = `${h}px`;
}

function startAquariumIntro(onDone) {
  const slot = $(SELECTORS.peceraSlot);
  if (!slot || !aquariumIntroAvailable()) {
    onDone();
    return;
  }

  const rect = slot.getBoundingClientRect(); // hueco final de la pecera en la rejilla
  let finished = false;
  const finish = () => {
    if (finished) return;
    finished = true;
    window.removeEventListener("resize", finish);
    slot.classList.remove("intro");
    slot.style.left = slot.style.top = slot.style.width = slot.style.height = "";
    const pending = STATE.pendingFirstEntry;
    STATE.pendingFirstEntry = null;
    onDone();
    if (pending) showEntry(pending);
  };

  slot.classList.add("intro");
  // estado inicial: ocupa toda la ventana visible
  setSlotRect(slot, 0, 0, window.innerWidth, window.innerHeight);
  slot.style.transition = "none"; // el salto inicial sin transición
  void slot.offsetWidth;          // fijar el estado inicial con un reflow
  slot.style.transition = "";     // restaurar la transición de 5 s de .intro
  // estado final: su hueco en la rejilla
  setSlotRect(slot, rect.left, rect.top, rect.width, rect.height);

  slot.addEventListener("transitionend", finish, { once: true });
  setTimeout(finish, PECERA_INTRO_MS + 300); // red de seguridad si transitionend no llega
  window.addEventListener("resize", finish); // cambio de tamaño/orientación: ir directo al final
}

// Lanza la primera ronda de una partida, en cola si la pecera está entrando.
function showFirstEntry(entry) {
  if (!entry) return;
  const slot = $(SELECTORS.peceraSlot);
  if (slot && slot.classList.contains("intro")) {
    STATE.pendingFirstEntry = entry;
    return;
  }
  showEntry(entry);
}

// ---------- rondas ----------
function pickRandom() {
  const pool = STATE.entries.filter((e) => e[2] === STATE.level);
  if (!pool.length) return null;
  return pool[Math.floor(Math.random() * pool.length)];
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
  STATE.revealedLetters = "";
  STATE.secondsLeft = ROUND_SECONDS;
  const lettersCount = Array.from(w).length;
  STATE.maxAttempts = lettersCount;

  updateWordDisplay();
  $(SELECTORS.definition).textContent = d;
  $(SELECTORS.guessFeedback).textContent =
    `Tiene ${lettersCount} letra(s). Definición: ${d}`;
  $(SELECTORS.attemptsInfo).textContent = `Tienes ${STATE.maxAttempts} intento(s)`;
  $(SELECTORS.guessInput).value = "";
  setControlsEnabled(true, true, true);
  // sin autofocus: el teclado solo se abre si el usuario toca el campo
  // (en Android abría el teclado y aplastaba la pecera)
  speak(`Palabra de ${lettersCount} letras. Definición: ${d}`);

  // cada ronda nueva pone a cero el reloj de inactividad de la pecera
  PECERA.run((aq) => aq.word());
  startCountdown();
}

function showNoWords() {
  STATE.roundResolved = true;
  clearRoundTimer();
  setControlsEnabled(false, false, STATE.gameActive);
  $(SELECTORS.guessFeedback).textContent =
    "No hay palabras para este nivel. Elige otro nivel o sube otro CSV.";
}

// ---------- partidas ----------
function newGame(announce = true) {
  clearRoundTimer();
  STATE.score = 0;
  STATE.gameActive = true;
  STATE.roundResolved = true;
  STATE.currentWord = null;
  STATE.currentEntry = null;
  STATE.revealCount = 0;
  STATE.revealedLetters = "";
  updateScore();
  updateBest();
  setControlsEnabled(false, false, true);
  if (announce) speak(`Partida nueva en nivel ${LEVEL_NAMES[STATE.level]}`, true);
  $(SELECTORS.word).textContent = "—";
  $(SELECTORS.definition).textContent = "";
  $(SELECTORS.guessFeedback).textContent = `Nivel ${LEVEL_NAMES[STATE.level]}: prepárate…`;
  $(SELECTORS.attemptsInfo).textContent = "";

  // nueva partida: agua al 40 %, pez vivo, sonido de fondo otra vez y,
  // si procede, animación de entrada
  PECERA.run((aq) => {
    aq.reset();
    if (aq.audio && aq.audio.setMuted) aq.audio.setMuted(false);
  });

  const first = pickRandom();
  if (first) {
    // la pecera entra (5 s a pantalla completa encogiéndose a su hueco) y la
    // primera pregunta arranca al terminar; sin pecera es inmediato
    startAquariumIntro(() => showEntry(first));
  } else {
    showNoWords();
  }
}

function resolveRound() {
  // cierra la ronda en pantalla y encadena la siguiente
  STATE.roundResolved = true;
  clearRoundTimer();
  setControlsEnabled(false, false, true);
  setTimeout(() => {
    if (!STATE.gameActive) return;
    const next = pickRandom();
    if (next) showEntry(next);
  }, 2000);
}

function checkGameOver() {
  if (STATE.gameActive && STATE.score <= MIN_SCORE_END) {
    finishGame(true);
  }
}

function finishGame(auto) {
  if (!STATE.gameActive) return;
  STATE.gameActive = false;
  STATE.roundResolved = true;
  // parar en seco el contador de minuto y dejarlo a cero
  clearRoundTimer();
  STATE.secondsLeft = ROUND_SECONDS;
  setControlsEnabled(false, false, false);
  document.body.classList.remove("playing");
  document.body.classList.add("game-over");
  // la pecera para su reloj de inactividad y su sonido de fondo; si la
  // partida la cierra el jugador (y no la muerte por −20) el pez se asusta
  // pero no muere
  PECERA.run((aq) => {
    if (aq.stopIdle) aq.stopIdle();
    if (!auto && aq.scared) aq.scared();
    // en muerte automática el sonido se silencia al mostrar el resumen, para
    // que la escena de la muerte suene mientras dura
    if (!auto && aq.audio && aq.audio.setMuted) aq.audio.setMuted(true);
  });

  const finalScore = STATE.score;
  const levelName = LEVEL_NAMES[STATE.level];
  const best = bestForLevel(STATE.level);
  const isRecord = finalScore > best;
  if (isRecord) {
    STATE.records[STATE.level] = finalScore;
    saveRecords();
    updateBest();
  }

  const title = auto ? "Partida terminada automáticamente" : "Partida finalizada";
  const recordText = isRecord
    ? `¡Nuevo récord del nivel ${levelName}!`
    : `Récord del nivel ${levelName}: ${Math.max(best, 0)}`;
  $(SELECTORS.resultBody).innerHTML =
    `<p>Puntuación de esta partida: <strong>${finalScore}</strong></p>` +
    `<p>${recordText}</p>` +
    (isRecord
      ? `<p class="new-record">Queda guardado como tu mejor resultado.</p>`
      : `<p>El resultado de esta partida se descarta.</p>`);

  speak(
    auto
      ? `Partida terminada por puntos negativos. Has conseguido ${finalScore} puntos. ${isRecord ? `¡Nuevo récord del nivel ${levelName}!` : recordText}`
      : `Has finalizado la partida con ${finalScore} puntos. ${isRecord ? `¡Nuevo récord del nivel ${levelName}!` : recordText}`,
    true
  );

  $(SELECTORS.word).textContent = "—";
  $(SELECTORS.guessFeedback).textContent = "";
  $(SELECTORS.attemptsInfo).textContent = "";

  if (auto) {
    // muerte por −20: dejar ver cómo muere el pez; el resumen se muestra
    // cuando la pecera avisa del fin de su animación (unos 3,4 s), con
    // temporizador de respaldo si la API no está disponible
    let shown = false;
    let aqForMute = null;
    const show = () => {
      if (shown) return;
      shown = true;
      if (aqForMute && aqForMute.audio && aqForMute.audio.setMuted) aqForMute.audio.setMuted(true);
      $(SELECTORS.overlayResult).classList.remove("hidden");
      mountStartBar(true);
    };
    clearTimeout(STATE.resultDelayTimer);
    STATE.resultDelayTimer = setTimeout(show, 4500); // respaldo
    PECERA.run((aq) => {
      aqForMute = aq;
      if (aq.onGameover) aq.onGameover(show);
    });
  } else {
    $(SELECTORS.overlayResult).classList.remove("hidden");
    mountStartBar(true); // «Nueva partida» + nivel, dentro del diálogo del resumen
  }
}

// ---------- pasapalabra ----------
// Pasa a otra definición pagando tantos puntos como letras tenga la palabra
// pedida (el fallo de la palabra no penaliza intentos adicionales).
function passWord() {
  if (!STATE.currentWord || STATE.roundResolved) return;
  const lettersCount = Array.from(STATE.currentWord).length;
  STATE.score -= lettersCount;
  STATE.roundResolved = true;
  clearRoundTimer();
  STATE.secondsLeft = ROUND_SECONDS;
  updateScore();
  $(SELECTORS.word).textContent = STATE.currentWord;
  $(SELECTORS.guessFeedback).textContent =
    `Pasapalabra: la palabra era "${STATE.currentWord}". -${lettersCount} puntos`;
  $(SELECTORS.guessInput).disabled = true;
  $(SELECTORS.guessSubmit).disabled = true;
  $(SELECTORS.attemptsInfo).textContent = "";
  speak(`Pasapalabra. La palabra era ${STATE.currentWord}. Menos ${lettersCount} puntos`, true);
  speakScore();
  resolveRound();
}

// ---------- dictado por voz (micrófono) ----------
// Reconocimiento de voz del navegador (Chrome/Edge/Safari): lo pronunciado
// sustituye por completo el contenido del cuadro de respuesta.
function setupMic() {
  const btn = document.getElementById("btn-mic");
  if (!btn) return;
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    btn.disabled = true;
    btn.title = "Reconocimiento de voz no disponible en este navegador";
    return;
  }
  btn.addEventListener("click", () => {
    const input = $(SELECTORS.guessInput);
    if (input.disabled) return;
    try {
      const rec = new SR();
      rec.lang = "es-ES";
      rec.interimResults = false;
      rec.maxAlternatives = 1;
      STATE.micRecognition = rec; // evitar que el navegador lo recoja
      btn.textContent = "…";
      btn.disabled = true;
      const restore = () => {
        btn.textContent = "🎤";
        btn.disabled = $(SELECTORS.guessInput).disabled;
      };
      rec.onresult = (ev) => {
        const said = (ev.results[0][0].transcript || "").trim();
        if (said) {
          input.value = said; // sustituye por completo lo que hubiera
          handleGuess(); // envío automático: lo dictado se comprueba al instante
        }
      };
      rec.onerror = (ev) => {
        if (ev.error === "not-allowed") {
          $(SELECTORS.guessFeedback).textContent = "Micrófono no permitido.";
        }
      };
      rec.onend = restore;
      rec.start();
      speak("Escuchando", true);
    } catch (e) {
      console.warn("Reconocimiento de voz no disponible:", e);
      btn.textContent = "🎤";
    }
  });
}

// ---------- pantalla completa ----------
// La app intenta arrancar a pantalla completa; si el navegador lo exige con
// un gesto del usuario, se pide con el primer toque/click.
function requestFullscreen() {
  const el = document.documentElement;
  const fn = el.requestFullscreen || el.webkitRequestFullscreen;
  if (!fn) return;
  try {
    const p = fn.call(el);
    if (p && p.catch) p.catch(() => { /* sin gesto: se reintentará */ });
  } catch (e) { /* sin gesto: se reintentará */ }
}

function setupFullscreen() {
  requestFullscreen();
  const retry = () => {
    window.removeEventListener("pointerdown", retry);
    if (!document.fullscreenElement && !document.webkitFullscreenElement) {
      requestFullscreen();
    }
  };
  window.addEventListener("pointerdown", retry, { once: true });
  // primer gesto: desbloquear también la síntesis de voz
  window.addEventListener("pointerdown", unlockTTS, { once: true });
}

// ---------- acciones del juego ----------
function buyLetter() {
  if (!STATE.currentWord || STATE.roundResolved) return;
  const letters = Array.from(STATE.currentWord);
  if (STATE.revealCount >= letters.length) {
    $(SELECTORS.guessFeedback).textContent = "Ya se han mostrado todas las letras.";
    return;
  }

  STATE.score -= 2;
  STATE.revealCount += 1;
  STATE.revealedLetters += letters[STATE.revealCount - 1];
  updateScore();
  updateWordDisplay();
  const revealed = letters.slice(0, STATE.revealCount).join("");

  const input = $(SELECTORS.guessInput);
  input.disabled = false;
  input.value = STATE.revealedLetters;
  // sin autofocus: no se abre el teclado al comprar letra
  $(SELECTORS.guessFeedback).textContent =
    `Letras reveladas: ${revealed} (-2 puntos)`;
  $(SELECTORS.attemptsInfo).textContent =
    `Letras reveladas: ${STATE.revealCount}/${letters.length}`;

  // la letra comprada devuelve el minuto completo
  resetCountdown();
  // y el reloj de la pecera vuelve también a cero (el tiempo lo gobierna el juego)
  PECERA.run((aq) => aq.word());

  // "Letra X" y, tras una pausa, todas las letras reveladas hasta ahora
  speak(`Letra ${revealed.slice(-1)}`, true);
  speakScore(); // "Tienes X" en cola tras el aviso de la letra
  setTimeout(() => {
    speak(`Letras reveladas: ${STATE.revealedLetters.split("").join(", ")}`, true);
  }, 700);
}

function normalizeForCompare(s) {
  if (!s) return "";
  return s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
}

function handleGuess() {
  if (!STATE.currentWord || STATE.roundResolved) return;
  const answer = normalizeForCompare(STATE.currentWord);
  const guess = normalizeForCompare($(SELECTORS.guessInput).value);
  if (!guess) return;

  STATE.attempts++;
  const lettersCount = Array.from(STATE.currentWord).length;
  const feedback = $(SELECTORS.guessFeedback);
  const input = $(SELECTORS.guessInput);

  if (guess === answer) {
    // acertar suma el número total de letras de la palabra
    const pointsEarned = lettersCount;
    STATE.score += pointsEarned;
    $(SELECTORS.word).textContent = STATE.currentWord;
    feedback.textContent =
      `Correcto — la palabra es "${STATE.currentWord}". +${pointsEarned} puntos`;
    input.disabled = true;
    $(SELECTORS.guessSubmit).disabled = true;
    input.blur(); // recoger el teclado al terminar la ronda
    STATE.roundResolved = true;
    clearRoundTimer();
    updateScore();
    // reacción del pez: acertar lo alegra (los deltas del juego son pequeños
    // para las reacciones automáticas de la pecera, que exigen ±5)
    PECERA.run((aq) => aq.happy());
    $(SELECTORS.attemptsInfo).textContent = "";
    resolveRound();
    speak(
      `Correcto. La palabra es ${STATE.currentWord}. Has ganado ${pointsEarned} puntos`,
      true
    );
    speakScore();
  } else {
    STATE.score -= 1;
    speak("Incorrecto, menos 1 punto", true);
    updateScore();
    speakScore();
    PECERA.run((aq) => aq.scared());
    const remainingAttempts = STATE.maxAttempts - STATE.attempts;
    if (remainingAttempts > 0 && STATE.gameActive) {
      feedback.textContent = "No es correcto. Inténtalo otra vez. -1 punto";
      $(SELECTORS.attemptsInfo).textContent = `Te quedan ${remainingAttempts} intento(s)`;
      // se conservan las letras compradas hasta ahora en el cuadro de edición
      input.value = STATE.revealedLetters;
      input.disabled = false;
      input.blur(); // recoger el teclado tras cada envío (TalkBack/Android)
    } else {
      feedback.textContent =
        `Fallaste. La palabra era: ${STATE.currentWord}. -1 punto`;
      $(SELECTORS.word).textContent = STATE.currentWord;
      speak(`Fallaste. La palabra era ${STATE.currentWord}.`, true);
      input.disabled = true;
      $(SELECTORS.guessSubmit).disabled = true;
      input.blur(); // recoger el teclado al terminar la ronda
      STATE.roundResolved = true;
      clearRoundTimer();
      updateScore();
      speakScore();
      $(SELECTORS.attemptsInfo).textContent = "";
      resolveRound();
    }
  }
}

// ---------- niveles ----------
// Elegir nivel solo define la dificultad (se guarda); la partida nueva
// arranca con el botón «Nueva partida» de la barra inferior.
function selectLevel(n) {
  STATE.level = n;
  lsSet(LS_LEVEL, String(n));
  $(SELECTORS.levelSelect).value = String(n);
  updateBest();
}

// ---------- arranque de partida desde la barra ----------
// En móvil, una barra fija puede quedar tapada por el teclado o el diálogo;
// por eso, en el fin de partida la barra se traslada DENTRO del diálogo.
function mountStartBar(inDialog) {
  const bar = document.getElementById("start-bar");
  const dlg = document.querySelector("#overlay-result .dialog");
  if (!bar || !dlg) return;
  if (inDialog && bar.parentElement !== dlg) dlg.appendChild(bar);
  else if (!inDialog && bar.parentElement === dlg) document.body.appendChild(bar);
}

function launchGame() {
  unlockTTS(); // la voz necesita el gesto del usuario para activarse
  hideOverlay(SELECTORS.overlayResult);
  mountStartBar(false);
  document.body.classList.remove("start-mode", "game-over");
  document.body.classList.add("playing");
  newGame(true);
}

// ---------- overlays ----------
function hideOverlay(sel) {
  $(sel).classList.add("hidden");
}

function openInstructions() {
  $(SELECTORS.overlayInstructions).classList.remove("hidden");
  document.body.classList.add("dialog-open"); // la columna del juego desaparece
  if (STATE.gameActive && !STATE.roundResolved) pauseTimer();
}

function closeInstructions() {
  hideOverlay(SELECTORS.overlayInstructions);
  document.body.classList.remove("dialog-open");
  if (STATE.gameActive) resumeTimer(); // nunca se muestran solas al empezar una partida
}

// ---------- datos ----------
function filterRows(rows) {
  const re = /[\s\d\-]/u;
  const out = [];
  for (const r of rows) {
    const w = ((r.word || r["word"] || "") + "").trim();
    const d = ((r.definition || r["definition"] || "") + "").trim();
    let lvl = parseInt(r.level, 10);
    if (!lvl || lvl < 1 || lvl > 5) lvl = 5;
    if (!w || !d) continue;
    if (re.test(w)) continue;
    out.push([w, d, lvl]);
  }
  return out;
}

function loadCsvText(text) {
  const parsed = Papa.parse(text, { header: true, skipEmptyLines: true });
  if (parsed.errors && parsed.errors.length) {
    console.warn("Errores parseo CSV:", parsed.errors.slice(0, 5));
  }
  STATE.entries = filterRows(parsed.data);
  STATE.loadAttempted = true;
  updateFallbackVisibility();

  if (!STATE.entries.length) {
    $(SELECTORS.count).textContent = "No hay entradas válidas en el CSV.";
    updateFallbackVisibility();
    return;
  }
  $(SELECTORS.count).textContent = ""; // no se informa del total cargado

  // si todavía no hay ronda activa (por ejemplo tras recargar), arrancamos;
  // si la pecera sigue en su animación de entrada, la ronda queda en cola
  if (!STATE.currentWord && STATE.roundResolved && STATE.gameActive) {
    showFirstEntry(pickRandom());
  }
}

function fetchCsv(path = "train.csv") {
  return fetch(path)
    .then((res) => {
      if (!res.ok) throw new Error(`No se pudo obtener ${path} (status ${res.status})`);
      return res.text();
    })
    .then((text) => {
      loadCsvText(text);
    })
    .catch((err) => {
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
  reader.readAsText(file, "utf-8");
}

// ---------- arranque ----------
function init() {
  STATE.records = loadRecords();
  let lvl = parseInt(lsGet(LS_LEVEL, "1"), 10);
  if (!lvl || lvl < 1 || lvl > 5) lvl = 1;
  STATE.level = lvl;

  updateScore();
  updateBest();
  updateFallbackVisibility();
  setControlsEnabled(false, false, false);
  $(SELECTORS.levelSelect).value = String(STATE.level);
  $(SELECTORS.levelSelect).addEventListener("change", (ev) => {
    selectLevel(Number(ev.target.value));
  });

  $(SELECTORS.btnBuyLetter).addEventListener("click", buyLetter);
  $(SELECTORS.btnPass).addEventListener("click", passWord);
  $(SELECTORS.btnFinish).addEventListener("click", () => finishGame(false));
  $(SELECTORS.btnInstructions).addEventListener("click", openInstructions);
  $(SELECTORS.btnCloseInstructions).addEventListener("click", closeInstructions);

  // conmutador de narración: voz de la app o lector de pantalla (TalkBack)
  const btnNarration = document.getElementById("btn-narration");
  const setNarrationLabel = () => {
    btnNarration.textContent = narrationMode() === "lector"
      ? "Narración: lector de pantalla"
      : "Narración: voz de la app";
  };
  setNarrationLabel();
  btnNarration.addEventListener("click", () => {
    const nuevo = narrationMode() === "lector" ? "voz" : "lector";
    lsSet(LS_NARRATION, nuevo);
    if (nuevo === "voz") {
      try { window.speechSynthesis && window.speechSynthesis.cancel(); } catch (e) { /* noop */ }
    }
    setNarrationLabel();
    // feedback por el canal activo
    speak(nuevo === "lector"
      ? "Modo lector de pantalla activado. Los avisos los dirá tu lector."
      : "Modo voz de la app activado.");
  });
  $(SELECTORS.btnNewGame).addEventListener("click", launchGame);

  setupMic();
  setupFullscreen();

  $(SELECTORS.fileInput).addEventListener("change", (ev) => {
    const f = ev.target.files && ev.target.files[0];
    if (!f) return;
    handleFileUpload(f);
  });

  const guessBtn = $(SELECTORS.guessSubmit);
  const guessInput = $(SELECTORS.guessInput);
  if (guessBtn && guessInput) {
    guessBtn.addEventListener("click", handleGuess);
    guessInput.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        handleGuess();
      }
    });
  }

  fetchCsv("train.csv").catch((err) => {
    console.warn("No se pudo cargar train.csv por fetch:", err);
    $(SELECTORS.count).textContent =
      "No se cargó train.csv automáticamente; por favor sube el archivo.";
    STATE.entries = [];
    updateFallbackVisibility();
  });

  // las instrucciones nunca se muestran automáticamente; solo con el botón.
  // El juego no arranca solo: espera a «Nueva partida» en la barra inferior.
}

document.addEventListener("DOMContentLoaded", init);
