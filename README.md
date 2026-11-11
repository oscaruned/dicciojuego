# Pecera de palabras

Juego web en HTML/JavaScript que carga `train.csv` (palabras y definiciones en español) y propone rondas para adivinar palabras.

## Cómo se juega

- Se muestra una palabra oculta (`_ _ _`) junto a su definición, con una fila de guiones por cada letra.
- Cada ronda da tantos intentos como letras tiene la palabra:
  - **Comprar letra**: revela la siguiente letra aún oculta (-2 puntos).
  - **Adivinar**: acertar suma el **número total de letras** de la palabra (p. ej. +7 puntos por una palabra de 7 letras); fallar resta 1 punto.
  - Pasar 1 minuto sin responder resta 1 punto.
- Al acertar (o agotar los intentos) pasa automáticamente a la siguiente ronda.

## Niveles y partidas

- Cinco niveles por frecuencia de uso (escala Zipf de wordfreq): **básico, fácil, intermedio, difícil y muy difícil** (columna `level` de `train.csv`), elegidos en un **desplegable**.
- Cambiar de nivel empieza una **partida nueva desde 0** (no se mezclan niveles). El nivel elegido queda guardado en el navegador y se restaura al recargar.
- Las instrucciones se muestran solo con el botón «Instrucciones del juego» (nunca automáticamente al empezar una partida).
- «Finalizar partida» termina la partida en curso: narra la puntuación y la compara con el récord del nivel; solo se guarda si es la mejor partida jugada en ese nivel (repositorio por nivel en el navegador).
- La partida termina automáticamente si se llega a **−20 puntos**.
- **Temporizador de ronda** (1 minuto): comprar letra devuelve el minuto completo; en los últimos 10 segundos suenan pitidos en escala ascendente; al cumplir el minuto se resta 1 punto ("Menos 1 punto") y arranca otro minuto.
- La app incluye síntesis de voz (TTS en español) y avisos sonoros (pitidos) vía Web Audio.

## Requisitos

- Cualquier navegador moderno. No hay backend ni dependencias de Python (PapaParse se carga desde CDN).

## Uso (Windows PowerShell)

El navegador no permite `fetch` de ficheros locales con `file://`, así que sirve la carpeta con un servidor local:

```powershell
# desde la carpeta del proyecto
python -m http.server 8000
# abrir en el navegador: http://localhost:8000
```

Si la carga automática falla, usa el selector de archivos de la página para subir `train.csv` manualmente.

## Archivos

- `index.html`: interfaz web (niveles, partidas, overlays de instrucciones y resultado).
- `app.js`: lógica del juego (carga y filtrado del CSV, niveles, rondas, partidas, récords, TTS).
- `styles.css`: estilos. La página se reparte en dos mitades con una rejilla según orientación: apaisado → juego a la izquierda (50 % del ancho, altura completa) y pecera a la derecha; vertical → juego arriba y pecera debajo (100 % de ancho, mitad de alto cada uno).
- `pecera/`: marcador visual de acuario (pez cartoon que sube y baja con el agua según la puntuación; muere a −20). `pecera/js/` son los módulos originales del widget; `pecera/integracion.js` monta la escena en `#pecera-slot` y publica la API en `window.aquarium`. Al empezar cada partida nueva la pecera parte cubriendo la ventana completa y durante 5 s se encoge hasta su hueco; la primera pregunta arranca al terminar (se salta solo con `prefers-reduced-motion`).
- `train.csv`: datos de entrada jugables — palabras marcadas como de uso en **España** en el Wikcionario (1.179 palabras; licencia CC BY-SA 4.0, atribución obligatoria al publicar), con la columna `level` (1–5) asignada por frecuencia de uso (escala Zipf de wordfreq). Reparto: básico 81 · fácil 167 · intermedio 290 · difícil 272 · muy difícil 369.
- `train-rae.csv`: copia del fichero generado desde el corpus del DLE (RAE; 65.795 palabras, sin columna `level`; uso personal, no publicable).
- `train corto.csv`: muestra pequeña para pruebas rápidas.
- `train-piloto-ia.csv`: pilotaje de definiciones propias (118 palabras frecuentes del listado de la RAE, redactadas de cero, verificadas con test de n-gramas contra la DLE — 0 coincidencias). El juego no lo carga por defecto.

## Notas

- Filtro de datos: se excluyen palabras que contienen espacios, dígitos o guiones.
- El archivo `train.csv` debe estar en la misma carpeta que `index.html` para la carga automática.
- La pecera es un espejo visual: el tiempo lo gobierna siempre el juego. `app.js` la alimenta con `setScore` (puntuación), `word()` (ronda nueva y letra comprada) y reacciones puntuales del pez (`happy`/`scared`); en «Finalizar partida» manual se para su reloj con `stopIdle()` sin matar al pez. La puntuación debería tocar el juego, no viceversa (cambios de modelo en `pecera/js/animation.js` solo si se coordina con `MIN_SCORE_END`).

## Licencia

- Código de ejemplo proporcionado como referencia para uso personal.
