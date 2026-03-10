import React, { useRef, useEffect, useState } from 'react';
import { AlertCircle, Info } from 'lucide-react';

const PacketRow = ({ packet, isAnomaly }) => {
  const timestamp = packet.timestamp ? new Date(packet.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
  
  return (
    <tr className={`border-b border-cyber-cyan/10 hover:bg-cyber-cyan/5 transition-colors ${
      isAnomaly ? 'bg-cyber-red/10' : ''
    }`}>
      <td className="py-2 px-2 font-mono text-xs">{timestamp}</td>
      <td className="py-2 px-2 font-mono text-xs">{packet.src_ip || '0.0.0.0'}</td>
      <td className="py-2 px-2 font-mono text-xs">{packet.dst_ip || '0.0.0.0'}</td>
      <td className="py-2 px-2 font-mono text-xs">{packet.protocol_name || 'TCP'}</td>
      <td className="py-2 px-2 font-mono text-xs">{packet.packet_size || 0}</td>
      <td className="py-2 px-2 font-mono text-xs">{packet.dst_port || 0}</td>
      <td className="py-2 px-2">
        {isAnomaly ? (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-mono bg-cyber-red/20 text-cyber-red border border-cyber-red/30">
            <AlertCircle className="w-3 h-3 mr-1" />
            ATTACK
          </span>
        ) : (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-mono bg-cyber-green/20 text-cyber-green border border-cyber-green/30">
            NORMAL
          </span>
        )}
      </td>
    </tr>
  );
};

const LiveTrafficFeed = ({ packets }) => {
  const scrollRef = useRef(null);
  const [selectedPacket, setSelectedPacket] = useState(null);

  useEffect(() => {
    // Auto-scroll to bottom when new packets arrive
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [packets]);

  return (
    <>
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto font-mono text-sm"
      >
        <table className="w-full">
          <thead className="sticky top-0 bg-cyber-darker/90 backdrop-blur">
            <tr className="text-left text-xs text-cyber-cyan/70 border-b border-cyber-cyan/30">
              <th className="py-2 px-2 font-medium">TIME</th>
              <th className="py-2 px-2 font-medium">SOURCE IP</th>
              <th className="py-2 px-2 font-medium">DEST IP</th>
              <th className="py-2 px-2 font-medium">PROTO</th>
              <th className="py-2 px-2 font-medium">SIZE</th>
              <th className="py-2 px-2 font-medium">PORT</th>
              <th className="py-2 px-2 font-medium">STATUS</th>
            </tr>
          </thead>
          <tbody>
            {packets.length > 0 ? (
              packets.slice().reverse().map((packet, index) => (
                <PacketRow 
                  key={packet.id || index}
                  packet={packet}
                  isAnomaly={packet.is_anomaly || packet.attack_type}
                />
              ))
            ) : (
              <tr>
                <td colSpan="7" className="text-center py-8 text-gray-500">
                  <Info className="w-6 h-6 mx-auto mb-2" />
                  Waiting for network traffic...
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Packet Detail Modal */}
      {selectedPacket && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
          <div className="glass-card p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <h3 className="text-cyber-cyan text-xl font-bold mb-4">Packet Details</h3>
            <pre className="bg-cyber-darker p-4 rounded font-mono text-xs overflow-x-auto">
              {JSON.stringify(selectedPacket, null, 2)}
            </pre>
            <button 
              onClick={() => setSelectedPacket(null)}
              className="mt-4 px-4 py-2 bg-cyber-cyan/20 text-cyber-cyan rounded hover:bg-cyber-cyan/30"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default LiveTrafficFeed;