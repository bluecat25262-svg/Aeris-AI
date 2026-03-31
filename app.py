import os
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
            timestamp TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

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
    return render_template("rooms.html", rooms=rooms_data)

@app.route("/alerts")
def alerts():
    return render_template("alerts.html")

@app.route("/immediate")
def immediate():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT room, gas, reading, status, timestamp
        FROM readings
        ORDER BY timestamp DESC
        LIMIT 5;
    """)
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

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO readings (room, gas, reading, status, timestamp)
        VALUES (%s, %s, %s, %s, %s);
    """, (room, gas, reading, status, datetime.utcnow()))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Data stored"}), 200

if __name__ == "__main__":
    app.run(debug=True)

import random

@app.route("/generate")
def generate_fake_data():
    conn = get_db_connection()
    cur = conn.cursor()

    rooms = ["Kitchen", "Garage", "Bedroom", "Basement"]
    gases = ["Carbon Monoxide", "Chlorine", "Hydrogen Sulfide"]

    for _ in range(10):  # generate 10 fake readings
        room = random.choice(rooms)
        gas = random.choice(gases)
        reading = random.randint(5, 60)

        if reading > 40:
            status = "danger"
        elif reading > 20:
            status = "warning"
        else:
            status = "normal"

        cur.execute("""
            INSERT INTO readings (room, gas, reading, status, timestamp)
            VALUES (%s, %s, %s, %s, NOW());
        """, (room, gas, reading, status))

    conn.commit()
    cur.close()
    conn.close()

    return "Fake data generated!"