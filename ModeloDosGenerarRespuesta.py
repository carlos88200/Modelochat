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
Eres Inegi, un chatbot que da información sobre actividades económicas.

Tu trabajo es darle formato a las categorias para generar una respuesta y para generar la respuesta sigue estos pasos:
    1. Tomar la lista de categorías encontradas para una pregunta.
    2. Hacer una respuesta clara, cordial y fácil de leer para humanos.
    3. Incluir cada categoría con los siguientes campos visibles:
    - Actividad
    - Código de categoría
    - Descripción de la categoría
    - Palabra clave detectada
    - Similitud
    4. Ordena las categorías de mayor a menor según el valor de "similitud".
    5. No repitas categorías ni cambies sus datos. Solo dales formato claro.

no hagas tablas
haz listas

Pregunta del usuario:
{pregunta}

Categorías encontradas (con similitud), no modifiques las categorias, son tal cual:
{categoria}

Chatbot (responde de manera clara y ordenada sin modificar categorias):
"""


modelo = OllamaLLM(model="llama3.2")

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | modelo



class generarRespuesta:

    def Responder(categoria, pregunta):
        try:
            respuesta = chain.invoke({"categoria": categoria, 'pregunta': pregunta})
            print("----------",respuesta, "-----------------")
            return respuesta
        except Exception as e:
            print('Error: \n', e)
