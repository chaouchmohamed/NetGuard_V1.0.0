import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const COLORS = {
  ddos: '#ff2d55',
  port_scan: '#ffb800',
  syn_flood: '#ff6b00',
  brute_force: '#7b2eda',
  data_exfiltration: '#00f5ff',
  other: '#4a5568'
};

const AttackTypeChart = ({ stats }) => {
  const [data, setData] = useState([]);

  useEffect(() => {
    if (stats?.attack_type_counts) {
      const chartData = Object.entries(stats.attack_type_counts).map(([name, value]) => ({
        name: name.replace('_', ' ').toUpperCase(),
        value,
        color: COLORS[name] || COLORS.other
      }));
      setData(chartData);
    }
  }, [stats]);

  const total = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="h-full flex flex-col">
      <ResponsiveContainer width="100%" height="70%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={40}
            outerRadius={60}
            paddingAngle={2}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#0d1117',
              border: '1px solid #00f5ff40',
              borderRadius: '4px',
              color: '#00f5ff'
            }}
          />
          <Legend
            wrapperStyle={{
              fontSize: '10px',
              color: '#9ca3af'
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="text-center mt-2">
        <span className="text-2xl font-bold text-cyber-cyan">{total}</span>
        <span className="text-xs text-gray-500 ml-2">total attacks</span>
      </div>
    </div>
  );
};

export default AttackTypeChart;
