from pydantic import BaseModel,Field
from uuid import UUID
from datetime import datetime


#POST /telemetry
class TelemetryCreateRequest(BaseModel):
  event_id:str =Field(min_length=1,max_length=100)
  # vehicle_id:UUID
  speed:float=Field(ge=0)
  temperature:float
  latitude:float=Field(ge=-90,le=90)
  longitude:float=Field(ge=-180,le=180)
  event_timestamp:datetime


class TelemetryResponse(BaseModel):
  telemetry_id:UUID
  event_id:str
  vehicle_id:UUID
  received_at:datetime
  status:str



# API → GET /vehicles/{vehicle_id}/telemetry
class TelemetryItemResponse(BaseModel):
    telemetry_id: UUID
    event_id: str
    speed: float
    temperature: float
    latitude: float
    longitude: float
    event_timestamp: datetime
    received_at: datetime

class TelemetryListResponse(BaseModel):
    vehicle_id: UUID
    items: list[TelemetryItemResponse]
    limit: int
    offset: int
    has_more: bool









  
