from app.core.database import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
import uuid
from sqlalchemy import UUID,DateTime,String,ForeignKey,Boolean,Index
from datetime import datetime,timezone

class VehicleDevice(Base):
  __tablename__="vehicle_devices"


  device_id :Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4
  )

  vehicle_id:Mapped[uuid.UUID] = mapped_column(
    ForeignKey("vehicles.vehicle_id"),
    nullable=False
  )

  device_name:Mapped[str] = mapped_column(
    String(100),
    nullable=False
  )

  key_hash:Mapped[str] = mapped_column(
    String(100),
    unique=True,
    nullable=False
  )

  is_active:Mapped[bool] = mapped_column(
    Boolean,
    nullable=False,
    default=True
  )

  created_at : Mapped[datetime] =mapped_column(
    DateTime(timezone=True),
    nullable=False,
    default=lambda : datetime.now(timezone.utc)
  )
# this ensure that one vehicle has only one active device
  __table_args__=(
    Index(
      "uq_vehicle_devices_one_active_per_vehicle",
      vehicle_id,
      unique=True,
      postgresql_where=is_active.is_(True),
    ),
  )
  vehicle=relationship("Vehicle",back_populates="vehicle_device")
