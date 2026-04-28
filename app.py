import os
import csv
import random
import sqlite3
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

DATABASE_URL = os.path.join(os.path.dirname(__file__), "readings.db")
CSV_PATH     = os.path.join(os.path.dirname(__file__), "data.csv")

# ── Danger thresholds ──────────────────────────────────────────────────────────
THRESHOLDS = {
    "temperature_C": {"warning": 27.0, "danger": 29.0},
    "humidity_%":    {"warning": 60.0, "danger": 65.0},
    "pressure_hPa":  {"warning": 1020.0, "danger": 1023.0},
}

# Each room gets a deterministic slice of the CSV rows
ROOM_SLICES = {
    "Processing Area C": (0,   72),
    "Storage Area B":    (72,  144),
    "Floor #01":         (144, 216),
}

def read_csv():
    rows = []
    if not os.path.exists(CSV_PATH):
        return rows
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "timestamp":     row["timestamp"],
                "temperature_C": float(row["temperature_C"]),
                "humidity_%":    float(row["humidity_%"]),
                "pressure_hPa":  float(row["pressure_hPa"]),
            })
    return rows

def rows_for_room(room_name):
    all_rows = read_csv()
    start, end = ROOM_SLICES.get(room_name, (0, len(all_rows)))
    return all_rows[start:end]

# ── DB helpers ─────────────────────────────────────────────────────────────────
def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT, gas TEXT, reading REAL, status TEXT,
            sensor_id TEXT, temperature REAL, humidity REAL,
            pressure REAL, air_quality TEXT,
            screenshot_path TEXT, timestamp TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# ── Page routes ────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/rooms")
def rooms():
    room_stats = {}
    for room_name in ROOM_SLICES:
        rows = rows_for_room(room_name)
        if rows:
            latest = rows[-1]
            room_stats[room_name] = {
                "temperature": latest["temperature_C"],
                "humidity":    latest["humidity_%"],
                "pressure":    latest["pressure_hPa"],
            }
    return render_template("rooms.html", room_stats=room_stats)

@app.route("/alerts")
def alerts():
    all_rows  = read_csv()
    triggered = []
    for row in all_rows:
        for field, limits in THRESHOLDS.items():
            val = row[field]
            if val >= limits["danger"]:
                triggered.append({"field": field, "value": val, "level": "danger",  "timestamp": row["timestamp"]})
            elif val >= limits["warning"]:
                triggered.append({"field": field, "value": val, "level": "warning", "timestamp": row["timestamp"]})
    triggered = triggered[-20:][::-1]
    return render_template("alerts.html", triggered=triggered)

@app.route("/immediate")
def immediate():
    conn = get_db_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT room, gas, reading, status, sensor_id,
               temperature, humidity, pressure, air_quality,
               screenshot_path, timestamp
        FROM readings ORDER BY timestamp DESC LIMIT 10;
    """)
    db_alerts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("immediate.html", alerts=db_alerts)

@app.route("/room/<room_name>")
def room_detail(room_name):
    rows   = rows_for_room(room_name)
    latest = rows[-1] if rows else {}
    return render_template("room_detail.html", room=room_name, latest=latest)

@app.route("/about")
def about():
    return render_template("about.html")

# ── Chart data API ─────────────────────────────────────────────────────────────
@app.route("/api/chart/<room_name>")
def chart_data(room_name):
    rows         = rows_for_room(room_name)
    labels       = [r["timestamp"][-8:-3] for r in rows]
    temperatures = [r["temperature_C"]    for r in rows]
    humidities   = [r["humidity_%"]       for r in rows]
    pressures    = [r["pressure_hPa"]     for r in rows]
    return jsonify({
        "labels": labels,
        "temperature": {"values": temperatures, "warning_thresh": THRESHOLDS["temperature_C"]["warning"], "danger_thresh": THRESHOLDS["temperature_C"]["danger"], "unit": "°C",  "label": "Temperature"},
        "humidity":    {"values": humidities,   "warning_thresh": THRESHOLDS["humidity_%"]["warning"],    "danger_thresh": THRESHOLDS["humidity_%"]["danger"],    "unit": "%",   "label": "Humidity"},
        "pressure":    {"values": pressures,    "warning_thresh": THRESHOLDS["pressure_hPa"]["warning"],  "danger_thresh": THRESHOLDS["pressure_hPa"]["danger"],  "unit": " hPa","label": "Pressure"},
    })

@app.route("/api/chart/all")
def chart_data_all():
    rows         = read_csv()
    labels       = [r["timestamp"][-8:-3] for r in rows]
    temperatures = [r["temperature_C"]    for r in rows]
    humidities   = [r["humidity_%"]       for r in rows]
    pressures    = [r["pressure_hPa"]     for r in rows]
    return jsonify({
        "labels": labels,
        "temperature": {"values": temperatures, "warning_thresh": THRESHOLDS["temperature_C"]["warning"], "danger_thresh": THRESHOLDS["temperature_C"]["danger"], "unit": "°C",  "label": "Temperature"},
        "humidity":    {"values": humidities,   "warning_thresh": THRESHOLDS["humidity_%"]["warning"],    "danger_thresh": THRESHOLDS["humidity_%"]["danger"],    "unit": "%",   "label": "Humidity"},
        "pressure":    {"values": pressures,    "warning_thresh": THRESHOLDS["pressure_hPa"]["warning"],  "danger_thresh": THRESHOLDS["pressure_hPa"]["danger"],  "unit": " hPa","label": "Pressure"},
    })

# ── Generate fake DB data ──────────────────────────────────────────────────────
@app.route("/generate")
def generate_fake_data():
    conn = get_db_connection()
    cur  = conn.cursor()
    rooms   = ["Processing Area C", "Storage Area B", "Floor #01"]
    gases   = ["Carbon Monoxide", "Chlorine", "Hydrogen Sulfide"]
    sensors = ["SEN-C12", "SEN-C08", "SEN-804"]
    for _ in range(15):
        room        = random.choice(rooms)
        gas         = random.choice(gases)
        reading     = round(random.uniform(5, 60), 1)
        sensor_id   = random.choice(sensors)
        temperature = random.randint(65, 75)
        humidity    = random.randint(30, 60)
        pressure    = random.randint(1010, 1015)
        air_quality = random.choice(["Normal", "Moderate", "Poor"])
        status      = "danger" if reading > 40 else "warning" if reading > 20 else "normal"
        cur.execute("""
            INSERT INTO readings (room, gas, reading, status, sensor_id, temperature, humidity, pressure, air_quality, screenshot_path, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (room, gas, reading, status, sensor_id, temperature, humidity, pressure, air_quality, None, datetime.utcnow().isoformat()))
    conn.commit()
    cur.close()
    conn.close()
    return "Fake data generated!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)