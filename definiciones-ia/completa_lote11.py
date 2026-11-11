# -*- coding: utf-8 -*-
# Completa el lote-11: corrige erratas del bloque escrito y añade las
# definiciones restantes desde 'combate' hasta 'haz'.
import io, json, sys

sys.stdout.reconfigure(encoding="utf-8")
path = r"C:\portable\diccio\definiciones-ia\lote-11.jsonl"

correcciones = {
    "reconocer": "Saber o admitir que alguien o algo es quien se dice o lo que era; también agradecer un bien recibido.",
    "definición": "Acción de definir; también frase breve con que se precisa qué es o qué significa algo.",
}

resto = [
    ("combate", "Acción de combatir."),
    ("caminar", "Andar con paso, trasladándose a pie."),
    ("argumento", "Razón con que se argumenta; también el asunto o plan de una obra literaria o artística."),
    ("arena", "Piedra desmenuzada en granos muy finos; también el recinto con que se hacen los combates (arena)."),
    ("alternativa", "Opción en que se puede elegir; también cada cosa con que otra puede ser sustituida."),
    ("agricultura", "Conjunto de labores e industria con que se cultiva la tierra y se producen vegetales."),
    ("ánimo", "Espíritu o disposición interior; también el valor o el aliento con que se actúa."),
    ("ventana", "Abertura, generalmente con vidrio, para la luz, el aire y la vista."),
    ("triunfo", "Victoria brillante y honrosa; también la alegría o el aplauso con que se celebra."),
    ("socialista", "Del socialismo, o que apoya sus ideas; también su defensor o militante."),
    ("servir", "Ser útil o aprovecharse para algo; también atender u obecechar a alguien, y, con 'de', ocupar el lugar de algo."),
    ("rural", "Del campo, o concerniente a la vida y las actividades del campo."),
    ("risa", "Movimiento del rostro y sonido con que se manifiesta alegría o una broma."),
    ("producir", "Crear o generar algo; también dar un beneficio, un efecto o un resultado."),
    ("ofrecer", "Presentar algo a alguien en voluntariado, como servicio, obsequio o trato."),
    ("locura", "Privación del juicio; also falta o exceso de sensatez."),
    ("inicial", "Que está en el comienzo; también cada letra con que empieza un nombre."),
    ("goles", "En el fútbol y otros deportes, el número o cada meta de os balones metidos en la portería."),
    ("estadio", "Recinto grande con gradas o localidades, para competiciones y espectáculos deportivos."),
    ("diálogo", "Conversación o trato por otros medios; también la comunicación del texto oral en una obra de teatro o cine."),
    ("considerar", "Examinar o pensar algo con atención; también poner en la cuenta o estimar algo."),
    ("cabello", "Pelo de la cabeza de una persona."),
    ("ausencia", "Falta o carencia; también el estar fuera alguien de su lugar o del lugar de otra."),
    ("agente", "Persona que obra o ejerce un cargo en nombre de otros; también lo que causa un efecto."),
    ("academia", "Corporación de académicos que cultiva una ciencia o un arte; también el establecimiento de enseñanza o el campo de la cultura."),
    ("senado", "Cámara alta de un parlamento."),
    ("procedimiento", "Manera de proceder con que algo se ejecuta o se llega a un fin."),
    ("poeta", "Persona que compone poesía."),
    ("olvidar", "No pensar o dejar de acordarse de algo; también descuidar algo o a alguien."),
    ("máxima", "Precepto o pensamiento general con que alguien gobierna su modo de obrar; también, referido a otra palabra, lo más grande o de más alto grado en su clase."),
    ("mina", "Excavación con que se extraen minerales de la tierra; también el artefacto explosivo enterrado o flotante."),
    ("marina", "Del mar o concerniente a él; también la institución militar de la guerra en el mar."),
    ("explicación", "Acción de explicar; también la declaración o aclaración con que se hace entender algo."),
    ("eliminar", "Excluir o poner fuera de algo; también destruir o suprimir."),
    ("detalle", "Cada punto o particularidad.",
     ),
    ("brazo", "Extremidad del cuerpo humano que va del hombro a la mano; también lo que sobresale o se cuenta (brazo de un río, de una sartén)."),
    ("bar", "Local donde se sirven bebidas y aperitivos."),
    ("asegurar", "Dar firmeza o garantía a algo; también afirmar con certeza, o fijar algo para que no se mueva."),
    ("andar", "Caminar o moverse con paso; también estar o hallarse en cierto estado o situación."),
    ("actor", "Persona que representa o interpreta un papel en teatro o cine."),
    ("acceder", "Entrar o pasar a un lugar; también consentir o conceder lo que se pide."),
    ("visitar", "Ir a ver a alguien o estar con él, o acudir a un lugar."),
    ("traer", "Llevar algo hacia donde está quien habla o el lugar de referencia; también ser la causa de algo."),
    ("torre", "Construcción alta y esbelta, o cuerpo alto que se alza sobresaliendo del resto de un edificio."),
    ("talento", "Capacidad o aptitud para hacer algo, entendida como habilidad natural."),
    ("salvar", "Poner a salvo a algo o alguien; también esquivar un mal o perder muchas menos cosas de lo esperado."),
    ("haz", "Conjunto o atado de cosas juntas, como leños; también el conjunto de rayos de luz o partículas con un fin común."),
]

# cargar y corregir entradas
objs = []
for l in io.open(path, encoding="utf-8"):
    s = l.strip()
    if not s:
        continue
    # línea rota: guardar el word si se puede leer el inicio
    if not s.endswith("}"):
        s = s[:s.rfind("}") + 1] if "}" in s else None
        if not s:
            continue
    try:
        o = json.loads(s)
    except Exception:
        # reconstruir el wield del combate truncado
        if '"word": "combate"' in l:
            continue
        raise
    if o["word"] in correcciones:
        o["definition"] = correcciones[o["word"]]
    objs.append(o)

# añadir el resto, sin duplicar si ya existiera
ya = {o["word"] for o in objs}
for w, d in resto:
    d = d.replace(" also ", " también ")
    if w not in ya:
        objs.append({"word": w, "definition": d})
        ya.add(w)

with io.open(path, "w", encoding="utf-8") as f:
    for o in objs:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")

print("lote-11:", len(objs), "definiciones")
