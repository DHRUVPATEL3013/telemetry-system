#!/usr/bin/env python3
"""Send synthetic telemetry for devices saved by provision_test_data.py.

Run from the project root, for example:
    python scripts/telemetry_simulator.py --count 5 --interval 1

Configure TELEMETRY_PATH to match the POST route in your FastAPI app, e.g.:
    TELEMETRY_PATH=/your/actual/telemetry/route python scripts/telemetry_simulator.py
"""

import argparse
import json
import os
import random
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

DEFAULT_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
# IMPORTANT: change this to the exact POST route defined in your FastAPI project.
DEFAULT_TELEMETRY_PATH = os.getenv("TELEMETRY_PATH", "/telemetries/create-telemetry")


def find_devices_file(explicit_path: str | None) -> Path:
    if explicit_path:
        path = Path(explicit_path)
        if not path.is_file():
            raise FileNotFoundError(f"Devices JSON file not found: {path}")
        return path

    candidates = list(Path.cwd().glob("test_devices_*.json"))
    if not candidates:
        raise FileNotFoundError(
            "No test_devices_*.json file found in the current directory. "
            "Run from the project root or pass --devices-file PATH."
        )
    return max(candidates, key=lambda p: p.stat().st_mtime)


def load_devices(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    # Support either a top-level list or a wrapper such as {"devices": [...]}.
    if isinstance(data, dict):
        data = data.get("devices", data.get("data", data.get("results")))

    if not isinstance(data, list) or not data:
        raise ValueError(f"Expected a non-empty list of device records in {path}")

    required = {"device_key"}
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict) or not required.issubset(item):
            raise ValueError(
                f"Device record #{index} must be an object containing 'device_key'."
            )
    return data


def make_payload(device_index: int, event_number: int) -> dict[str, Any]:
    """Generate one sample payload. Keep these keys aligned with your Pydantic schema."""
    # Synthetic starting point around Surat; small random changes imitate movement.
    latitude = 21.1702 + random.uniform(-0.03, 0.03) + event_number * 0.0005
    longitude = 72.8311 + random.uniform(-0.03, 0.03) + event_number * 0.0005

    return {
        "event_id": str(uuid.uuid4()),
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
        "latitude": round(latitude, 6),
        "longitude": round(longitude, 6),
        "speed": round(random.uniform(0, 200), 2),
        "temperature": round(random.uniform(24, 38), 2),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulate telemetry from provisioned devices.")
    parser.add_argument("--devices-file", help="Path to test_devices_*.json")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="FastAPI base URL")
    parser.add_argument(
        "--path",
        default=DEFAULT_TELEMETRY_PATH,
        help="Telemetry POST route, e.g. /telemetry/ingest (must match your app)",
    )
    parser.add_argument(
        "--count", type=int, default=5,
        help="Number of telemetry rounds per device (default: 5)",
    )
    parser.add_argument(
        "--interval", type=float, default=1.0,
        help="Seconds to wait between rounds (default: 1)",
    )
    parser.add_argument(
        "--timeout", type=float, default=10.0,
        help="HTTP timeout per request in seconds (default: 10)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print sample request data without calling the API",
    )
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be at least 1")
    if args.interval < 0:
        parser.error("--interval cannot be negative")

    try:
        devices_path = find_devices_file(args.devices_file)
        devices = load_devices(devices_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Setup error: {exc}", file=sys.stderr)
        return 2

    endpoint = f"{args.base_url.rstrip('/')}/{args.path.lstrip('/')}"
    print(f"Devices file: {devices_path}")
    print(f"Loaded devices: {len(devices)}")
    print(f"POST endpoint: {endpoint}")
    print(f"Planned requests: {len(devices) * args.count}")

    if args.dry_run:
        sample = make_payload(0, 0)
        print("\nSample request (device key hidden):")
        print(json.dumps({"headers": {"X-Device-Key": "<hidden>"}, "json": sample}, indent=2))
        print("\nDry run only; no request was sent.")
        return 0

    session = requests.Session()
    success_count = 0
    failure_count = 0
    start_time = time.perf_counter()
    for round_number in range(1, args.count + 1):
        print(f"\nRound {round_number}/{args.count}")
        for device_index, device in enumerate(devices, start=1):
            # The vehicle_id is deliberately NOT sent in the body; the API should
            # identify the vehicle from this device's authenticated key.
            headers = {"X-Device-Key": str(device["device_key"])}
            payload = make_payload(device_index, round_number)
            label = device.get("device_id") or device.get("vehicle_id") or f"device-{device_index}"

            try:
                response = session.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=args.timeout,
                )
                if response.ok:
                    success_count += 1
                    print(f"  OK   {label}: HTTP {response.status_code}")
                else:
                    failure_count += 1
                    detail = response.text.replace("\n", " ")[:300]
                    print(f"  FAIL {label}: HTTP {response.status_code} - {detail}")
            except requests.RequestException as exc:
                failure_count += 1
                print(f"  FAIL {label}: request error - {exc}")

        if round_number < args.count and args.interval:
            time.sleep(args.interval)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print("\n--- Summary ---")
    print(f"Successful requests: {success_count}")
    print(f"Failed requests:     {failure_count}")
    print(f"Total attempted:     {success_count + failure_count}")
    print(f"Total elapsed time:  {elapsed_time:.2f} seconds")

    return 0 if failure_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
