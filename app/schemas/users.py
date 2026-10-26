from datetime import datetime

from pydantic import BaseModel,EmailStr,field_validator,model_validator
from uuid import UUID
from ..core.config import contains_special_character,contains_number

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password :str
    role: str = "user"

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

    @field_validator("name")
    @classmethod
    def validate_name(cls,name:str):
        if len(name.strip())< 2 :
            return f"name must be greater than 2 characters."
        return name.strip()

    @model_validator(mode="after")
    def validate_confirm_password(self):
        if self.password != self.confirm_password:
            raise ValueError("Password and confirm password must match.")
        return self


class UserResponse(BaseModel):
    user_id: UUID
    organization_id: UUID
    name: str
    email: str
    role: str
    created_at: datetime
    updated_at: datetime



    



