# -*- coding: utf-8 -*-
# Separa la línea pegada de la luna y reescribe con líneas completas.
import io, json, sys
sys.stdout.reconfigure(encoding="utf-8")
path = r"C:\portable\diccio\definiciones-ia\lote-07.jsonl"
bruto = io.open(path, encoding="utf-8").read().replace("}\n{", "}\n{")

# separar objetos: cada JSONL empieza en '{"word"'
partes = []
i = 0
while True:
    j = bruto.find('{"word"', i + 1)
    if j == -1:
        break
    trozo = bruto[i:j].strip()
    if trozo:
        partes.append(trozo)
    i = j
partes.append(bruto[i:].strip())

objs = [json.loads(p) for p in partes if p]
with io.open(path, "w", encoding="utf-8") as f:
    for o in objs:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
print("lote-07:", len(objs), "definiciones, líneas normalizadas")
