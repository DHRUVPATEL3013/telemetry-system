from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.dependencies.auth_dependencies import get_current_user  # Use your actual import path

client = TestClient(app)


def test_viewer_cannot_access_telemetry_history():
    def override_current_user():
        return SimpleNamespace(
            user_id=uuid4(),
            organization_id=uuid4(),
            role="viewer",
        )

    app.dependency_overrides[get_current_user] = (
        override_current_user
    )

    try:
        vehicle_id = uuid4()

        response = client.get(
            f"/vehicles/{vehicle_id}/telemetry"
        )

        assert response.status_code == 403

    finally:
        app.dependency_overrides.clear()