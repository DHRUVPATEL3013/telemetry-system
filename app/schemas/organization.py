from pydantic import BaseModel,Field
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel,EmailStr,field_validator,model_validator

from app.core.config import contains_number, contains_special_character


class CreateOrganization(BaseModel):
  organization_name:str
  admin_name:str
  admin_email:EmailStr
  password:str
  confirm_password:str


  
  @field_validator("admin_name")
  @classmethod
  def validate_name(cls,admin_name:str):
          if len(admin_name.strip())< 2 :
              return f"name must be greater than 2 characters."
          return admin_name.strip()

  
  @field_validator("password")
  @classmethod
  def validate_password(cls,password:str):
          if len(password)< 6:
              raise ValueError(f"password must be greater than 6 characters.")
          if not contains_special_character(password):
              raise ValueError(f"password should contain special characters.")
          if not contains_number(password):
              raise ValueError(f"password should contain numbers.")
          return password
  
  @model_validator(mode="after")
  def validate_confirm_password(self):
          if self.password != self.confirm_password:
              raise ValueError("Password and confirm password must match.")
          return self

class OrganizationResponse(BaseModel):
    organization_id: UUID
    organization_name: str
    admin_name:str
    admin_email:EmailStr
    created_at: datetime
    updated_at: datetime

