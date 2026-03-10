import React from 'react';
import StatsCards from './StatsCards';
import AnomalyChart from './AnomalyChart';
import LiveTrafficFeed from './LiveTrafficFeed';
import ThreatAlerts from './ThreatAlerts';

const Dashboard = ({ packets, alerts, stats, isConnected, latestPacket }) => {
  return (
    <div className="h-full grid grid-cols-12 gap-4">
      {/* Stats Cards - Top Row */}
      <div className="col-span-12">
        <StatsCards stats={stats} packets={packets} isConnected={isConnected} />
      </div>

      {/* Anomaly Chart - Middle Top */}
      <div className="col-span-8 h-64">
        <div className="glass-card p-4 h-full">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-cyber-cyan font-semibold tracking-wider">
              ANOMALY SCORE OVER TIME
            </h3>
            <div className="text-xs font-mono text-cyber-cyan/60">
              threshold: 0.5
            </div>
          </div>
          <AnomalyChart packets={packets} />
        </div>
      </div>

      {/* Threat Level Indicator - Middle Top Right */}
      <div className="col-span-4 h-64">
        <div className="glass-card p-4 h-full flex flex-col">
          <h3 className="text-cyber-cyan font-semibold tracking-wider mb-4">
            CURRENT THREAT LEVEL
          </h3>
          <div className="flex-1 flex flex-col items-center justify-center">
            <div className={`text-6xl font-bold mb-4 ${
              stats?.total_anomalies > 100 ? 'text-cyber-red' :
              stats?.total_anomalies > 50 ? 'text-orange-500' :
              stats?.total_anomalies > 20 ? 'text-cyber-amber' :
              'text-cyber-green'
            } glow-text`}>
              {stats?.total_anomalies > 100 ? 'CRITICAL' :
               stats?.total_anomalies > 50 ? 'HIGH' :
               stats?.total_anomalies > 20 ? 'ELEVATED' :
               'NORMAL'}
            </div>
            <div className="w-full bg-cyber-darker rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-500 ${
                  stats?.total_anomalies > 100 ? 'bg-cyber-red' :
                  stats?.total_anomalies > 50 ? 'bg-orange-500' :
                  stats?.total_anomalies > 20 ? 'bg-cyber-amber' :
                  'bg-cyber-green'
                }`}
                style={{ width: `${Math.min((stats?.total_anomalies || 0) / 2, 100)}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-4 font-mono">
              {stats?.anomaly_rate?.toFixed(2)}% anomaly rate
            </p>
          </div>
        </div>
      </div>

      {/* Live Traffic Feed - Bottom Left */}
      <div className="col-span-7 h-[calc(100vh-28rem)]">
        <div className="glass-card p-4 h-full flex flex-col">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-cyber-cyan font-semibold tracking-wider">
              LIVE TRAFFIC FEED
            </h3>
            <span className="text-xs font-mono text-cyber-cyan/60">
              {packets.length} packets
            </span>
          </div>
          <LiveTrafficFeed packets={packets} />
        </div>
      </div>

      {/* Threat Alerts - Bottom Right */}
      <div className="col-span-5 h-[calc(100vh-28rem)]">
        <div className="glass-card p-4 h-full flex flex-col">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-cyber-red font-semibold tracking-wider">
              THREAT ALERTS
            </h3>
            <span className="text-xs font-mono text-cyber-red/60">
              {alerts.length} active
            </span>
          </div>
          <ThreatAlerts alerts={alerts} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;