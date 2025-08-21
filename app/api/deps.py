# app/api/deps.py

from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core import security
from app.schemas.token import TokenData
from app.models.user import User
from app.services import user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(
            token, security.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenData(username=payload.get("sub"))
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = user_service.get_user_by_username(db, username=token_data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_active_manager_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Giriş yapmış, aktif ve rolü 'YONETICI' olan kullanıcıyı getirir.
    Koşullar sağlanmazsa hata fırlatır.
    """
    if not current_user.aktif:
        raise HTTPException(status_code=400, detail="Inactive user")
    if current_user.rol != "YONETICI":
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user