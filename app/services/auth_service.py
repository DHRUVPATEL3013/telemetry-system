from ..schemas.auth import UserLogin
from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.user import user_get
from ..exceptions.user_exception import UserDoesNotExist,InValidCredenetials
from ..utils.security import verify_password
from ..utils.jwt_helper import create_access_token
from fastapi.responses import JSONResponse


class AuthService:

  async def login_user(self,data:UserLogin,session:AsyncSession):
    user = await user_get(data.email,session)
    if user and verify_password(data.password,user.password_hash):
        paylod={
          "uid":str(user.user_id),
          "email":user.email,
          "role":user.role
        }

        access_token=create_access_token(paylod)

        return JSONResponse(
          content={
            "message":"Login Successfull",
            "access_token":access_token
          }
        )
    raise InValidCredenetials()

      
    



