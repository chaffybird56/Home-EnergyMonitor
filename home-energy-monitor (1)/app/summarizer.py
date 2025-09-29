from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app
from .models import db, Reading, DailySummary
import pandas as pd
from sqlalchemy import select
from datetime import datetime, timedelta

scheduler = BackgroundScheduler()

def init_scheduler(app):
    with app.app_context():
        hh, mm = map(int, app.config["rollups"]["daily_time"].split(":"))
        scheduler.add_job(_run_daily_rollup, "cron", hour=hh, minute=mm, args=[app])
        scheduler.add_job(_scan_alarms, "interval", minutes=1, args=[app])
    scheduler.start()

def _df_from_rows(rows):
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame([{
        "ts": r.ts, "meter_id": r.meter_id,
        "kw": r.kw, "kvar": r.kvar, "volts": r.volts, "hertz": r.hertz,
        "quality_ok": r.quality_ok
    } for r in rows]).set_index("ts").sort_index()
    return df

def _run_daily_rollup(app):
    with app.app_context():
        end = datetime.now()
        start = (end - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        rows = db.session.scalars(
            select(Reading).where(Reading.ts >= start, Reading.ts < end)
        ).all()
        df = _df_from_rows(rows)
        if df.empty: 
            return
        for meter_id, g in df.groupby("meter_id"):
            g1 = g.resample("1min").ffill()
            kwh = (g1["kw"].fillna(0) / 60.0).sum()
            peak_kw = g["kw"].max()
            peak_ts = g["kw"].idxmax()
            min_voltage = g["volts"].min()
            dq_missing_pct = 100 * (1 - g["quality_ok"].mean())
            db.session.add(DailySummary(
                meter_id=meter_id, date=start.date(),
                kwh=float(kwh), peak_kw=float(peak_kw) if peak_kw is not None else None, 
                peak_ts=peak_ts, min_voltage=float(min_voltage) if min_voltage is not None else None,
                dq_missing_pct=float(dq_missing_pct)
            ))
        db.session.commit()

def _scan_alarms(app):
    # Placeholder for evaluating rolling metrics; wiring left for future extension.
    return