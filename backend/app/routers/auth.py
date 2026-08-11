# Google OAuth login; JWT cookie session

from datetime import datetime
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth import create_jwt
from app.config import settings
from app.database import get_db
from app.models.recipe import User

FRONTEND = settings.frontend_url.rstrip("/")
API_BASE = settings.api_base_url.rstrip("/")

GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO = "https://www.googleapis.com/oauth2/v3/userinfo"
GOOGLE_REDIRECT = f"{API_BASE}/auth/callback/google"

COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 60 * 60 * 24 * 7

router = APIRouter(prefix="/auth", tags=["auth"])


def _cookie_secure() -> bool:
    if settings.cookie_secure is not None:
        return settings.cookie_secure

    return settings.frontend_url.startswith("https")


def _sanitize_next(next_path: str | None) -> str:
    """
    only allow same-site relative paths
    """

    if not next_path:
        return "/"
    path = next_path.strip()
    if not path.startswith("/") or path.startswith("//"):
        return "/"
    if "://" in path:
        return "/"
    return path


def _frontend_redirect(next_path: str | None) -> str:
    return f"{FRONTEND}{_sanitize_next(next_path)}"


def _set_auth_cookie(response: RedirectResponse, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=COOKIE_MAX_AGE,
        samesite="lax",
        secure=_cookie_secure(),
        path="/",
    )


def _clear_auth_cookie(response: RedirectResponse) -> None:
    response.delete_cookie(
        key=COOKIE_NAME, 
        path="/",
        secure=_cookie_secure(),
        samesite="lax",
    )


def _upsert_user(db: Session, *, provider_user_id: str, email: str, name: str) -> User:
    user = (
        db.query(User)
        .filter(
            User.auth_provider == "google",
            User.provider_user_id == provider_user_id,
        )
        .first()
    )
    if user:
        if email and user.email != email:
            user.email = email
        if name and user.name != name:
            user.name = name
        db.commit()
        db.refresh(user)
        return user

    if email:
        by_email = db.query(User).filter(User.email == email).first()
        if by_email:
            by_email.auth_provider = "google"
            by_email.provider_user_id = provider_user_id
            if name:
                by_email.name = name
            db.commit()
            db.refresh(by_email)
            return by_email

    user = User(
        auth_provider="google",
        provider_user_id=provider_user_id,
        email=email,
        name=name or email or "User",
        date_created=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _finish_login(user: User, next_path: str | None) -> RedirectResponse:
    token = create_jwt(user.id)
    response = RedirectResponse(url=_frontend_redirect(next_path))
    _set_auth_cookie(response, token)
    return response


@router.get("/google")
def google_login(next: str | None = Query(default="/")):
    """
    redirect user to Google consent screen
    """

    if not settings.google_client_id:
        raise HTTPException(status_code=500, detail="Google OAuth is not configured")

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": GOOGLE_REDIRECT,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
        "state": _sanitize_next(next),
    }
    return RedirectResponse(f"{GOOGLE_AUTH}?{urlencode(params)}")


@router.get("/callback/google")
def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    complete Google OAuth and set session cookie
    """

    error = request.query_params.get("error")
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")

    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    next_path = _sanitize_next(request.query_params.get("state"))

    token_response = httpx.post(
        GOOGLE_TOKEN,
        data={
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": GOOGLE_REDIRECT,
            "grant_type": "authorization_code",
        },
    )
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange Google code")

    access_token = token_response.json().get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Google token response missing access_token")

    userinfo_res = httpx.get(GOOGLE_USER_INFO, headers={"Authorization": f"Bearer {access_token}"})
    if userinfo_res.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get Google user info")

    userinfo = userinfo_res.json()
    provider_user_id = userinfo.get("sub")
    email = userinfo.get("email") or ""
    name = userinfo.get("name") or ""
    if not provider_user_id:
        raise HTTPException(status_code=400, detail="Google user info missing sub")

    user = _upsert_user(db, provider_user_id=provider_user_id, email=email, name=name)
    
    return _finish_login(user, next_path)


@router.get("/logout")
def logout(next: str | None = Query(default="/")):
    """
    clear login cookie and return to the page the user came from
    """

    response = RedirectResponse(url=_frontend_redirect(next))
    _clear_auth_cookie(response)
    return response


@router.get("/test")
def test():
    return {"message": "Auth router is working"}
