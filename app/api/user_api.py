from sqlalchemy.ext.asyncio import AsyncSession
from ..services.user_service import UserService
from ..schemas.users import UserResponse,CreateUserRequest
from fastapi import Depends,APIRouter
from ..core.database import get_session
from ..exceptions.organizations_exception import OrganizationDoesNotExist,OrganizationNotProvided
from ..exceptions.user_exception import UserAlreadyExist,UserDoesNotExist
from uuid import UUID
from fastapi import HTTPException,status
from ..dependencies.auth_dependencies import RoleChecker
from ..models.user import User


user_service=UserService()
user_router=APIRouter()

@user_router.post("/create-user",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
async def add_user(data:CreateUserRequest,session:AsyncSession=Depends(get_session),current_user:User=Depends(RoleChecker(['admin']))):

  try:
    organization_id=current_user.organization_id
    user=await user_service.user_add(data,organization_id,session)
    return user
  except UserAlreadyExist:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"user with email {data.email} Already Exist")
  except OrganizationDoesNotExist:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"organization with id {data.organization_id} does not exist.")
  except OrganizationNotProvided:
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,detail=f"please provide organization id ")


@user_router.get("/get-user",response_model=UserResponse)
async def get_user(email:str,session:AsyncSession=Depends(get_session),current_user:User=Depends(RoleChecker(['admin']))):

  try:
    user=await user_service.get_user(email,session)
    return user
  except UserDoesNotExist:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"user with email {email} Does Not Exist")
