import os
import random
from flask import Flask, render_template, request, jsonify
import psycopg2
from datetime import datetime

app = Flask(__name__)

# ---------------------------------
# DATABASE CONNECTION
# ---------------------------------

DATABASE_URL = "postgresql://aeris_db_plyi_user:9kKFF5gHTAwuUfevT02OVJMqrgWdplVS@dpg-d6o9flf5gffc73eq89e0-a.oregon-postgres.render.com/aeris_db_plyi"
API_KEY = os.environ.get("API_KEY")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# ---------------------------------
# CREATE TABLE IF NOT EXISTS
# ---------------------------------

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id SERIAL PRIMARY KEY,
            room VARCHAR(100),
            gas VARCHAR(100),
            reading FLOAT,
            status VARCHAR(20),
            sensor_id VARCHAR(50),
            temperature FLOAT,
            humidity FLOAT,
            pressure FLOAT,
            air_quality VARCHAR(50),
            screenshot_path VARCHAR(255),
            timestamp TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route("/room/<room_name>")
def room_detail(room_name):
    return render_template("room_detail.html", room=room_name)

rooms_data = [
    {"name": "Kitchen", "risk": "danger"},
    {"name": "Garage", "risk": "warning"},
    {"name": "Bedroom", "risk": "normal"},
    {"name": "Basement", "risk": "normal"},
]


# ---------------------------------
# ROUTES
# ---------------------------------

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

@app.route("/about")
def about():
    data = {
        "title": "Aeris.AI",
        "tagline": "AI-driven gas detection",
        "features": ["Leak prediction", "Sensor status", "Live alerts"]
    }
    return render_template("about.html", data=data)

    alerts = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("immediate.html", alerts=alerts)

# ---------------------------------
# API ENDPOINT FOR RASPBERRY PI
# ---------------------------------

@app.route("/api/upload", methods=["POST"])
def upload_data():
    auth_key = request.headers.get("x-api-key")

    if auth_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    room = data.get("room")
    gas = data.get("gas")
    reading = data.get("reading")
    status = data.get("status")
    sensor_id = data.get("sensor_id")
    temperature = data.get("temperature")
    humidity = data.get("humidity")
    pressure = data.get("pressure")
    air_quality = data.get("air_quality")
    screenshot_path = data.get("screenshot_path")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO readings (room, gas, reading, status, sensor_id, temperature, humidity, pressure, air_quality, screenshot_path, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, (room, gas, reading, status, sensor_id, temperature, humidity, pressure, air_quality, screenshot_path, datetime.utcnow()))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Data stored"}), 200

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

        if reading > 40:
            status = "danger"
        elif reading > 20:
            status = "warning"
        else:
            status = "normal"

        cur.execute("""
            INSERT INTO readings (room, gas, reading, status, sensor_id, temperature, humidity, pressure, air_quality, screenshot_path, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW());
        """, (room, gas, reading, status, sensor_id, temperature, humidity, pressure, air_quality, None))

    conn.commit()
    cur.close()
    conn.close()

    return "Fake data generated!"

if __name__ == "__main__":
    app.run(debug=True)


