import pytest
from uuid import UUID


from tests.fake_data import fake_student, fake_course, fake_admin


@pytest.mark.asyncio
async def test_get_all_courses(async_client, create_student, create_course):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = await async_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": email, "password": password},
        headers={"curr_env": "test"},
    )

    access_token: str = sign_in_res.json()["access_token"]

    res = await async_client.get(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {access_token}", "curr_env": "test"},
    )

    json_res = res.json()

    assert len(json_res["data"]) >= 1


@pytest.mark.asyncio
async def test_get_course_by_id(async_client, create_student, create_course):
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

    res = await async_client.get(
        f"/api/v1/courses/{course_id}/",
        headers={"Authorization": f"Bearer {access_token}", "curr_env": "test"},
    )

    json_res = res.json()

    assert json_res["data"]["code"] == fake_course.get("code")


@pytest.mark.asyncio
async def test_create_course(create_course):
    course, _ = create_course

    course_json = course.json()

    assert course.status_code == 201
    assert "id" in course_json["data"]


@pytest.mark.asyncio
async def test_unauthorized_courses(async_client, create_student):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = await async_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": email, "password": password},
        headers={"curr_env": "test"},
    )

    access_token: str = sign_in_res.json()["access_token"]

    res = await async_client.post(
        "/api/v1/courses/",
        json=fake_course,
        headers={"Authorization": f"Bearer {access_token}", "curr_env": "test"},
    )

    assert res.status_code == 403


@pytest.mark.asyncio
async def test_update_course(async_client, create_course):
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

    res = await async_client.patch(
        f"/api/v1/courses/{course_id}/",
        json={"code": "newfakecoursecode"},
        headers={"Authorization": f"Bearer {access_token}", "curr_env": "test"},
    )

    json_res = res.json()

    assert res.status_code == 200
    assert json_res["data"]["code"] == "newfakecoursecode"


@pytest.mark.asyncio
async def test_deactivate_course(async_client, create_course):
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

    res = await async_client.request(
        "DELETE",
        f"/api/v1/courses/{course_id}/deactivate/",
        headers={"Authorization": f"Bearer {access_token}", "curr_env": "test"},
    )

    assert res.status_code == 204


@pytest.mark.asyncio
async def test_reactivate_course(async_client, create_course):
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

    await async_client.patch(
        f"/api/v1/courses/{course_id}/deactivate/",
        headers={"Authorization": f"Bearer {access_token}", "curr_env": "test"},
    )

    res = await async_client.patch(
        f"/api/v1/courses/{course_id}/reactivate/",
        headers={"Authorization": f"Bearer {access_token}", "curr_env": "test"},
    )

    json_res = res.json()

    assert res.status_code == 200
    assert json_res["data"]["is_active"] is True


@pytest.mark.asyncio
async def test_delete_course(async_client, create_course):
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

    res = await async_client.request(
        "DELETE",
        f"/api/v1/courses/{course_id}/",
        headers={"Authorization": f"Bearer {access_token}", "curr_env": "test"},
    )

    assert res.status_code == 204
