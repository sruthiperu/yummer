# Daily AI token limits for clean/modify

from __future__ import annotations
from datetime import date, datetime, timezone
from uuid import uuid4
from fastapi import HTTPException, Request, Response
from sqlalchemy.orm import Session
from app.models.recipe import DailyTokenUsage
from app.routers.auth import _cookie_secure

DAILY_TOKEN_LIMIT = 25000
LIMIT_MESSAGE = "Sorry! You've reached your token limit for the day. Check back in tomorrow!"
ANON_COOKIE = "yummer_anon_id"
ANON_COOKIE_MAX_AGE = 60 * 60 * 24 * 365


def utc_today() -> date:
    return datetime.now(timezone.utc).date()


def resolve_subject(request: Request, optional_user_id: int | None) -> tuple[str, str | None]:
    """
    return (subject_key, anon_id_to_set)
    anon_id_to_set is set when a new anonymous cookie must be written on the response
    """
    
    if optional_user_id is not None:
        return f"user:{optional_user_id}", None

    existing = request.cookies.get(ANON_COOKIE)
    if existing:
        return f"anon:{existing}", None

    anon_id = str(uuid4())
    return f"anon:{anon_id}", anon_id


def attach_anon_cookie(response: Response, anon_id: str | None) -> None:
    if not anon_id:
        return
    
    response.set_cookie(
        key=ANON_COOKIE,
        value=anon_id,
        httponly=True,
        secure=_cookie_secure(),
        samesite="lax",
        path="/",
        max_age=ANON_COOKIE_MAX_AGE,
    )


def get_tokens_used(db: Session, subject_key: str, usage_date: date | None = None) -> int:
    day = usage_date or utc_today()
    row = (db.query(DailyTokenUsage).filter(DailyTokenUsage.subject_key == subject_key, DailyTokenUsage.usage_date == day).first())

    return int(row.tokens_used) if row else 0


def ensure_under_limit(db: Session, subject_key: str) -> None:
    if get_tokens_used(db, subject_key) >= DAILY_TOKEN_LIMIT:
        raise HTTPException(status_code=429, detail=LIMIT_MESSAGE)


def add_tokens(db: Session, subject_key: str, tokens: int, usage_date: date | None = None) -> None:
    if tokens <= 0:
        return
    
    day = usage_date or utc_today()
    row = (db.query(DailyTokenUsage).filter(DailyTokenUsage.subject_key == subject_key, DailyTokenUsage.usage_date == day).first())
    if row:
        row.tokens_used = int(row.tokens_used or 0) + tokens
    else:
        db.add(DailyTokenUsage(subject_key=subject_key, usage_date=day, tokens_used=tokens))
    db.commit()
