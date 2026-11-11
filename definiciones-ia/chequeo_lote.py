# -*- coding: utf-8 -*-
# Compara el rango del lote-03 con la lista maestra para identificar las omitidas.
import io, json, sys

sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\portable\diccio\definiciones-ia"
lista = json.load(io.open(base + r"\lista.json", encoding="utf-8"))
prog = json.load(io.open(base + r"\progreso.json", encoding="utf-8"))
ini = prog["siguiente"]

escritas = set()
for l in io.open(base + r"\lote-03.jsonl", encoding="utf-8"):
    if l.strip():
        escritas.add(json.loads(l)["word"])

rango = lista[ini:330]
omitidas = [w for w in rango if w not in escritas]
print("inicio:", ini, "fin:", 330, "palabras en rango:", len(rango))
print("escritas:", len(escritas & set(rango)))
print("omitidas:", ", ".join(omitidas))
