from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import re
from pathlib import Path
from ollama import chat
import re

#pip install spacy
#python -m spacy download es_core_news_sm
import spacy
nlp = spacy.load("es_core_news_sm")



template = """
Tu tarea es detectar si el usuario menciona alguno de los siguientes elementos:

1. **Intención** válida (solo puede ser una de estas: vender, servir o hacer)
2. **Producto o servicio** (PdSr)
3. **Establecimiento o local** (Local)

REGLAS IMPORTANTES:
- Solo considera como intención válida: vender, servir o hacer. Si se menciona otra palabra distinta, ignórala a menos que sea un sinonimo de las 3 principales.
- Si no se menciona ninguna intención válida ni producto ni establecimiento, responde con: `norp`
- Si solo se menciona el producto o servicio, responde así: `PdSr: <producto>`
- Si se menciona el establecimiento, responde así: `Local: <establecimiento>` , `Intencion: servir 
- Si se menciona intención válida + producto, responde así: `Intencion: <intención>, PdSr: <producto>`
- Si hay errores ortográficos, corrígelos (ej. "lenderia" → "lencería")

FORMATO DE RESPUESTA:
- Si hay datos válidos, responde en este formato exacto: `Intencion: <intención>, PdSr: <producto>` o `Local: <establecimiento>`
- Si no hay información útil, responde solo: `norp`

EJEMPLOS:
- "Quiero vender pizza" → Intencion: vender, PdSr: pizza
- "Quiero hacer cerveza" → Intencion: hacer, PdSr: cerveza
- "Quiero abrir una taquería" → Local: taquería, Intencion: servir
- "hola" → norp
- "¿Qué actividades hay?" → norp

para tu respuesta hay 3 casos:
*Si solo te menciona el producto o servicio:
    PdSr
*Si en la pregunta se menciono el establecimiento en donde se vende el producto:
    Local:
    Intencion:
*si solo se menciona  la intencion y el producto el formato de tu respuesta debe de ser:
    Intencion:
    PdSr:
no des más información.

Ahora analiza la siguiente pregunta:

"{pregunta}"

Responde SOLO el resultado, sin explicaciones.
"""


modelo = OllamaLLM(model="llama3.2")

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | modelo

def lematizacion(texto):
    doc = nlp(texto)
    for token in doc:
        return token.lemma_


def pregunta(pregunta):
    try:
        respuesta = chain.invoke({"pregunta": pregunta}) 

        #intencion_match = re.search(r"Intencion:\s*([^\n\r]+)", respuesta)
        intencion_match = re.search(r"Intencion:\s*(vender|hacer|servir)", respuesta)
        pdsr_match = re.search(r"PdSr:\s*([^\n\r]+)", respuesta)
        local_match = re.search(r"Local:\s*([^,\n\r]+)", respuesta)

        intencion = intencion_match.group(1).strip() if intencion_match else None
        pdsr_ = pdsr_match.group(1).strip() if pdsr_match else None
        local = local_match.group(1).strip() if local_match else None
        
        #print("respuesta",respuesta,"\npregunta", pregunta,"\nrespuesta: \n", respuesta)
    except Exception as e:
        return {"error":e}
    

    if not intencion and not pdsr_ and not local: #ccuando sea un hola o alguna otra cosa
        return {"respuesta":pregunta}
    elif intencion and pdsr_:#cuando hay intencion y producto
        pdsr = pdsr_
        print("res",respuesta)
        print( "PdSr", pdsr)
        print("Intencion",intencion)
        return {  "PdSr": pdsr, "Intencion":intencion}
    elif not local and not intencion and pdsr_: #cuando solo diga el producto o servicio
        pdsr = pdsr_
        return {  "PdSr": pdsr}
    elif not pdsr_: #cuando se mencione establecimiento
        return {"Intencion": intencion, "Local": local}





