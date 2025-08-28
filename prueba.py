import json


with open('categorias.json', "r", encoding="utf-8") as j:
    datos = json.load(j)
    busqueda = 'cerveza'
    diccionario = []

    for actividad in datos['actividades_economicas']:
       
        for categoria in actividad['categorias']:
            for palabra in categoria['palabras_clave']:
                if busqueda.lower() in palabra.lower():
                    diccionario.append(
                        {
                            "Actividad": actividad['actividad'],
                            "codigo": categoria['codigo'],
                            "descripcion": categoria['descripcion']
                        }
                    )
                    break

print("guardados: \n")

for i in diccionario:
    print(i)


from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")
emb1 = model.encode("huarache", convert_to_tensor=True)
emb2 = model.encode("huaraches", convert_to_tensor=True)

sim = util.cos_sim(emb1, emb2)
print("Similitud huarache vs huaraches:", sim.item())
                