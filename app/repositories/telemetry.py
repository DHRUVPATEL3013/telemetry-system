from ..schemas.telemetry import TelemetryCreateRequest
from ..core.database import get_session
from ..core.settings import setting
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.telemetry import Telemetry
from ..models.vehicle_state import VehicleState
from ..models.alert import Alert
from ..models.vehicle import Vehicle
from ..exceptions.vehicle_exception import VehicleDoesNotExist
from sqlalchemy.dialects.postgresql import insert
from uuid import UUID


async def insert_telemetry(
      data:TelemetryCreateRequest,
      vehicle_id:UUID,
      session:AsyncSession,
      alert_type:str | None = None,
      alert_message:str | None = None,):
    try:
      # lock this vehicle before processing its telemetry.
      # other requests for the same vehicle must wait.
      lock_statement=(
         select(Vehicle)
         .where(Vehicle.vehicle_id==vehicle_id)
         .with_for_update()
                     )
      lock_result=await session.execute(lock_statement)
      vehicle = lock_result.scalar_one_or_none()

      if vehicle is None:
         raise VehicleDoesNotExist()
      # DUPLICATE EVENT HANDLING (this will insert telemetry if it is new other wise return None) 
      telemetry_values=data.model_dump()
      telemetry_values["vehicle_id"]=vehicle_id
      statement=(
         insert(Telemetry)
         .values(**telemetry_values)
         .on_conflict_do_nothing(
            index_elements=[
               Telemetry.vehicle_id,
               Telemetry.event_id
            ]
         ).returning(Telemetry)
      )

      result=await session.execute(statement)
      new_telemetry=result.scalar_one_or_none()

      if new_telemetry is None:
         await session.rollback()
         # if new telemetry is None that means arrived telemetry is already in databse ,so we return that received telemetry.
         statement=select(Telemetry).where(Telemetry.vehicle_id==vehicle_id,Telemetry.event_id==data.event_id)
         result=await session.execute(statement)
         existing_telemetry=result.scalar_one()

         return existing_telemetry,"already_received"

      #session.add(new_telemetry)   # this should be remove because insert telemetry statement already add this
      #await session.flush()

      #saves the current vehicle state(if telemetry is new then only this will run because if telemetry is already received then we already return that telemetry so this code never executed )

      statement=select(VehicleState).where(VehicleState.vehicle_id==new_telemetry.vehicle_id)
      result=await session.execute(statement)
      vehicle_state=result.scalar_one_or_none()
   
      is_overspeed = new_telemetry.speed > setting.OVERSPEED_LIMIT_KMH  # check whether current telemetry is contain overspeed or not.
      if vehicle_state is None:
          
          is_newer_event = True
          was_overspeed=False
          vehicle_state=VehicleState(
            vehicle_id=new_telemetry.vehicle_id,
            speed=new_telemetry.speed,
            temperature=new_telemetry.temperature,
            latitude=new_telemetry.latitude,
            longitude=new_telemetry.longitude,
            last_event_timestamp=new_telemetry.event_timestamp,
            )
          session.add(vehicle_state)

      
      else:
         # if vehicle state is not none then we check whether its previous speed is overspeed or not
         was_overspeed = vehicle_state.speed > 100 
         
         #check whether the telemetry is latest or not
         is_newer_event = (new_telemetry.event_timestamp > vehicle_state.last_event_timestamp) 
         if is_newer_event:
            vehicle_state.speed=new_telemetry.speed
            vehicle_state.temperature=new_telemetry.temperature
            vehicle_state.latitude=new_telemetry.latitude
            vehicle_state.longitude=new_telemetry.longitude
            vehicle_state.last_event_timestamp=new_telemetry.event_timestamp


      if (
         is_newer_event
         and is_overspeed
         and not was_overspeed
         and alert_type == "overspeed"
         ):

         if alert_type is not None:
            new_alert=Alert(
               telemetry_id=new_telemetry.telemetry_id,
               vehicle_id=new_telemetry.vehicle_id,
               alert_type=alert_type,
               message=alert_message,
            )

            session.add(new_alert)
            await session.flush()



      await session.commit()
      await session.refresh(new_telemetry)
      
      return new_telemetry,"received"

    except Exception as e:
       await session.rollback()
       raise


async def fetch_telemetry(vehicle_id:UUID,limit:int,offset:int,session:AsyncSession):
   try:
      statement =(
               select(Telemetry)
               .where(Telemetry.vehicle_id==vehicle_id)
               .order_by(Telemetry.event_timestamp.desc())
               .limit(limit+1)
               .offset(offset)

      )
      result=await session.execute(statement)
      records= result.scalars().all()
      has_more=len(records) > limit
      return records[:limit],has_more
   
   except Exception as e:
      await session.rollback()
      raise


       





  
  