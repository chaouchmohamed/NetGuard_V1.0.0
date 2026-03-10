/**
 * Format bytes to human readable string
 */
export const formatBytes = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

/**
 * Format timestamp to relative time
 */
export const timeAgo = (timestamp) => {
  const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);
  
  const intervals = {
    year: 31536000,
    month: 2592000,
    week: 604800,
    day: 86400,
    hour: 3600,
    minute: 60,
    second: 1
  };
  
  for (const [unit, secondsInUnit] of Object.entries(intervals)) {
    const interval = Math.floor(seconds / secondsInUnit);
    if (interval >= 1) {
      return interval + ' ' + unit + (interval === 1 ? '' : 's') + ' ago';
    }
  }
  
  return 'just now';
};

/**
 * Truncate IP address for display
 */
export const truncateIP = (ip, maxLength = 15) => {
  if (ip.length <= maxLength) return ip;
  return ip.substring(0, maxLength - 3) + '...';
};

/**
 * Get color class based on severity
 */
export const getSeverityColor = (severity) => {
  const colors = {
    CRITICAL: 'text-cyber-red border-cyber-red/30 bg-cyber-red/20',
    HIGH: 'text-orange-500 border-orange-500/30 bg-orange-500/20',
    MEDIUM: 'text-cyber-amber border-cyber-amber/30 bg-cyber-amber/20',
    LOW: 'text-cyber-cyan border-cyber-cyan/30 bg-cyber-cyan/20'
  };
  
  return colors[severity] || colors.LOW;
};

/**
 * Calculate statistics from packets
 */
export const calculateStats = (packets) => {
  const total = packets.length;
  const anomalies = packets.filter(p => p.is_anomaly || p.attack_type).length;
  
  const attackTypes = {};
  packets.forEach(p => {
    if (p.attack_type) {
      attackTypes[p.attack_type] = (attackTypes[p.attack_type] || 0) + 1;
    }
  });
  
  return {
    total,
    anomalies,
    anomalyRate: total > 0 ? (anomalies / total) * 100 : 0,
    attackTypes
  };
};

/**
 * Generate random ID
 */
export const generateId = () => {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
};
