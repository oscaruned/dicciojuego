// integracion.js - puente entre "Pecera de palabras" y el marcador de acuario
// Monta la escena SVG en #aquarium-root y publica la API en window.aquarium.
// Aviso: NO reutiliza el bootstrap demo de la pecera porque tomaba por error
// el elemento #score del juego; aquí cada elemento se busca dentro del SVG.
import { Aquarium } from './js/animation.js'
import { buildScene } from './js/scene.js'

function initAquarium() {
  const root = document.getElementById('aquarium-root');
  if (!root) return;

  const built = buildScene(root);
  const svgRoot = built.svgRoot;

  const els = {
    water: svgRoot.querySelector('#water'),
    waterRect: svgRoot.querySelector('#waterRect'),
    waveA: svgRoot.querySelector('#waveA'),
    waveB: svgRoot.querySelector('#waveB'),
    foam: svgRoot.querySelector('#foamA'),
    splashes: svgRoot.querySelector('#splashes'),
    bubbles: svgRoot.querySelector('#bubbles'),
    fish: svgRoot.querySelector('#fish'),
    companions: svgRoot.querySelector('#companions'),
  };

  const aq = new Aquarium(svgRoot, els);
  aq.start();

  // El juego termina la partida por su cuenta ("Finalizar partida") sin que el
  // pez muera ahogado; en ese caso hay que detener el reloj de inactividad de
  // la pecera a mano (sin muerte del pez, la API original no lo para).
  aq.stopIdle = () => {
    aq.idleRunning = false;
    aq._emit('idleTick', { elapsed: -1, max: aq.idleMax });
  };

  window.aquarium = {
    setScore: (score) => aq.setScore(score),   // puntuación absoluta (modelo completo)
    reset: () => aq.reset(),                   // nueva partida: agua al 40 %, pez vivo
    word: () => aq.word(),                     // cada ronda nueva: reloj de inactividad a 0
    stopIdle: () => aq.stopIdle(),             // partida terminada sin muerte del pez
    happy: () => aq.fish.happy(),              // reacciones puntuales del pez
    scared: () => aq.fish.scared(),
    audio: aq.audio,                           // setVolume / setMuted
  };
  window.aquariumInstance = aq;

  // app.js (script clásico) corre antes que este módulo; usa este evento para
  // saber que la API ya está disponible.
  document.dispatchEvent(new CustomEvent('aquarium-ready'));
}

document.addEventListener('DOMContentLoaded', initAquarium);
