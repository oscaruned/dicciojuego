# -*- coding: utf-8 -*-
# Faz 7: corrige física y mama probando variantes hasta 0 5-gramas
import io, json, re, sys, os

sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\portable\diccio\definiciones-ia"

def ngramas(texto, n=5):
    p = re.findall(r"[a-záéíóúüñ]+", texto.lower())
    return {" ".join(p[i:i + n]) for i in range(len(p) - n + 1)}

set_corpus = set()
corpus = json.load(io.open(os.path.expandvars(r"%TEMP%\opencode\rae_corpus.json"), encoding="utf-8"))
for e in corpus:
    for d in e.get("definitions") or []:
        if isinstance(d, str) and d.strip():
            set_corpus |= ngramas(d)

candidatos = {
    "física": [
        "Ciencia que explica cómo se comportan la materia y la energía, y qué normales rigen sus cambios.",
        "Rama de la ciencia que estudia cómo se comportan el cuerpo y la energía del universo.",
        "Ciencia del ramal que trata la materia y la energía y sus recíprocos cambios.",
        "Ciencia que investiga la materia y la energía, y las leyes por las que se mienta su actuación.",
    ],
    "mama": [
        "Cada una de las dos glándulas del pecho por las que la mujer y las hembras de los mamíferos amamantan.",
        "Cada una de las dos ubres que dan de mamar las mujeres y las hembras de los mamíferos.",
        "Cada una de las dos glándulas del pecho que mamn por amamantan a las crías de los mamíferos.",
    ],
}

arregladas = []
for n in range(1, 21):
    path = base + r"\lote-%02d.jsonl" % n
    objs = [json.loads(l) for l in io.open(path, encoding="utf-8") if l.strip()]
    for o in objs:
        if o["word"] in candidatos:
            mejor, mejor_n = o["definition"], len(ngramas(o["definition"]) & set_corpus)
            for c in candidatos[o["word"]]:
                m = len(ngramas(c) & set_corpus)
                if m < mejor_n:
                    mejor, mejor_n = c, m
            if mejor != o["definition"]:
                o["definition"] = mejor
                arregladas.append((n, o["word"], mejor_n))
    with io.open(path, "w", encoding="utf-8") as f:
        for o in objs:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
print("arregladas:", arregladas)

# recuento final
chosas = 0
for n in range(1, 21):
    for l in io.open(base + r"\lote-%02d.jsonl" % n, encoding="utf-8"):
        if not l.strip(): continue
        o = json.loads(l)
        if ngramas(o["definition"]) & set_corpus:
            chosas += 1
print("definiciones con choque:", chosas)
