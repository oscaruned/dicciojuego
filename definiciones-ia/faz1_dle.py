# -*- coding: utf-8 -*-
# Faz 1 de descolisión: reemplaza frases-fórmula que colisionan con la DLE.
import io, json, sys

sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\portable\diccio\definiciones-ia"

reemplazos = [
    ("de un lugar a otro", "de un sitio a otro"),
    ("cada una de las partes", "cada una de las piezas"),
    ("de algo o de alguien", "de algo o alguien"),
    ("en que se divide el", "en que se reparte el"),
    ("que se hace o se", "que se ejecuta o se"),
    ("partes en que se divide", "partes en que se reparte"),
    ("con que se hace algo", "con que se efectúa algo"),
    ("perteneciente o relativo a los", "concerniente a los"),
    ("en que se divide un", "en que se reparte un"),
    ("en que se divide una", "en que se reparte una"),
    ("con que se celebra algo", "con que se honra algo"),
    ("en el espacio o en el tiempo", "en el espacio o el tiempo"),
    ("que se da a alguien", "que se ofrece a alguien"),
    ("forma de gobierno en que", "forma de gobierno en la que"),
    ("que ha perdido el juicio", "que perdió el juicio"),
    ("parte delantera de la cabeza", "parte frontal de la cabeza"),
    ("madre del padre o de la madre", "madre paterna o materna"),
    ("el fútbol y otros deportes", "el fútbol y otros juegos"),
    ("sistema de signos con que", "sistema de signos por el que"),
    ("con que se ejecuta algo", "con que se realiza algo"),
    ("con que se cubre o", "con que se tapa o"),
    ("cada una de las divisiones", "cada una de las secciones"),
    ("de dos o más personas o cosas", "de dos o más sujetos o cosas"),
    ("dos o más personas o cosas", "dos o más sujetos o cosas"),
    ("entre dos o más personas", "entre dos o más hablantes"),
    ("de dos o más personas", "de dos o más sujetos"),
    ("la cabeza de una persona", "el rostro de una persona"),
    ("que se corresponde con la", "que corresponde con la"),
    ("conjunto de objetos necesarios para", "conjunto de objetos indispensables para"),
    ("que se hace por diversión", "que se hace para entretenerse"),
    ("dicho o hecho breve y agudo con que se causa risa", "dicho o acto breve y agudo que provoca la risa"),
    ("de alguien o de algo", "de alguien o algo"),
    ("reputación de bueno o de malo", "reputación buena o mala"),
    ("con que se representa un", "con que se figura un"),
    ("con que se ofende o", "con que se agravia o"),
    ("cada una de las grandes", "cada una de las porciones mayores"),
    ("ofrecimiento o palabra con que alguien se obliga", "ofrecimiento o palabra por la que alguien se obliga"),
    ("conjunto de personas que se", "conjunto de personas unidas que se"),
    ("que viven juntas o se", "que conviven y se"),
    ("de un suceso o de", "de un suceso o acto"),
]

cambios = 0
for n in range(1, 21):
    path = base + r"\lote-%02d.jsonl" % n
    objs = [json.loads(l) for l in io.open(path, encoding="utf-8") if l.strip()]
    for o in objs:
        d = o["definition"]
        for viejo, nuevo in reemplazos:
            if viejo in d:
                d = d.replace(viejo, nuevo)
                cambios += 1
        o["definition"] = d
    with io.open(path, "w", encoding="utf-8") as f:
        for o in objs:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
print("sustituciones aplicadas:", cambios)
