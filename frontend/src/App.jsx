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
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-sm font-mono">
              {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
            </span>
          </div>
        </div>
        <div className="flex items-center space-x-6">
          <div className="text-sm font-mono">
            <span className="text-cyber-cyan/60">PKTS: </span>
            <span className="text-cyber-cyan">{stats?.total_packets || 0}</span>
          </div>
          <div className="text-sm font-mono">
            <span className="text-red-500/60">THREATS: </span>
            <span className="text-red-500">{stats?.total_anomalies || 0}</span>
          </div>
          <div className="text-sm font-mono text-cyber-cyan">
            {currentTime.toLocaleTimeString()}
          </div>
        </div>
      </header>

      {/* Connection Status Banner */}
      {!isConnected && (
        <div className="mx-4 mb-2 p-3 bg-red-500/20 border border-red-500/30 rounded-lg text-center">
          <p className="text-red-500 font-mono animate-pulse">
            ⚠️ Disconnected from server. Attempting to reconnect...
          </p>
        </div>
      )}

      {/* Main Dashboard */}
      <main className="flex-1 mx-4 mb-4 overflow-hidden">
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