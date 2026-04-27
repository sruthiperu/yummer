# Creates JWT tokens to handle user authentication 

from jose import jwt, JWTError
from fastapi import HTTPException, Cookie
from app.config import settings

from datetime import datetime, timedelta

def create_jwt(user_id):
    """
    generates a login token to validate user
    """

    payload = {"sub": str(user_id), "exp": datetime.utcnow() + timedelta(days=7)}

    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_jwt(token):
    """
    checks if token is valid
    """

    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or Expired token")
    

def get_current_user_id(access_token: str = Cookie(default=None)):
    """
    reads token from browser cookies, requires login
    returns user id 
    """

    if not access_token: raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = decode_jwt(access_token)

    return int(payload["sub"])


def get_optional_user_id(access_token: str = Cookie(default=None)):
    """
    reads token from browser cookies, login is optional
    returns user id
    """
    
    if not access_token: return None
    
    try:
        payload = decode_jwt(access_token)
        return int(payload["sub"])
    except:
        return None
