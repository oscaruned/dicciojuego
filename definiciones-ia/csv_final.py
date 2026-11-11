# -*- coding: utf-8 -*-
# Construye el CSV final jugable: word, definition, level (zipf 1-5)
import io, json, csv, sys

sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\portable\diccio\definiciones-ia"

# 1. maestro final (lease todos los lotes, sin duplicados)
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
        lineas.append(o)
maestro = base + r"\definiciones-ia-2001.jsonl"
with io.open(maestro, "w", encoding="utf-8") as f:
    for o in lineas:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
print("maestro:", len(lineas))

# 2. nivel por zipf
import wordfreq

def nivel(w):
    z = wordfreq.zipf_frequency(w, "es")
    if z >= 4.5: return 1
    if z >= 3.5: return 2
    if z >= 2.5: return 3
    if z >= 1.5: return 4
    return 5

salida = r"C:\portable\diccio\train-ia-2000.csv"
with io.open(salida, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    w.writerow(["word", "definition", "level"])
    for o in lineas:
        w.writerow([o["word"], o["definition"], nivel(o["word"])])
print("csv:", salida)

# reparto de niveles
from collections import Counter
c = Counter(nivel(o["word"]) for o in lineas)
print("niveles:", dict(sorted(c.items())))
