import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import squareform
import fastcluster
import logging
import time
import json
import gc
from collections import Counter

# Configuración del Logger Modular
logger = logging.getLogger("nlp_engine")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(console_handler)

# Fase 2: Motor de Clustering NLP
def load_data(file_path: str, max_rows: int = None) -> pd.DataFrame:
    logger.info(f"Cargando dataset limpio desde: {file_path}")
    df = pd.read_csv(file_path, sep=';', dtype={'COMENTARIO': str, 'frecuencia': int})
    df = df.dropna(subset=['COMENTARIO'])
    
    if max_rows and len(df) > max_rows:
        logger.warning(f"ATENCIÓN: Limitando dataset a las top {max_rows} filas.")
        df = df.head(max_rows)
        
    logger.info(f"Total de comentarios a procesar: {len(df)}")
    return df

def vectorize_text(texts: list, metric: str):
    logger.info(f"Iniciando vectorización. Estrategia seleccionada: {metric.upper()}")
    if metric.lower() == 'coseno':
        vectorizer = TfidfVectorizer(max_df=0.85, min_df=2)
        sparse_matrix = vectorizer.fit_transform(texts)
    elif metric.lower() == 'jaccard':
        vectorizer = CountVectorizer(binary=True, ngram_range=(1, 2), min_df=2)
        sparse_matrix = vectorizer.fit_transform(texts)
    else:
        raise ValueError("La métrica debe ser 'Coseno' o 'Jaccard'")
        
    num_features = sparse_matrix.shape[1]
    logger.info(f"Vectorización finalizada. Dimensiones: {sparse_matrix.shape[0]} x {num_features}.")
    return sparse_matrix

def compute_distances(sparse_matrix, metric: str) -> np.ndarray:
    logger.info("Calculando matriz de distancias densa (O(N^2)). Consumo alto de RAM...")
    if metric.lower() == 'coseno':
        dist_matrix = pairwise_distances(sparse_matrix, metric='cosine', n_jobs=-1)
    elif metric.lower() == 'jaccard':
        dense_bool_matrix = sparse_matrix.toarray().astype(bool)
        dist_matrix = pairwise_distances(dense_bool_matrix, metric='jaccard', n_jobs=-1)
        del dense_bool_matrix
        
    dist_matrix = np.clip(dist_matrix, 0, 1)
    np.fill_diagonal(dist_matrix, 0)
    
    logger.info("Convirtiendo a matriz condensada para optimizar clustering...")
    condensed_dist = squareform(dist_matrix, checks=False)
    
    del dist_matrix
    gc.collect() 
    
    logger.info("Matriz condensada generada exitosamente. Matriz densa eliminada de RAM.")
    return condensed_dist

def execute_clustering(condensed_dist) -> np.ndarray:
    logger.info("Ejecutando fastcluster.linkage...")
    Z = fastcluster.linkage(condensed_dist, method='average')
    logger.info("Clustering jerárquico completado.")
    return Z

def build_dendrogram_tree(Z: np.ndarray, labels: list, frequencies: list) -> dict:
    logger.info("Estructurando árbol jerárquico y calculando top keywords (TF-IDF heurístico)...")
    n_samples = len(labels)
    tree_nodes = {}
    
    # 1. Instanciar hojas
    for i in range(n_samples):
        words = [w for w in labels[i].split() if len(w) > 3]
        word_counts = Counter({w: int(frequencies[i]) for w in words})
        
        tree_nodes[i] = {
            "name": labels[i],
            "value": int(frequencies[i]),
            "is_leaf": True,
            "words": word_counts
        }
        
    for i, merge in enumerate(Z):
        node_id = n_samples + i
        left_id = int(merge[0])
        right_id = int(merge[1])
        dist = float(merge[2])
        
        left_node = tree_nodes[left_id]
        right_node = tree_nodes[right_id]
        
        merged_words = left_node["words"] + right_node["words"]
        top_words = [w for w, count in merged_words.most_common(3)]
        
        cluster_name = f"Grupo: {', '.join(top_words)}" if top_words else f"Cluster_{node_id}"
        
        left_node.pop("words", None)
        right_node.pop("words", None)
        
        tree_nodes[node_id] = {
            "name": cluster_name,
            "dist": dist,
            "children": [left_node, right_node],
            "is_leaf": False,
            "words": merged_words 
        }
        
    root_node_id = 2 * n_samples - 2
    root = tree_nodes[root_node_id]
    root.pop("words", None)
    
    logger.info("Árbol JSON con etiquetas semánticas completado.")
    return root

def run_nlp_pipeline(input_path: str, metric: str = 'coseno', max_rows: int = 15000) -> dict:
    start_time = time.time()
    logger.info(f"--- INICIO FASE 2: MOTOR NLP ({metric.upper()}) ---")
    try:
        df = load_data(input_path, max_rows=max_rows)
        texts = df['COMENTARIO'].tolist()
        frequencies = df['frecuencia'].tolist()
        
        sparse_matrix = vectorize_text(texts, metric=metric)
        condensed_dist = compute_distances(sparse_matrix, metric=metric)
        Z = execute_clustering(condensed_dist)
        tree_dict = build_dendrogram_tree(Z, texts, frequencies)
        
        elapsed = time.time() - start_time
        logger.info(f"--- FASE 2 COMPLETADA EN {elapsed:.2f} SEGUNDOS ---")
        return {
            "tree": tree_dict,
            "stats": {
                "rows_processed": len(texts),
                "features_dimension": sparse_matrix.shape[1],
                "time_seconds": round(elapsed, 2)
            }
        }
    except Exception as e:
        logger.error(f"Error en Motor NLP: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    pass
