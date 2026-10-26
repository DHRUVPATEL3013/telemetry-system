from ..models.telemetry import Telemetry
from sqlalchemy.ext.asyncio import AsyncSession
from ..services.telemetry_service import TelemetryService
from ..schemas.telemetry import TelemetryCreateRequest,TelemetryResponse
from fastapi import Depends,APIRouter
from ..core.database import get_session
from ..exceptions.vehicle_exception import VehicleDoesNotExist
from fastapi import HTTPException,status
from ..dependencies.device_auth_dependency import get_current_device
from ..models.vehicle_device import VehicleDevice


telemetry_service=TelemetryService()
telemetry_router=APIRouter()

@telemetry_router.post("/create-telemetry",response_model=TelemetryResponse)
async def create_telemetry(data:TelemetryCreateRequest,device:VehicleDevice=Depends(get_current_device),session:AsyncSession=Depends(get_session)):

  try:
    telemetry_obj,status_of_telemetry=await telemetry_service.create_telemetry(data,device.vehicle_id,session)
    return TelemetryResponse(
      telemetry_id=telemetry_obj.telemetry_id,
          event_id=telemetry_obj.event_id,
          vehicle_id=telemetry_obj.vehicle_id,
          received_at=telemetry_obj.received_at,
          status=status_of_telemetry,
    )
  except VehicleDoesNotExist:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"vehicle with id {device.vehicle_id} does not exist.")

