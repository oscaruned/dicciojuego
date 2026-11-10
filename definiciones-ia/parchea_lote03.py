# -*- coding: utf-8 -*-
# Añade al lote-03 las omitidas de contenido (meses restantes, campo, partir,
# opinión, plaza) y reescribe las tres definiciones "Femenino de..." por otras jugables.
import io, json, sys

sys.stdout.reconfigure(encoding="utf-8")
path = r"C:\portable\diccio\definiciones-ia\lote-03.jsonl"

adiciones = [
    {"word": "octubre", "definition": "Décimo mes del año, que tiene treinta y un días."},
    {"word": "diciembre", "definition": "Duodécimo y último mes del año, que tiene treinta y un días."},
    {"word": "abril", "definition": "Cuarto mes del año, que tiene treinta días."},
    {"word": "noviembre", "definition": "Undécimo mes del año, que tiene treinta días."},
    {"word": "campo", "definition": "Terreno extenso fuera de la ciudad; superficie dedicada a pastos o a cultivo."},
    {"word": "partir", "definition": "Dividir o separar una cosa en dos o más pedazos; también comenzar a moverse o a hacer algo."},
    {"word": "opinión", "definition": "Juicio o parecer que una persona forma sobre algo; idea particular de cada uno."},
    {"word": "plaza", "definition": "Espacio público urbano, descubierto y rodeado de edificios, donde se puede pasear o congregarse; también puesto o oportunidad disponible."},
]

correcciones = {
    "alta": "Que se extiende más de lo normal de abajo a arriba; también elevación, o incorporación oficial en un registro o en una organización.",
    "santa": "Que, por haber vivido con especial virtud según su religión, es objeto de culto por la iglesia; también persona de conducta ejemplar.",
    "pública": "Que pertenece o está al servicio de todos, o que se hace y se sabe sin reserva ante la gente.",
}

lineas = []
for l in io.open(path, encoding="utf-8"):
    if l.strip():
        o = json.loads(l)
        if o["word"] in correcciones:
            o["definition"] = correcciones[o["word"]]
        lineas.append(o)
lineas.extend(adiciones)

with io.open(path, "w", encoding="utf-8") as f:
    for o in lineas:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")

print("lote-03 ahora tiene", len(lineas), "definiciones")
