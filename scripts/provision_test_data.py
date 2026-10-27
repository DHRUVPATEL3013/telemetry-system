import json
import os
import secrets
from datetime import datetime
from pathlib import Path

import requests


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

# Existing super_admin JWT token
# SUPER_ADMIN_TOKEN = os.environ["SUPER_ADMIN_TOKEN"]

ORGANIZATION_COUNT = 3
VEHICLES_PER_ORGANIZATION = 10

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

OUTPUT_FILE = Path(f"test_devices_{RUN_ID}.json")


# --------------------------------------------------
# UPDATE THESE PATHS TO MATCH YOUR ROUTES
# Check your FastAPI /docs page.
# --------------------------------------------------

ORGANIZATION_CREATE_PATH = "/organizations/create-organization"
LOGIN_PATH = "/auth/login"
VEHICLE_CREATE_PATH = "/vehicles/create-vehicle"

DEVICE_REGISTER_PATH = "/vehicles/{vehicle_id}/devices/register-device"


# --------------------------------------------------
# HELPER: SEND REQUEST
# --------------------------------------------------

def api_request(
    method: str,
    path: str,
    token: str | None = None,
    json_body: dict | None = None,
    form_data: dict | None = None,
):
    headers = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.request(
        method=method,
        url=f"{BASE_URL}{path}",
        headers=headers,
        json=json_body,
        data=form_data,
        timeout=30,
    )

    if not response.ok:
        # Do not print device keys or authorization headers.
        raise RuntimeError(
            f"{method} {path} failed: "
            f"HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    if not response.content:
        return {}

    return response.json()


# --------------------------------------------------
# HELPER: FIND FIELD IN RESPONSE
# Supports direct or commonly nested API responses.
# --------------------------------------------------

def get_field(data: dict, field: str):
    if field in data:
        return data[field]

    for nested_key in ("data", "organization", "vehicle", "result"):
        nested = data.get(nested_key)

        if isinstance(nested, dict):
            if field in nested:
                return nested[field]

    raise KeyError(
        f"Response does not contain '{field}'. "
        f"Check your API response schema."
    )


# --------------------------------------------------
# 1. CREATE ORGANIZATION + ITS ADMIN
# Adapt this payload to your Organization schema.
# --------------------------------------------------

def build_organization_payload(
    index: int,
    admin_name:str,
    admin_email: str,
    password: str,
    confirm_password: str

):
    return {
        "organization_name": f"Logistics-{RUN_ID} {index}",
        "admin_name": admin_name,
        "admin_email": admin_email,
        "password": password,
        "confirm_password": confirm_password

        # Add or rename fields required by your schema.
    }


# --------------------------------------------------
# 2. LOGIN AS THE NEW ORGANIZATION ADMIN
# Adapt this if your login endpoint accepts JSON
# rather than OAuth2 form data.
# --------------------------------------------------

def login_admin(email: str, password: str) -> str:
    response = api_request(
        method="POST",
        path=LOGIN_PATH,
        json_body={
            "email": email,
            "password": password,
        },
    )

    token = get_field(response, "access_token")
    return token


# --------------------------------------------------
# 3. CREATE VEHICLE
# Adapt these fields to your VehicleCreateRequest.
# Organization ownership should be derived from the
# authenticated admin on the backend, if supported.
# --------------------------------------------------

def build_vehicle_payload(org_index:int,vehicle_index: int):
    return {
        "registration_number": f"GJ-TST-{RUN_ID}-{org_index}-{vehicle_index}"
        # Add all other required vehicle fields here.
        # Do not send organization_id if your API
        # derives it from the authenticated admin.
    }


# --------------------------------------------------
# SAVE KEYS AS SOON AS DEVICES ARE REGISTERED
# This file contains secrets. Keep it local.
# --------------------------------------------------

def save_credentials(devices: list[dict]):
    OUTPUT_FILE.write_text(
        json.dumps(devices, indent=2),
        encoding="utf-8",
    )

    # Restrict file permissions on systems that support chmod.
    try:
        os.chmod(OUTPUT_FILE, 0o600)
    except OSError:
        pass


# --------------------------------------------------
# MAIN PROVISIONING FLOW
# --------------------------------------------------

def main():
    credentials = []

    for org_index in range(1, ORGANIZATION_COUNT + 1):
        print(
            f"Creating organization "
            f"{org_index}/{ORGANIZATION_COUNT}"
        )
        admin_name = f"test-admin-{RUN_ID}-{org_index}"
        admin_email = (
            f"test-admin-{RUN_ID}-{org_index}@testing.com"
        )
        admin_password = "testing@123"

        # Create organization and its admin.
        organization_response = api_request(
            method="POST",
            path=ORGANIZATION_CREATE_PATH,
            json_body=build_organization_payload(
                org_index,
                admin_name,
                admin_email,
                admin_password,
                admin_password
            ),
        )

        organization_id = get_field(
            organization_response,
            "organization_id",
        )

        # Log in as that organization's admin.
        admin_token = login_admin(
            admin_email,
            admin_password,
        )

        for vehicle_index in range(
            1,
            VEHICLES_PER_ORGANIZATION + 1,
        ):
            vehicle_name = (
                f"Org{org_index}-Vehicle{vehicle_index}"
            )

            print(
                f"  Creating vehicle "
                f"{vehicle_index}/{VEHICLES_PER_ORGANIZATION}"
            )

            # Create vehicle.
            vehicle_response = api_request(
                method="POST",
                path=VEHICLE_CREATE_PATH,
                token=admin_token,
                json_body=build_vehicle_payload(
                    org_index,
                    vehicle_index
                ),
            )

            vehicle_id = get_field(
                vehicle_response,
                "vehicle_id",
            )

            # Register device for that vehicle.
            device_path = DEVICE_REGISTER_PATH.format(
                vehicle_id=vehicle_id
            )

            device_response = api_request(
                method="POST",
                path=device_path,
                token=admin_token,
                json_body={
                    "device_name": f"GPS-{vehicle_name}"
                },
            )

            # Your registration API must return the original
            # device key once. The DB should store only its hash.
            device_key = get_field(
                device_response,
                "device_key",
            )

            device_id = get_field(
                device_response,
                "device_id",
            )

            credentials.append({
                "organization_id": str(organization_id),
                "vehicle_id": str(vehicle_id),
                "device_id": str(device_id),
                "device_key": device_key,
            })

            # Save immediately so keys aren't lost if a later
            # request fails.
            save_credentials(credentials)

    print("\nProvisioning complete.")
    print(f"Devices created: {len(credentials)}")
    print(f"Credentials saved to: {OUTPUT_FILE}")
    print("Do not commit this file to Git.")


if __name__ == "__main__":
    main()