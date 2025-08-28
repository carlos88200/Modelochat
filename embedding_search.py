from sentence_transformers import SentenceTransformer
import json
import numpy as np

class EmbeddingSearch:
    def __init__(self, categorias_path="categorias.json", model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.categorias = []
        self.embeddings = []
        self.actividades = []
        self.load_categorias(categorias_path)
        
    def load_categorias(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for actividad in data['actividades_economicas']:
            self.actividades.append({
                "actividad": actividad["actividad"],
                "clave": actividad["clave"]
            })
            for categoria in actividad['categorias']:
                for palabra in categoria['palabras_clave']:
                    self.categorias.append({
                        "actividad": actividad["actividad"],
                        "claves": actividad["clave"],
                        "categoria_codigo": categoria['codigo'],
                        "categoria_descripcion": categoria['descripcion'],
                        "palabra_clave": palabra
                    })
        # Crear embeddings para todas las palabras clave
        textos = [c['palabra_clave'] for c in self.categorias]
        self.embeddings = self.model.encode(textos, convert_to_numpy=True)
        
    def buscar_categoria(self, texto, intencion, top_k=10):
        if texto and intencion:
            texto_embedding = self.model.encode([texto], convert_to_numpy=True)[0]

            # Filtrar categorías que tengan la intención en sus claves
            #indices_validos = [i for i, c in enumerate(self.categorias) if intencion in c['claves']]
            indices_validos = []

            for i, c in enumerate(self.categorias):
                if intencion in c['claves']:
                    indices_validos.append(i)

           
            if not indices_validos:
                resp = f'No se encontro {texto} en {intencion}, pero se encontro estas posibilidades: '
                return []
            # Calcular similitud coseno solo con categorías válidas
            embeddings_validos = self.embeddings[indices_validos]
            
            # Normalizar para coseno
            texto_norm = texto_embedding / np.linalg.norm(texto_embedding)
            emb_norms = embeddings_validos / np.linalg.norm(embeddings_validos, axis=1, keepdims=True)
            


            similitudes = np.dot(emb_norms, texto_norm)
            
            # Obtener top_k índices de mayor similitud
            top_indices_relativos = np.argsort(similitudes)[::-1][:top_k]
            top_indices = [indices_validos[i] for i in top_indices_relativos]
            
            resultados = []
            for idx in top_indices:
                cat = self.categorias[idx]
                resultados.append({
                    "actividad": cat['actividad'],
                    "categoria_codigo": cat['categoria_codigo'],
                    "categoria_descripcion": cat['categoria_descripcion'],
                    "palabra_clave": cat['palabra_clave'],
                    "similitud": float(similitudes[top_indices_relativos[top_indices.index(idx)]])
                })
            #print("resultados embeding", resultados)
            return resultados
        elif texto:
            texto_embedding = self.model.encode([texto], convert_to_numpy=True)[0]

            texto_norm = texto_embedding / np.linalg.norm(texto_embedding)
            emb_norms = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)
            
            similitudes = np.dot(emb_norms, texto_norm)
            top_indices = np.argsort(similitudes)[::-1][:top_k]
            resultadosPDSR = []
            for idx in top_indices:
                cat = self.categorias[idx]
                resultadosPDSR.append({
                    "actividad": cat['actividad'],
                    "categoria_codigo": cat['categoria_codigo'],
                    "categoria_descripcion": cat['categoria_descripcion'],
                    "palabra_clave": cat['palabra_clave'],
                    "similitud": float(similitudes[idx])
                })
            return resultadosPDSR
        
        elif intencion:
            
            texto_embedding = self.model.encode([texto], convert_to_numpy=True)[0]

            indices_validos = []

            for i, c in enumerate(self.categorias):
                if intencion in c['claves']:
                    indices_validos.append(i)

            if not indices_validos:
                indices_validos = []

            embedings_indValidos = self.embeddings[indices_validos]
            # Normalizar para coseno
            texto_norm = texto_embedding / np.linalg.norm(texto_embedding)
            emb_norms = embeddings_validos / np.linalg.norm(embeddings_validos, axis=1, keepdims=True)
            


            similitudes = np.dot(emb_norms, texto_norm)
            
            # Obtener top_k índices de mayor similitud
            top_indices_relativos = np.argsort(similitudes)[::-1][:top_k]
            top_indices = [indices_validos[i] for i in top_indices_relativos]
            
            resultados = []



