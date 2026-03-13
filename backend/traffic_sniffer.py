import time
import uuid
import logging
import threading
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Callable
from collections import deque

logger = logging.getLogger(__name__)

# Try to import scapy
try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP, conf
    conf.verb = 0  # Suppress scapy output
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    logger.warning("scapy not installed. Run: pip install scapy")


class RealTrafficSniffer:
    """
    Captures real network traffic and outputs packets in the same
    format as TrafficSimulator — zero changes needed downstream.
    """

    PROTOCOLS = {
        6: 'TCP',
        17: 'UDP',
        1: 'ICMP',
    }

    COMMON_PORTS = {
        80: 'HTTP', 443: 'HTTPS', 53: 'DNS', 22: 'SSH',
        3389: 'RDP', 21: 'FTP', 25: 'SMTP', 110: 'POP3',
        143: 'IMAP', 8080: 'HTTP-ALT', 8443: 'HTTPS-ALT',
    }

    def __init__(self, interface: Optional[str] = None, packet_callback: Optional[Callable] = None):
        """
        Args:
            interface:       Network interface to sniff on (e.g. 'eth0', 'wlan0').
                             None = scapy picks the default interface.
            packet_callback: Optional function called with each parsed packet dict.
        """
        if not SCAPY_AVAILABLE:
            raise RuntimeError("scapy is required. Install it with: pip install scapy")

        self.interface = interface
        self.packet_callback = packet_callback

        # Shared state (thread-safe via deque / simple counters)
        self._packet_queue: deque = deque(maxlen=10000)
        self._packet_count = 0
        self._last_packet_time = time.time()

        # Rate tracking (1-second sliding window)
        self._packet_rate_window: deque = deque()
        self._byte_rate_window: deque = deque()

        # Connection tracking (mirrors simulator)
        self._active_connections: Dict[str, Dict] = {}
        self._connections_lock = threading.Lock()

        # Sniffer thread
        self._sniff_thread: Optional[threading.Thread] = None
        self._running = False

    # ------------------------------------------------------------------
    # Public API  (same shape as TrafficSimulator)
    # ------------------------------------------------------------------

    def start(self):
        """Start sniffing in a background thread."""
        if self._running:
            return
        self._running = True
        self._sniff_thread = threading.Thread(target=self._sniff_loop, daemon=True)
        self._sniff_thread.start()
        logger.info(f"RealTrafficSniffer started on interface: {self.interface or 'default'}")

    def stop(self):
        """Stop the background sniffer."""
        self._running = False
        logger.info("RealTrafficSniffer stopped")

    def get_packet(self) -> Optional[Dict]:
        """Pop one packet from the queue (non-blocking). Returns None if empty."""
        try:
            return self._packet_queue.popleft()
        except IndexError:
            return None

    def get_packet_nowait(self) -> Optional[Dict]:
        """Alias for get_packet()."""
        return self.get_packet()

    def get_current_rates(self) -> Tuple[float, float]:
        """Return (packets_per_second, bytes_per_second) — same as simulator."""
        now = time.time()
        cutoff = now - 1.0
        pps = sum(1 for t in self._packet_rate_window if t > cutoff)
        bps = sum(s for t, s in self._byte_rate_window if t > cutoff)
        return float(pps), float(bps)

    @property
    def packet_count(self) -> int:
        return self._packet_count

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _sniff_loop(self):
        """Background thread: continuously sniff packets."""
        sniff(
            iface=self.interface,
            prn=self._handle_raw_packet,
            store=False,
            stop_filter=lambda _: not self._running,
        )

    def _handle_raw_packet(self, raw):
        """Called by scapy for every captured packet."""
        if not raw.haslayer(IP):
            return  # skip non-IP (ARP, etc.)

        parsed = self._parse_packet(raw)
        if parsed is None:
            return

        self._packet_queue.append(parsed)

        if self.packet_callback:
            try:
                self.packet_callback(parsed)
            except Exception as e:
                logger.error(f"packet_callback error: {e}")

    def _parse_packet(self, raw) -> Optional[Dict]:
        """
        Convert a scapy packet into the same dict format
        that TrafficSimulator.generate_packet() returns.
        """
        try:
            ip = raw[IP]
            current_time = time.time()

            src_ip = ip.src
            dst_ip = ip.dst
            protocol = ip.proto
            ttl = ip.ttl
            packet_size = len(raw)

            # Ports & flags
            src_port, dst_port, flags = self._extract_transport(raw, protocol)

            # Inter-arrival time
            time_since_last = current_time - self._last_packet_time
            self._last_packet_time = current_time

            # Rate windows
            self._update_rate_windows(current_time, packet_size)
            packets_per_second, bytes_per_second = self.get_current_rates()

            # Connection tracking
            conn_id = f"{src_ip}:{src_port}-{dst_ip}:{dst_port}"
            with self._connections_lock:
                if conn_id not in self._active_connections:
                    self._active_connections[conn_id] = {
                        'start_time': current_time,
                        'packets': 0,
                    }
                self._active_connections[conn_id]['packets'] += 1
                connection_duration = current_time - self._active_connections[conn_id]['start_time']

                # Prune old connections
                if len(self._active_connections) > 1000:
                    oldest = sorted(
                        self._active_connections.items(),
                        key=lambda x: x[1]['start_time']
                    )[:500]
                    for cid, _ in oldest:
                        del self._active_connections[cid]

            self._packet_count += 1

            return {
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'timestamp_epoch': current_time,
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'src_port': src_port,
                'dst_port': dst_port,
                'protocol': protocol,
                'protocol_name': self.PROTOCOLS.get(protocol, 'UNKNOWN'),
                'packet_size': packet_size,
                'ttl': ttl,
                'flags': flags,
                'inter_arrival_time': time_since_last,
                'packets_per_second': packets_per_second,
                'bytes_per_second': bytes_per_second,
                'connection_duration': connection_duration,
                # Real traffic has no ground-truth attack label.
                # The ML model fills this in after prediction.
                'attack_type': None,
                'service': self.COMMON_PORTS.get(dst_port, 'unknown'),
            }

        except Exception as e:
            logger.debug(f"Failed to parse packet: {e}")
            return None

    def _extract_transport(self, raw, protocol: int) -> Tuple[int, int, Dict]:
        """Extract ports and TCP flags from the transport layer."""
        flags = {k: False for k in ('syn', 'ack', 'fin', 'rst', 'psh', 'urg')}
        src_port = 0
        dst_port = 0

        if protocol == 6 and raw.haslayer(TCP):  # TCP
            tcp = raw[TCP]
            src_port = tcp.sport
            dst_port = tcp.dport
            flag_int = tcp.flags
            flags['syn'] = bool(flag_int & 0x02)
            flags['ack'] = bool(flag_int & 0x10)
            flags['fin'] = bool(flag_int & 0x01)
            flags['rst'] = bool(flag_int & 0x04)
            flags['psh'] = bool(flag_int & 0x08)
            flags['urg'] = bool(flag_int & 0x20)

        elif protocol == 17 and raw.haslayer(UDP):  # UDP
            udp = raw[UDP]
            src_port = udp.sport
            dst_port = udp.dport

        # ICMP has no ports — leave as 0

        return src_port, dst_port, flags

    def _update_rate_windows(self, current_time: float, packet_size: int):
        cutoff = current_time - 1.0
        # Prune old entries
        while self._packet_rate_window and self._packet_rate_window[0] < cutoff:
            self._packet_rate_window.popleft()
        while self._byte_rate_window and self._byte_rate_window[0][0] < cutoff:
            self._byte_rate_window.popleft()

        self._packet_rate_window.append(current_time)
        self._byte_rate_window.append((current_time, packet_size))
