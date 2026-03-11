import { useState, useEffect, useRef } from 'react';

const useWebSocket = (url) => {
  const [packets, setPackets] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({
    total_packets: 0,
    total_anomalies: 0,
    anomaly_rate: 0,
    attack_type_counts: {}
  });
  const [isConnected, setIsConnected] = useState(false);
  const [latestPacket, setLatestPacket] = useState(null);

  const ws = useRef(null);
  const reconnectTimeout = useRef(null);

  useEffect(() => {
    const connectWebSocket = () => {
      console.log(`🔌 Connecting to WebSocket: ${url}`);
      
      try {
        ws.current = new WebSocket(url);
        
        ws.current.onopen = () => {
          console.log('✅ WebSocket connected successfully!');
          setIsConnected(true);
        };
        
        ws.current.onclose = (event) => {
          console.log(`❌ WebSocket closed: ${event.code} - ${event.reason || 'No reason'}`);
          setIsConnected(false);
          
          // Try to reconnect after 3 seconds
          reconnectTimeout.current = setTimeout(() => {
            console.log('🔄 Attempting to reconnect...');
            connectWebSocket();
          }, 3000);
        };
        
        ws.current.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
        };
        
        ws.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'packet') {
              // Update packets (keep last 100)
              setPackets(prev => {
                const newPackets = [data.packet, ...prev];
                return newPackets.slice(0, 100);
              });

              setLatestPacket(data.packet);
              setStats(data.stats);
              
              // Create alert if anomaly
              if (data.prediction?.is_anomaly) {
                const alert = {
                  id: `alert-${Date.now()}-${Math.random()}`,
                  timestamp: data.timestamp,
                  severity: data.prediction.severity || 'MEDIUM',
                  attack_type: data.prediction.attack_type,
                  description: `${data.prediction.attack_type || 'Anomaly'} detected from ${data.packet.src_ip}`,
                  source_ip: data.packet.src_ip,
                  destination_ip: data.packet.dst_ip,
                  anomaly_score: data.prediction.anomaly_score,
                  confidence: data.prediction.confidence
                };

                setAlerts(prev => {
                  const newAlerts = [alert, ...prev];
                  return newAlerts.slice(0, 30);
                });
              }
            }
          } catch (error) {
            console.error('Error parsing message:', error);
          }
        };
      } catch (error) {
        console.error('Error creating WebSocket:', error);
        reconnectTimeout.current = setTimeout(connectWebSocket, 3000);
      }
    };

    connectWebSocket();

    // Cleanup
    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, [url]);

  return {
    packets,
    alerts,
    stats,
    isConnected,
    latestPacket
  };
};

export default useWebSocket;