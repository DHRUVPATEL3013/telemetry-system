from app.core.database import Base
from sqlalchemy import ForeignKey,UUID,DateTime,String,Float,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column,relationship
import uuid

from datetime import datetime,timezone





class User(Base):
  __tablename__="users"


  user_id:Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4
  )

  organization_id:Mapped[uuid.UUID]=mapped_column(
      ForeignKey("organizations.organization_id"),
      nullable=False
    )
  name:Mapped[str]=mapped_column(
      String(100),
      nullable=False
    )
  email:Mapped[str]=mapped_column(
      String(255),
      unique=True,
      nullable=False
    )
  password_hash:Mapped[str]=mapped_column(
      String(255),
      nullable=False
    )
  role:Mapped[str]=mapped_column(
      String(50),
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

  organization=relationship("Organization",back_populates="users")

