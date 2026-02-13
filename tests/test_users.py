import pytest
from uuid import UUID

from tests.fake_data import fake_student


@pytest.mark.asyncio
async def test_get_user_profile(async_client, create_student):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = await async_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": email, "password": password},
        headers={"curr_env": "test"},
    )

    access_token: str = sign_in_res.json()["access_token"]

    res = await async_client.get(
        "/api/v1/users/me/",
        headers={"Authorization": f"Bearer {access_token}", "curr_env": "test"},
    )

    json_res = res.json()

    assert res.status_code == 200
    assert email == json_res["data"]["email"]


@pytest.mark.asyncio
async def test_get_user_courses(async_client, create_student, create_course):
    course, tt = create_course
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = await async_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": email, "password": password},
        headers={"curr_env": "test"},
    )

    access_token: str = sign_in_res.json()["access_token"]
    course_id: UUID = course.json()["data"]["id"]

    await async_client.post(
        f"/api/v1/courses/{course_id}/enrollments/",
        headers={"Authorization": f"Bearer {access_token}", "curr_env": "test"},
    )

    res = await async_client.get(
        "/api/v1/users/me/courses/",
        headers={"Authorization": f"Bearer {access_token}", "curr_env": "test"},
    )

    json_res = res.json()

    assert res.status_code == 200
    assert len(json_res["data"]) >= 1


@pytest.mark.asyncio
async def test_user_course_not_found(async_client, create_student, create_course):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = await async_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": email, "password": password},
        headers={"curr_env": "test"},
    )

    access_token: str = sign_in_res.json()["access_token"]

    res = await async_client.get(
        "/api/v1/users/me/courses/",
        headers={"Authorization": f"Bearer {access_token}", "curr_env": "test"},
    )

    assert res.status_code == 404


@pytest.mark.asyncio
async def test_unauthenticated_users(async_client, create_student, create_course):
    res = await async_client.get(
        "/api/v1/users/me/courses/",
        headers={"curr_env": "test"},
    )

    assert res.status_code == 401


@pytest.mark.asyncio
async def test_update_user(async_client, create_student):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = await async_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": email, "password": password},
        headers={"curr_env": "test"},
    )

    access_token: str = sign_in_res.json()["access_token"]

    res = await async_client.patch(
        "/api/v1/users/me/",
        json={"nationality": "new_fake_nationality"},
        headers={"Authorization": f"Bearer {access_token}", "curr_env": "test"},
    )

    json_res = res.json()

    assert res.status_code == 200
    assert json_res["data"]["nationality"] == "new_fake_nationality"
