
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
# NetGuard

Network intrusion detection system built with Isolation Forest. Spins up a live dashboard that visualizes traffic anomalies as they happen — no root access needed, everything runs on synthetic traffic.

---

## What it does

Runs a trained ML model against a stream of network packets and flags anything that looks off. The frontend shows a live feed, anomaly scores, attack type distribution, and a basic network flow map. Everything updates via WebSocket every 500ms.

Five attack types are covered: DDoS, port scan, SYN flood, brute force, and data exfiltration. There's also a script to generate fake attack traffic so you can actually test it.

---

## Stack

**Backend** — FastAPI + scikit-learn (Isolation Forest) + SQLite via SQLAlchemy + Uvicorn

**Frontend** — React + Vite + Tailwind + Recharts

---

## Getting started

You'll need Python 3.8+ and Node 16+.

```bash
git clone https://github.com/chaouchmohamed/NetGuard_V1.0.0.git
cd NetGuard_V1.0.0
```

**Linux / macOS:**
```bash
chmod +x scripts/setup.sh && ./scripts/setup.sh
./scripts/run_dev.sh
```

**Windows:**
```batch
scripts\setup.bat
scripts\run_dev.bat
```

Setup creates a virtualenv, installs dependencies, and trains the model if there's no `detector.pkl` yet. First run takes a minute.

Once running:
- Dashboard → http://localhost:5173
- API → http://localhost:8000
- Swagger docs → http://localhost:8000/docs

---

## Generating test traffic

Open a second terminal and run the attack simulator:

```bash
source backend/venv/bin/activate   # or backend\venv\Scripts\activate on Windows
python3 scripts/generate_attacks.py
```

Pick an attack type from the menu and watch it show up in the dashboard.

---

## API

Seven REST endpoints:

| Method | Path | What it does |
|--------|------|--------------|
| GET | `/api/health` | Model status + system health |
| GET | `/api/alerts` | Full alert history (paginated) |
| GET | `/api/alerts/recent` | Last 20 alerts |
| GET | `/api/stats` | Aggregate stats |
| GET | `/api/traffic/history` | Last 500 packets |
| GET | `/api/model/info` | Model metadata |
| POST | `/api/model/retrain` | Kick off a retrain in the background |

WebSocket at `ws://localhost:8000/ws/traffic`. Each message contains the packet, the prediction (score + severity), and running stats.

---

## How the model works

Isolation Forest anomaly detection — the short version: normal traffic takes many random splits to isolate, attack traffic gets isolated quickly. The model scores each packet 0–1 based on average path length across 100 trees.

13 features per packet: packet size, inter-arrival time, src/dst ports, protocol, packets/sec, bytes/sec, TCP flags (SYN, ACK, FIN, RST), and connection duration.

Trained on 10,000 synthetic normal traffic samples. Contamination is set to ~10%, so you'll see some false positives on normal traffic — that's expected.

Severity thresholds:

| Score | Severity |
|-------|----------|
| 0.85+ | CRITICAL |
| 0.65–0.85 | HIGH |
| 0.45–0.65 | MEDIUM |
| < 0.45 | LOW |

Some attack types (data exfiltration, DDoS) floor the severity regardless of score.

---

## Docker

```bash
docker-compose up --build
```

Or individually:

```bash
docker build -t netguard-backend ./backend && docker run -p 8000:8000 netguard-backend
docker build -t netguard-frontend ./frontend && docker run -p 5173:5173 netguard-frontend
```

---

## Project layout

```
NetGuard_V1.0.0/
├── backend/
│   ├── main.py
│   ├── models/
│   │   ├── isolation_forest.py
│   │   ├── train_model.py
│   │   └── detector.pkl         # generated on first run
│   ├── core/
│   │   ├── traffic_simulator.py
│   │   ├── feature_extractor.py
│   │   └── alert_manager.py
│   ├── database/
│   │   ├── db.py
│   │   └── models.py
│   ├── api/
│   │   ├── routes.py
│   │   └── websocket.py
│   └── utils/logger.py
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── hooks/useWebSocket.js
│       └── components/
│           ├── Dashboard.jsx
│           ├── StatsCards.jsx
│           ├── AnomalyChart.jsx
│           ├── LiveTrafficFeed.jsx
│           ├── ThreatAlerts.jsx
│           ├── AttackTypeChart.jsx
│           ├── NetworkMap.jsx
│           └── StatusBar.jsx
├── scripts/
│   ├── setup.sh / setup.bat
│   ├── run_dev.sh / run_dev.bat
│   └── generate_attacks.py
├── sample_data/sample_packets.json
└── docker-compose.yml
```

---

## Notes

- Detection latency is under 100ms in testing
- The WebSocket broadcast is async so it handles multiple clients fine
- Model is ~5MB, memory footprint stays under 500MB
- PRs welcome — follow PEP 8 for Python, run ESLint before pushing JS
