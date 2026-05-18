import pytest


pytestmark = pytest.mark.asyncio


async def test_users_list_returns_empty_list(client):
    response = await client.get("/users")

    assert response.status_code == 200
    assert response.json() == []


async def test_user_create_creates_user(client, user_payload):
    response = await client.post("/users", json=user_payload)

    assert response.status_code == 201
    assert response.json()["id"] > 0
    assert response.json()["email"] == user_payload["email"]


async def test_user_detail_returns_user(client, user_payload):
    create_response = await client.post("/users", json=user_payload)
    user_id = create_response.json()["id"]

    response = await client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": user_id,
        "email": user_payload["email"],
    }


async def test_user_detail_returns_404_for_missing_user(client):
    response = await client.get("/users/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


async def test_user_update_changes_user(client, user_payload):
    create_response = await client.post("/users", json=user_payload)
    user_id = create_response.json()["id"]

    response = await client.put(
        f"/users/{user_id}",
        json={
            "username": "updated",
            "email": "updated@example.com",
            "password": "updated-password",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": user_id,
        "email": "updated@example.com",
    }


async def test_user_update_returns_404_for_missing_user(client, user_payload):
    response = await client.put("/users/999", json=user_payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


async def test_user_delete_removes_user(client, user_payload):
    create_response = await client.post("/users", json=user_payload)
    user_id = create_response.json()["id"]

    delete_response = await client.delete(f"/users/{user_id}")
    get_response = await client.get(f"/users/{user_id}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": f"User {user_id} deleted"}
    assert get_response.status_code == 404


async def test_user_delete_returns_404_for_missing_user(client):
    response = await client.delete("/users/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
