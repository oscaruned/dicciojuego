# -*- coding: utf-8 -*-
# Validación rápida del lote: JSON válido en cada línea, palabras únicas y
# presentes en la lista maestra, sin erratas típicas (letras sueltas).
import io, json, sys

sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\portable\diccio\definiciones-ia"
lista = json.load(io.open(base + r"\lista.json", encoding="utf-8"))
conocidas = set(lista)

tot = 0
prob = []
for nombre in ["lote-01.jsonl", "lote-02.jsonl", "lote-03.jsonl", "lote-04.jsonl", "lote-05.jsonl", "lote-06.jsonl", "lote-07.jsonl", "lote-08.jsonl", "lote-09.jsonl", "lote-10.jsonl", "lote-11.jsonl", "lote-12.jsonl", "lote-13.jsonl", "lote-14.jsonl", "lote-15.jsonl", "lote-16.jsonl", "lote-17.jsonl", "lote-18.jsonl", "lote-19.jsonl", "lote-20.jsonl"]:
    vistos = []
    for l in io.open(base + "\\" + nombre, encoding="utf-8"):
        if not l.strip():
            continue
        tot += 1
        try:
            o = json.loads(l)
        except Exception as e:
            prob.append((nombre, "JSON inválido: " + str(e)))
            continue
        w = o.get("word")
        vistos.append(w)
        if w not in conocidas:
            prob.append((nombre, "palabra no está en lista: " + w))
        if set(o.keys()) != {"word", "definition"}:
            prob.append((nombre, "claves raras en " + w))
        d = o.get("definition", "")
        if len(d) < 25 or len(d) > 220:
            prob.append((nombre, "longitud sospechosa en " + w))
        # erratas: mayúscula inicial, sin punto final, dobles espacios?
        if not d[0].isupper() or not d.rstrip().endswith("."):
            prob.append((nombre, "formato (mayúsc./punto) en " + w))
        if "  " in d:
            prob.append((nombre, "doble espacio en " + w))
    dup = [w for k, w in [(i, vistos[i]) for i in range(len(vistos))] if vistos.count(w) > 1]
    if dup:
        prob.append((nombre, "duplicadas en el propio lote: " + ", ".join(set(dup))))

# duplicados entre lotes
todos = {}
for nombre in ["lote-01.jsonl", "lote-02.jsonl", "lote-03.jsonl", "lote-04.jsonl", "lote-05.jsonl", "lote-06.jsonl", "lote-07.jsonl", "lote-08.jsonl", "lote-09.jsonl", "lote-10.jsonl", "lote-11.jsonl", "lote-12.jsonl", "lote-13.jsonl", "lote-14.jsonl", "lote-15.jsonl", "lote-16.jsonl", "lote-17.jsonl", "lote-18.jsonl", "lote-19.jsonl", "lote-20.jsonl"]:
    for l in io.open(base + "\\" + nombre, encoding="utf-8"):
        if not l.strip():
            continue
        w = json.loads(l)["word"]
        if w in todos:
            prob.append((nombre, "repetida también en " + todos[w] + ": " + w))
        todos[w] = nombre

print("total de definiciones:", tot)
if prob:
    print("PROBLEMAS:")
    for n, m in prob:
        print(" -", n, "->", m)
else:
    print("todo en orden")
