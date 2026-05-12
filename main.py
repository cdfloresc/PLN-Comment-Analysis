import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Importar los módulos que construimos en las Fases 1 y 2
import etl
import nlp_engine

app = FastAPI(
    title="NLP Clustering Enterprise API",
    description="API RESTful asíncrona para procesamiento de texto, vectorización y clustering.",
    version="1.0.0"
)

# ==========================================
# 1. Configuración de CORS
# ==========================================
# Fundamental para que React.js/Next.js (Frontend) pueda comunicarse sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción cambiar por ej: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2. Interceptor de Logs en Memoria
# ==========================================
# Permite que el endpoint GET /logs capture los logs que emiten etl.py y nlp_engine.py
log_buffer: List[str] = []

class MemoryLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_buffer.append(log_entry)
        # Prevenir fugas de memoria limitando el buffer
        if len(log_buffer) > 500:
            log_buffer.pop(0)

# Acoplamos el handler en memoria a los loggers de nuestros módulos
memory_handler = MemoryLogHandler()
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', datefmt='%H:%M:%S')
memory_handler.setFormatter(formatter)

logger_etl = logging.getLogger("nlp_etl")
logger_nlp = logging.getLogger("nlp_engine")
logger_etl.addHandler(memory_handler)
logger_nlp.addHandler(memory_handler)

# ==========================================
# 3. Estado Global (State Management Simple)
# ==========================================
process_state = {
    "status": "idle", # Posibles: idle, processing, completed, error
    "tree_data": None,
    "stats": None
}

class ProcessConfig(BaseModel):
    metric: str = 'coseno'
    max_rows: int = 15000

# ==========================================
# 4. Tarea en Background (Evita bloqueo)
# ==========================================
def execute_pipeline_background(config: ProcessConfig):
    """
    Función que ejecuta los procesos pesados sin colapsar el hilo principal de la API REST.
    """
    global process_state
    
    try:
        # FASE 1: Limpieza
        input_file = "REP_COMENTARIO2.csv"
        cleaned_file = "comentarios_limpios.csv"
        etl.run_etl(input_file, cleaned_file)
        
        # FASE 2: Clustering
        result = nlp_engine.run_nlp_pipeline(cleaned_file, metric=config.metric, max_rows=config.max_rows)
        
        # Éxito: Guardar datos y actualizar estado
        process_state["tree_data"] = result["tree"]
        process_state["stats"] = result["stats"]
        process_state["status"] = "completed"
        logger_nlp.info("=== PROCESO FINALIZADO. DENDROGRAMA LISTO PARA EL FRONTEND ===")
        
    except Exception as e:
        process_state["status"] = "error"
        logger_nlp.error(f"Fallo Crítico en el Pipeline: {str(e)}", exc_info=True)


# ==========================================
# 5. Endpoints de la API
# ==========================================

@app.post("/procesar")
async def start_processing(config: ProcessConfig, background_tasks: BackgroundTasks):
    """
    Dispara la ejecución del pipeline completo.
    """
    global process_state, log_buffer
    
    if process_state["status"] == "processing":
        raise HTTPException(status_code=400, detail="Ya existe un proceso en ejecución. Espera a que termine.")
        
    # Reset de estado para una nueva ejecución
    process_state["status"] = "processing"
    process_state["tree_data"] = None
    process_state["stats"] = None
    log_buffer.clear()
    
    # Encolar a BackgroundTasks
    background_tasks.add_task(execute_pipeline_background, config)
    
    return {
        "message": "Proceso inicializado en background",
        "config": config.dict()
    }

@app.get("/logs")
async def get_status_and_logs():
    """
    Endpoint de Polling para el Frontend.
    """
    return {
        "status": process_state["status"],
        "logs": log_buffer,
        "stats": process_state["stats"]
    }

import sys
import json
from fastapi.responses import Response
sys.setrecursionlimit(100000) # Previene RecursionError en árboles inmensamente profundos

@app.get("/dendrograma")
async def get_dendrogram_data():
    """
    Entrega el árbol jerárquico listo para renderizar.
    """
    if process_state["status"] == "processing":
        raise HTTPException(status_code=202, detail="El árbol aún se está procesando.")
    elif process_state["status"] == "error":
        raise HTTPException(status_code=500, detail="Ocurrió un error en la generación del árbol.")
    elif process_state["status"] == "idle":
        raise HTTPException(status_code=404, detail="No se ha iniciado ningún procesamiento.")
        
    if not process_state["tree_data"]:
        raise HTTPException(status_code=500, detail="Los datos del árbol no se encontraron.")
        
    # Usamos json.dumps y Response directo para saltar el jsonable_encoder de FastAPI
    # que causa RecursionError en estructuras anidadas masivas.
    tree_str = json.dumps(process_state["tree_data"], ensure_ascii=False)
    return Response(content=tree_str, media_type="application/json")

if __name__ == "__main__":
    import uvicorn
    # Comando útil para levantar localmente: uvicorn main:app --reload
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
