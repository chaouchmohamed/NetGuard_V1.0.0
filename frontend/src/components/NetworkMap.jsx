import React, { useEffect, useRef, useState } from 'react';

const NetworkMap = ({ packets }) => {
  const canvasRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const updateDimensions = () => {
      if (canvasRef.current) {
        const container = canvasRef.current.parentElement;
        setDimensions({
          width: container.clientWidth,
          height: container.clientHeight
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    if (!canvasRef.current || dimensions.width === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    canvas.width = dimensions.width;
    canvas.height = dimensions.height;

    // Clear canvas
    ctx.fillStyle = '#0a0e1a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Get unique IPs from recent packets
    const recentPackets = packets.slice(-20);
    const sourceIPs = [...new Set(recentPackets.map(p => p.src_ip))].slice(0, 8);
    const destIPs = [...new Set(recentPackets.map(p => p.dst_ip))].slice(0, 8);

    // Draw nodes (source IPs on left, dest IPs on right)
    const nodeRadius = 6;
    const leftX = 100;
    const rightX = canvas.width - 100;
    
    // Draw connections first (so they appear behind nodes)
    recentPackets.forEach((packet) => {
      const sourceIndex = sourceIPs.indexOf(packet.src_ip);
      const destIndex = destIPs.indexOf(packet.dst_ip);
      
      if (sourceIndex !== -1 && destIndex !== -1) {
        const startY = 50 + (sourceIndex * 30);
        const endY = 50 + (destIndex * 30);
        
        // Calculate threat level for color
        const isAnomaly = packet.is_anomaly || packet.attack_type;
        
        // Draw connection line
        ctx.beginPath();
        ctx.moveTo(leftX + nodeRadius, startY);
        ctx.lineTo(rightX - nodeRadius, endY);
        
        // Gradient based on threat level
        const gradient = ctx.createLinearGradient(leftX, startY, rightX, endY);
        if (isAnomaly) {
          gradient.addColorStop(0, '#ff2d55');
          gradient.addColorStop(1, '#ff2d5580');
          ctx.lineWidth = 2;
        } else {
          gradient.addColorStop(0, '#00f5ff');
          gradient.addColorStop(1, '#00f5ff40');
          ctx.lineWidth = 1;
        }
        
        ctx.strokeStyle = gradient;
        ctx.stroke();
        
        // Add animation (moving dot) for recent packets
        if (packet === recentPackets[recentPackets.length - 1]) {
          const progress = (Date.now() % 2000) / 2000;
          const x = leftX + nodeRadius + (rightX - leftX - 2 * nodeRadius) * progress;
          const y = startY + (endY - startY) * progress;
          
          ctx.beginPath();
          ctx.arc(x, y, 3, 0, Math.PI * 2);
          ctx.fillStyle = isAnomaly ? '#ff2d55' : '#00f5ff';
          ctx.shadowColor = isAnomaly ? '#ff2d55' : '#00f5ff';
          ctx.shadowBlur = 10;
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      }
    });

    // Draw source nodes (left side)
    sourceIPs.forEach((ip, index) => {
      const y = 50 + (index * 30);
      
      // Node glow
      ctx.shadowColor = '#00f5ff';
      ctx.shadowBlur = 10;
      
      // Node circle
      ctx.beginPath();
      ctx.arc(leftX, y, nodeRadius, 0, Math.PI * 2);
      ctx.fillStyle = '#00f5ff20';
      ctx.fill();
      ctx.strokeStyle = '#00f5ff';
      ctx.lineWidth = 2;
      ctx.stroke();
      
      // Node label
      ctx.shadowBlur = 0;
      ctx.font = '10px JetBrains Mono';
      ctx.fillStyle = '#00f5ff';
      ctx.textAlign = 'right';
      ctx.fillText(ip, leftX - 15, y + 3);
    });

    // Draw destination nodes (right side)
    destIPs.forEach((ip, index) => {
      const y = 50 + (index * 30);
      
      // Node glow
      ctx.shadowColor = '#00f5ff';
      ctx.shadowBlur = 10;
      
      // Node circle
      ctx.beginPath();
      ctx.arc(rightX, y, nodeRadius, 0, Math.PI * 2);
      ctx.fillStyle = '#00f5ff20';
      ctx.fill();
      ctx.strokeStyle = '#00f5ff';
      ctx.lineWidth = 2;
      ctx.stroke();
      
      // Node label
      ctx.shadowBlur = 0;
      ctx.font = '10px JetBrains Mono';
      ctx.fillStyle = '#00f5ff';
      ctx.textAlign = 'left';
      ctx.fillText(ip, rightX + 15, y + 3);
    });

  }, [packets, dimensions]);

  return (
    <canvas
      ref={canvasRef}
      className="w-full h-full"
      style={{ background: '#0a0e1a' }}
    />
  );
};

export default NetworkMap;
