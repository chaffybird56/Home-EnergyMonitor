from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from datetime import datetime

db = SQLAlchemy()

class Meter(db.Model):
    __tablename__ = "meters"
    id = db.Column(db.Integer, primary_key=True)
    meter_id = db.Column(db.String(64), unique=True, nullable=False)
    voltage_level = db.Column(db.String(8), nullable=False, default="LV")  # MV/LV
    feeder = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Reading(db.Model):
    __tablename__ = "readings"
    id = db.Column(db.Integer, primary_key=True)
    meter_id = db.Column(db.String(64), index=True, nullable=False)
    ts = db.Column(db.DateTime, index=True, nullable=False)
    kw = db.Column(db.Float)      # instantaneous kW (or interval kW)
    kvar = db.Column(db.Float)
    volts = db.Column(db.Float)
    hertz = db.Column(db.Float)
    quality_ok = db.Column(db.Boolean, default=True)
    __table_args__ = (UniqueConstraint("meter_id", "ts", name="uq_meter_ts"),)

class DailySummary(db.Model):
    __tablename__ = "daily_summaries"
    id = db.Column(db.Integer, primary_key=True)
    meter_id = db.Column(db.String(64), index=True, nullable=False)
    date = db.Column(db.Date, index=True, nullable=False)
    kwh = db.Column(db.Float)     # daily energy
    peak_kw = db.Column(db.Float)
    peak_ts = db.Column(db.DateTime)
    min_voltage = db.Column(db.Float)
    dq_missing_pct = db.Column(db.Float)

def init_db():
    db.create_all()