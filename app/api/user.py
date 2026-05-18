from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.user import UserCreate, UserRead

from app.crud.user import (
    get_all_users,
    get_user,
    create_user,
    update_user,
    delete_user
)
from app.core.metrics import USERS_CREATED_TOTAL, USERS_DELETED_TOTAL

router = APIRouter()


# Отримати всіх користувачів
@router.get(
    "/users",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK
)
async def users_list(
        db: AsyncSession = Depends(get_db)
):
    return await get_all_users(db)


# Отримати одного користувача
@router.get(
    "/users/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK
)
async def user_detail(
        user_id: int,
        db: AsyncSession = Depends(get_db)
):
    user = await get_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# Створити користувача
@router.post(
    "/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED
)
async def user_create(
        user: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    created_user = await create_user(
        db,
        user.email
    )
    USERS_CREATED_TOTAL.inc()
    return created_user


# Оновити користувача
@router.put(
    "/users/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK
)
async def user_update(
        user_id: int,
        user: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    updated_user = await update_user(
        db,
        user_id,
        user.email
    )

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return updated_user


# Видалити користувача
@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK
)
async def user_delete(
        user_id: int,
        db: AsyncSession = Depends(get_db)
):
    deleted_user = await delete_user(
        db,
        user_id
    )

    if deleted_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    USERS_DELETED_TOTAL.inc()

    return {
        "message": f"User {user_id} deleted"
    }
