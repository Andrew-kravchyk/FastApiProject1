import pytest

from app.crud.user import (
    create_user,
    delete_user,
    get_all_users,
    get_user,
    update_user,
)


pytestmark = pytest.mark.asyncio


async def test_create_user(db_session):
    user = await create_user(db_session, "created@example.com")

    assert user.id > 0
    assert user.email == "created@example.com"


async def test_get_all_users(db_session):
    await create_user(db_session, "first@example.com")
    await create_user(db_session, "second@example.com")

    users = await get_all_users(db_session)

    assert [user.email for user in users] == [
        "first@example.com",
        "second@example.com",
    ]


async def test_get_user_returns_user(db_session):
    created_user = await create_user(db_session, "found@example.com")

    user = await get_user(db_session, created_user.id)

    assert user is not None
    assert user.id == created_user.id
    assert user.email == "found@example.com"


async def test_get_user_returns_none_for_missing_user(db_session):
    user = await get_user(db_session, 999)

    assert user is None


async def test_update_user_changes_email(db_session):
    created_user = await create_user(db_session, "old@example.com")

    updated_user = await update_user(
        db_session,
        created_user.id,
        "new@example.com",
    )

    assert updated_user is not None
    assert updated_user.id == created_user.id
    assert updated_user.email == "new@example.com"


async def test_update_user_returns_none_for_missing_user(db_session):
    updated_user = await update_user(
        db_session,
        999,
        "new@example.com",
    )

    assert updated_user is None


async def test_delete_user_removes_user(db_session):
    created_user = await create_user(db_session, "delete@example.com")

    deleted_user = await delete_user(db_session, created_user.id)
    user_after_delete = await get_user(db_session, created_user.id)

    assert deleted_user is not None
    assert deleted_user.id == created_user.id
    assert user_after_delete is None


async def test_delete_user_returns_none_for_missing_user(db_session):
    deleted_user = await delete_user(db_session, 999)

    assert deleted_user is None
