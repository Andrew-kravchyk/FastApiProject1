import pytest

from app.core.security import create_access_token


pytestmark = pytest.mark.asyncio


async def test_register_creates_user(client, user_payload):
    response = await client.post("/auth/register", json=user_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] > 0
    assert data["username"] == user_payload["username"]
    assert data["email"] == user_payload["email"]
    assert data["hashed_password"] != user_payload["password"]


async def test_register_duplicate_email_returns_400(client, user_payload):
    await client.post("/auth/register", json=user_payload)

    response = await client.post("/auth/register", json=user_payload)

    assert response.status_code == 400
    assert response.json() == {"detail": "User already exists"}


async def test_login_sets_access_token_cookie(client, user_payload):
    await client.post("/auth/register", json=user_payload)

    response = await client.post(
        "/auth/login",
        json={
            "email": user_payload["email"],
            "password": user_payload["password"],
        },
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Login successful"}
    assert "access_token" in response.cookies


async def test_login_with_wrong_email_returns_401(client, user_payload):
    response = await client.post(
        "/auth/login",
        json={
            "email": user_payload["email"],
            "password": user_payload["password"],
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


async def test_login_with_wrong_password_returns_401(client, user_payload):
    await client.post("/auth/register", json=user_payload)

    response = await client.post(
        "/auth/login",
        json={
            "email": user_payload["email"],
            "password": "bad-password",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


async def test_me_returns_current_user(client, user_payload):
    register_response = await client.post("/auth/register", json=user_payload)
    login_response = await client.post(
        "/auth/login",
        json={
            "email": user_payload["email"],
            "password": user_payload["password"],
        },
    )

    response = await client.get(
        "/auth/me",
        cookies={"access_token": login_response.cookies["access_token"]},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": register_response.json()["id"],
        "username": user_payload["username"],
        "email": user_payload["email"],
    }


async def test_profile_returns_greeting(client, user_payload):
    await client.post("/auth/register", json=user_payload)
    login_response = await client.post(
        "/auth/login",
        json={
            "email": user_payload["email"],
            "password": user_payload["password"],
        },
    )

    response = await client.get(
        "/auth/profile",
        cookies={"access_token": login_response.cookies["access_token"]},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Hello {user_payload['username']}"}


async def test_me_without_cookie_returns_401(client):
    response = await client.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


async def test_me_with_invalid_token_returns_401(client):
    response = await client.get(
        "/auth/me",
        cookies={"access_token": "invalid-token"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


async def test_me_with_missing_user_returns_401(client):
    token = create_access_token({"sub": "999"})

    response = await client.get(
        "/auth/me",
        cookies={"access_token": token},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "User not found"}
