from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from Modelouno import pregunta
import json
#from ModeloDosRespuestasBasicas import contestarbasico
from embedding_search import EmbeddingSearch
from ModeloDosRespuestasBasicas import modelodosgenerar
from ModeloDosGenerarRespuesta import generarRespuesta
from fastapi.middleware.cors import CORSMiddleware



embedding_search = EmbeddingSearch()

app = FastAPI()


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5501",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    #allow_origins=origins,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

@app.post("/procesar")
async def procesar(conversacion: Question):
    respuestaunoo = await primermodelo(conversacion.question)
    print("respuno", respuestaunoo)
    if 'respuesta' in respuestaunoo.keys():#mensajes generales
        print("respuesta general=======")
        respuestaproducto = await segundomodelo(respuestaunoo['respuesta'])
        
        return respuestaproducto

    elif 'PdSr' in respuestaunoo.keys() and 'Intencion' in respuestaunoo.keys():#producto intencion
        print("respuesta pdsr y intencion=======")

        respuestaproducto = await buscaqueda(respuestaunoo['PdSr'], respuestaunoo['Intencion'])

        masProbacles = Masprobalbes(respuestaproducto,0.50)

        LIMPIOS = quitarRepetidos(masProbacles)
        res = tercermodelo(LIMPIOS,conversacion.question)############
        reslimpia = saltos(res)
        return {"respuesta": reslimpia}

        #return {"respuesta": respuestaproducto['resp'], 'Categorias': LIMPIOS}
    elif 'PdSr' in respuestaunoo.keys():#producto    ####
        print("respuesta pdsr=======")

        respuestaproducto = await buscaquedaPS(respuestaunoo['PdSr'])
        masProbacles = Masprobalbes(respuestaproducto,0.1)
        LIMPIOS = quitarRepetidos(masProbacles)
        
        #print(f"*******respuestaproducto{respuestaproducto}, \nlimpios; {LIMPIOS}")
        print("va a entrar")
        res = tercermodelo(LIMPIOS,conversacion.question)############
        reslimpia = saltos(res)
        #print("RESSSSSSSSSSS", res)
        return {"respuesta": reslimpia}
        #return {"respuesta": respuestaproducto['resp'], 'Categorias': LIMPIOS}
    elif 'Intencion' in respuestaunoo.keys() and 'Local' in respuestaunoo.keys():#local e Intencion
        print("respuesta intencion local=======")

        respuestaproducto = await buscaqueda(respuestaunoo['Local'], respuestaunoo['Intencion'])
        masProbacles = Masprobalbes(respuestaproducto,0.8)
        LIMPIOS = quitarRepetidos(masProbacles)
        res = tercermodelo(LIMPIOS,conversacion.question)############
        reslimpia = saltos(res)
        return {"respuesta": reslimpia}

        #return {"respuesta": respuestaproducto['resp'], 'Categorias': LIMPIOS}
    elif 'Intencion' in respuestaunoo.keys():
        print("respuesta intencion=======")

        generarRespuesta = await busquedaIntencion(respuestaunoo['Intencion'])



async def segundomodelo(pregunta):
    Modelodos = modelodosgenerar()
    respuesta = Modelodos.contestarbasico(pregunta)
    return respuesta

async def primermodelo(preguntaa):
    respuesta = pregunta(preguntaa)
    return respuesta

async def buscaqueda(PDSR, INTENCION):

    resultados = embedding_search.buscar_categoria(PDSR, INTENCION, top_k=10)
    if resultados:
        return {"encontrado": resultados, "resp": ""}
    else:

        resultados_otras = embedding_search.buscar_categoria(PDSR, "", top_k=10)
        if resultados_otras:
            return {
                "encontrado": resultados_otras,
                "resp": f"No se encontró '{PDSR}' en la actividad '{INTENCION}', pero sí en otras actividades."
            }
        else:
            return {"encontrado": [], "resp": f"No se encontró '{PDSR}' en ninguna actividad."}

async def buscaquedaPS(PDSR):

    resultados = embedding_search.buscar_categoria(PDSR, "", top_k=10)

    if resultados:

        return {"encontrado": resultados, "resp": ""}
    else:

        resultados_otras = embedding_search.buscar_categoria(PDSR, "", top_k=10)
        if resultados_otras:
            return {
                "encontrado": resultados_otras,
                "resp": f"No se encontró '{PDSR}' en la actividad , pero sí en otras actividades."
            }
        else:
            return {"encontrado": [], "resp": f"No se encontró '{PDSR}' en ninguna actividad."}


async def busquedaIntencion(Intencion):
    resultados = embedding_search.buscar_categoria("", Intencion, top_k=10)

    if resultados:

        return {"encontrado": resultados, "resp": ""}
    else:

        resultados_otras = embedding_search.buscar_categoria("", Intencion, top_k=10)
        if resultados_otras:
            return {
                "encontrado": resultados_otras,
                "resp": f"No se encontró '{Intencion}' en la actividad , pero sí en otras actividades."
            }
        else:
            return {"encontrado": [], "resp": f"No se encontró '{Intencion}' en ninguna actividad."}



def quitarRepetidos(categorias):
    snRepetidos=[]
    nmCategoria = []
    for cat in categorias:
        if cat['categoria_codigo'] not in nmCategoria:
            snRepetidos.append(cat)
            nmCategoria.append(cat['categoria_codigo'])

    return snRepetidos


def Masprobalbes(categorias, probabilida):
    guardar = []
    for cat in categorias['encontrado']:
       
       if float(cat['similitud'])>probabilida:
         guardar.append(cat)  

    return guardar


def tercermodelo(categorias, pregunta):
    res = generarRespuesta.Responder(categorias, pregunta)
    return res

def saltos(res):
    nuevo = res.replace("\n", "<br>")
    #nuevo = res.replace("*", "<br>")

    return nuevo



    



























#ya no se usa
def buscaquedaprod(respuestauno):
    encontrado = []
    with open("categorias.json", "r", encoding="utf-8") as j:
        datos = json.load(j)
    
    for actividades in datos['actividades_economicas']:
        for categoria in actividades['categorias']:
            for palabraClave in categoria['palabras_clave']:
                if respuestauno.lower() in palabraClave.lower():
                    encontrado.append(
                        {
                            "actividad": actividades['actividad'],
                            "categoria": categoria['codigo'],
                            "descripcion": categoria['descripcion']
                        }
                    )
                    break
    
    return encontrado
