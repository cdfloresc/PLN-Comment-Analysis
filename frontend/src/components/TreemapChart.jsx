import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

export default function TreemapChart({ data }) {
    const chartRef = useRef(null);

    useEffect(() => {
        if (!data || !chartRef.current) return;

        const chart = echarts.init(chartRef.current);
        
        const option = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'item',
                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                textStyle: { color: '#f8fafc' },
                borderWidth: 1,
                borderColor: '#334155',
                padding: 16,
                borderRadius: 8,
                formatter: function (info) {
                    var value = info.value;
                    var name = info.name;
                    return `<div style="max-width:350px; white-space:normal;">
                        <div style="color:#94a3b8; font-size:11px; letter-spacing:1px; margin-bottom:6px;">NODO SEMÁNTICO</div>
                        <div style="font-size:14px; font-weight:500; margin-bottom:12px; line-height: 1.4;">${echarts.format.encodeHTML(name)}</div>
                        <div style="color:#94a3b8; font-size:11px; letter-spacing:1px; margin-bottom:4px;">FRECUENCIA (PESO)</div>
                        <div style="font-size:15px; color:#38bdf8; font-weight:bold;">${value}</div>
                    </div>`;
                }
            },
            series: [{
                type: 'treemap',
                data: [data],
                roam: true,
                nodeClick: 'link', // click to zoom into a node
                breadcrumb: {
                    show: true,
                    top: 'bottom',
                    itemStyle: {
                        color: '#334155',
                        textStyle: { color: '#f8fafc' }
                    }
                },
                itemStyle: {
                    borderColor: '#fff',
                    borderWidth: 1,
                    gapWidth: 1
                },
                levels: [
                    {
                        itemStyle: { borderColor: '#777', borderWidth: 0, gapWidth: 2 }
                    },
                    {
                        itemStyle: { borderColor: '#aaa', borderWidth: 2, gapWidth: 2 },
                        colorSaturation: [0.35, 0.5]
                    },
                    {
                        itemStyle: { borderColor: '#ccc', borderWidth: 1, gapWidth: 1 },
                        colorSaturation: [0.35, 0.5]
                    }
                ]
            }]
        };

        chart.setOption(option);
        const handleResize = () => chart.resize();
        window.addEventListener('resize', handleResize);
        return () => {
            chart.dispose();
            window.removeEventListener('resize', handleResize);
        };
    }, [data]);

    return <div ref={chartRef} style={{ width: '100%', height: '70vh' }} />;
}
