from ..models.vehicle import Vehicle
from sqlalchemy.ext.asyncio import AsyncSession
from ..services.vehicle_service import VehicleService
from ..services.telemetry_service import TelemetryService
from ..schemas.vehicle import VehicleCreateRequest,VehicleResponse,VehicleStateResponse,AlertListResponse,VehicleDeviceRegister,VehicleDeviceResponse
from ..schemas.telemetry import TelemetryListResponse
from fastapi import Depends,APIRouter, Query
from ..core.database import get_session
from ..exceptions.organizations_exception import OrganizationDoesNotExist
from ..exceptions.vehicle_exception import VehicleDoesNotExist,CurrentStateNotFound,NoAlertsFound
from fastapi import HTTPException,status
from uuid import UUID
from ..dependencies.auth_dependencies import RoleChecker
from ..models.user import User


vehicle_service=VehicleService()
telemetries_service=TelemetryService()
vehicle_router=APIRouter()

@vehicle_router.post("/create-vehicle",response_model=VehicleResponse)
async def create_telemetry(data:VehicleCreateRequest,session:AsyncSession=Depends(get_session),current_user:User=Depends(RoleChecker(["admin"]))):
  try:
    organization_id=current_user.organization_id
    vehicle_obj=await vehicle_service.create_vehicle(data,organization_id,session)
    return vehicle_obj
  except OrganizationDoesNotExist:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Organization with id {data.organization_id} does not exists.")



@vehicle_router.post("/vehicles/{vehicle_id}",response_model=VehicleResponse)
async def get_vehicle(vehicle_id:UUID,session:AsyncSession=Depends(get_session),current_user:User=Depends(RoleChecker(["admin","fleet_manager"]))):
  try:
    vehicle=await vehicle_service.get_vehicle(vehicle_id,current_user.organization_id,session)
    return vehicle
  except VehicleDoesNotExist:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Vehicle with id {vehicle_id} does not exists.")


@vehicle_router.get("/vehicles/{vehicle_id}/telemetry",response_model=TelemetryListResponse)
async def get_vehicle_telemetries(
  vehicle_id:UUID,
  limit:int=Query(default=100,ge=1,le=1000),
  offset:int=Query(default=0,ge=0),
  session:AsyncSession=Depends(get_session),
  current_user:User=Depends(RoleChecker(["admin","fleet_manager"]))
  ):
  try:
    telemetries=await telemetries_service.get_telemetries(vehicle_id,current_user.organization_id,limit,offset,session)
    return telemetries
  except VehicleDoesNotExist:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Vehicle with id {vehicle_id} does not exists.")


@vehicle_router.get("/vehicles/{vehicle_id}/state",response_model=VehicleStateResponse)
async def get_vehicle_current_state(
  vehicle_id:UUID,
  session:AsyncSession=Depends(get_session),
  current_user:User=Depends(RoleChecker(["admin","fleet_manager"]))
  ):
  try:
    vehicle_current_state=await vehicle_service.get_vehicle_state(vehicle_id,current_user.organization_id,session)
    print(vehicle_current_state)

    return vehicle_current_state
  except VehicleDoesNotExist:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Vehicle with id {vehicle_id} does not exists.")
  except CurrentStateNotFound:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Current state is not available yet for vehicle ID {vehicle_id}.")


@vehicle_router.get("/vehicles/{vehicle_id}/alerts",response_model=AlertListResponse)
async def get_vehicle_alerts(
  vehicle_id:UUID,
  limit:int=Query(default=100,ge=1,le=1000),
  offset:int=Query(default=0,ge=0),
  session:AsyncSession=Depends(get_session),
  current_user:User=Depends(RoleChecker(["admin","fleet_manager"]))
  ):
  try:
    vehicle_alerts=await vehicle_service.get_vehicle_alerts(vehicle_id,current_user.organization_id,limit,offset,session)
    print(vehicle_alerts)
    return vehicle_alerts
  
  except VehicleDoesNotExist:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Vehicle with id {vehicle_id} does not exists.")
  
  except NoAlertsFound:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No Alerts Found for  Vehicle id {vehicle_id}")



@vehicle_router.post("/vehicles/{vehicle_id}/devices",response_model=VehicleDeviceResponse)
async def register_device(data:VehicleDeviceRegister,vehicle_id:UUID,session:AsyncSession=Depends(get_session)):
  try:
    device= await vehicle_service.device_register(data,vehicle_id,session)
    return device

  except VehicleDoesNotExist:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Vehicle Nott found")


  


  

  



