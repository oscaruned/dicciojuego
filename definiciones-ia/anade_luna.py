# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding="utf-8")
linea = '{"word": "luna", "definition": "Cuerpo celeste que rodea la tierra, que brilla con luz reflejada del sol; el satélite natural de la tierra."}\n'
with io.open(r"C:\portable\diccio\definiciones-ia\lote-07.jsonl", "a", encoding="utf-8") as f:
    f.write(linea)
print("añadida luna")
