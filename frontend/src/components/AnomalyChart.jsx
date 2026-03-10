import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Area
} from 'recharts';

const AnomalyChart = ({ packets }) => {
  const [data, setData] = useState([]);

  useEffect(() => {
    // Transform packets into chart data
    const chartData = packets.slice(-60).map((packet, index) => ({
      time: index,
      score: packet.anomaly_score || (packet.attack_type ? 0.8 : 0.1),
      timestamp: packet.timestamp ? new Date(packet.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString()
    }));

    // If no packets, show some sample data
    if (chartData.length === 0) {
      const sampleData = [];
      for (let i = 0; i < 20; i++) {
        sampleData.push({
          time: i,
          score: 0.1 + Math.random() * 0.2,
          timestamp: new Date().toLocaleTimeString()
        });
      }
      setData(sampleData);
    } else {
      setData(chartData);
    }
  }, [packets]);

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
        <defs>
          <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#00f5ff" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#00f5ff" stopOpacity={0}/>
          </linearGradient>
        </defs>
        
        <CartesianGrid strokeDasharray="3 3" stroke="#00f5ff20" />
        
        <XAxis 
          dataKey="time" 
          stroke="#00f5ff60"
          tick={{ fill: '#00f5ff80', fontSize: 10 }}
        />
        
        <YAxis 
          domain={[0, 1]} 
          stroke="#00f5ff60"
          tick={{ fill: '#00f5ff80', fontSize: 10 }}
        />
        
        <Tooltip
          contentStyle={{
            backgroundColor: '#0d1117',
            border: '1px solid #00f5ff40',
            borderRadius: '4px',
            color: '#00f5ff'
          }}
          labelStyle={{ color: '#00f5ff' }}
          formatter={(value) => [value.toFixed(3), 'Anomaly Score']}
          labelFormatter={(label) => `Packet ${label}`}
        />
        
        <ReferenceLine 
          y={0.5} 
          stroke="#ff2d55" 
          strokeDasharray="3 3"
          label={{ value: 'Threshold', fill: '#ff2d55', fontSize: 10 }}
        />
        
        <Area
          type="monotone"
          dataKey="score"
          stroke="none"
          fill="url(#colorGradient)"
        />
        
        <Line
          type="monotone"
          dataKey="score"
          stroke="#00f5ff"
          strokeWidth={2}
          dot={(props) => {
            const { cx, cy, payload } = props;
            if (payload.score > 0.5) {
              return (
                <circle
                  cx={cx}
                  cy={cy}
                  r={4}
                  fill="#ff2d55"
                  stroke="none"
                  style={{ filter: 'drop-shadow(0 0 5px #ff2d55)' }}
                />
              );
            }
            return (
              <circle
                cx={cx}
                cy={cy}
                r={2}
                fill="#00f5ff"
                stroke="none"
              />
            );
          }}
          activeDot={{ r: 6, fill: '#00f5ff', stroke: '#fff' }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default AnomalyChart;