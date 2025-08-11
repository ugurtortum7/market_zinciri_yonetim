from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db.session import get_db
from app.core import security
from app.schemas.token import TokenData
from app.services import user_service
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    JWT token'ı çözer, kullanıcıyı veritabanından alır ve döndürür.
    Eğer token geçersizse veya kullanıcı bulunamazsa hata fırlatır.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, security.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = user_service.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_manager_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Mevcut kullanıcının rolünün 'YONETICI' olup olmadığını kontrol eder.
    Değilse, yetkisiz erişim hatası fırlatır.
    """
    if current_user.rol != "YONETICI":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlemi yapmaya yetkiniz yok.",
        )
    return current_user

def get_current_cashier_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Mevcut kullanıcının rolünün 'KASIYER' olup olmadığını ve bir süpermarkete
    atanmış olup olmadığını kontrol eder.
    """
    if current_user.rol != "KASIYER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlemi sadece kasiyerler yapabilir.",
        )
    if not current_user.lokasyon or current_user.lokasyon.tip != "SUPERMARKET":
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kasiyer geçerli bir süpermarkete atanmamış.",
        )
    return current_user