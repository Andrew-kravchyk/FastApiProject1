from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi import Cookie

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

from app.models.user import User

from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse
)

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.core.metrics import USERS_CREATED_TOTAL

from jose import jwt, JWTError

from app.core.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register")
async def register(
        user: UserCreate,
        db: AsyncSession = Depends(get_db)
):

    stmt = select(User).where(User.email == user.email)

    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)
    USERS_CREATED_TOTAL.inc()

    return new_user


@router.post("/login")
async def login(
        user_data: UserLogin,
        response: Response,
        db: AsyncSession = Depends(get_db)
):

    stmt = select(User).where(User.email == user_data.email)

    result = await db.execute(stmt)

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
            user_data.password,
            user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {
            "sub": str(user.id)
        }
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True
    )

    return {
        "message": "Login successful"
    }


async def get_current_user(
        access_token: str = Cookie(None),
        db: AsyncSession = Depends(get_db)
):

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    try:
        payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    stmt = select(User).where(User.id == int(user_id))

    result = await db.execute(stmt)

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


@router.get(
    "/me",
    response_model=UserResponse
)
async def get_me(
        current_user: User = Depends(get_current_user)
):
    return current_user


@router.get("/profile")
async def profile(
        current_user: User = Depends(get_current_user)
):
    return {
        "message": f"Hello {current_user.username}"
    }
