from typing import Generator

from fastapi import Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_token
from app.core.database import SessionLocal
from app.models.user import User


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def admin_auth(x_admin_token: str | None = Header(default=None, alias="X-Admin-Token")) -> None:
    if x_admin_token is None or x_admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="Unauthorized")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    subject = decode_token(token)
    if subject is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not str(subject).isdigit():
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = db.get(User, int(subject))
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user
