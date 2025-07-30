from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import User
# from app.schemas.user import UserCreate # UserCreate는 이제 create_user 함수의 직접적인 입력으로 사용되지 않습니다.
# from app.core.security import get_password_hash # 비밀번호 해싱은 auth.py에서 처리하므로 여기서 필요 없습니다.
from app.schemas.user import UserInDB # 반환 타입을 위해 필요할 수 있습니다.

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

# --- create_user 함수를 수정합니다. ---
# 이제 username과 이미 해시된 비밀번호를 직접 인자로 받습니다.
async def create_user(db: AsyncSession, username: str, hashed_password: str):
    # 비밀번호는 이미 auth.py에서 해시되어 넘어왔으므로, 여기서 다시 해시할 필요 없습니다.
    db_user = User(username=username, password_hash=hashed_password) # <-- hashed_password를 바로 사용합니다.
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user) # DB에서 생성된 ID 등을 가져오기 위해 refresh

    # UserInDB 스키마로 변환하여 반환 (FastAPI 라우트의 response_model과 일치시키기 위함)
    return UserInDB.model_validate(db_user) # Pydantic v2: from_orm 대신 model_validate 사용

# --- authenticate_user 함수 추가 (로그인 로직에서 필요) ---
# 이 함수는 단순히 사용자 객체를 가져오는 역할을 합니다. 비밀번호 검증은 auth.py에서 합니다.
async def authenticate_user(db: AsyncSession, username: str):
    user = await get_user_by_username(db, username)
    return user # user 객체를 반환하면 auth.py에서 verify_password로 비밀번호를 검증합니다.