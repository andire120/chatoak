# app/core/security.py

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import get_settings

settings = get_settings()

# 토큰 인증을 위한 OAuth2PasswordBearer 설정
# "token"은 토큰을 가져올 엔드포인트의 이름입니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 비밀번호 해시를 위한 CryptContext 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    일반 텍스트 비밀번호와 해시된 비밀번호가 일치하는지 확인합니다.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    비밀번호를 해시하여 반환합니다.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT Access Token을 생성합니다.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    JWT Access Token을 디코딩하고 페이로드를 반환합니다.
    JWT 오류 발생 시 None을 반환합니다.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    FastAPI 의존성 주입을 통해 현재 인증된 사용자를 가져옵니다.
    HTTP 요청 헤더에서 JWT 토큰을 추출하고, 토큰을 검증하여 페이로드를 반환합니다.
    토큰이 유효하지 않으면 401 Unauthorized 에러를 발생시킵니다.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    # 페이로드에서 사용자 정보를 추출하고 필요에 따라 추가 검증을 수행할 수 있습니다.
    user_data = payload.get("sub")
    if user_data is None:
        raise credentials_exception
    return payload
