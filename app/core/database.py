from sqlalchemy.orm import declarative_base,sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from app.core.settings import setting
from typing import AsyncGenerator

Base=declarative_base()

async_engine=create_async_engine(
  url=setting.DATABASE_URL,
  echo=False
)


async def get_session()->AsyncGenerator[AsyncSession,None]:
  Session=sessionmaker(bind=async_engine,class_=AsyncSession,expire_on_commit=False)

  async with Session() as session:
    yield session

