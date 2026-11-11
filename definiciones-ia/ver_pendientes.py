# -*- coding: utf-8 -*-
"""Leata los siguientes N pendientes y estado de progreso del lote de definiciones IA."""
import json, io, os, sys

sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\portable\diccio\definiciones-ia"
lista = json.load(io.open(os.path.join(base, "lista.json"), encoding="utf-8"))
prog = json.load(io.open(os.path.join(base, "progreso.json"), encoding="utf-8"))
n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
i = prog["siguiente"]
seg = lista[i:i + n]
print(json.dumps({"proximas": seg, "proximo_indice": i}, ensure_ascii=False, indent=0))
