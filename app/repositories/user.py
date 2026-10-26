from ..schemas.users import CreateUserRequest
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user import User
from sqlalchemy import select
from uuid import UUID
from ..utils.security import hash_password

async def insert_user(data:CreateUserRequest,organization_id:UUID,session:AsyncSession):
 try:
    hashed_password=hash_password(data.password)
    new_user = User(
      organization_id=organization_id,
      name=data.name,
      email=data.email,
      password_hash=hashed_password,
      role=data.role
      )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user
 
 except Exception as e:
    
    await session.rollback()
    raise


async def user_get(email:str,session:AsyncSession):

  statement=select(User).where(User.email==email)
  result=await session.execute(statement)
  user=result.scalar_one_or_none()
  return user

async def user_get_by_uid(user_id:UUID,session:AsyncSession):

  statement=select(User).where(User.user_id==user_id)
  result=await session.execute(statement)
  user=result.scalar_one_or_none()
  return user


