import pytest
from uuid import UUID

from tests.fake_data import fake_student


@pytest.mark.asyncio
async def test_get_user_profile(test_client, create_student):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": email, "password": password}
    )

    access_token: str = sign_in_res.json()["access_token"]

    res = test_client.get("/api/v1/users/me/", headers={"Authorization": access_token})

    json_res = res.json()

    assert res.status_code == 200
    assert email == json_res["data"]["email"]


@pytest.mark.asyncio
async def test_get_user_courses(test_client, create_student, create_course):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": email, "password": password}
    )

    access_token: str = sign_in_res.json()["access_token"]
    course_id: UUID = create_course.json()["data"]["id"]

    test_client.post(
        f"/api/v1/courses/{course_id}/enrollments/",
        headers={"Authorization": access_token},
    )

    res = test_client.get(
        "/api/v1/users/me/courses/", headers={"Authorization": access_token}
    )

    json_res = res.json()

    assert res.status_code == 200
    assert len(json_res["data"]) >= 1


@pytest.mark.asyncio
async def test_user_course_not_found(test_client, create_student, create_course):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": email, "password": password}
    )

    access_token: str = sign_in_res.json()["access_token"]

    res = test_client.get(
        "/api/v1/users/me/courses/", headers={"Authorization": access_token}
    )

    assert res.status_code == 404


@pytest.mark.asyncio
async def test_authenticated_users(test_client, create_student, create_course):
    res = test_client.get("/api/v1/users/me/courses/")

    assert res.status_code == 401


@pytest.mark.asyncio
async def test_update_user(test_client, create_student):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": email, "password": password}
    )

    access_token: str = sign_in_res.json()["access_token"]

    res = test_client.patch(
        "/api/v1/users/me/",
        json={"nationality": "new_fake_nationality"},
        headers={"Authorization": access_token},
    )

    json_res = res.json()

    assert res.status_code == 200
    assert json_res["data"]["nationality"] == "new_fake_nationality"
