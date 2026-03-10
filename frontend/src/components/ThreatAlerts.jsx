import React, { useRef, useEffect } from 'react';
import { AlertTriangle, Skull, Server, Activity } from 'lucide-react';

const severityConfig = {
  CRITICAL: {
    bg: 'bg-cyber-red/20',
    border: 'border-cyber-red/30',
    text: 'text-cyber-red',
    icon: Skull,
    glow: 'shadow-[0_0_10px_rgba(255,45,85,0.5)]'
  },
  HIGH: {
    bg: 'bg-orange-500/20',
    border: 'border-orange-500/30',
    text: 'text-orange-500',
    icon: AlertTriangle,
    glow: ''
  },
  MEDIUM: {
    bg: 'bg-cyber-amber/20',
    border: 'border-cyber-amber/30',
    text: 'text-cyber-amber',
    icon: AlertTriangle,
    glow: ''
  },
  LOW: {
    bg: 'bg-cyber-cyan/20',
    border: 'border-cyber-cyan/30',
    text: 'text-cyber-cyan',
    icon: Activity,
    glow: ''
  }
};

const AlertCard = ({ alert }) => {
  const config = severityConfig[alert.severity] || severityConfig.LOW;
  const Icon = config.icon;
  
  const timeAgo = (timestamp) => {
    if (!timestamp) return 'just now';
    const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    return `${Math.floor(seconds / 3600)}h ago`;
  };

  return (
    <div className={`${config.bg} border ${config.border} rounded-lg p-3 mb-2 animate-slide-in ${config.glow}`}>
      <div className="flex items-start">
        <Icon className={`w-4 h-4 ${config.text} mt-1 mr-2`} />
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <span className={`text-xs font-mono ${config.text} font-bold`}>
              {alert.severity}
            </span>
            <span className="text-xs text-gray-500 font-mono">
              {timeAgo(alert.timestamp)}
            </span>
          </div>
          <p className="text-sm mt-1">{alert.description || 'Anomaly detected'}</p>
          <div className="flex items-center mt-2 text-xs text-gray-400 font-mono">
            <Server className="w-3 h-3 mr-1" />
            {alert.source_ip || '0.0.0.0'} → {alert.destination_ip || '0.0.0.0'}
          </div>
          <div className="mt-2 w-full bg-cyber-darker rounded-full h-1">
            <div 
              className={`h-1 rounded-full ${config.text} bg-current`}
              style={{ width: `${(alert.anomaly_score || 0) * 100}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

const ThreatAlerts = ({ alerts }) => {
  const scrollRef = useRef(null);

  useEffect(() => {
    // Auto-scroll to top when new alerts arrive
    if (scrollRef.current && alerts.length > 0) {
      scrollRef.current.scrollTop = 0;
    }
  }, [alerts]);

  return (
    <div 
      ref={scrollRef}
      className="flex-1 overflow-y-auto pr-2"
    >
      {alerts.length === 0 ? (
        <div className="flex items-center justify-center h-32 text-gray-600">
          <Activity className="w-4 h-4 mr-2" />
          No threats detected
        </div>
      ) : (
        alerts.map((alert) => (
          <AlertCard key={alert.id} alert={alert} />
        ))
      )}
    </div>
  );
};

export default ThreatAlerts;