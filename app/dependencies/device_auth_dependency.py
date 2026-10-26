
from fastapi import HTTPException,status,Depends
from ..utils.device_keys import hash_device_key
from sqlalchemy import select
from ..models.vehicle_device import VehicleDevice
from ..core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession


async def get_current_device(x_device_key:str,session:AsyncSession=Depends(get_session)):
  if not x_device_key:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Device key is required")

  key_hash=hash_device_key(x_device_key)

  statement=select(VehicleDevice).where(VehicleDevice.key_hash==key_hash)
  result=await session.execute(statement)

  device = result.scalar_one_or_none()

  if not device:
     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Device key")

  return device



