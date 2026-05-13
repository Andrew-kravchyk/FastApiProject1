from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import User


async def get_all_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()


async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str):
    user = User(email=email)

    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user


async def update_user(
        db: AsyncSession,
        user_id: int,
        email: str
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        return None

    user.email = email

    await db.commit()
    await db.refresh(user)

    return user


async def delete_user(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        return None

    await db.delete(user)
    await db.commit()

    return user