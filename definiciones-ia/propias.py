# -*- coding: utf-8 -*-
# propias.csv: word,definition (2 columnas) con las 2.001 escritas
import io, json, csv, sys

sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\portable\diccio\definiciones-ia"
vistos, lineas = set(), []
for n in range(1, 21):
    for l in io.open(base + r"\lote-%02d.jsonl" % n, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        o = json.loads(l)
        if o["word"] in vistos:
            continue
        vistos.add(o["word"])
        lineas.append((o["word"], o["definition"]))

salida = r"C:\portable\diccio\propias.csv"
with io.open(salida, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    w.writerow(["word", "definition"])
    for a, b in lineas:
        w.writerow([a, b])
print("propias.csv:", len(lineas), "definiciones")

# los 10 primeros para ojear
for a, b in lineas[:8]:
    print(" -", a, "|", b[:60])
