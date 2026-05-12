import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

import requests


DEFAULT_BASE_URL = os.environ.get("AERIS_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
POLL_SECONDS = 3


def run_script(script_path):
    script_path = Path(script_path).resolve()
    subprocess.run([sys.executable, str(script_path)], check=True, cwd=script_path.parent)


def poll_for_requests(base_url, fake_script, send_script):
    print(f"Polling {base_url}/api/trigger/poll for dashboard requests...")
    while True:
        try:
            response = requests.get(f"{base_url}/api/trigger/poll", timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "pending":
                print("Request received. Generating and sending new sensor data...")
                run_script(fake_script)
                run_script(send_script)

                complete = requests.post(f"{base_url}/api/trigger/complete", timeout=10)
                complete.raise_for_status()
                print("Done. Waiting for the next request.")
        except requests.RequestException as exc:
            print(f"Could not reach Aeris app: {exc}")
        except subprocess.CalledProcessError as exc:
            print(f"Pi data script failed: {exc}")

        time.sleep(POLL_SECONDS)


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Run this on the Raspberry Pi so Aeris dashboard clicks generate and upload data."
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public URL of the Aeris Flask app.")
    parser.add_argument("--fake-script", default=root / "FAKEDATA.py", type=Path)
    parser.add_argument("--send-script", default=root / "SendData.py", type=Path)
    args = parser.parse_args()

    poll_for_requests(args.base_url.rstrip("/"), args.fake_script, args.send_script)


if __name__ == "__main__":
    main()
