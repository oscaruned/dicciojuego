# AGENTS.md

## Propósito
Este repositorio contiene "Pecera de palabras", un juego web estático que carga `train.csv` y propone rondas para adivinar una palabra a partir de su definición.

## Archivos clave

- `README.md`: instrucciones de uso y reglas del juego.
- `index.html`: interfaz web y estructura principal.
- `app.js`: lógica JavaScript para cargar y filtrar el CSV, gestionar rondas, puntuación y TTS.
- `styles.css`: estilos de la versión web.
- `train.csv`: datos de entrada jugables — solo palabras con marca de España en el Wikcionario, 1.179 entradas (solo letras, longitud >= 3, sin formas verbales de verbo). Columnas: `word,definition,level` con nivel 1-5 asignado por frecuencia Zipf (wordfreq). Licencia CC BY-SA 4.0.
- `train-rae.csv`: fichero del corpus DLE/RAE (65.795 palabras) conservado pero no cargado por el juego.
- `train corto.csv`: muestra pequeña para pruebas.

## Qué debe saber un agente

1. El proyecto no tiene sistema de construcción ni dependencias de Node.js ni de Python.
2. Es una app estática que usa `PapaParse` desde CDN para parsear `train.csv`.
3. El filtrado excluye palabras que contienen espacios, dígitos o guiones.
4. `train.csv` no se puede cargar con `file://` en la mayoría de navegadores, por lo que la documentación sugiere servir la carpeta con un servidor local (`python -m http.server 8000`) o usar el selector de archivos.
5. El juego entrega la puntuación mediante TTS (speechSynthesis en `es-ES`).
6. El marcador visual de acuario vive en `pecera/` (`js/` copiado del widget original de `c:\portable\pecera` + `integracion.js`). El bootstrap demo de la pecera (`js/app.js`) se eliminó a propósito: tomaba el `#score` del juego por su `getElementById`. Puntos de enganche en `app.js`: `PECERA.run` de `updateScore` (que además evoca `setScore`, y `newGame` llama antes a `reset()`), `word()` en `showEntry` y `buyLetter`, `happy()/scared()` en `handleGuess`, y `stopIdle()`/`scared()` en `finishGame`. La API llega vía el evento DOM `aquarium-ready` (módulo ES corre tras `app.js`).
7. La animación de entrada de la pecera (clase CSS `.intro` en `#pecera-slot`, técnica FLIP con `top/left/width/height`) dura `PECERA_INTRO_MS` (5 s) al empezar cualquier partida nueva; la primera palabra queda en `STATE.pendingFirstEntry` hasta que acaba (también igual si el CSV llega tarde). Se salta con `prefers-reduced-motion`. Cambiar tamaño/orientación durante la intro la corta y la coloca directamente.
8. El layout es CSS puro: `body` en rejilla con `@media (orientation: …)`; apaisado 50 %/50 % columnas, vertical filas 50/50, cada mitad con scroll propio (`100dvh`, `overflow: hidden` en `body`).
9. Estados de interfaz por clases en `body`: `start-mode` (arranque: solo pecera a pantalla completa + barra fija `.start-bar` con «Nueva partida» y `#level-select`), `playing` (barra oculta), `game-over` (paneles del juego ocultos; queda el encabezado y la barra), `dialog-open` (instrucciones: `main` entero oculto). El juego NO arranca al cargar: espera a «Nueva partida»; la intro de la pecera (5 s) discurre al pulsarlo y la primera pregunta llega al terminar. Cambiar nivel solo define la dificultad (no inicia partida). El botón «Continuar» cierra las instrucciones.
10. Extras: «Pasapalabra» resta tantos puntos como letras tenga la palabra y salta a otra definición (`passWord`); botón 🎤 junto a la respuesta dicta por SpeechRecognition (sustituye todo el contenido del input, `setupMic`); la app intenta pantalla completa al cargar y lo reintenta con el primer gesto (`setupFullscreen`); no se informa al jugador del total de palabras cargadas (sin `#pool`, `#count` solo para errores).

## Reglas del juego (implementadas en app.js)

- Palabra oculta letra a letra; cada ronda da tantos intentos como letras tiene la palabra.
- Comprar letra: -2 puntos. Acierto: +número total de letras de la palabra (cambio de 2026-11-08 pedido por el usuario; antes era +letras − intentos). Fallo: -1 punto. Un minuto sin responder: -1 punto.
- Al resolver la ronda (acierto o agotar intentos) arranca la siguiente automáticamente.
- Niveles: básico, fácil, intermedio, difícil, muy difícil (1-5, según columna `level`), en un desplegable (`#level-select`). Cambiar de nivel inicia partida nueva desde 0; el nivel y el récord por nivel se guardan en localStorage; al recargar se restaura el nivel.
- Las instrucciones nunca se muestran automáticamente al empezar partida; solo se abren con el botón «Instrucciones del juego».
- Temporizador de ronda: 60 s con `setInterval` de 1 s; comprar letra reinicia el minuto completo; los últimos 10 s suenan pitidos ascendentes (Web Audio, `SCALE_HZ`); al llegar a 0 se dice "Menos 1 punto" (sin anunciar la puntuación) y se resetea el ciclo.
- TTS: al arrancar una ronda se dice "Palabra de N letras. Definición: ..." (sin "Nueva ronda" ni nivel); acciones como comprar letra, adivinar o el aviso de minuto interrumpen la síntesis previa (`speechSynthesis.cancel()`) para no acumular mensajes.

## Recomendaciones para cambios

- Mantener la aplicación simple: no agregar herramientas de compilación innecesarias.
- Si se ajusta `app.js`, conservar la carga automática de `train.csv` y el fallback de subida manual.
- No cambiar la lógica del filtrado ni la de la puntuación sin explicar por qué.

## Cómo ejecutar

```powershell
python -m http.server 8000
# abrir http://localhost:8000
```

## Notas

- No hay backend separado ni base de datos.
- No existe app de escritorio ni de Android; todas las interfaces adicionales fueron retiradas.
