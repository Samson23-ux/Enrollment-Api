import pytest

from tests.fake_data import fake_student


@pytest.mark.asyncio
async def test_sign_up(create_student):
    json_res = create_student.json()["data"]
    assert create_student.status_code == 201
    assert "id" in json_res


@pytest.mark.asyncio
async def test_duplicate_user(test_client, create_student):
    res = test_client.post("/api/v1/auth/sign-up/", json=fake_student)
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_sign_in(test_client, create_student):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": email, "password": password}
    )
    json_res = res.json()

    assert res.status_code == 201
    assert "access_token" in json_res


@pytest.mark.asyncio
async def test_invalid_creds(test_client, create_student):
    username: str = "invalid_username"
    password: str = "invalid_password"

    res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": username, "password": password}
    )

    assert res.status_code == 400


@pytest.mark.asyncio
async def test_get_access_token(test_client, create_student):
    res = test_client.get(
        "/api/v1/auth/refresh/",
    )
    json_res = res.json()

    assert res.status_code == 200
    assert "access_token" in json_res


@pytest.mark.asyncio
async def test_update_password(test_client, create_student):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": email, "password": password}
    )

    access_token: str = sign_in_res.json()["access_token"]

    res = test_client.patch(
        "/api/v1/auth/update-password/",
        data={"curr_password": password, "new_password": "new_password"},
        headers={"Authorization": access_token},
    )

    assert res.status_code == 200


@pytest.mark.asyncio
async def test_reset_password(test_client, create_student):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    res = test_client.patch(
        "/api/v1/auth/reset-password/", data={"email": email, "new_password": password}
    )

    assert res.status_code == 200


@pytest.mark.asyncio
async def test_deactivate_account(test_client, create_student):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": email, "password": password}
    )

    access_token: str = sign_in_res.json()["access_token"]

    res = test_client.request(
        "DELETE",
        "/api/v1/auth/deactivate/",
        data={"email": email, "password": password},
        headers={"Authorization": access_token},
    )

    assert res.status_code == 204


@pytest.mark.asyncio
async def test_unauthenticated_auth(test_client, create_student):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    res = test_client.request(
        "DELETE",
        "/api/v1/auth/deactivate/",
        data={"email": email, "password": password},
    )

    assert res.status_code == 401


@pytest.mark.asyncio
async def test_delete_account(test_client, create_student):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    res = test_client.request(
        "DELETE", "/auth/delete-account/", data={"email": email, "password": password}
    )

    assert res.status_code == 204
