# -*- coding: utf-8 -*-
# Faz 3: descolisión con candidatos probados contra el set de 5-gramas DLE.
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
print("5-gramas DLE:", len(set_corpus))

# reglas: (regex, [candidatos]; {g}=grupo 1, {g1}..=grupos)
def cands_lista(pat, lista, m):
    plantillas = []
    for s in lista:
        for i in range(1, (m.re.groups or 0) + 1):
            s = s.replace("{g%d}" % i, m.group(i) or "")
        plantillas.append(s)
    return plantillas

reglas = [
    (r"de un (lugar|sitio|punto) a otro", ["del punto de partida al de destino", "del sitio de partida al de llegada", "desde un {g1} hasta otro {g1}", "de {g1} en {g1} distinto"]),
    (r"[cC]ada una de las (partes|piezas|secciones) en que", ["cada tramo en que", "cada trozo en que"]),
    (r"[cC]ada una de las (partes|piezas|secciones) que", ["cada porción que"]),
    (r"[cC]ada una de las (partes|piezas|secciones)", ["cada porción"]),
    (r"[pP]erteneciente o relativo a (los|las|el|la|un|una) ", ["concerniente a {g1} ", "de {g1} "]),
    (r"que alguien o algo se", ["que una persona o cosa se"]),
    (r"que se ejecuta o se", ["que se cumple o se"]),
    (r"a una persona o a una (cosa|animal|obra)", ["a alguien o a una {g1}"]),
    (r"persona o a una cosa", ["persona o a un elemento"]),
    (r"[Aa] una persona o cosa", ["a un sujeto o su cosa"]),
    (r"se hace o se produce", ["sucede o se genera"]),
    (r"conjunto de personas o de", ["grupo de personas o de"]),
    (r"de personas o de cosas", ["de personas o de elementos"]),
    (r"de un estado a otro", ["de una fase a otra", "de un modo a otro"]),
    (r"[fF]orma de gobierno en que el", ["forma de gobierno en la que el"]),
    (r"[fF]orma de gobierno en que", ["forma de gobierno en la que"]),
    (r"conjunto de dos personas o", ["unión de dos sujetos o"]),
    (r"dos personas o cosas que", ["dos sujetos o cosas que"]),
    (r"de dos personas o cosas", ["de dos sujetos o cosas"]),
    (r"o lograr lo que se", ["y lograr lo que se"]),
    (r"para el fin que se", ["para la finalidad que se"]),
    (r"que se ha de resolver", ["que hay que resolver"]),
    (r"del cuerpo humano o de", ["del cuerpo humano o sus"]),
    (r"de las personas y de", ["de la gente y de"]),
    (r"las personas y de los", ["la gente y de los"]),
    (r"a algo o a alguien", ["a algo o a una persona"]),
    (r"de un edificio y el", ["de un edificio y de la"]),
    (r"cualidad de lo que es", ["condición de lo que es"]),
    (r"cada uno de los puntos", ["cada punto de"]),
    (r"a alguien o algo de", ["a alguien o algo"]),
    (r"fiesta con que se celebra", ["fiesta con que se honra"]),
    (r"en especial la que se", ["en concreto la que se"]),
    (r"del padre o de la madre", ["del padre o de la progenitora"]),
    (r"que se da cuenta de", ["que se advierte de"]),
    (r"el rostro de una persona", ["la cara de alguien"]),
    (r"el fútbol y otros juegos", ["el balompié y otros juegos"]),
    (r"(dicho|acto) o hecho con que", ["dicho o acto con que"]),
    (r"o figura con que se", ["o designación con que se"]),
    (r"que alguien o algo tiene", ["que alguien o algo posee"]),
    (r"cada una de las secciones", ["cada sección"]),
    (r"con que se tapa o", ["con que se resguarda o"]),
    (r"o nota en que se", ["o nota con que se"]),
    (r"o la realización de algo", ["o la ejecución de algo"]),
    (r"las personas que lo habitan", ["la gente que lo habita"]),
    (r"y a las personas que", ["y la gente que"]),
    (r"que se hace de un hecho", ["que nace de un hecho"]),
    (r"tiempo en que sucede algo", ["tiempo en que ocurre algo"]),
    (r"a la nación de que se", ["a la nación a la que se"]),
    (r"los elementos de un conjunto", ["los componentes de un conjunto"]),
    (r"palabra o conjunto de palabras", ["palabra o serie de palabras"]),
    (r"con que se ejecuta o", ["con que se cumple o"]),
    (r"en que se considera dividida", ["en que se imagina partida"]),
    (r"cada una de las mitades", ["cada mitad igual"]),
    (r"que se pide o se", ["que se solicita o se"]),
    (r"de la vida de un", ["de la existencia de un"]),
    (r"acción y efecto de sustituir", ["acción de sustituir una cosa por otra"]),
    (r"al rey o a la", ["al soberano o a la"]),
    (r"materia de la que se trata", ["materia tratada"]),
    (r"de la que se (?:trata|habla)", ["de que se ocupa"]),
    (r"conjunto de personas que", ["grupo de personas que"]),
    (r"de las partes que", ["de las porciones que"]),
    (r"o circunstancia en que se", ["o condición con que está"]),
    (r"en que se encuentra alguien o", ["con que está alguien o"]),
]

def aplicar(texto):
    totals = {}
    for pat, cands in reglas:
        m = re.search(pat, texto)
        if not m:
            continue
        plantillas = cands_lista(pat, cands, m)
        mejor, mejor_n = None, float("inf")
        for p in [m.group(0)] + plantillas:
            prueba = texto[:m.start()] + p + texto[m.end():]
            n = len(ngramas(prueba) & set_corpus)
            if n < mejor_n:
                mejor, mejor_n = p, n
        if mejor != m.group(0):
            texto = texto[:m.start()] + mejor + texto[m.end():]
    return texto

cambiadas = 0
for n in range(1, 21):
    path = base + r"\lote-%02d.jsonl" % n
    objs = [json.loads(l) for l in io.open(path, encoding="utf-8") if l.strip()]
    for o in objs:
        d = o["definition"]
        nuevo = aplicar(d)
        if nuevo != d:
            o["definition"] = nuevo
            cambiadas += 1
    with io.open(path, "w", encoding="utf-8") as f:
        for o in objs:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
print("definiciones tocadas por reglas:", cambiadas)

# recuento final
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
print("con 3-5:", sorted([p for p, k in por_def if 3 <= k <= 5]))
print("con >=6:", sorted([p for p, k in por_def if k >= 6]))
print("== ngramas restantes más frecuentes ==")
for g, k in choque.most_common(40):
    print(k, "|", g)
