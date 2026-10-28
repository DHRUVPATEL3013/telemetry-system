
#!/usr/bin/env python3

import argparse
import json
import os
import random
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import requests


BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

TELEMETRY_PATH = os.getenv(
    "TELEMETRY_PATH",
    "/telemetries/create-telemetry",
)

thread_local = threading.local()
print_lock = threading.Lock()


def get_session():
    """Each device thread gets its own HTTP session."""
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()

    return thread_local.session


def load_devices(file_path=None):
    if file_path:
        path = Path(file_path)
    else:
        files = list(Path.cwd().glob("test_devices_*.json"))

        if not files:
            raise FileNotFoundError(
                "No test_devices_*.json file found. "
                "Run from the project root."
            )

        path = max(files, key=lambda f: f.stat().st_mtime)

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict):
        data = data.get(
            "devices",
            data.get("data", data.get("results")),
        )

    if not isinstance(data, list) or not data:
        raise ValueError("The devices file must contain a non-empty list.")

    for device in data:
        if not isinstance(device, dict) or not device.get("device_key"):
            raise ValueError("Every device must contain device_key.")

    print(f"Devices file: {path}")
    return data


def generate_telemetry(event_number):
    return {
        "event_id": str(uuid.uuid4()),
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
        "latitude": round(
            21.1702 + random.uniform(-0.03, 0.03), 6
        ),
        "longitude": round(
            72.8311 + random.uniform(-0.03, 0.03), 6
        ),
        "speed": round(random.uniform(0, 200), 2),
        "temperature": round(random.uniform(24, 38), 2),
    }


def send_telemetry(device, device_number, event_number, endpoint, timeout):
    device_label = (
        device.get("device_id")
        or device.get("vehicle_id")
        or f"device-{device_number}"
    )

    payload = generate_telemetry(event_number)

    headers = {
        "X-Device-Key": str(device["device_key"])
    }

    started = time.perf_counter()

    try:

        response = get_session().post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=timeout,
        )

        latency = time.perf_counter() - started

        result = {
            "ok": response.ok,
            "device": device_label,
            "event": event_number,
            "status": response.status_code,
            "latency": latency,
            "error": (
                "" if response.ok
                else response.text.replace("\n", " ")[:250]
            ),
        }

    except requests.RequestException as exc:
        result = {
            "ok": False,
            "device": device_label,
            "event": event_number,
            "status": None,
            "latency": time.perf_counter() - started,
            "error": str(exc),
        }

    with print_lock:
        if result["ok"]:
            print(
                f"OK   {device_label} | "
                f"event {event_number} | "
                f"HTTP {result['status']} | "
                f"{result['latency'] * 1000:.0f} ms",
                flush=True,
            )
        else:
            print(
                f"FAIL {device_label} | "
                f"event {event_number} | "
                f"{result['status']} | {result['error']}",
                flush=True,
            )

    return result


def run_device(
    device,
    device_number,
    count,
    interval,
    endpoint,
    timeout,
    start_barrier,
):
    """One independent telemetry loop for one device."""

    results = []

    # All devices begin at approximately the same time.
    start_barrier.wait()

    next_send = time.monotonic()

    for event_number in range(1, count + 1):

        # Wait only for THIS device's next scheduled send.
        delay = next_send - time.monotonic()

        if delay > 0:
            time.sleep(delay)

        result = send_telemetry(
            device,
            device_number,
            event_number,
            endpoint,
            timeout,
        )

        results.append(result)

        # Schedule this device's next event independently.
        next_send += interval

        # If this request ran late, avoid sending a catch-up burst.
        if next_send < time.monotonic():
            next_send = time.monotonic() + interval

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Simulate independently scheduled vehicle telemetry."
    )

    parser.add_argument("--devices-file")
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--path", default=TELEMETRY_PATH)
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Telemetry events per device",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds between each device's scheduled events",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
    )

    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be at least 1")

    if args.interval < 0:
        parser.error("--interval cannot be negative")

    if args.timeout <= 0:
        parser.error("--timeout must be positive")

    try:
        devices = load_devices(args.devices_file)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Setup error: {exc}", file=sys.stderr)
        return 2

    endpoint = (
        f"{args.base_url.rstrip('/')}/"
        f"{args.path.lstrip('/')}"
    )

    total_planned = len(devices) * args.count

    print(f"Devices loaded: {len(devices)}")
    print(f"Endpoint: {endpoint}")
    print(f"Events per device: {args.count}")
    print(f"Each device's interval: {args.interval}s")
    print(f"Total planned requests: {total_planned}")

    if args.dry_run:
        print("\nSample payload:")
        print(json.dumps(generate_telemetry(1), indent=2))
        print("\nDry run only; no requests sent.")
        return 0

    # One thread runs the independent loop for each device.
    start_barrier = threading.Barrier(len(devices))
    all_results = []
    test_started = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=len(devices)
    ) as executor:

        futures = [
            executor.submit(
                run_device,
                device,
                index,
                args.count,
                args.interval,
                endpoint,
                args.timeout,
                start_barrier,
            )
            for index, device in enumerate(devices, start=1)
        ]

        for future in as_completed(futures):
            try:
                all_results.extend(future.result())
            except Exception as exc:
                print(f"Device simulator error: {exc}", file=sys.stderr)

    elapsed = time.perf_counter() - test_started

    successful = sum(r["ok"] for r in all_results)
    failed = sum(not r["ok"] for r in all_results)
    latencies = sorted(r["latency"] for r in all_results)

    average_ms = (
        sum(latencies) / len(latencies) * 1000
        if latencies else 0
    )

    p95_ms = (
        latencies[min(len(latencies) - 1, int(0.95 * len(latencies)))] * 1000
        if latencies else 0
    )

    print("\n--- Summary ---")
    print(f"Successful requests: {successful}")
    print(f"Failed requests: {failed}")
    print(f"Total completed requests: {len(all_results)}")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print(
        f"Throughput: "
        f"{len(all_results) / elapsed if elapsed else 0:.2f} requests/second"
    )
    print(f"Average response time: {average_ms:.2f} ms")
    print(f"Approx. p95 response time: {p95_ms:.2f} ms")

    if len(all_results) != total_planned:
        return 1

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
