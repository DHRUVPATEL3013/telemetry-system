from sqlalchemy.orm import mapped_column,Mapped, relationship
import uuid
from sqlalchemy import UUID,String,ForeignKey,DateTime
from datetime import datetime,timezone
from app.core.database import Base




class Vehicle(Base):
  __tablename__="vehicles"

  vehicle_id:Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4
  )

  organization_id:Mapped[uuid.UUID] = mapped_column(
    ForeignKey("organizations.organization_id"),
    nullable=False

  )

  registration_number:Mapped[str] = mapped_column(
    String(50),
    nullable=False,
    unique=True
  )

  status : Mapped[str] = mapped_column(
    String(20),
    nullable=False,
    default="active"
  )

  created_at : Mapped[datetime] =mapped_column(
    DateTime(timezone=True),
    nullable=False,
    default=lambda : datetime.now(timezone.utc)
  )

  updated_at : Mapped[datetime] =mapped_column(
    DateTime(timezone=True),
    nullable=False,
    default=lambda : datetime.now(timezone.utc),
    onupdate=lambda : datetime.now(timezone.utc)
  )

  alerts=relationship("Alert",back_populates="vehicle")
  telemetries=relationship("Telemetry",back_populates="vehicle")
  vehicle_state=relationship("VehicleState",back_populates="vehicle",uselist=False)
  organization = relationship("Organization",back_populates="vehicles")
  vehicle_device=relationship("VehicleDevice",back_populates="vehicle")




  

