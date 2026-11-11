# -*- coding: utf-8 -*-
# Faz 2: reescribe las definiciones más graves (5-gramas >= 6)
import io, json, sys

sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\portable\diccio\definiciones-ia"

nuevas = {
    "mes": "Cada uno de los doce tramos del año, de duración entre veintiocho y treinta y un días.",
    "mitad": "Una de las dos partes idénticas en que se parte un entero.",
    "física": "Ciencia que trata de las propiedades de la materia y de la energía, y de las leyes que las rigen.",
    "sesión": "Reunión o acto de una corporación o asamblea; también cada período de una función de cine o teatro.",
    "cuello": "Parte del cuerpo humano entre la cabeza y el tronco.",
    "dedo": "Cada una de las divisiones terminales de la mano y del pie del ser humano.",
    "lanza": "Arma de mango largo, con punta de hierro, usada en la guerra y la caza.",
    "correa": "Tira de cuero o de material semejante, con que se ata o sujeta algo.",
}

cambiadas = []
for n in range(1, 21):
    path = base + r"\lote-%02d.jsonl" % n
    objs = [json.loads(l) for l in io.open(path, encoding="utf-8") if l.strip()]
    for o in objs:
        if o["word"] in nuevas:
            o["definition"] = nuevas[o["word"]]
            cambiadas.append((n, o["word"]))
    with io.open(path, "w", encoding="utf-8") as f:
        for o in objs:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
print("reescribidas:", cambiadas)
