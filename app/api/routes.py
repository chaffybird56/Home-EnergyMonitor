from flask import jsonify, request, Blueprint
from datetime import datetime, timedelta
from sqlalchemy import select
import pandas as pd
from ..models import db, Reading, DailySummary

api_bp = Blueprint("api", __name__)

@api_bp.get("/timeseries")
def timeseries():
    hours = int(request.args.get("hours", 24))
    end = datetime.utcnow()
    start = end - timedelta(hours=hours)
    rows = db.session.scalars(
        select(Reading).where(Reading.ts >= start, Reading.ts <= end)
    ).all()
    if not rows:
        return jsonify({"series": [], "peak": None})
    df = pd.DataFrame([{
        "ts": r.ts, "meter_id": r.meter_id, "kw": r.kw, "volts": r.volts
    } for r in rows])
    df["ts"] = pd.to_datetime(df["ts"])
    g = df.groupby("ts").agg({"kw":"sum", "volts":"mean"}).sort_index()
    peak_kw = float(g["kw"].max())
    peak_ts = g["kw"].idxmax().isoformat()
    out = {
        "series": [{"t": t.isoformat(), "kw": float(row.kw), "volts": float(row.volts)} for t,row in g.iterrows()],
        "peak": {"kw": peak_kw, "ts": peak_ts}
    }
    return jsonify(out)

@api_bp.get("/daily")
def daily():
    days = int(request.args.get("days", 14))
    rows = db.session.scalars(
        select(DailySummary).order_by(DailySummary.date.desc()).limit(days)
    ).all()
    rows = list(reversed(rows))
    return jsonify([{
        "date": r.date.isoformat(), "meter_id": r.meter_id, "kwh": r.kwh,
        "peak_kw": r.peak_kw, "min_voltage": r.min_voltage, "dq_missing_pct": r.dq_missing_pct
    } for r in rows])