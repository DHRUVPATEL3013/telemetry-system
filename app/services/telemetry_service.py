from app.schemas.telemetry import TelemetryCreateRequest
from ..repositories.telemetry import insert_telemetry,fetch_telemetry
from ..repositories.vehicle import get_vehicle_for_organization, vehicle_get
from sqlalchemy.ext.asyncio import AsyncSession
from ..exceptions.vehicle_exception import VehicleDoesNotExist
from uuid import UUID
from ..core.settings import setting



class TelemetryService:
    async def create_telemetry(self,data:TelemetryCreateRequest,vehicle_id,session:AsyncSession):

        # if not await vehicle_get(vehicle_id,session):
        #     raise VehicleDoesNotExist()

        alert_type=None
        alert_message=None

        if data.speed > setting.OVERSPEED_LIMIT_KMH:
            alert_type="overspeed"
            alert_message=(
                f"Vehicle speed {data.speed} km/h "
                f"exceeded the limit of "
                f"{setting.OVERSPEED_LIMIT_KMH} km/h."
            )


        return await insert_telemetry(
            data,
            vehicle_id,
            session,
            alert_type,
            alert_message
            )

    async def get_telemetries(self,vehicle_id:UUID,organization_id:UUID,limit,offset,session:AsyncSession):
        if not await vehicle_get(vehicle_id,session):
            raise VehicleDoesNotExist()

        if await get_vehicle_for_organization(vehicle_id,organization_id,session) is None:
            raise VehicleDoesNotExist()

        records,has_more= await fetch_telemetry(vehicle_id,limit,offset,session)

        return {
        "vehicle_id": vehicle_id,
        "items": records,
        "limit": limit,
        "offset": offset,
        "has_more": has_more,
    }


    

