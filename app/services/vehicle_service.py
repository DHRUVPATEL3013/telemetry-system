from ..schemas.vehicle import VehicleCreateRequest,VehicleDeviceRegister
from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.vehicle import insert_vehicle,vehicle_get,vehicle_state_get,vehicle_alert_get,register_new_device
from ..repositories.organization import is_organization_already_exist
from ..exceptions.organizations_exception import OrganizationDoesNotExist
from ..exceptions.vehicle_exception import VehicleDoesNotExist,CurrentStateNotFound,NoAlertsFound
from uuid import UUID
from ..repositories.vehicle import get_vehicle_for_organization
from ..utils.device_keys import hash_device_key,generate_device_key



class VehicleService:

  async def create_vehicle(self,data:VehicleCreateRequest,organization_id:UUID
,session:AsyncSession):

    if await is_organization_already_exist(session=session,organization_id=organization_id):
      return await insert_vehicle(data,organization_id,session)
    raise OrganizationDoesNotExist()


  async def get_vehicle(self,vehicle_id:UUID,organization_id:UUID,session:AsyncSession):
    vehicle = await vehicle_get(vehicle_id,session)

    if await get_vehicle_for_organization(vehicle_id,organization_id,session) is None:
      raise VehicleDoesNotExist()

    if not vehicle:
      raise VehicleDoesNotExist()
    
    return vehicle

  async def get_vehicle_state(self,vehicle_id:UUID,organization_id:UUID,session:AsyncSession):
    vehicle = await vehicle_get(vehicle_id,session)
    if not vehicle:
      raise VehicleDoesNotExist()
    if await get_vehicle_for_organization(vehicle_id,organization_id,session) is None:
      raise VehicleDoesNotExist()
    current_vehicle_state = await vehicle_state_get(vehicle_id,session)
    if current_vehicle_state is None:
      raise CurrentStateNotFound()
    return current_vehicle_state


  async def get_vehicle_alerts(self,vehicle_id:UUID,organization_id:UUID,limit:int,offset:int,session:AsyncSession):
    vehicle = await vehicle_get(vehicle_id,session)
    if not vehicle:
      raise VehicleDoesNotExist()
    if await get_vehicle_for_organization(vehicle_id,organization_id,session) is None:
      raise VehicleDoesNotExist()
    alerts,has_more = await vehicle_alert_get(vehicle_id,limit,offset,session)
    if not alerts:
      raise NoAlertsFound()
    return {
      "vehicle_id":vehicle_id,
      "items": alerts,
      "limit" :limit,
      "offset":offset,
      "has_more" :has_more

    }


  async def device_register(self,data:VehicleDeviceRegister,vehicle_id:UUID,session:AsyncSession):
    if await vehicle_get(vehicle_id,session) is None:
      print("hhh")
      raise VehicleDoesNotExist()
    print("huhu")
    device_key=generate_device_key()
    hash_key=hash_device_key(device_key)

    device = await register_new_device(data,vehicle_id,hash_key,session)
    return device

    
  



      
