from app.schemas.organization import CreateOrganization
from ..repositories.organization import insert_organization,is_organization_already_exist
from sqlalchemy.ext.asyncio import AsyncSession
from ..exceptions.organizations_exception import OrganizationAlreadyExist
from ..exceptions.user_exception import UserAlreadyExist
from ..repositories.user import user_get
from ..utils.security import hash_password



class OrganizationService:
  async def create_organization(self,data:CreateOrganization,session:AsyncSession):
    if await is_organization_already_exist(organization_name=data.organization_name,session=session):
      raise OrganizationAlreadyExist()

    if await user_get(data.admin_email,session ):
      raise UserAlreadyExist()

    password_hash=hash_password(data.password)
    
    return await insert_organization(data,password_hash,session)