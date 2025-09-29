import threading, json
from datetime import datetime
import pandas as pd
import paho.mqtt.client as mqtt
from .models import db, Reading, Meter

def start_mqtt_worker(app):
    t = threading.Thread(target=_run, args=(app,), daemon=True)
    t.start()

def _run(app):
    with app.app_context():
        host = app.config["MQTT_BROKER_HOST"]; port = int(app.config["MQTT_BROKER_PORT"])
        topics = [t.strip() for t in app.config["MQTT_TOPICS"].split(",")]
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = lambda c,u,fl,rc,props=None: [_subscribe(c, t) for t in topics]
        client.on_message = lambda c,u,msg: _handle_message(app, msg)
        client.connect(host, port)
        client.loop_forever()

def _subscribe(client, topic):
    client.subscribe(topic, qos=1)

def _handle_message(app, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except Exception:
        return
    parts = msg.topic.split("/")
    meter_id = parts[2] if len(parts) >= 3 else payload.get("meter_id", "UNKNOWN")
    ts = pd.to_datetime(payload.get("ts", datetime.utcnow()))
    r = Reading(
        meter_id=meter_id, ts=ts.to_pydatetime(),
        kw=payload.get("kw"), kvar=payload.get("kvar"),
        volts=payload.get("volts"), hertz=payload.get("hertz")
    )
    m = Meter.query.filter_by(meter_id=meter_id).first()
    if not m:
        m = Meter(meter_id=meter_id, voltage_level=payload.get("voltage_level","LV"), feeder=payload.get("feeder"))
        db.session.add(m)
    db.session.add(r); db.session.commit()