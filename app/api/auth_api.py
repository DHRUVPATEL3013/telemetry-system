from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends,APIRouter
from ..core.database import get_session
from ..services.auth_service import AuthService
from ..exceptions.user_exception import InValidCredenetials
from fastapi import HTTPException,status
from ..schemas.auth import UserLogin


auth_service=AuthService()
auth_router=APIRouter()


@auth_router.post("/login")
async def login(data:UserLogin,session:AsyncSession=Depends(get_session),):
  try:
    token=await auth_service.login_user(data,session)
    return token
  except InValidCredenetials:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Credentials")
