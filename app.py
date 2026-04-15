import os
import random
import sqlite3
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

DATABASE_URL = os.path.join(os.path.dirname(__file__), "readings.db")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT,
            gas TEXT,
            reading REAL,
            status TEXT,
            sensor_id TEXT,
            temperature REAL,
            humidity REAL,
            pressure REAL,
            air_quality TEXT,
            screenshot_path TEXT,
            timestamp TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/rooms")
def rooms():
    return render_template("rooms.html")

@app.route("/alerts")
def alerts():
    return render_template("alerts.html")

@app.route("/immediate")
def immediate():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT room, gas, reading, status, sensor_id, temperature, humidity, pressure, air_quality, screenshot_path, timestamp
        FROM readings
        ORDER BY timestamp DESC
        LIMIT 10;
    """)
    alerts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("immediate.html", alerts=alerts)

@app.route("/room/<room_name>")
def room_detail(room_name):
    return render_template("room_detail.html", room=room_name)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/generate")
def generate_fake_data():
    conn = get_db_connection()
    cur = conn.cursor()
    rooms = ["Processing Area C", "Storage Area B", "Floor #01"]
    gases = ["Carbon Monoxide", "Chlorine", "Hydrogen Sulfide"]
    sensors = ["SEN-C12", "SEN-C08", "SEN-804"]

    for _ in range(15):
        room = random.choice(rooms)
        gas = random.choice(gases)
        reading = round(random.uniform(5, 60), 1)
        sensor_id = random.choice(sensors)
        temperature = random.randint(65, 75)
        humidity = random.randint(30, 60)
        pressure = random.randint(1010, 1015)
        air_quality = random.choice(["Normal", "Moderate", "Poor"])
        status = "danger" if reading > 40 else "warning" if reading > 20 else "normal"

        cur.execute("""
            INSERT INTO readings (room, gas, reading, status, sensor_id, temperature, humidity, pressure, air_quality, screenshot_path, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (room, gas, reading, status, sensor_id, temperature, humidity, pressure, air_quality, None, datetime.utcnow().isoformat()))

    conn.commit()
    cur.close()
    conn.close()
    return "Fake data generated!"

if __name__ == "__main__":
    app.run(debug=True)


