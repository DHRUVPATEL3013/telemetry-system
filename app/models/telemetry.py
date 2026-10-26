from app.core.database import Base
from sqlalchemy import ForeignKey,UUID,DateTime,String,Float,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column, relationship
import uuid
from datetime import datetime, timezone


class Telemetry(Base):
  __tablename__="telemetries"

  __table_args__=(
    UniqueConstraint(
      "vehicle_id",
      "event_id",
      name="uq_vehicle_event"
    ),
  )

  telemetry_id:Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4
  )

  event_id:Mapped[str]=mapped_column(
    String(50),
    nullable=False
  )

  vehicle_id:Mapped[uuid.UUID]=mapped_column(
      ForeignKey("vehicles.vehicle_id"),
      nullable=False
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
  event_timestamp:Mapped[datetime]=mapped_column(
      DateTime(timezone=True),
      nullable=False,
    )
  received_at:Mapped[datetime]=mapped_column(
      DateTime(timezone=True),
      default=lambda: datetime.now(timezone.utc),
      nullable=False
    )

  alerts=relationship("Alert",back_populates="telemetry")
  vehicle=relationship("Vehicle",back_populates="telemetries")


