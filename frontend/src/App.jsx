import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import useWebSocket from './hooks/useWebSocket';

function App() {
  const { 
    packets, 
    alerts, 
    stats, 
    isConnected, 
    connectionQuality,
    latestPacket 
  } = useWebSocket('ws://localhost:8000/ws/traffic');

  const [currentTime, setCurrentTime] = useState(new Date());

  // Update clock every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="h-screen flex flex-col bg-cyber-dark text-gray-200 font-sans relative">
      {/* Header */}
      <header className="glass-card m-4 p-4 flex justify-between items-center border-b-2 border-cyber-cyan/30">
        <div className="flex items-center space-x-4">
          <div className="text-3xl font-bold text-cyber-cyan glow-text tracking-wider">
            NETGUARD
            <span className="text-xs ml-2 font-mono text-cyber-cyan/60">v1.0</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-cyber-green animate-pulse' : 'bg-cyber-red'}`} />
            <span className="text-sm font-mono">
              {isConnected ? 'SECURE CONNECTION' : 'DISCONNECTED'}
            </span>
          </div>
        </div>
        <div className="flex items-center space-x-6">
          <div className="text-sm font-mono">
            <span className="text-cyber-cyan/60">PKTS: </span>
            <span className="text-cyber-cyan">{stats?.total_packets || 0}</span>
          </div>
          <div className="text-sm font-mono">
            <span className="text-cyber-red/60">THREATS: </span>
            <span className="text-cyber-red">{stats?.total_anomalies || 0}</span>
          </div>
          <div className="text-sm font-mono text-cyber-cyan">
            {currentTime.toLocaleTimeString()}
          </div>
        </div>
      </header>

      {/* Main Dashboard */}
      <main className="flex-1 mx-4 mb-4 overflow-hidden">
        {!isConnected && (
          <div className="bg-cyber-red/20 border border-cyber-red/30 rounded-lg p-4 mb-4 text-center">
            <p className="text-cyber-red font-mono">
              ⚠️ Disconnected from server. Attempting to reconnect...
            </p>
          </div>
        )}
        <Dashboard 
          packets={packets}
          alerts={alerts}
          stats={stats}
          isConnected={isConnected}
          latestPacket={latestPacket}
        />
      </main>

      {/* Scanline effect */}
      <div className="scanline pointer-events-none fixed inset-0 z-50 opacity-10" />
    </div>
  );
}

export default App;