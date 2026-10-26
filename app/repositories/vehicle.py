from ..schemas.vehicle import VehicleCreateRequest,VehicleDeviceRegister
from ..models.vehicle import Vehicle
from ..models.vehicle_state import VehicleState
from ..models.alert import Alert
from ..models.vehicle_device import VehicleDevice
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select

async def insert_vehicle(data:VehicleCreateRequest,organization_id:UUID,session:AsyncSession):
  try:

    new_vehicle=Vehicle(
      organization_id=organization_id,
      registration_number=data.registration_number
    )
    session.add(new_vehicle)
    await session.commit()
    await session.refresh(new_vehicle)

    return new_vehicle

  except Exception as e:
    await session.rollback()
    raise

async def vehicle_get(vehicle_id:UUID,session:AsyncSession):
  statement=select(Vehicle).where(Vehicle.vehicle_id==vehicle_id)
  result=await session.execute(statement)
  vehicle=result.scalar_one_or_none()
  return vehicle

async def vehicle_state_get(vehicle_id:UUID,session:AsyncSession):
  statement=select(VehicleState).where(VehicleState.vehicle_id==vehicle_id)
  result=await session.execute(statement)
  current_state=result.scalar_one_or_none()

  return current_state

async def vehicle_alert_get(vehicle_id:UUID,limit:int,offset:int,session:AsyncSession):
  statement=(
    select(Alert)
    .where(Alert.vehicle_id==vehicle_id)
    .order_by(Alert.created_at.desc())
    .limit(limit+1)
    .offset(offset)
  )
  result=await session.execute(statement)
  alerts=result.scalars().all()

  has_more=len(alerts) > limit

  return alerts[:limit],has_more


async def get_vehicle_for_organization(
    vehicle_id: UUID,
    organization_id: UUID,
    session: AsyncSession,
):
    statement = select(Vehicle).where(
        Vehicle.vehicle_id == vehicle_id,
        Vehicle.organization_id == organization_id,
    )

    result = await session.execute(statement)
    return result.scalar_one_or_none()



async def register_new_device(data:VehicleDeviceRegister,vehicle_id:UUID,key_hash,session:AsyncSession):

    try:
      device=VehicleDevice(
        vehicle_id=vehicle_id,
        device_name=data.device_name,
        key_hash=key_hash
      )

      session.add(device)
      await session.commit()
      await session.refresh(device)
      print("this")

      return device
    except Exception as e:
      print("djnfjnjf")
      await session.rollback()
      raise
