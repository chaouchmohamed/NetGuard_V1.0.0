import { useState, useEffect, useRef, useCallback } from 'react';

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
  const [connectionQuality, setConnectionQuality] = useState('good');
  const [latestPacket, setLatestPacket] = useState(null);

  const ws = useRef(null);
  const reconnectTimeout = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 50;

  const connect = useCallback(() => {
    // List of URLs to try
    const urlsToTry = [
      url,
      'ws://localhost:8000/ws/traffic',
      'ws://127.0.0.1:8000/ws/traffic',
      'ws://0.0.0.0:8000/ws/traffic'
    ];
    
    // Remove duplicates
    const uniqueUrls = [...new Set(urlsToTry)];
    let currentUrlIndex = 0;
    
    function attemptConnection() {
      if (currentUrlIndex >= uniqueUrls.length) {
        console.error('❌ All WebSocket connection attempts failed');
        setIsConnected(false);
        
        // Retry after delay
        reconnectTimeout.current = setTimeout(() => {
          reconnectAttempts.current += 1;
          if (reconnectAttempts.current < maxReconnectAttempts) {
            console.log(`🔄 Reconnect attempt ${reconnectAttempts.current}/${maxReconnectAttempts}`);
            currentUrlIndex = 0;
            attemptConnection();
          }
        }, 5000);
        return;
      }
      
      const currentUrl = uniqueUrls[currentUrlIndex];
      console.log(`🔌 Attempting WebSocket connection to ${currentUrl} (attempt ${currentUrlIndex + 1}/${uniqueUrls.length})`);
      
      try {
        if (ws.current) {
          ws.current.close();
        }
        
        ws.current = new WebSocket(currentUrl);
        
        ws.current.onopen = () => {
          console.log(`✅ WebSocket connected to ${currentUrl}`);
          setIsConnected(true);
          reconnectAttempts.current = 0;
          setConnectionQuality('good');
        };
        
        ws.current.onclose = (event) => {
          console.log(`❌ WebSocket closed: ${event.code} - ${event.reason || 'No reason'}`);
          setIsConnected(false);
          
          // Try next URL
          currentUrlIndex++;
          setTimeout(attemptConnection, 1000);
        };
        
        ws.current.onerror = (error) => {
          console.error(`❌ WebSocket error with ${currentUrl}:`, error);
          // Don't increment here, let onclose handle it
        };
        
        ws.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'packet') {
              // Update packets (keep last 200)
              setPackets(prev => {
                const newPackets = [...prev, data.packet];
                if (newPackets.length > 200) {
                  return newPackets.slice(-200);
                }
                return newPackets;
              });

              setLatestPacket(data.packet);

              // Update stats
              setStats(data.stats);

              // Update alerts if anomaly
              if (data.prediction?.is_anomaly) {
                const alert = {
                  id: `alert-${Date.now()}-${Math.random()}`,
                  timestamp: data.timestamp,
                  severity: data.prediction.severity || 'MEDIUM',
                  attack_type: data.prediction.attack_type,
                  description: `Anomaly detected from ${data.packet.src_ip}`,
                  source_ip: data.packet.src_ip,
                  destination_ip: data.packet.dst_ip,
                  anomaly_score: data.prediction.anomaly_score,
                  confidence: data.prediction.confidence
                };

                setAlerts(prev => {
                  const newAlerts = [alert, ...prev];
                  if (newAlerts.length > 50) {
                    return newAlerts.slice(0, 50);
                  }
                  return newAlerts;
                });
              }
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
      } catch (error) {
        console.error('Error creating WebSocket:', error);
        currentUrlIndex++;
        setTimeout(attemptConnection, 1000);
      }
    }
    
    attemptConnection();
  }, [url]);

  useEffect(() => {
    connect();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, [connect]);

  return {
    packets,
    alerts,
    stats,
    isConnected,
    connectionQuality,
    latestPacket
  };
};

export default useWebSocket;