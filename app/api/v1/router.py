from fastapi import APIRouter, Depends, HTTPException
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

router = APIRouter()


@router.get("/users", response_model=list[UserRead])
async def users_list(db: AsyncSession = Depends(get_db)):
    return await get_all_users(db)


@router.get("/users/{user_id}", response_model=UserRead)
async def user_detail(
        user_id: int,
        db: AsyncSession = Depends(get_db)
):
    user = await get_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@router.post("/users", response_model=UserRead)
async def user_create(
        user: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    return await create_user(db, user.email)


@router.put("/users/{user_id}", response_model=UserRead)
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
            status_code=404,
            detail="User not found"
        )

    return updated_user


@router.delete("/users/{user_id}")
async def user_delete(
        user_id: int,
        db: AsyncSession = Depends(get_db)
):
    deleted_user = await delete_user(db, user_id)

    if deleted_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": f"User {user_id} deleted"
    }

