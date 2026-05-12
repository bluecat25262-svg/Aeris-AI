import os
from pathlib import Path

import requests


PYTHONANYWHERE_USERNAME = os.environ.get("PYTHONANYWHERE_USERNAME", "zyadwazeer")
PYTHONANYWHERE_API_TOKEN = os.environ.get("PYTHONANYWHERE_API_TOKEN")
LOCAL_CSV = Path(os.environ.get("AERIS_SENSOR_CSV", "sensor_data.csv"))
REMOTE_CSV = os.environ.get(
    "AERIS_REMOTE_CSV",
    f"/home/{PYTHONANYWHERE_USERNAME}/Aeris-AI/data.csv",
)


def upload_sensor_data():
    if not PYTHONANYWHERE_API_TOKEN:
        raise RuntimeError("Set PYTHONANYWHERE_API_TOKEN before running SendData.py.")

    if not LOCAL_CSV.exists():
        raise FileNotFoundError(f"Could not find {LOCAL_CSV}. Run FAKEDATA.py first.")

    url = (
        f"https://www.pythonanywhere.com/api/v0/user/{PYTHONANYWHERE_USERNAME}"
        f"/files/path{REMOTE_CSV}"
    )

    with LOCAL_CSV.open("rb") as file:
        response = requests.post(
            url,
            headers={"Authorization": f"Token {PYTHONANYWHERE_API_TOKEN}"},
            files={"content": file},
            timeout=30,
        )

    response.raise_for_status()
    print(f"Uploaded {LOCAL_CSV} to {REMOTE_CSV}. Status: {response.status_code}")


if __name__ == "__main__":
    upload_sensor_data()
