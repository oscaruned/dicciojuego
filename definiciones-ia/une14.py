# -*- coding: utf-8 -*-
# Reutilizable: fusiona los trozos cN*.jsonl de un lote en lote-NN.jsonl
# y comprueba JSON, duplicados y cobertura de rango.
import io, json, re, sys

sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\portable\diccio\definiciones-ia"
prefijo = "c14"          # trozos a fusionar
salida = "lote-14.jsonl" # fichero resultante
ini, fin = 1530, 1650    # rango [ini, fin) en lista.json

lineas, palabras = [], []
for t in sorted(re.findall(prefijo + r"[a-z]+\.jsonl", " ".join(
        __import__("os").listdir(base)))):
    for l in io.open(base + "\\" + t, encoding="utf-8-sig"):
        l = l.strip()
        if l:
            lineas.append(l)
for l in lineas:
    palabras.append(json.loads(l)["word"])

with io.open(base + "\\" + salida, "w", encoding="utf-8") as f:
    for l in lineas:
        f.write(l + "\n")

print(salida, "=>", len(palabras), "definiciones")
dup = {w for w in palabras if palabras.count(w) > 1}
if dup:
    print("DUPLICADOS:", dup)
lista = json.load(io.open(base + "\\lista.json", encoding="utf-8"))
rango = lista[ini:fin]
escritas = set(palabras)
faltan = [w for w in rango if w not in escritas]
print("rango:", len(rango), "| escritas:", len(rango) - len(faltan))
print("faltan:", ", ".join(faltan))
