# -*- coding: utf-8 -*-
# Agrega los 5-gramas chocantes por frecuencia para atacarlos en bloque.
import io, json, re, sys, os
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\portable\diccio\definiciones-ia"
corpus_path = os.path.expandvars(r"%TEMP%\opencode\rae_corpus.json")

def ngramas(texto, n=5):
    palabras = re.findall(r"[a-záéíóúüñ]+", texto.lower())
    return {" ".join(palabras[i:i + n]) for i in range(len(palabras) - n + 1)}

corpus = json.load(io.open(corpus_path, encoding="utf-8"))
set_corpus = set()
for entrada in corpus:
    for d in entrada.get("definitions") or []:
        if isinstance(d, str) and d.strip():
            set_corpus |= ngramas(d)
print("5-gramas DLE:", len(set_corpus))

chocan = []
cont = Counter()
por_def = []
for n in range(1, 21):
    for l in io.open(base + r"\lote-%02d.jsonl" % n, encoding="utf-8"):
        l = l.strip()
        if not l: continue
        o = json.loads(l)
        gs = ngramas(o["definition"]) & set_corpus
        if gs:
            por_def.append((o["word"], len(gs)))
            for g in gs:
                cont[g] += 1

print("definiciones con choque:", len(por_def))
print("con 1-2 ngramas:", sum(1 for _, k in por_def if k <= 2))
print("con >=6 ngramas:", sorted([p for p, k in por_def if k >= 6]))
print()
print("== 5-gramas más frecuentes ==")
for g, k in cont.most_common(80):
    print(k, "|", g)
