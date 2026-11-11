# -*- coding: utf-8 -*-
# Faz 5: reescrituras manuales de las def. con >=3 5-gramas DLE
import io, json, sys

sys.stdout.reconfigure(encoding="utf-8")
base = r"C:\portable\diccio\definiciones-ia"

nuevas = {
    "justicia": "Principio de dar a cada uno lo merecido; también el poder que aplica las leyes y castiga las faltas.",
    "media": "Prenda de tejido que envuelve el pie y la pierna; también valor central de un conjunto de números.",
    "precio": "Valor en dinero que se paga por un objeto o un trabajo.",
    "página": "Cada hoja de papel de un cuaderno o de un libro impreso; también dirección de Internet con contenidos.",
    "fecha": "Señalamiento del día, el mes y el año en que acontece o se da algo.",
    "río": "Corriente de agua grande y continua que discurre por la tierra y acaba en el mar, en algún lago o en otro río.",
    "mensaje": "Aviso o información que alguien manda a otro para comunicar algo.",
    "carrera": "Competición en que se compite por llegar primero; también los estudios superiores, y el oficio que alguien cultiva en su vida.",
    "buscar": "Hacer gestos o medios para hallar algo o a alguien, o para lograrlo.",
    "entrar": "Pasar desde fuera al interior de un sitio, un estado o un asunto.",
    "época": "Período o lapso en que alguien o algo se distingue por sus hechos o rasgos propios.",
    "dolor": "Sensación dañosa y desagradable en el cuerpo o en la mente; también la pena o aflicción.",
    "asunto": "Materia tratada, o pendiente de resolver.",
    "escuchar": "Dar atención a lo que se oye, y reconocerlo.",
    "referencia": "Relación o allusión a algo; también persona o cosa que sirve de modelo o garantía, y los datos para localizar algo.",
    "cama": "Mueble con ropas para dormir; también el lecho de un curso de agua, y superficie dispuesta para algo.",
    "copa": "Vaso con base y tallo, en que se bebe; también trofeo con esta forma, y la más elevada de un árbol y de un sombrero.",
    "sección": "Corte o división de algo; también cada parte de un organismo, de un texto o de una entidad.",
    "pan": "Alimento hecho con una pasta de harina y agua, fermentada y cocida al horno.",
    "estación": "Cada uno de los cuatro tramos del año por su clima; también el lugar de parada de trenes y autobuses.",
    "blanca": "Del color de la nieve o del papel; también persona de piel clara, y, en la baraja, la carta de menos valor.",
    "conciencia": "Conocimiento interior que alguien tiene de sí; también el criterio del bien y del mal.",
    "idioma": "Habla o lengua de un país o de una cultura.",
    "estadounidense": "De los Estados Unidos, o relativo a aquel país de América.",
    "playa": "Franja de arena o tierra junto al mar, a los ríos o a los lagos, para el paseo y el baño.",
    "privada": "Que posee una persona o un grupo, y no se extiende al estado o a todos.",
    "física": "Ciencia que estudia las propiedades de la materia y de la energía, y las leyes de su comportamiento.",
    "audiencia": "Acto de escuchar, o cantidad de personas presentes en un acto o emisión; también recepción oficial y tribunal antiguo.",
    "señal": "Todo lo que se advierte para dar una idea, con figura, sonido o movimiento; también el rastro que delata.",
    "espalda": "Parte del cuerpo humano que va de los hombros a las caderas, tras el pecho.",
    "labor": "Trabajo o tarea, en concreto aquello que se realiza con las manos.",
    "amistad": "Afecto sincero y desinteresado, compartido con alguien.",
    "recuperar": "Recobrar lo que se vendió o extravió; también devolver a alguien o algo al estado anterior.",
    "argumento": "Razón con que se sustenta algo; también el asunto o trama de una obra literaria o artística.",
    "visitar": "Ir a ver a otro, o acudir a un lugar.",
    "princesa": "Hija de un rey o reina; también la mujer de un príncipe.",
    "interpretación": "Acción de interpretar; también la representación de una obra musical o teatral.",
    "rivera": "Orilla de un río o del mar.",
    "metal": "Cuerpo simple, de color y lustre propios, y buen transmisor del calor y de la electricidad.",
    "desayuno": "Comida matinal que se toma al principio del día.",
    "álbum": "Cuaderno o libro dedicado a guardar y coleccionar fotografías, láminas o sellos; también disco recopilatorio de música.",
    "mama": "Cada una de las dos glándulas del pecho de las mujeres y de las hembras de los mamíferos, por las que dan de mamar.",
    "fórmula": "Modo determinado de decir o de expresar algo; también, en la ciencia, la representación por símbolos de una ley.",
    "autonomía": "Capacidad o poder con que alguien se gobierna a sí mismo.",
    "pinta": "Apariencia o porte de alguien o algo; también la marca con que se distingue el ganado.",
    "misterio": "Acción o cosa inescrutable o inexplicable; también el secreto reservado.",
    "conducir": "Guiar o llevar algo o a alguien un camino; también manejar el coche.",
    "crónica": "Historia relatada por orden de tiempos; también artículo de sucesos actuales en un medio de comunicación.",
    "cruzar": "Atravesar o pasar de un extremo a otro; también cruzar la aguja con dos líneas.",
    "llave": "Instrumento de metal dentado con que se abre o cierra una puerta o una caja.",
    "excelencia": "Cualidad de algo o alguien de rango elevado; también el tratamiento honorífico de algunos personajes.",
    "sacrificio": "Ofrecimiento con que se consagra algo a dios; también la privación que se impone, o renuncia de algo.",
    "provocar": "Excitar o mover algo o a alguien, para que se engendre o se enoje.",
    "recibo": "Acción de recibir; también comprobante de que se ha recibido algo.",
}

cambiadas = []
for n in range(1, 21):
    path = base + r"\lote-%02d.jsonl" % n
    objs = [json.loads(l) for l in io.open(path, encoding="utf-8") if l.strip()]
    for o in objs:
        if o["word"] in nuevas:
            o["definition"] = nuevas[o["word"]]
            cambiadas.append((n, o["word"]))
    with io.open(path, "w", encoding="utf-8") as f:
        for o in objs:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
print("reescribidas:", len(cambiadas), cambiadas)
