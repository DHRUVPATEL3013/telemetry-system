from app.core.database import Base
from sqlalchemy import ForeignKey,UUID,DateTime,String,Float,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column,relationship
import uuid
from datetime import datetime,timezone





class Alert(Base):
  __tablename__="alerts"

  alert_id:Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4
  )

  telemetry_id:Mapped[uuid.UUID]=mapped_column(
    ForeignKey("telemetries.telemetry_id"),
    nullable=False
  )

  vehicle_id:Mapped[uuid.UUID]=mapped_column(
      ForeignKey("vehicles.vehicle_id"),
      nullable=False
    )
  alert_type:Mapped[str]=mapped_column(
      String,
      nullable=False
    )
  message:Mapped[str]=mapped_column(
      String,
      nullable=False
    )
  created_at:Mapped[datetime]=mapped_column(
      DateTime(timezone=True),
      nullable=False,
      default=lambda : datetime.now(timezone.utc)
    )

  telemetry=relationship("Telemetry",back_populates="alerts")
  vehicle=relationship("Vehicle",back_populates="alerts")
  
