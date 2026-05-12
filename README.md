# PLN-Comment-Analysis

Proyecto de Procesamiento de Lenguaje Natural (NLP) diseñado para agrupar (clustering) grandes volúmenes de comentarios utilizando vectorización TF-IDF y Agrupamiento Jerárquico Aglomerativo (usando Enlace de Ward y distancia Euclidiana). El proyecto cuenta además con una API en FastAPI y un Dashboard interactivo en React/Vite para visualizar los resultados (Dendrogramas y Treemaps).

## Estructura del Proyecto

El repositorio está dividido en dos partes principales:
1. **Backend (Python / FastAPI):** Procesa los datos, limpia los comentarios, vectoriza el texto y genera los clusters.
2. **Frontend (React / Vite):** Interfaz de usuario para visualizar los análisis en tiempo real.

## 🛠️ Requisitos y Librerías

### Para el Backend (Python)
Asegúrate de tener **Python 3.8+** instalado. Las librerías principales utilizadas son:
- `fastapi`: Framework web para construir la API.
- `uvicorn`: Servidor ASGI para ejecutar la API.
- `pandas` y `numpy`: Manipulación y análisis de datos.
- `scikit-learn`: Para cálculos de TF-IDF y agrupamiento jerárquico (`AgglomerativeClustering`).
- `scipy`: Para el cálculo de distancias y la creación del árbol jerárquico (`scipy.cluster.hierarchy`).
- `spacy`: Para el proceso de lematización y limpieza del texto mediante expresiones regulares.

### Para el Frontend (Node.js)
Asegúrate de tener **Node.js (v16+)** instalado.
- `react` y `react-dom`
- `vite`
- `echarts` y `echarts-for-react`: Para las gráficas de Dendrograma y Treemap.
- `axios` (opcional, para las peticiones HTTP)

---

## 🚀 Guía de Instalación y Ejecución

### 1. Configuración del Backend

1. **Abrir la terminal en la raíz del proyecto:**
   Asegúrate de estar en `d:\Universidad\Ing. Sistemas\9no Semestre\PROCESAMIENTO DE LENGUAJE NATURAL\Unidad1`.

2. **Crear y activar un entorno virtual (Recomendado):**
   ```bash
   python -m venv .venv
   
   # En Windows:
   .venv\Scripts\activate
   ```

3. **Instalar las dependencias:**
   (Si tienes un archivo `requirements.txt`, ejecuta `pip install -r requirements.txt`. Si no, instala las necesarias manualmente):
   ```bash
   pip install fastapi uvicorn pandas numpy scikit-learn scipy spacy
   python -m spacy download es_core_news_sm
   ```

4. **Iniciar el servidor Backend:**
   Ejecuta el archivo principal (generalmente `main.py`) usando Uvicorn:
   ```bash
   uvicorn main:app --reload
   ```
   *La API estará disponible en `http://localhost:8000` (puedes ver la documentación en `http://localhost:8000/docs`).*

---

### 2. Configuración del Frontend

1. **Abrir otra terminal y navegar a la carpeta del frontend:**
   ```bash
   cd frontend
   ```

2. **Instalar las dependencias de Node:**
   ```bash
   npm install
   ```

3. **Iniciar el servidor de desarrollo del Frontend:**
   ```bash
   npm run dev
   ```
   *El dashboard interactivo estará disponible generalmente en `http://localhost:5173`.*

---

## 💡 Notas Adicionales
- Para que el clustering funcione correctamente, asegúrate de tener el dataset base (ej. `comentarios_limpios.csv`) en la raíz del proyecto para que `nlp_engine.py` o `etl.py` puedan procesarlo.
- Se ha configurado `.gitignore` para excluir archivos pesados, entornos virtuales y cachés.
