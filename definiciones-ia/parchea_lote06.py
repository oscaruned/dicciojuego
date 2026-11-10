# -*- coding: utf-8 -*-
# Correcciones de redacción en el lote-06.
import io, json, sys

sys.stdout.reconfigure(encoding="utf-8")
path = r"C:\portable\diccio\definiciones-ia\lote-06.jsonl"

correcciones = {
    "referencia": "Relación o allusión a algo; también persona o cosa que sirve de guía o garantía, y los datos para localizar algo.",
    "opción": "Cada una de las alternativas que pueden elegirse; también derecho de adquirir o de hacer algo.",
    "aumento": "Acción de aumentar o de crecer; también la cantidad o el nivel añadidos.",
    "marca": "Señal que distingue o advierte algo; también el distintivo comercial de un producto.",
    "tratar": "Ocuparse de un asunto; también comportarse con alguien de cierta forma, y aplicar una cura a un mal.",
    "triste": "Que está sin alegría o está lleno de pena; también que causa pesadumbre.",
    "pelo": "Cada fibra o hebra que sale de la piel de las personas y de los mamíferos, o el conjunto de ellas.",
    "reforma": "Cambio o modificación de algo sin sustituirlo del todo, como una ley, una institución o un edificio.",
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

print("lote-06 tiene", len(lineas), "definiciones;", len(correcciones), "reescritas")
