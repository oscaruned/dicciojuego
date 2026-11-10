# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding="utf-8")
path = r"C:\portable\diccio\definiciones-ia\lote-12.jsonl"
texto = io.open(path, encoding="utf-8-sig").read()
lineas = [l for l in texto.splitlines() if l.strip()]
with io.open(path, "w", encoding="utf-8") as f:
    for l in lineas:
        f.write(l.strip() + "\n")
print("lote-12 reescrito sin BOM:", len(lineas), "definiciones")
