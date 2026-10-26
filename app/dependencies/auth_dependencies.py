from fastapi.security import HTTPBearer
from fastapi import Depends, Request,HTTPException,status
from fastapi.security.http import HTTPAuthorizationCredentials
from ..utils.jwt_helper import decode_token
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from ..core.database import get_session
from ..models.user import User
from ..repositories.user import user_get_by_uid



class TokenBearer(HTTPBearer):

    def __init__(self,auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request:Request)->HTTPAuthorizationCredentials | None:
        creds= await super().__call__(request)
        token=creds.credentials
        
        token_data=decode_token(token)

        if not token_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid or Expired Token")

        self.verify_token_data(token_data)


        return token_data



    def verify_token_data(self,token_data):
        raise NotImplementedError("Please Override this method in child class")
    



class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data:dict)->None:
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please Provide an Access token"
            )

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data:dict)->None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please Provide Refresh Token"
            )

async def get_current_user(
    token_data: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
) -> User:
    user_id = token_data.get("user", {}).get("uid")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    try:
        parsed_user_id = UUID(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid user ID",
        )


    user = await user_get_by_uid(user_id,session)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user



from fastapi import Depends, HTTPException, status
from ..models.user import User


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
    ):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

        return current_user
