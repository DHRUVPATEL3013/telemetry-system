from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.telemetry import TelemetryCreateRequest


def valid_payload():
    return {
        "event_id": "evt-101",
        "vehicle_id": str(uuid4()),
        "speed": 60,
        "temperature": 35,
        "latitude": 21.17,
        "longitude": 72.83,
        "event_timestamp": "2026-10-13T10:00:00Z",
    }


def test_valid_telemetry_is_accepted():
    data = TelemetryCreateRequest(**valid_payload())

    assert data.speed == 60
    assert data.event_id == "evt-101"


def test_zero_speed_is_accepted():
    payload = valid_payload()
    payload["speed"] = 0

    data = TelemetryCreateRequest(**payload)

    assert data.speed == 0


def test_negative_speed_is_rejected():
    payload = valid_payload()
    payload["speed"] = -10

    with pytest.raises(ValidationError):
        TelemetryCreateRequest(**payload)


def test_invalid_latitude_is_rejected():
    payload = valid_payload()
    payload["latitude"] = 100

    with pytest.raises(ValidationError):
        TelemetryCreateRequest(**payload)


def test_empty_event_id_is_rejected():
    payload = valid_payload()
    payload["event_id"] = ""

    with pytest.raises(ValidationError):
        TelemetryCreateRequest(**payload)