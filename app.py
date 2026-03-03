from flask import Flask, render_template

app = Flask(__name__)

rooms_data = [
    {"name": "Kitchen", "risk": "danger"},
    {"name": "Garage", "risk": "warning"},
    {"name": "Bedroom", "risk": "normal"},
    {"name": "Basement", "risk": "normal"},
]

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/rooms")
def rooms():
    return render_template("rooms.html", rooms=rooms_data)

@app.route("/room/<room_name>")
def room_detail(room_name):
    return render_template("room_detail.html", room=room_name)

@app.route("/alerts")
def alerts():
    return render_template("alerts.html")

@app.route("/immediate")
def immediate():
    return render_template("immediate.html")

@app.route("/gas/<gas_name>")
def gas_page(gas_name):
    gas_data = {
        "Carbon Monoxide": {"reading": "12 ppm", "status": "normal"},
        "Chlorine": {"reading": "3 ppm", "status": "warning"},
        "Hydrogen Sulfide": {"reading": "25 ppm", "status": "danger"},
    }

    data = gas_data.get(gas_name, {"reading": "Unknown", "status": "normal"})

    return render_template("gas.html", gas=gas_name, data=data)

if __name__ == "__main__":
    app.run(debug=True)