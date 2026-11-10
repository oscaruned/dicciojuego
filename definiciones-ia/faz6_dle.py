# -*- coding: utf-8 -*-
# Faz 6: normaliza mayúscula inicial y punto final en todas las definiciones
import io, json, sys

sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\portable\diccio\definiciones-ia"

arregladas = []
for n in range(1, 21):
    path = base + r"\lote-%02d.jsonl" % n
    objs = [json.loads(l) for l in io.open(path, encoding="utf-8") if l.strip()]
    for o in objs:
        d = o["definition"].strip()
        d = d[0].upper() + d[1:]
        if not d.endswith("."):
            d = d + "."
        if o["definition"] != d:
            o["definition"] = d
            arregladas.append((n, o["word"]))
    with io.open(path, "w", encoding="utf-8") as f:
        for o in objs:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
print("normalizadas:", len(arregladas))
for x in arregladas:
    print("  ", x)
