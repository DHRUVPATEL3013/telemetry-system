from datetime import timedelta,datetime,timezone
import uuid
from jose import jwt,JWTError
from ..core.settings import setting


def create_access_token(user_data:dict,expiry:timedelta=None,refresh:bool=False):
    """ generate the access token and return that token """
    
    payload={}
    payload['user']=user_data
    payload["exp"]=datetime.now(timezone.utc) + (expiry if expiry is not None else timedelta(hours=setting.ACCESS_TOKEN_EXPIRY))
    payload['jti']=str(uuid.uuid4())
    payload['refresh']=refresh


    token=jwt.encode(
        payload,
        setting.SECRET_KEY,
        algorithm=setting.ALGORITHM
    )

    return token

def decode_token(token:str) -> dict:
    """ decode the access token and return the token data (token data only includes payload ,not secret key ,algorithms or signature) """
    try:
        token_data=jwt.decode(
            token,
            key=setting.SECRET_KEY,
            algorithms=[setting.ALGORITHM]
        ) # jwt.decode only returns the payload .it does not return secret key,algorithms or signature

        return token_data
    except JWTError as e:
        print(e)
        return None
