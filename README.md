# 🏠⚡ Home Energy Monitoring Dashboard

A practical, demo‑ready system for **collecting smart‑meter telemetry** and turning it into **clear operational insights**:
- Track **MV/LV feeder load** and **peak‑demand trends** for retrofit planning.
- Catch **data gaps** or suspicious values with **data‑quality checks** and **alarms**.
- Roll up **daily energy (kWh)**, **peak kW**, and **min voltage** for maintenance/outage coordination.

This repo includes everything to run locally with **Docker** (broker + app) plus a **data simulator** so you can showcase the dashboard right away—perfect for **portfolios, prototypes, and internal demos**.

---

## 📸 Screenshots

- **Feeder Load — last 24h (kW)**  
<img width="600" height="500" alt="SCR-20250929-pviq" src="https://github.com/user-attachments/assets/9c723d47-250c-4d78-8b65-8ead9b0d1b82" />

- **Average Voltage across meters (V)**  
<img width="600" height="500" alt="SCR-20250929-pvji" src="https://github.com/user-attachments/assets/a4b089dd-ea04-457e-b93a-cf604be50817" />

- **Terminal — simulated meter publishes**  
<img width="600" height="500" alt="SCR-20250929-psvj" src="https://github.com/user-attachments/assets/7125da87-caa9-479a-a940-0cae6b597895" />

---

## ✨ What’s inside (features)

- **MQTT ingest** (Paho) subscribing to `utility/meter/+/reading` and persisting to SQLite.
- **Dashboard** (Flask + Chart.js):  
  - Feeder **kW** (last 24 h) with peak badge  
  - **Average voltage** across meters (last 24 h)  
  - **Daily kWh** bars (last 14 days)
- **Daily summaries** (APScheduler): kWh, peak kW + timestamp, min voltage, % missing.
- **Data quality checks** (pandas resampling): hourly missing‑data flagging.
- **Configurable alarms** (`config/alarms.yml`) e.g., peak‑kW threshold, data‑gap minutes.
- **Portable dev setup**: one `docker compose up --build`.
- **Simulator** for reproducible screenshots and testing.
- **Extensible**: SQLAlchemy models; easy swap to Postgres; room for SSE/WebSockets.

---

## 🧱 Architecture

```
Meters/Simulator → MQTT (Mosquitto)
        ↓
   Flask (Paho subscriber) → SQLite (SQLAlchemy)
        ↓
APScheduler (daily rollups & alarm scans)
        ↓
 Flask JSON API → Chart.js dashboard
```

**Topic & payload**
```
utility/meter/{meter_id}/reading
{
  "ts": "ISO8601",
  "kw": <float>, "kvar": <float>,
  "volts": <float>, "hertz": <float>,
  "voltage_level": "MV"|"LV",
  "feeder": "FDR-12"
}
```

---

## 🚀 End‑to‑end setup (Mac/Windows/Linux)

### 0) Prereqs (once)
- **Docker Desktop** (starts Docker Engine + Compose v2)
- **Python 3.11+** (for the simulator)

### 1) Get the project
- **Option A (ZIP in releases)**: Unzip and `cd` into the folder; ensure you can see `.env.example`.
- **Option B (clone)**:
  ```bash
  git clone https://github.com/yourname/home-energy-monitor.git
  cd home-energy-monitor
  ```

### 2) Prepare env/config
```bash
# If present:
cp .env.example .env

# If not present, create .env:
cat > .env <<'EOF'
FLASK_ENV=development
FLASK_APP=app
SECRET_KEY=dev-change-me
DATABASE_URL=sqlite:///energy.db
MQTT_BROKER_HOST=broker
MQTT_BROKER_PORT=1883
MQTT_TOPICS=utility/meter/+/reading
TIMEZONE=America/Toronto
EOF
```

(Optional) Adjust thresholds/time in `config/alarms.yml` and `config/app.example.yml`.

### 3) Start services (Docker)
```bash
docker compose up --build
```
- Broker (**Mosquitto**) on `localhost:1883`
- Web app (Flask) on `http://localhost:5000`

> Leave this terminal open to see logs.

### 4) Start the **data simulator** (new terminal)
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export MQTT_BROKER_HOST=localhost MQTT_BROKER_PORT=1883
python simulator/publisher.py
```
You’ll see lines like:
```
-> utility/meter/MTR-1001/reading {"ts":"...","kw":...,"volts":...}
```

### 5) Open the dashboard
- Navigate to **http://localhost:5000**
- You should see feeder **kW** and **Voltage** charts filling within seconds.
- Let it run a bit to populate the **Daily kWh** bars.

### 6) (Optional) Verify MQTT messages
```bash
docker exec -it hem-mosquitto sh -c "mosquitto_sub -h localhost -t 'utility/meter/#' -v | head -n 10"
```

---

## 🧪 Tests
```bash
pytest -q
```

---

## 🛠️ Configuration notes

- **Daily rollups schedule**: `rollups.daily_time` (local timezone)  
- **Data quality**: `quality.max_missing_percent_per_hour`  
- **Alarm rules**: `config/alarms.yml` (metric, comparator, threshold, window)

---

## 🧭 Troubleshooting

- **“.env.example: No such file or directory”**  
  Ensure you’re in the correct folder (`pwd`; `ls -la`). If missing, create `.env` using the block in step **2**.

- **Charts are empty**  
  Simulator might not be running—or broker not reachable. Start the simulator (step **4**). Check the `web` service logs in the `docker compose` terminal for MQTT connection status.

- **Compose not found**  
  Use `docker compose` (space), not `docker-compose`. Verify with `docker compose version`.

---

## 🔮 Potential future enhancements

- Live streaming (WebSockets/SSE) and real‑time peak markers  
- Postgres + Alembic migrations; retention policies  
- Per‑feeder/zone filters, meter list & drill‑downs  
- Export endpoints (CSV/Parquet) and API tokens  
- Alarm delivery channels (email/Slack/webhooks) and acknowledge UI  
- IEC 61850/DNP3 gateways; AMI head‑end adapters  
- Role‑based access, dashboards per site

---

## 📚 Tech references (quick)
- Flask application factory & blueprints  
- Eclipse Paho MQTT client (Python)  
- APScheduler BackgroundScheduler  
- Chart.js getting started  
- pandas `DataFrame.resample()`  
- Docker Desktop / Docker Compose v2  
- Eclipse Mosquitto broker (official image)

*(See repository Wiki for links.)*
