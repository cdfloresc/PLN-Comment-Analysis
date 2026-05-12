import pandas as pd
import re
import unicodedata
import logging
import time
from typing import Set

logger = logging.getLogger("nlp_etl")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(console_handler)


# Funciones de Limpieza y Procesamiento
def clean_text(text: str) -> str:
    if not isinstance(text, str) or pd.isna(text):
        return ""
    text = text.lower()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def is_noise(text: str, valid_short_words: Set[str]) -> bool:
    if not text:
        return True
    if len(text) <= 3:
        if text in valid_short_words:
            return False
        if text.isnumeric():
            return False
        return True
        
    words = text.split()
    for word in words:
        if len(word) >= 5 and not re.search(r'[aeiou]', word):
            return True
            
    return False

# Pipeline Principal (ETL)
def run_etl(input_path: str, output_path: str) -> pd.DataFrame:
    start_time = time.time()
    logger.info(f"Iniciando Fase 1: ETL y Limpieza. Archivo: {input_path}")
    
    try:
        # 1. Cargar datos
        logger.info("Cargando dataset en memoria (Pandas)...")
        # Especificamos dtype={'COMENTARIO': str} para optimizar y evitar warnings
        df = pd.read_csv(input_path, sep=';', on_bad_lines='skip', engine='c', dtype={'COMENTARIO': str})
        total_inicial = len(df)
        logger.info(f"Dataset cargado con éxito. Filas iniciales: {total_inicial:,}")
        
        if 'COMENTARIO' not in df.columns:
            raise ValueError("El dataset no contiene la columna 'COMENTARIO'")
            
        # 2. Normalización Vectorizada (apply sobre Pandas Series)
        logger.info("Aplicando normalización (minúsculas, tildes, caracteres especiales)...")
        df['texto_limpio'] = df['COMENTARIO'].apply(clean_text)
        
        # 3. Filtro de Ruido
        logger.info("Aplicando filtro de ruido y retención inteligente...")
        palabras_permitidas = {"si", "no", "ok", "ya", "ah", "eh", "uh", "u", "a", "q", "k", "xq", "pq", "oka", "yes"}
        df['es_ruido'] = df['texto_limpio'].apply(lambda x: is_noise(x, palabras_permitidas))
        
        df_filtrado = df[~df['es_ruido']].copy()
        filas_ruido = total_inicial - len(df_filtrado)
        logger.info(f"Filtro completado. Filas descartadas (basura/vacías): {filas_ruido:,}")
        
        # 4. Deduplicación y Cálculo de Frecuencia (CRÍTICO)
        logger.info("Iniciando deduplicación y cálculo de frecuencias (compresión del dataset)...")
        # Agrupamos por el texto limpio y contamos las ocurrencias
        df_agrupado = df_filtrado.groupby('texto_limpio').size().reset_index(name='frecuencia')
        
        # Ordenamos de mayor a menor frecuencia para que los más comunes salgan primero
        df_agrupado = df_agrupado.sort_values(by='frecuencia', ascending=False).reset_index(drop=True)
        
        # Renombramos para estandarizar
        df_agrupado.rename(columns={'texto_limpio': 'COMENTARIO'}, inplace=True)
        
        total_final = len(df_agrupado)
        tasa_compresion = (1 - (total_final / total_inicial)) * 100
        
        logger.info(f"Deduplicación exitosa.")
        logger.info(f"  -> Comentarios únicos resultantes: {total_final:,}")
        logger.info(f"  -> Tasa de compresión de memoria: {tasa_compresion:.2f}%")
        
        # 5. Guardar el resultado procesado
        logger.info(f"Guardando dataset limpio en: {output_path}")
        df_agrupado.to_csv(output_path, sep=';', index=False, encoding='utf-8')
        
        elapsed = time.time() - start_time
        logger.info(f"¡Fase 1 completada exitosamente en {elapsed:.2f} segundos!")
        
        return df_agrupado
        
    except Exception as e:
        logger.error(f"Error crítico en el pipeline ETL: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    # Prueba de ejecución local (esto no se ejecutará cuando FastAPI importe el módulo)
    INPUT_FILE = "REP_COMENTARIO2.csv"
    OUTPUT_FILE = "comentarios_limpios.csv"
    
    run_etl(INPUT_FILE, OUTPUT_FILE)
