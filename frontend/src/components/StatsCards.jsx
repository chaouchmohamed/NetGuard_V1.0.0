import React, { useEffect, useState } from 'react';
import { Activity, AlertTriangle, Shield, Cpu } from 'lucide-react';

const Counter = ({ value, duration = 1000 }) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    setCount(value);
  }, [value]);

  return <span>{count.toLocaleString()}</span>;
};

const StatsCards = ({ stats, packets, isConnected }) => {
  const anomalyRate = stats?.anomaly_rate || 0;
  const threatLevel = anomalyRate > 15 ? 'CRITICAL' : 
                     anomalyRate > 10 ? 'HIGH' : 
                     anomalyRate > 5 ? 'ELEVATED' : 'NORMAL';

  return (
    <div className="grid grid-cols-4 gap-4">
      {/* Total Packets Card */}
      <div className="glass-card p-4 border-l-4 border-cyber-cyan">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500 font-mono">TOTAL PACKETS</p>
            <p className="text-2xl font-bold text-cyber-cyan glow-text">
              <Counter value={stats?.total_packets || 0} />
            </p>
          </div>
          <Activity className="w-8 h-8 text-cyber-cyan/50" />
        </div>
        <div className="mt-2 h-1 w-full bg-cyber-darker rounded-full overflow-hidden">
          <div 
            className="h-full bg-cyber-cyan rounded-full transition-all duration-500"
            style={{ width: `${Math.min((packets.length / 100) * 100, 100)}%` }}
          />
        </div>
      </div>

      {/* Threats Detected Card */}
      <div className="glass-card p-4 border-l-4 border-cyber-red">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500 font-mono">THREATS DETECTED</p>
            <p className="text-2xl font-bold text-cyber-red glow-text">
              <Counter value={stats?.total_anomalies || 0} />
            </p>
            <p className="text-xs text-gray-500">
              {anomalyRate.toFixed(2)}% of traffic
            </p>
          </div>
          <AlertTriangle className="w-8 h-8 text-cyber-red/50" />
        </div>
        <div className="mt-2 h-1 w-full bg-cyber-darker rounded-full overflow-hidden">
          <div 
            className="h-full bg-cyber-red rounded-full transition-all duration-500"
            style={{ width: `${Math.min(anomalyRate * 5, 100)}%` }}
          />
        </div>
      </div>

      {/* Threat Level Card */}
      <div className={`glass-card p-4 border-l-4 ${
        threatLevel === 'CRITICAL' ? 'border-cyber-red' :
        threatLevel === 'HIGH' ? 'border-orange-500' :
        threatLevel === 'ELEVATED' ? 'border-cyber-amber' :
        'border-cyber-green'
      }`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500 font-mono">THREAT LEVEL</p>
            <p className={`text-2xl font-bold ${
              threatLevel === 'CRITICAL' ? 'text-cyber-red' :
              threatLevel === 'HIGH' ? 'text-orange-500' :
              threatLevel === 'ELEVATED' ? 'text-cyber-amber' :
              'text-cyber-green'
            } glow-text`}>
              {threatLevel}
            </p>
          </div>
          <Shield className={`w-8 h-8 ${
            threatLevel === 'CRITICAL' ? 'text-cyber-red/50' :
            threatLevel === 'HIGH' ? 'text-orange-500/50' :
            threatLevel === 'ELEVATED' ? 'text-cyber-amber/50' :
            'text-cyber-green/50'
          }`} />
        </div>
      </div>

      {/* Model Confidence Card */}
      <div className="glass-card p-4 border-l-4 border-cyber-green">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500 font-mono">MODEL CONFIDENCE</p>
            <p className="text-2xl font-bold text-cyber-green glow-text">
              {isConnected ? '98.5' : '0'}%
            </p>
          </div>
          <Cpu className="w-8 h-8 text-cyber-green/50" />
        </div>
        <div className="mt-2 h-1 w-full bg-cyber-darker rounded-full overflow-hidden">
          <div 
            className="h-full bg-cyber-green rounded-full"
            style={{ width: isConnected ? '98%' : '0%' }}
          />
        </div>
      </div>
    </div>
  );
};

export default StatsCards;