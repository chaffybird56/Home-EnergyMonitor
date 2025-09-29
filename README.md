# 🏠⚡ Home Energy Monitoring Dashboard

Python/Flask + MQTT tool to ingest smart‑meter data and visualize **MV/LV load profiling** and **peak‑demand trends** for retrofit planning. Includes **configurable alarms**, **data‑quality checks**, and **daily summaries** to support maintenance & outage coordination. Ships with a **Mosquitto** broker (Docker), a **data simulator**, and a clean **Chart.js** dashboard.

---

## ✨ Features

- **MQTT ingest** (Eclipse Paho): subscribe to `utility/meter/+/reading` and persist to SQLite.  
- **Time‑series dashboard**: Feeder kW, average voltage, and 14‑day kWh rollups.  
- **Data‑quality**: hourly missing‑data flags; propagate into daily DQ %.  
- **Alarms** (`config/alarms.yml`): thresholds on peak kW, data gaps, etc.  
- **Daily summaries**: kWh, peak kW, min voltage via background scheduler.  
- **Portable**: single `docker compose up` starts broker + app.

> References: Flask App Factory, Paho MQTT client, APScheduler background scheduler, and pandas resampling. See the **Tech refs** at the end.

---

## 🧱 Architecture

```
MQTT (Mosquitto) → Paho subscriber → SQLite (SQLAlchemy)
                               ↘ APScheduler: daily rollups & alarm scans
Flask API (JSON) → Chart.js frontend (kW, V, kWh)
```

**Topic schema**
```
utility/meter/{meter_id}/reading
payload: {
  "ts": "ISO8601",
  "kw": <float>, "kvar": <float>,
  "volts": <float>, "hertz": <float>,
  "voltage_level": "MV"|"LV",
  "feeder": "FDR-12"
}
```

---

## 🚀 Quick start

### Option A — Docker (recommended)

```bash
git clone https://github.com/chaffybird56/Home-EnergyMonitor/tree/main
cd home-energy-monitor
cp .env.example .env
docker compose up --build
```
Open **http://localhost:5000** (dashboard), and in another terminal push demo data:
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export MQTT_BROKER_HOST=localhost MQTT_BROKER_PORT=1883
python simulator/publisher.py
```

### Option B — Local (without Docker)

1) Ensure an MQTT broker (e.g., Mosquitto).  
2) Set env vars in `.env` (or export at shell).  
3) Install deps and run:
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app
flask --app app run --host 0.0.0.0 --port 5000
```

---

## ⚙️ Configuration

- App/site: `config/app.example.yml` (copy & adjust for site title, timezone).  
- Alarms: `config/alarms.yml`.  
- Environment: `.env` (see `.env.example`).  

**Daily rollups**: `rollups.daily_time` (local TZ).  
**Data quality**: `quality.max_missing_percent_per_hour`.

---

## 📊 Dashboard

- **Feeder Load (kW)** — 24h line chart + peak badge  
- **Average Voltage (V)** — 24h line chart  
- **Daily Energy (kWh)** — last 14 days (sum across meters)

Front‑end calls `/api/timeseries` and `/api/daily` and renders with Chart.js.

---

## 🛠️ Extending

- Swap SQLite for Postgres; models are SQLAlchemy‑backed.  
- Add auth/RBAC and an admin UI for alarm rules.  
- Live updates with SSE/WebSockets.  
- Wire to real AMI head‑end / substation gateway.

---

## 📜 Sensor & Data Validation (spec extract)

**Sensors**: minute‑level readings with `kw`, `kvar`, `volts`, `hertz`, ISO8601 `ts`.  
**Accuracy targets**: ±0.5% power, ±0.5% voltage; 60 Hz nominal.  
**MQTT**: topic `utility/meter/{meter_id}/reading`, QoS 1, JSON payload in UTC.  
**Validation**: schema presence; numeric ranges (`kw` [0, 10000], `volts` within MV/LV norms, `hertz` ~ [49.5, 60.5]); reject stale `ts` beyond drift window.  
**Rollups**: hourly/daily via `pandas.DataFrame.resample()`; daily energy ≈ Σ(kW per minute)/60.

---

## 🧪 Tests

```bash
pytest -q
```

---

## 📚 Tech refs

- Flask app factory & patterns (official docs).  
- Eclipse Paho MQTT Python client docs.  
- APScheduler BackgroundScheduler docs.  
- Chart.js getting started.  
- pandas `DataFrame.resample()`.

(Direct links are provided in the repository issue template or project wiki.)
