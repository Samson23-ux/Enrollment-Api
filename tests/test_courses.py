import pytest
from uuid import UUID


from tests.fake_data import fake_student, fake_course, fake_admin


@pytest.mark.asyncio
async def test_get_active_courses(test_client, create_student, create_course):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": email, "password": password}
    )

    access_token: str = sign_in_res.json()["access_token"]

    res = test_client.get("/api/v1/courses/", headers={"Authorization": access_token})

    json_res = res.json()

    assert len(json_res["data"]) >= 1


@pytest.mark.asyncio
async def test_get_course_by_id(test_client, create_student, create_course):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": email, "password": password}
    )

    access_token: str = sign_in_res.json()["access_token"]
    course_id: UUID = create_course.json()["data"]

    res = test_client.get(
        f"/api/v1/courses/{course_id}/", headers={"Authorization": access_token}
    )

    json_res = res.json()

    assert json_res["data"]["code"] == fake_course.get("code")


@pytest.mark.asyncio
async def test_create_course(create_course):
    course = create_course.json()

    assert create_course.status_code == 201
    assert "id" in course["data"]


@pytest.mark.asyncio
async def test_unauthorized_courses(test_client, create_student):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": email, "password": password}
    )

    access_token: str = sign_in_res.json()["access_token"]

    res = test_client.post(
        "/api/v1/courses/", json=fake_course, headers={"Authorization": access_token}
    )

    assert res.status_code == 403


@pytest.mark.asyncio
async def test_update_course(test_client, create_course):
    email: str = fake_admin.get("email")
    password: str = fake_admin.get("email")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": email, "password": password}
    )

    access_token: str = sign_in_res.json()["access_token"]
    course_id: UUID = create_course.json()["data"]["id"]

    res = test_client.patch(
        f"/api/v1/courses/{course_id}/",
        json={"code": "newfakecoursecode"},
        headers={"Authorization": access_token},
    )

    json_res = res.json()

    assert res.status_code == 200
    assert json_res["data"]["code"] == "newfakecoursecode"


@pytest.mark.asyncio
async def test_deactivate_course(test_client, create_course):
    email: str = fake_admin.get("email")
    password: str = fake_admin.get("email")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": email, "password": password}
    )

    access_token: str = sign_in_res.json()["access_token"]
    course_id: UUID = create_course.json()["data"]["id"]

    res = test_client.patch(
        f"/api/v1/courses/{course_id}/deactivate/",
        headers={"Authorization": access_token},
    )

    json_res = res.json()

    assert res.status_code == 200
    assert json_res["data"]["is_active"] is False


@pytest.mark.asyncio
async def test_reactivate_course(test_client, create_course):
    email: str = fake_admin.get("email")
    password: str = fake_admin.get("email")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": email, "password": password}
    )

    access_token: str = sign_in_res.json()["access_token"]
    course_id: UUID = create_course.json()["data"]["id"]

    test_client.patch(
        f"/api/v1/courses/{course_id}/deactivate/",
        headers={"Authorization": access_token},
    )

    res = test_client.patch(
        f"/api/v1/courses/{course_id}/reactivate/",
        headers={"Authorization": access_token},
    )

    json_res = res.json()

    assert res.status_code == 200
    assert json_res["data"]["is_active"] is True


@pytest.mark.asyncio
async def test_delete_course(test_client, create_course):
    email: str = fake_admin.get("email")
    password: str = fake_admin.get("email")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": email, "password": password}
    )

    access_token: str = sign_in_res.json()["access_token"]
    course_id: UUID = create_course.json()["data"]["id"]

    res = test_client.request(
        "DELETE",
        f"/api/v1/courses/{course_id}/",
        headers={"Authorization": access_token},
    )

    assert res.status_code == 204
