from ..models.telemetry import Telemetry
from sqlalchemy.ext.asyncio import AsyncSession
from ..services.organization_service import OrganizationService
from ..schemas.organization import CreateOrganization,OrganizationResponse
from fastapi import Depends,APIRouter
from ..core.database import get_session
from ..exceptions.organizations_exception import OrganizationAlreadyExist
from ..exceptions.user_exception import UserAlreadyExist
from fastapi import HTTPException,status


organization_service=OrganizationService()
organization_router=APIRouter()

@organization_router.post("/create-organization",response_model=OrganizationResponse,status_code=status.HTTP_201_CREATED)
async def create_organization(data:CreateOrganization,session:AsyncSession=Depends(get_session)):
  try:
    organization_obj,admin_obj=await organization_service.create_organization(data,session)
    return OrganizationResponse(
      organization_id=organization_obj.organization_id,
      organization_name=organization_obj.organization_name,
      admin_name=admin_obj.name,
      admin_email=admin_obj.email,
      created_at=organization_obj.created_at,
      updated_at=organization_obj.updated_at
    )
  except OrganizationAlreadyExist:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Organization with name {data.organization_name} Already Exist.")
  except UserAlreadyExist:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"User with email {data.admin_email} Already Exist.")

