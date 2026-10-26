from app.core.database import Base
from sqlalchemy import UUID,DateTime,String
from sqlalchemy.orm import Mapped,mapped_column,relationship
import uuid
from datetime import datetime,timezone



class Organization(Base):
  __tablename__="organizations"

  organization_id:Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4
  )

  organization_name:Mapped[str]=mapped_column(
    String(100),
    unique=True,
    nullable=False
  )

  created_at:Mapped[datetime]=mapped_column(
      DateTime(timezone=True),
      nullable=False,
      default=lambda : datetime.now(timezone.utc)

    )
  updated_at:Mapped[datetime]=mapped_column(
      DateTime(timezone=True),
      nullable=False,
      default=lambda : datetime.now(timezone.utc),
      onupdate=lambda : datetime.now(timezone.utc)
    )

  users=relationship("User",back_populates="organization")
  vehicles = relationship("Vehicle",back_populates="organization")




