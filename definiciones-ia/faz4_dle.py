# -*- coding: utf-8 -*-
# Faz 4: purga case-insensitive de los 5-gramas que anidan (física incluida)
import io, json, re, sys, os
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\portable\diccio\definiciones-ia"
corpus_path = os.path.expandvars(r"%TEMP%\opencode\rae_corpus.json")

def ngramas(texto, n=5):
    p = re.findall(r"[a-záéíóúüñ]+", texto.lower())
    return {" ".join(p[i:i + n]) for i in range(len(p) - n + 1)}

set_corpus = set()
corpus = json.load(io.open(corpus_path, encoding="utf-8"))
for e in corpus:
    for d in e.get("definitions") or []:
        if isinstance(d, str) and d.strip():
            set_corpus |= ngramas(d)

def mejor_de(texto, reglas):
    cambiado = texto
    for pat, cands in reglas:
        for m in list(re.finditer(pat, cambiado)):
            opciones = [cambiado[:m.start()] + c + cambiado[m.end():] for c in cands]
            base_n = len(ngramas(cambiado) & set_corpus)
            mejor_op = min(opciones, key=lambda t: len(ngramas(t) & set_corpus))
            if len(ngramas(mejor_op) & set_corpus) < base_n:
                cambiado = mejor_op
    return cambiado

def esc(s):
    return re.escape(s)

reglas = []
def R(fr, cands):
    reglas.append((re.compile(fr, re.IGNORECASE), cands))

R(r"[cC]iencia que trata de las propiedades de la materia y de la energía, y de las leyes que las rigen",
  ["Rama de la ciencia que se ocupa de la materia, de la energía y de sus cambios."])
R(r"[Cc]onjunto de personas o de", ["grupo de gente o de", "grupo de sujetos o de"])
R(r"[Dd]icho o acto con que se", ["dicho breve con que se"])
R(r"que se trata o que se", ["de que se encarga o que se"])
R(r"[Cc]ualidad de lo que es", ["condición de lo que es"])
R(f"{esc('del padre o de la')}", ["paterno o materno de la"])
R(r"conjunto de personas que están", ["grupo de gente que está"])
R(r"[Oo] la realización de algo", ["o la ejecución de algo"])
R(r"palabra o conjunto de palabras", ["palabra o serie de palabras"])
R(r"o conjunto de palabras con", ["o serie de palabras con"])
R(r"[Aa] la que llega una", ["a la que se llega en"])
R(r"cada una de las mitades", ["cada mitad igual"])
R(r"o partes en que se", ["o trozos en que se"])
R(r"acción y efecto de sustituir", ["acción de sustituir una cosa por otra"])
R(r"conjunto de personas que se", ["grupo de personas con"])
R(r"servir o atender a alguien", ["ser útil a alguien"])
R(r"que sigue inmediatamente a otra", ["que viene tras otra"])
R(r"auxilio que se presta a", ["souvenir que se ofrece a"])
R(r"que se presta a quien", ["que se da a la persona"])
R(r"una cosa o un lugar", ["una cosa o un sitio"])
R(r"que se estaba haciendo o", ["que estaba en curso"])
R(r"cada uno de los doce", ["cada uno de los 12"])
R(r"tierra que se usa para", ["camino trazado para"])
R(r"o punto de partida de", ["o arranque de"])
R(r"ojos la nariz y la", ["ojos, la nariz y la"])
R(r"la nariz y la boca", ["la nariz y las fauces"])
R(r"parte delantera de la cabeza", ["parte frontal del rostro"])
R(r"tiempo en un lugar o", ["tiempo en un sitio o"])
R(r"conjunto de habitantes de un", ["gente que habita un"])
R(r"colocar algo en un lugar", ["dejar algo en un sitio"])
R(r"que se puede hacer o", ["que cabe hacer o"])
R(r"en los juegos de azar", ["en el juego de azar"])
R(r"con el fin de producir", ["para lograr producir"])
R(r"de los cuatro puntos cardinales", ["de los cuatro rumbos principales"])
R(r"que alguien o algo se", ["que un sujeto o cosa se"])
R(r"conjunto de sujetos o de", ["grupo de sujetos o de"])

cambiadas = 0
for n in range(1, 21):
    path = base + r"\lote-%02d.jsonl" % n
    objs = [json.loads(l) for l in io.open(path, encoding="utf-8") if l.strip()]
    for o in objs:
        d = o["definition"]
        nuevo = mejor_de(d, reglas)
        if nuevo != d:
            o["definition"] = nuevo
            cambiadas += 1
    with io.open(path, "w", encoding="utf-8") as f:
        for o in objs:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
print("definiciones tocadas:", cambiadas)

choque = Counter()
por_def = []
for n in range(1, 21):
    for l in io.open(base + r"\lote-%02d.jsonl" % n, encoding="utf-8"):
        if not l.strip(): continue
        o = json.loads(l)
        gs = ngramas(o["definition"]) & set_corpus
        if gs:
            por_def.append((o["word"], len(gs)))
            for g in gs: choque[g] += 1
print("definiciones con choque:", len(por_def))
print("con >=2:", len([1 for _, k in por_def if k >= 2]))
print("con >=3:", sorted([p for p, k in por_def if k >= 3]))
print("== ngramas más frecuentes ==")
for g, k in choque.most_common(50):
    print(k, "|", g)
