from pydantic import BaseModel
from uuid import UUID
from datetime import datetime



class VehicleCreateRequest(BaseModel):
  registration_number:str
  


class VehicleResponse(BaseModel):
    vehicle_id: UUID
    organization_id: UUID
    registration_number: str
    status: str
    created_at: datetime
    updated_at: datetime


class VehicleStateResponse(BaseModel):
    vehicle_id: UUID
    speed: float
    temperature: float
    latitude: float
    longitude: float
    last_event_timestamp: datetime
    updated_at: datetime


class AlertItemResponse(BaseModel):
        alert_id: UUID
        telemetry_id: UUID
        alert_type: str
        message: str
        created_at: datetime

class AlertListResponse(BaseModel):
        vehicle_id: UUID
        items: list[AlertItemResponse]
        limit: int
        offset: int
        has_more: bool


class VehicleDeviceRegister(BaseModel):
     device_name:str

class VehicleDeviceResponse(BaseModel):
     device_id:UUID
     vehicle_id:UUID
     device_name:str
     is_active:bool
     created_at:datetime





