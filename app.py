from flask import Flask, render_template

app = Flask(__name__)

# ---------------- MOCK DATA ---------------- #

rooms = [
    {"name": "Kitchen", "risk": "danger"},
    {"name": "Garage", "risk": "warning"},
    {"name": "Bedroom", "risk": "normal"},
    {"name": "Basement", "risk": "normal"},
]

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/rooms")
def room_overview():
    return render_template("rooms.html", rooms=rooms)

@app.route("/room/<room_name>")
def sensor_detail(room_name):
    return render_template("sensor.html", room=room_name)

@app.route("/alerts")
def alerts():
    return render_template("alerts.html")

@app.route("/gas/<gas_name>")
def gas_page(gas_name):
    return render_template("gas.html", gas=gas_name)

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)
