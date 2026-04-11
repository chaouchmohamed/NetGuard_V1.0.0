
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

# NetGuard - Network Attack Detection System

A real-time network traffic analyzer that spots attacks using machine learning. Works without root privileges, which was a requirement for me.

---

## What it does

Listens to network traffic in real-time, runs it through an Isolation Forest model, and shows you what's happening on a live dashboard.

**The dashboard shows:**
- Live traffic feed
- Attack alerts with severity levels
- Anomaly score chart
- Simple network map
- Stats cards with counts

---

## Tech stack

| Layer | What I used |
|-------|--------------|
| ML model | Isolation Forest (scikit-learn) |
| Backend | FastAPI + WebSockets + SQLite |
| Frontend | React + Tailwind + Recharts |
| Deployment | Docker compose works, but you can run it raw too |

---

## Getting it running

**What you need:**
- Python 3.8 or newer
- Node.js 16+ and npm

**Steps:**

```bash
git clone https://github.com/chaouchmohamed/NetGuard_V1.0.0.git
cd NetGuard_V1.0.0
Then run the setup script for your OS:

Linux/Mac:

bash
chmod +x scripts/setup.sh
./scripts/setup.sh
Windows:

batch
scripts\setup.bat
This sets up a virtual env, installs dependencies, and trains the model on first run.

To start everything:

bash
./scripts/run_dev.sh   # Linux/Mac
# or
scripts\run_dev.bat    # Windows
Where to find things:

Dashboard: http://localhost:5173

API: http://localhost:8000

Swagger docs: http://localhost:8000/docs

What attacks it detects
Right now it recognizes 5 patterns:

Attack	Severity
DDoS	CRITICAL
Data exfiltration	CRITICAL
Port scan	HIGH
SYN flood	HIGH
Brute force	MEDIUM
The severity isn't hardcoded - it's based on the anomaly score plus some rules I added for specific patterns.

How the detection works
Isolation Forest in plain english:

The model builds random decision trees. Normal traffic takes many splits to isolate (ends up deep in the tree). Attack traffic gets isolated quickly (shallow tree = high anomaly score).

Features the model looks at (13 total):

Packet size, port numbers, protocol type

Packets per second, bytes per second

TCP flags (SYN, ACK, FIN, RST)

Connection duration

Inter-arrival times between packets

The model was trained on synthetic normal traffic (about 10k samples). It auto-trains on first run if it doesn't find a saved detector.pkl file.

API endpoints
REST:

Method	Endpoint	What it does
GET	/api/health	Check if everything's ok
GET	/api/alerts	List of all alerts (paginated)
GET	/api/alerts/recent	Last 20 alerts
GET	/api/stats	Summary counts
GET	/api/traffic/history	Last 500 packets
GET	/api/model/info	When model was trained, how many samples
POST	/api/model/retrain	Force a retrain
WebSocket:

ws://localhost:8000/ws/traffic

Messages come in as JSON with the packet data, prediction result, and current stats. The frontend updates live.

Project layout
text
NetGuard_V1.0.0/
├── backend/
│   ├── main.py                 # App entry point
│   ├── models/
│   │   ├── isolation_forest.py # AnomalyDetector class
│   │   └── detector.pkl        # Saved model (generated)
│   ├── core/
│   │   ├── traffic_simulator.py # Packet generator
│   │   ├── feature_extractor.py # Turns packets into feature arrays
│   │   └── alert_manager.py     # Severity logic
│   ├── database/                # SQLite stuff
│   ├── api/                     # Routes and WebSocket
│   └── utils/                   # Logging config
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── hooks/
│       │   └── useWebSocket.js  # Auto-reconnect logic
│       └── components/          # Dashboard pieces
├── scripts/                     # Setup and run scripts
├── docker-compose.yml
└── README.md
Docker
bash
docker-compose up --build
That's it. Both frontend and backend run inside containers.

Performance
Metric	Value
Packet throughput	~2/sec (you can change this)
Detection latency	Under 100ms
Model size	~5 MB
RAM usage	Under 500 MB
Contributing
If you want to add something or fix a bug, go ahead. Just keep the code readable and update the README if you change something important.

<div align="center">
Built mostly to learn, but if it helps someone else, that's cool too.

</div> 
