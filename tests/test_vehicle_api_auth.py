from fastapi.testclient import TestClient

from app.main import app  # Adjust if your FastAPI app is defined elsewhere


client = TestClient(app)


def test_vehicle_telemetry_requires_login():
    vehicle_id = "1673e9b6-503d-4401-8be7-f7b1391012e4"

    response = client.get(
        f"/vehicles/{vehicle_id}/telemetry"
    )

    assert response.status_code == 401