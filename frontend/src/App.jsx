import React, { useState, useEffect } from 'react';
import PipelineStats from './components/PipelineStats';
import DendrogramChart from './components/DendrogramChart';
import TreemapChart from './components/TreemapChart';
import './App.css';

const API_BASE = 'http://localhost:8000';

export default function App() {
    const [metric, setMetric] = useState('coseno');
    const [status, setStatus] = useState('en espera');
    const [stats, setStats] = useState(null);
    const [treeData, setTreeData] = useState(null);
    const [isPolling, setIsPolling] = useState(false);
    const [activeTab, setActiveTab] = useState('dendrogram');

    const handleStart = async () => {
        try {
            const res = await fetch(`${API_BASE}/procesar`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ metric, max_rows: 15000 })
            });
            if (res.ok) {
                setStatus('procesando');
                setStats(null);
                setTreeData(null);
                setIsPolling(true);
            } else {
                const err = await res.json();
                alert(`Error de API: ${err.detail}`);
            }
        } catch (e) {
            alert('Error de red. Verifica que tu backend FastAPI esté activo.');
        }
    };

    useEffect(() => {
        let interval;
        if (isPolling) {
            interval = setInterval(async () => {
                try {
                    const res = await fetch(`${API_BASE}/logs`);
                    const data = await res.json();
                    
                    let estadoActual = data.status;
                    if (estadoActual === 'idle') estadoActual = 'en espera';
                    if (estadoActual === 'processing') estadoActual = 'procesando';
                    if (estadoActual === 'completed') estadoActual = 'completado';
                    if (estadoActual === 'error') estadoActual = 'error';

                    setStatus(estadoActual);
                    if (data.stats) {
                        setStats(data.stats);
                    }

                    if (data.status === 'completed') {
                        setIsPolling(false);
                        fetchTreeData();
                    } else if (data.status === 'error') {
                        setIsPolling(false);
                        alert("El proceso falló. Por favor reinicia el sistema.");
                    }
                } catch (e) {
                    console.error("Error en polling", e);
                }
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [isPolling]);

    const fetchTreeData = async () => {
        try {
            const res = await fetch(`${API_BASE}/dendrograma`);
            if (res.ok) {
                const data = await res.json();
                setTreeData(data);
            }
        } catch (e) {
            console.error("Error obteniendo datos", e);
        }
    };

    return (
        <div className="dashboard-container">
            <header className="header">
                <h1>Clustering de PNL Empresarial</h1>
                <p>Agrupación semántica y análisis jerárquico de distancias</p>
            </header>
            
            <div className="control-panel-wrapper">
                <div className="glass-card">
                    <h3>Configuración del Pipeline</h3>
                    <div className="form-group">
                        <label>Métrica de Distancia</label>
                        <select 
                            value={metric} 
                            onChange={e => setMetric(e.target.value)} 
                            className="custom-select"
                            disabled={status === 'procesando'}
                        >
                            <option value="coseno">Similitud del Coseno (Vectorizador TF-IDF)</option>
                            <option value="jaccard">Distancia de Jaccard (N-Gramas Binarios)</option>
                        </select>
                    </div>
                    
                    <button 
                        onClick={handleStart} 
                        disabled={status === 'procesando'}
                        className="btn-primary"
                    >
                        {status === 'procesando' ? 'Procesando Pipeline NLP...' : 'Iniciar Procesamiento'}
                    </button>
                </div>
                
                <div className="logs-wrapper">
                    <PipelineStats status={status} stats={stats} />
                </div>
            </div>

            {treeData && (
                <div className="visualization-section">
                    <div className="tabs-container">
                        <button 
                            className={`tab-btn ${activeTab === 'dendrogram' ? 'active' : ''}`}
                            onClick={() => setActiveTab('dendrogram')}
                        >
                            Dendrograma Jerárquico
                        </button>
                        <button 
                            className={`tab-btn ${activeTab === 'treemap' ? 'active' : ''}`}
                            onClick={() => setActiveTab('treemap')}
                        >
                            Mapa de Árbol Semántico (Treemap)
                        </button>
                    </div>

                    <div className="chart-container">
                        {activeTab === 'dendrogram' ? (
                            <DendrogramChart data={treeData} />
                        ) : (
                            <TreemapChart data={treeData} />
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
