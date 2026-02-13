import pytest
from uuid import UUID

from tests.fake_data import fake_student, fake_admin


@pytest.mark.asyncio
async def test_create_enrollments(async_client, create_student, create_course):
    course, _ = create_course
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = await async_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": email, "password": password},
        headers={"curr_env": "test"},
    )

    access_token: str = sign_in_res.json()["access_token"]
    course_id: UUID = course.json()["data"]["id"]

    res = await async_client.post(
        f"/api/v1/courses/{course_id}/enrollments/",
        headers={"Authorization": f"Bearer {access_token}", "curr_env": "test"},
    )

    assert res.status_code == 201


@pytest.mark.asyncio
async def test_delete_enrollments(async_client, create_student, create_course):
    course, _ = create_course
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

    res = await async_client.request(
        "DELETE",
        f"/api/v1/courses/{course_id}/enrollments/",
        headers={"Authorization": f"Bearer {access_token}", "curr_env": "test"},
    )

    assert res.status_code == 204


@pytest.mark.asyncio
async def test_unauthenticated_enrollments(async_client, create_student, create_course):
    course, _ = create_course

    course_id: UUID = course.json()["data"]["id"]
    res = await async_client.post(
        f"/api/v1/courses/{course_id}/enrollments/",
        headers={"curr_env": "test"},
    )

    assert res.status_code == 401


@pytest.mark.asyncio
async def test_unauthorized_enrollments(async_client, create_admin, create_course):
    course, _ = create_course
    email: str = fake_admin.get("email")
    password: str = fake_admin.get("password")

    sign_in_res = await async_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": email, "password": password},
        headers={"curr_env": "test"},
    )

    access_token: str = sign_in_res.json()["access_token"]
    course_id: UUID = course.json()["data"]["id"]

    res = await async_client.post(
        f"/api/v1/courses/{course_id}/enrollments/",
        headers={"Authorization": f"Bearer {access_token}", "curr_env": "test"},
    )

    assert res.status_code == 403
