import argparse
import csv
import random
import time
from datetime import datetime
from pathlib import Path


def generate_temperature():
    return round(random.uniform(20.0, 30.0), 2)


def generate_humidity():
    return round(random.uniform(30.0, 70.0), 2)


def generate_pressure():
    return round(random.uniform(990.0, 1025.0), 2)


def write_fake_data(filename, samples, interval, append):
    path = Path(filename)
    mode = "a" if append else "w"

    with path.open(mode=mode, newline="") as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow(["timestamp", "temperature_C", "humidity_%", "pressure_hPa"])

        print(f"Generating {samples} fake sensor readings...")
        for _ in range(samples):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            temp = generate_temperature()
            hum = generate_humidity()
            pres = generate_pressure()

            writer.writerow([timestamp, temp, hum, pres])
            file.flush()

            print(f"{timestamp} | Temp: {temp} C | Humidity: {hum}% | Pressure: {pres} hPa")
            if interval:
                time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Generate fake Aeris sensor CSV data.")
    parser.add_argument("--file", default="sensor_data.csv", help="CSV file to write.")
    parser.add_argument("--samples", type=int, default=216, help="Number of rows to generate.")
    parser.add_argument("--interval", type=float, default=0.05, help="Seconds between generated rows.")
    parser.add_argument("--append", action="store_true", help="Append instead of replacing the CSV.")
    args = parser.parse_args()

    write_fake_data(args.file, args.samples, args.interval, args.append)


if __name__ == "__main__":
    main()
