import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

export default function DendrogramChart({ data }) {
    const chartRef = useRef(null);

    useEffect(() => {
        if (!data || !chartRef.current) return;

        const chart = echarts.init(chartRef.current);
        
        const option = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'item',
                triggerOn: 'mousemove',
                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                textStyle: { color: '#f8fafc' },
                borderWidth: 1,
                borderColor: '#334155',
                padding: 16,
                borderRadius: 8,
                formatter: function (info) {
                    if (info.data.is_leaf) {
                        return `<div style="max-width:350px; white-space:normal;">
                            <div style="color:#94a3b8; font-size:11px; letter-spacing:1px; margin-bottom:6px;">COMENTARIO</div>
                            <div style="font-size:14px; font-weight:500; margin-bottom:12px; line-height: 1.4;">${info.name}</div>
                            <div style="color:#94a3b8; font-size:11px; letter-spacing:1px; margin-bottom:4px;">FRECUENCIA</div>
                            <div style="font-size:15px; color:#38bdf8; font-weight:bold;">${info.value}</div>
                        </div>`;
                    }
                    return `<div style="padding: 4px;">
                        <div style="color:#94a3b8; font-size:11px; letter-spacing:1px; margin-bottom:6px;">DATOS DEL CLÚSTER</div>
                        <div style="font-size:14px; font-weight:500; margin-bottom:10px;">${info.name}</div>
                        <div style="font-size:13px; color:#cbd5e1;">Distancia: <span style="color:#f8fafc; font-weight:bold;">${info.data.dist ? info.data.dist.toFixed(4) : 0}</span></div>
                    </div>`;
                }
            },
            series: [
                {
                    type: 'tree',
                    data: [data],
                    orient: 'TB', // Top to Bottom representation like classical dendrograms
                    edgeShape: 'polyline', // Orthogonal right-angle lines
                    initialTreeDepth: 3, 
                    top: '8%',
                    left: '5%',
                    bottom: '22%', // Leave space for vertical text at leaves
                    right: '5%',
                    symbol: 'emptyCircle',
                    symbolSize: 7,
                    itemStyle: { 
                        color: '#ffffff', 
                        borderColor: '#38bdf8',
                        borderWidth: 2
                    },
                    lineStyle: { 
                        color: '#cbd5e1', 
                        width: 1.5,
                        type: 'solid'
                    },
                    label: {
                        position: 'top',
                        verticalAlign: 'middle',
                        align: 'center',
                        fontSize: 12,
                        color: '#334155',
                        backgroundColor: '#f8fafc',
                        padding: [3, 6],
                        borderRadius: 4,
                        distance: 8
                    },
                    leaves: {
                        label: {
                            position: 'bottom',
                            rotate: -90, // Rotated vertical text for bottom leaves
                            verticalAlign: 'middle',
                            align: 'left',
                            color: '#0f172a',
                            fontWeight: 500,
                            distance: 12,
                            fontSize: 11
                        }
                    },
                    expandAndCollapse: true,
                    animationDuration: 550,
                    animationDurationUpdate: 750,
                    roam: true
                }
            ]
        };

        chart.setOption(option);

        const handleResize = () => chart.resize();
        window.addEventListener('resize', handleResize);

        return () => {
            chart.dispose();
            window.removeEventListener('resize', handleResize);
        };
    }, [data]);

    return (
        <div 
            ref={chartRef} 
            style={{ width: '100%', height: '70vh' }} 
        />
    );
}
