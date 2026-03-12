
<div align="center">

```
 ███╗   ██╗███████╗████████╗ ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗ 
 ████╗  ██║██╔════╝╚══██╔══╝██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗
 ██╔██╗ ██║█████╗     ██║   ██║  ███╗██║   ██║███████║██████╔╝██║  ██║
 ██║╚██╗██║██╔══╝     ██║   ██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║
 ██║ ╚████║███████╗   ██║   ╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
 ╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝
```

# 🛡️ NetGuard — Network Attack Detection System

**Real-time network intrusion detection powered by Machine Learning**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4.3-38BDF8?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4.2-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-FFD700?style=for-the-badge)](LICENSE)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Testing with Attack Generator](#-testing-with-attack-generator)
- [Detected Attack Types](#-detected-attack-types)
- [API Documentation](#-api-documentation)
- [Tech Stack](#-tech-stack)
- [Docker Deployment](#-docker-deployment)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Performance](#-performance)
- [Contributing](#-contributing)

---

## 📖 Overview

**NetGuard** is a production-ready network attack detection system that uses **Isolation Forest** machine learning to identify anomalous network traffic patterns in real-time. It features a cyberpunk-themed dashboard with live traffic visualization, threat alerts, anomaly scoring charts, and a network flow map — all updating live via WebSocket.

No root privileges required. No real network access needed. Fully synthetic traffic simulation built-in.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **ML Detection** | Isolation Forest model trained on 10,000 synthetic normal traffic samples |
| ⚡ **Real-time Stream** | WebSocket-based live feed updating every 500ms |
| 🎯 **5 Attack Types** | DDoS, Port Scan, SYN Flood, Brute Force, Data Exfiltration |
| 📊 **Live Dashboard** | Anomaly chart, attack distribution donut, network flow map |
| 🔔 **Severity Alerts** | 4-tier classification: LOW / MEDIUM / HIGH / CRITICAL |
| 💾 **Persistent Storage** | SQLite database for full alert history and traffic logs |
| 🔄 **Auto-train** | Model trains automatically on first run if no `.pkl` exists |
| 🎮 **Attack Simulator** | Built-in script to generate real test attacks |
| 🐳 **Docker Ready** | One-command deployment with Docker Compose |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                          NETGUARD SYSTEM                             │
├─────────────────────┬───────────────────────────┬────────────────────┤
│     FRONTEND        │         BACKEND            │      ML CORE       │
│  React + Vite       │        FastAPI             │  Isolation Forest  │
│  Tailwind CSS       │                            │                    │
├─────────────────────┼───────────────────────────┼────────────────────┤
│  • Dashboard        │  • WebSocket Server        │  • Anomaly Score   │
│  • Live Charts      │  • REST API (7 endpoints)  │  • 13 Features     │
│  • Threat Alerts    │  • Traffic Simulator       │  • Auto-training   │
│  • Network Map      │  • Alert Manager           │  • Model Save/Load │
│  • Stats Cards      │  • SQLite via SQLAlchemy   │                    │
└─────────────────────┴───────────────────────────┴────────────────────┘
         ↕ WebSocket (ws://localhost:8000/ws/traffic)
         ↕ REST API  (http://localhost:8000/api/*)
```

---

## 🚀 Quick Start

### Prerequisites

- Python **3.8+**
- Node.js **16+**
- npm or yarn

### 1. Clone the repository

```bash
git clone https://github.com/chaouchmohamed/NetGuard_V1.0.0.git
cd NetGuard_V1.0.0
```

### 2. Run setup script

**Linux / macOS:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

**Windows:**
```batch
scripts\setup.bat
```

This will:
- Create a Python virtual environment
- Install all Python dependencies
- Train the ML model (`detector.pkl`)
- Install all Node.js packages

### 3. Start the application

**Linux / macOS:**
```bash
./scripts/run_dev.sh
```

**Windows:**
```batch
scripts\run_dev.bat
```

### 4. Open the dashboard

| Service | URL |
|---------|-----|
| 🖥️ Frontend Dashboard | http://localhost:5173 |
| ⚙️ Backend API | http://localhost:8000 |
| 📚 API Docs (Swagger) | http://localhost:8000/docs |

---

## 🎮 Testing with Attack Generator

Run the attack generator in a **separate terminal** to simulate real attacks:

```bash
# Activate virtual environment first
source backend/venv/bin/activate      # Linux/macOS
# or
backend\venv\Scripts\activate         # Windows

python3 scripts/generate_attacks.py
```

Then choose an attack mode from the interactive menu:

```
[1] 🔴  DDoS Attack
[2] 🔵  Port Scan
[3] 🟡  SYN Flood
[4] 🟠  Brute Force
[5] 🟣  Data Exfiltration
[6] 🎯  All Attacks (sequential)
[7] 🎲  Mixed Traffic (50% attacks)
```



---

## 📊 Detected Attack Types

| Attack | Icon | Description | Severity |
|--------|------|-------------|----------|
| **DDoS** | 🌊 | High-volume traffic from many source IPs targeting one destination | 🔴 CRITICAL |
| **Port Scan** | 🔍 | Sequential port probing with SYN-only packets | 🟠 HIGH |
| **SYN Flood** | ⚡ | Rapid TCP SYN packets with no ACK responses | 🟠 HIGH |
| **Brute Force** | 🔨 | Repeated connection attempts to SSH (22) or RDP (3389) | 🟡 MEDIUM |
| **Data Exfiltration** | 📤 | Large sustained transfers to unusual external ports | 🔴 CRITICAL |

---

## 📡 API Documentation

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | System health & model status |
| `GET` | `/api/alerts` | Paginated list of all alerts |
| `GET` | `/api/alerts/recent` | Last 20 alerts |
| `GET` | `/api/stats` | Overall statistics summary |
| `GET` | `/api/traffic/history` | Last 500 traffic logs |
| `GET` | `/api/model/info` | Model metadata (trained_at, n_samples) |
| `POST` | `/api/model/retrain` | Trigger background model retraining |

### WebSocket

```
ws://localhost:8000/ws/traffic
```

Each message payload:
```json
{
  "packet": { "src_ip": "...", "dst_ip": "...", "protocol": "TCP", ... },
  "prediction": {
    "is_anomaly": true,
    "anomaly_score": 0.94,
    "confidence": 0.88,
    "severity": "CRITICAL"
  },
  "stats": {
    "total_packets": 1234,
    "total_anomalies": 87,
    "anomaly_rate": 0.07,
    "attack_type_counts": { "ddos": 12, "port_scan": 8 }
  }
}
```

Interactive API docs (Swagger UI): **http://localhost:8000/docs**

---

## 🛠️ Tech Stack

### Backend
| Library | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.111.0 | High-performance async web framework |
| scikit-learn | 1.4.2 | Isolation Forest ML model |
| SQLAlchemy | 2.0.30 | ORM for SQLite database |
| Uvicorn | 0.29.0 | ASGI server |
| Joblib | 1.4.2 | Model serialization (.pkl) |
| Pydantic | 2.7.1 | Data validation |
| websockets | 12.0 | Real-time communication |

### Frontend
| Library | Version | Purpose |
|---------|---------|---------|
| React | 18.2.0 | UI component library |
| Vite | 5.3.1 | Build tool & dev server |
| Tailwind CSS | 3.4.3 | Utility-first styling |
| Recharts | 2.12.7 | Charts & visualizations |
| Lucide React | 0.383.0 | Icon library |

---

## 🐳 Docker Deployment

```bash
# Build and run everything
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop
docker-compose down
```

Or build images separately:
```bash
docker build -t netguard-backend ./backend
docker run -p 8000:8000 netguard-backend

docker build -t netguard-frontend ./frontend
docker run -p 5173:5173 netguard-frontend
```

---

## 📁 Project Structure

```
NetGuard_V1.0.0/
├── backend/
│   ├── main.py                  # FastAPI entry point + lifespan
│   ├── requirements.txt         # Python dependencies
│   ├── models/
│   │   ├── isolation_forest.py  # AnomalyDetector class
│   │   ├── train_model.py       # Training script (auto-runs on startup)
│   │   └── detector.pkl         # Saved model (generated on first run)
│   ├── core/
│   │   ├── traffic_simulator.py # Packet generator + 5 attack modes
│   │   ├── feature_extractor.py # Packet → 13-feature numpy array
│   │   └── alert_manager.py     # Severity classification + alert queue
│   ├── database/
│   │   ├── db.py                # SQLAlchemy engine + session factory
│   │   └── models.py            # TrafficLog + Alert ORM models
│   ├── api/
│   │   ├── routes.py            # 7 REST endpoints
│   │   └── websocket.py         # WS broadcast + background task
│   └── utils/
│       └── logger.py            # Structured logging config
├── frontend/
│   └── src/
│       ├── App.jsx              # Root component + error boundary
│       ├── hooks/
│       │   └── useWebSocket.js  # Auto-reconnect WS hook
│       └── components/
│           ├── Dashboard.jsx        # Main layout
│           ├── StatsCards.jsx       # 4 KPI cards with sparklines
│           ├── AnomalyChart.jsx     # Real-time area chart
│           ├── LiveTrafficFeed.jsx  # Scrolling packet table + modal
│           ├── ThreatAlerts.jsx     # Alert panel with animations
│           ├── AttackTypeChart.jsx  # Donut chart by attack type
│           ├── NetworkMap.jsx       # SVG IP flow visualization
│           └── StatusBar.jsx        # Connection status indicator
├── scripts/
│   ├── setup.sh / setup.bat         # Full environment setup
│   ├── run_dev.sh / run_dev.bat     # Start both servers
│   └── generate_attacks.py          # Interactive attack simulator
├── sample_data/
│   └── sample_packets.json          # 100 pre-labeled packets
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🧠 How It Works

### Isolation Forest Algorithm

Isolation Forest detects anomalies by randomly isolating observations:

1. **Random partitioning** — Randomly select a feature and a split value
2. **Isolation depth** — Anomalies are isolated in fewer splits (shorter tree paths)
3. **Score normalization** — Path length is normalized to a 0–1 anomaly score

```
Normal traffic  → deep in tree   → low score  (< 0.5) ✓
Attack traffic  → near tree root → high score (> 0.5) ⚠
```

### The 13 Features Used

| # | Feature | Description |
|---|---------|-------------|
| 1 | `packet_size` | Bytes per packet |
| 2 | `inter_arrival_time` | Seconds between packets |
| 3 | `port_number` | Destination port |
| 4 | `protocol_encoded` | TCP=0, UDP=1, ICMP=2 |
| 5 | `packets_per_second` | Current PPS rate |
| 6 | `bytes_per_second` | Current throughput |
| 7 | `src_port` | Source port |
| 8 | `dst_port` | Destination port |
| 9 | `flag_syn` | TCP SYN flag (0/1) |
| 10 | `flag_ack` | TCP ACK flag (0/1) |
| 11 | `flag_fin` | TCP FIN flag (0/1) |
| 12 | `flag_rst` | TCP RST flag (0/1) |
| 13 | `connection_duration` | Session length in seconds |

### Severity Classification

| Score Range | Severity | Color |
|-------------|----------|-------|
| 0.85 – 1.00 | CRITICAL | 🔴 |
| 0.65 – 0.85 | HIGH | 🟠 |
| 0.45 – 0.65 | MEDIUM | 🟡 |
| 0.00 – 0.45 | LOW | 🔵 |

Attack type also elevates severity — e.g. `data_exfiltration` is always at least CRITICAL.

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Throughput | 2 packets/sec (configurable) |
| Detection latency | < 100ms |
| Normal traffic anomaly rate | ~10% (contamination parameter) |
| DDoS detection score | ~0.93 |
| Max WebSocket clients | Unlimited (async broadcast) |
| Model size | ~5 MB |
| Memory usage | < 500 MB |

---

## 🤝 Contributing

### Contributions are welcome!

**Guidelines:**
- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript
- Write tests for new features
- Update this README for significant changes



---

<div align="center">

### Built with ❤️ to learn, try new things, and meet awesome people

⭐ Star this repo if you find it useful!

</div>
