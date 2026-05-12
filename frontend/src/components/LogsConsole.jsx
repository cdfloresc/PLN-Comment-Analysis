import React, { useEffect, useRef } from 'react';

export default function LogsConsole({ logs, status }) {
    const endRef = useRef(null);

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    return (
        <div style={{ 
            background: '#020617', color: '#a7f3d0', padding: '24px', 
            borderRadius: '16px', height: '280px', overflowY: 'auto', 
            fontFamily: '"Fira Code", monospace', border: '1px solid rgba(255,255,255,0.05)',
            boxShadow: 'inset 0 0 20px rgba(0,0,0,0.5)'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: '15px', marginBottom: '15px' }}>
                <span style={{ color: '#94a3b8', fontWeight: '600', fontSize: '0.9rem', letterSpacing: '1px' }}>SYSTEM TERMINAL</span>
                <span style={{ 
                    color: status === 'processing' ? '#fbbf24' : status === 'completed' ? '#34d399' : '#64748b',
                    textTransform: 'uppercase',
                    fontSize: '0.75rem',
                    letterSpacing: '1.5px',
                    fontWeight: '700',
                    background: 'rgba(255,255,255,0.05)',
                    padding: '4px 10px',
                    borderRadius: '20px'
                }}>
                    STATUS: {status}
                </span>
            </div>
            {logs.length === 0 && <div style={{ color: '#475569', fontStyle: 'italic', fontSize: '13px' }}>Awaiting pipeline execution...</div>}
            {logs.map((log, i) => (
                <div key={i} style={{ marginBottom: '8px', fontSize: '13px', lineHeight: '1.5' }}>
                    <span style={{ color: '#3b82f6', marginRight: '8px' }}>&gt;</span>
                    {log}
                </div>
            ))}
            <div ref={endRef} />
        </div>
    );
}
