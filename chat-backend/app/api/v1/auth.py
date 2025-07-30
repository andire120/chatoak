from fastapi import APIRouter, Depends, HTTPException, status
# OAuth2PasswordRequestForm은 폼 데이터 로그인용이므로, JSON 로그인용이라면 삭제해도 됩니다.
# from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.crud import users as crud_users # users.py에 create_user, get_user_by_username, authenticate_user 함수가 있다고 가정
from app.schemas.user import UserCreate, Token, UserInDB, UserLogin # 스키마 가져오기
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

# --- 사용자 회원가입 (register) 엔드포인트 ---
# 이 라우트는 이제 유일합니다.
@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate, # 프론트엔드에서 'username'과 'password'를 JSON으로 받음
    db: AsyncSession = Depends(get_db)
):
    # 1. 사용자 이름 중복 확인
    db_user = await crud_users.get_user_by_username(db, username=user_data.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 사용자 이름입니다."
        )

    # 2. 받은 평문 비밀번호를 해시
    hashed_password = get_password_hash(user_data.password)

    # 3. 데이터베이스에 저장할 사용자 생성
    # crud_users.create_user 함수가 username과 hashed_password를 직접 받도록 가정합니다.
    # 만약 crud_users.create_user가 UserCreate 스키마를 받고 내부에서 해시한다면, 이 부분은 달라집니다.
    # 하지만 일반적으로 CRUD 함수는 이미 해시된 비밀번호를 받는 것이 좋습니다.
    created_user = await crud_users.create_user(
        db=db,
        username=user_data.username,
        hashed_password=hashed_password
    )
    # create_user 함수가 UserInDB 객체를 반환한다고 가정합니다.

    return created_user

# --- 사용자 로그인 (login) 엔드포인트 ---
# 이 라우트도 이제 유일합니다.
@router.post("/login", response_model=Token)
async def login_for_access_token(
    user_data: UserLogin, # 프론트엔드에서 'username'과 'password'를 JSON으로 받음
    db: AsyncSession = Depends(get_db)
):
    # 1. 사용자 정보를 DB에서 가져옴
    user = await crud_users.get_user_by_username(db, username=user_data.username)

    # 2. 사용자 존재 여부 및 비밀번호 확인
    # verify_password 함수가 평문 비밀번호(user_data.password)와 DB에 저장된 해시된 비밀번호(user.password_hash)를 비교
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 잘못되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 액세스 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}