from uuid import UUID
from ..repositories.user import user_get,insert_user
from sqlalchemy.ext.asyncio import AsyncSession
from ..exceptions.user_exception import UserDoesNotExist,UserAlreadyExist
from ..schemas.users import CreateUserRequest
from ..repositories.organization import is_organization_already_exist
from ..exceptions.organizations_exception import OrganizationDoesNotExist,OrganizationNotProvided


class UserService:


  async def user_add(self,data:CreateUserRequest,organization_id:UUID,session:AsyncSession):
    
      organization=await is_organization_already_exist(session,organization_id=organization_id)
      
      if not organization:
        raise OrganizationDoesNotExist()
      

      user=await user_get(data.email,session)
      if user:
        raise UserAlreadyExist()
      return await insert_user(data,organization_id,session)
   


  async def get_user(self,email:str,session:AsyncSession):
    user=await user_get(email,session)
    if user is None:
      raise UserDoesNotExist()
    return user
