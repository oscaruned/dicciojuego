# -*- coding: utf-8 -*-
# Correcciones de redacción en el lote-04.
import io, json, sys

sys.stdout.reconfigure(encoding="utf-8")
path = r"C:\portable\diccio\definiciones-ia\lote-04.jsonl"

correcciones = {
    "aire": "Mezcla de gases inodora e invisible que forma la atmósfera y respiran los seres vivos.",
    "carrera": "Competición en la que se trata de llegar primero; también conjunto de estudios, o actividad u oficio que alguien cultiva a lo largo de su vida.",
    "comer": "Llevar a la boca y tragar los alimentos para nutrirse.",
    "baja": "Que está a poca altura o tiene menos nivel que aquello con lo que se compara; también descenso de algo, y en lo militar, la pérdida o el retiro de un miembro.",
    "jugar": "Entretenerse y divertirse con un juego; también intervenir en un deporte, un pasatiempo o una apuesta.",
    "evitar": "Hacer lo posible para que no suceda algo, o para no encontrarse con alguien.",
    "puerto": "Lugar de la costa donde las embarcaciones pueden llegar, anclar y descargar su carga.",
    "presente": "Que existe u ocurre ahora; tiempo actual; también cosa que se obsequia sin pedir nada a cambio.",
    "corte": "Acción de dividir o separar algo con un instrumento cortante; también la tribuna o el séquito del rey.",
    "posición": "Forma o manera de estar colocado un cuerpo respecto de otro; también postura o parecer de alguien en un asunto.",
    "fuego": "Reacción rápida de combustión, con llama, calor y luz; también lo que arde, como obstáculo o para calentarse y avisar.",
    "entender": "Comprender o captar el significado de algo.",
    "empezar": "Dar comienzo a una cosa.",
    "culpa": "Acción o desatino por el que se considera responsable a alguien; también el remordimiento que esa acción produce.",
    "mamá": "Nombre afectuoso con que los hijos denominan a su madre.",
    "llamada": "Acción de llamar; con el teléfono, comunicación establecida con quien se quiere hablar.",
    "creer": "Dar por verdadero algo sin tener pruebas plenas; también tener fe o tener por bueno el juicio de otra persona.",
}

lineas = []
for l in io.open(path, encoding="utf-8"):
    if l.strip():
        o = json.loads(l)
        if o["word"] in correcciones:
            o["definition"] = correcciones[o["word"]]
        lineas.append(o)

with io.open(path, "w", encoding="utf-8") as f:
    for o in lineas:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")

print("lote-04 tiene", len(lineas), "definiciones;", len(correcciones), "reescritas")
