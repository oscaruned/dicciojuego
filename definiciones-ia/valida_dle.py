# -*- coding: utf-8 -*-
# Fusiona todos los lotes en definiciones-ia/definiciones-ia-2001.jsonl
# y valida los 5-gramas contra el corpus DLE (rae_corpus.json).
# Marca las definiciones con 5-gramas compartidos con el corpus.
import io, json, re, sys, os

sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\portable\diccio\definiciones-ia"
corpus_path = os.path.expandvars(r"%TEMP%\opencode\rae_corpus.json")

# 1. concatenar lotes en un solo fichero maestro
lineas, palabras = [], []
for n in range(1, 21):
    for l in io.open(base + r"\lote-%02d.jsonl" % n, encoding="utf-8"):
        l = l.strip()
        if l:
            o = json.loads(l)
            palabras.append(o["word"])
            lineas.append(l)
maestro = base + r"\definiciones-ia-2001.jsonl"
with io.open(maestro, "w", encoding="utf-8") as f:
    for l in lineas:
        f.write(l + "\n")
print("maestro:", len(palabras), "definiciones")
dup = {w for w in palabras if palabras.count(w) > 1}
if dup:
    print("DUPLICADOS:", dup)

# 2. descargar/leer corpus DLE y contruir set de 5-gramas
def ngramas(texto, n=5):
    palabras = re.findall(r"[a-záéíóúüñ]+", texto.lower())
    return {" ".join(palabras[i:i + n]) for i in range(len(palabras) - n + 1)}

corpus = json.load(io.open(corpus_path, encoding="utf-8"))
textos = []
for entrada in corpus:
    definiciones = entrada.get("definitions") or []
    for d in definiciones:
        if isinstance(d, str) and d.strip():
            textos.append(d)
print("corpus:", len(textos), "definiciones cargadas")

set_corpus = set()
for t in textos:
    set_corpus |= ngramas(t)
print("5-gramas del corpus DLE:", len(set_corpus))

# 3. comprobar definiciones propias
chocan = []
for l in lineas:
    o = json.loads(l)
    total = len(ngramas(o["definition"]))
    parte = ngramas(o["definition"]) & set_corpus
    if parte:
        chocan.append((o["word"], sorted(parte)[:4], total))
print("definiciones que chocan con DLE:", len(chocan))
for w, gs, t in chocan[:60]:
    print(" -", w, "|", " ; ".join(gs), "| ngramas:", t)
