# -*- coding: utf-8 -*-
# Fusiona los trozos del lote 13 en lote-13.jsonl (UTF-8 sin BOM)
# y comprueba la cobertura del rango 1410-1529 contra lista.json.
import io, json, sys

sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\portable\diccio\definiciones-ia"

trozos = ["c13a.jsonl", "c13b.jsonl", "c13c.jsonl", "c13d.jsonl"]
lineas = []
for t in trozos:
    for l in io.open(base + "\\" + t, encoding="utf-8-sig"):
        l = l.strip()
        if l:
            l = l.rstrip("}\n")
            if not l.endswith("}"):
                l = l + "}" if not l.endswith("}") else l
            lineas.append(l)

with io.open(base + "\\lote-13.jsonl", "w", encoding="utf-8") as f:
    for l in lineas:
        f.write(l + "\n")

# comprobar que todas las líneas son JSON válido y no hay duplicados
palabras = []
for l in lineas:
    palabras.append(json.loads(l)["word"])
print("lote-13 fusionado:", len(palabras), "definiciones")
dup = {w for w in palabras if palabras.count(w) > 1}
if dup:
    print("DUPLICADOS:", dup)

# cobertura del rango
lista = json.load(io.open(base + "\\lista.json", encoding="utf-8"))
rango = lista[1410:1530]
escritas = set(palabras)
faltan = [w for w in rango if w not in escritas]
print("rango:", len(rango), "| escritas del rango:", len(rango) - len(faltan))
print("faltan:", ", ".join(faltan))
