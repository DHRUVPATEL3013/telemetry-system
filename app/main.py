from fastapi import FastAPI
from .api.telemetry_api import telemetry_router
from .api.organization_api import organization_router
from .api.vehicle_api import vehicle_router
from .api.user_api import user_router
from .api.auth_api import auth_router
from app.models import (
    Organization,
    User,
    Vehicle,
    Telemetry,
    VehicleState,
    Alert,
)


app=FastAPI()

app.include_router(auth_router,tags=["Auth"])
app.include_router(organization_router,tags=["Organization"])
app.include_router(user_router,tags=["User"])
app.include_router(vehicle_router,tags=["Vehicle"])
app.include_router(telemetry_router,tags=["Telemetry"])

