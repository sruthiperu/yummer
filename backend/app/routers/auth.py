# Implements google oauth login, allows users to sign in with their google account rather than creating an account/password

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi import Request
from sqlalchemy.orm import Session

from app.auth import create_jwt
from app.database import get_db
from app.models.recipe import User
from app.config import settings


GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO = "https://www.googleapis.com/oauth2/v3/userinfo"
REDIRECT = "http://localhost:8000/api/v1/auth/callback"     # update when deploying
FRONTEND = "http://localhost:3000"                        # update when deploying

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/google")
def google_login():
    """
    redirects user to google consent screen
    """

    params = {"client_id": settings.google_client_id, "redirect_uri": REDIRECT, "response_type": "code", 
              "scope": "openid email profile", "access_type": "offline"}
    
    # convert params into 1 string
    params_lst = []
    for k, v in params.items():
        params_lst.append(f"{k}={v}")
    params_str = '&'.join(params_lst)

    return RedirectResponse(f"{GOOGLE_AUTH}?{params_str}")

    # full_url = f"{GOOGLE_AUTH}?{params_str}"
    # print(f"DEBUG: Full URL: {full_url}") 
    # return RedirectResponse(full_url)


@router.get("/callback")
def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    completes login process after user signs in with google
    given: code (str), db (session)
    """
    code = request.query_params.get("code")
    print("=" * 50)
    print("CALLBACK WAS HIT")
    print("=" * 50)
    # get code
    token_response = httpx.post(GOOGLE_TOKEN, data={"code": code, "client_id": settings.google_client_id, 
                                                    "client_secret": settings.google_client_secret, 
                                                    "redirect_uri": REDIRECT, "grant_type": "authorization_code"})
    if token_response.status_code != 200: raise HTTPException(status_code=400, detail="Failed to get valid code")
    
    access_token = token_response.json()["access_token"]

    # get user info
    userinfo_res = httpx.get(GOOGLE_USER_INFO, headers={"Authorization": f"Bearer {access_token}"})
    if userinfo_res.status_code != 200: raise HTTPException(status_code=400, detail="Failed to get user info")

    # extract info (id, email, name) for database
    userinfo = userinfo_res.json()
    google_id = userinfo["sub"]
    email = userinfo["email"]
    name = userinfo.get("name", "")

    # check if user already exists in database
    user = db.query(User).filter(User.google_id == google_id).first()

    if not user:    # user not in database, create user
        user = User(google_id=google_id, email=email, name=name, date_created=__import__("datetime").datetime.utcnow())
        
        db.add(user)
        db.commit()
        db.refresh(user)
    
    
    token = create_jwt(user.id)

    # redirect to frontend
    response = RedirectResponse(url=FRONTEND)
    # max_age = 60 * 60 * 24 * 7 -> cookie expires after 7 days
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=604800, samesite="lax")
    
    
    return response

        
@router.get("/logout")
def logout():
    """
    Logs user out by deleting login cookie, redirects to frontend
    """
    response = RedirectResponse(url=FRONTEND)
    response.delete_cookie("access_token")
    
    return response
    

@router.get("/test")
def test():
    print("TEST ROUTE WAS HIT")
    return {"message": "Auth router is working"}