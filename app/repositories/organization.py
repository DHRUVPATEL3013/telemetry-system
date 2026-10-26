from ..schemas.organization import CreateOrganization 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.organization import Organization
from ..models.user import User
from uuid import UUID
from ..exceptions.organizations_exception import OrganizationNotProvided



async def insert_organization(data:CreateOrganization,password_hash:str,session:AsyncSession):

  try:
    new_organization=Organization(
       organization_name=data.organization_name
       )
    session.add(new_organization)
    await session.flush()

    new_user=User(
       organization_id=new_organization.organization_id,
       name=data.admin_name,
       email=data.admin_email,
       role="admin",
       password_hash=password_hash
    )
    print(f"new_user: {new_user}")
    session.add(new_user)
    await session.commit()
    await session.refresh(new_organization)
    await session.refresh(new_user)

    return new_organization,new_user

  except Exception as e:
    await session.rollback()
    raise


async def is_organization_already_exist(session:AsyncSession,organization_name:str=None,organization_id:UUID=None):
    
    if organization_name:
      statement=select(Organization).where(Organization.organization_name==organization_name)
    elif organization_id:
      statement=select(Organization).where(Organization.organization_id==organization_id)
    else:
        raise OrganizationNotProvided()
    result=await session.execute(statement)
    organization = result.scalar_one_or_none()

    if organization:
       return True
    return False




    


    

  
