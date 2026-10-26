from app.core.database import Base
from sqlalchemy import ForeignKey,UUID,DateTime,String,Float,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column, relationship
import uuid
from datetime import datetime,timezone





class VehicleState(Base):
  __tablename__="vehicle_states"



  vehicle_id:Mapped[uuid.UUID]=mapped_column(
      ForeignKey("vehicles.vehicle_id"),
      primary_key=True
    )

  speed:Mapped[float]=mapped_column(
      Float,
      nullable=False
    )
  temperature:Mapped[float]=mapped_column(
      Float,
      nullable=False
    )
  latitude:Mapped[float]=mapped_column(
      Float,
      nullable=False
    )
  longitude:Mapped[float]=mapped_column(
      Float,
      nullable=False
    )
  last_event_timestamp:Mapped[datetime]=mapped_column(
      DateTime(timezone=True),
      nullable=False,
    )
  updated_at:Mapped[datetime]=mapped_column(
      DateTime(timezone=True),
      nullable=False,
      default=lambda: datetime.now(timezone.utc),
      onupdate=lambda: datetime.now(timezone.utc)
    )
  vehicle=relationship("Vehicle",back_populates="vehicle_state")

  

