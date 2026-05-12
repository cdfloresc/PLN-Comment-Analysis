import React from 'react';

export default function PipelineStats({ status, stats }) {
    
    const getStatusColor = () => {
        if (status === 'procesando') return '#0284c7'; // Blue
        if (status === 'completado') return '#10b981'; // Emerald
        if (status === 'error') return '#ef4444'; // Red
        return '#94a3b8'; // Slate
    };

    return (
        <div style={{ 
            background: 'rgba(30, 41, 59, 0.6)', 
            backdropFilter: 'blur(12px)',
            color: '#f8fafc', padding: '24px', 
            borderRadius: '16px', height: '100%', 
            border: '1px solid rgba(255, 255, 255, 0.08)',
            boxShadow: '0 20px 40px rgba(0,0,0,0.2)',
            display: 'flex', flexDirection: 'column'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255, 255, 255, 0.1)', paddingBottom: '15px', marginBottom: '20px' }}>
                <span style={{ color: '#f8fafc', fontWeight: '600', fontSize: '1.1rem', letterSpacing: '0.5px' }}>
                    Analíticas del Modelo
                </span>
                <span style={{ 
                    color: getStatusColor(),
                    textTransform: 'uppercase',
                    fontSize: '0.75rem',
                    letterSpacing: '1.5px',
                    fontWeight: '800',
                    background: 'rgba(0,0,0,0.2)',
                    padding: '6px 12px',
                    borderRadius: '20px',
                    border: `1px solid ${getStatusColor()}40`
                }}>
                    {status}
                </span>
            </div>
            
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '15px', justifyContent: 'center' }}>
                {!stats ? (
                    <div style={{ textAlign: 'center', color: '#94a3b8', fontStyle: 'italic' }}>
                        {status === 'procesando' ? 'Calculando matrices NLP en tiempo real...' : 'Esperando inicialización...'}
                    </div>
                ) : (
                    <>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', background: 'rgba(15, 23, 42, 0.4)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.03)' }}>
                            <span style={{ color: '#94a3b8', fontWeight: 500, fontSize: '0.95rem' }}>Dataset Deduplicado</span>
                            <span style={{ color: '#38bdf8', fontWeight: 700, fontSize: '1.2rem' }}>{stats.rows_processed.toLocaleString()} filas</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', background: 'rgba(15, 23, 42, 0.4)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.03)' }}>
                            <span style={{ color: '#94a3b8', fontWeight: 500, fontSize: '0.95rem' }}>Dimensiones del Vector</span>
                            <span style={{ color: '#38bdf8', fontWeight: 700, fontSize: '1.2rem' }}>{stats.features_dimension.toLocaleString()}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', background: 'rgba(15, 23, 42, 0.4)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.03)' }}>
                            <span style={{ color: '#94a3b8', fontWeight: 500, fontSize: '0.95rem' }}>Tiempo de Ejecución</span>
                            <span style={{ color: '#38bdf8', fontWeight: 700, fontSize: '1.2rem' }}>{stats.time_seconds} s</span>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
