import pytest
from uuid import uuid4, UUID

from app.api.v1.schemas.users import UserRole
from tests.fake_data import fake_student, fake_admin


@pytest.mark.asyncio
async def test_get_all_students(test_client, create_admin, create_student):
    email: str = fake_admin.get("email")
    password: str = fake_admin.get("password")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": email, "password": password}
    )

    access_token: str = sign_in_res.json()["access_token"]

    res = test_client.get(
        "/api/v1/admin/students/", headers={"Authorization": access_token}
    )

    json_res = res.json()

    assert res.status_code == 200
    assert len(json_res["data"]) >= 1


@pytest.mark.asyncio
async def test_get_all_courses(test_client, create_course):
    email: str = fake_admin.get("email")
    password: str = fake_admin.get("password")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/", data={"username": email, "password": password}
    )

    access_token: str = sign_in_res.json()["access_token"]

    res = test_client.get(
        "/api/v1/admin/courses/", headers={"Authorization": access_token}
    )

    json_res = res.json()

    assert res.status_code == 200
    assert len(json_res["data"]) >= 1


@pytest.mark.asyncio
async def test_get_all_enrollments(test_client, create_student, create_course):
    admin_email: str = fake_admin.get("email")
    admin_password: str = fake_admin.get("password")

    student_email: str = fake_student.get("email")
    student_password: str = fake_student.get("password")

    admin_sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": admin_email, "password": admin_password},
    )

    student_sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": student_email, "password": student_password},
    )

    course_id: UUID = create_course.json()["data"]["id"]
    admin_access_token: str = admin_sign_in_res.json()["access_token"]
    student_access_token: str = student_sign_in_res.json()["access_token"]

    test_client.post(
        f"/api/v1/courses/{course_id}/enrollments/",
        headers={"Authorization": student_access_token},
    )

    res = test_client.get(
        "/api/v1/admin/enrollments/", headers={"Authorization": admin_access_token}
    )

    json_res = res.json()

    assert res.status_code == 200
    assert len(json_res["data"]) >= 1


@pytest.mark.asyncio
async def test_get_course_enrollments(test_client, create_student, create_course):
    admin_email: str = fake_admin.get("email")
    admin_password: str = fake_admin.get("password")

    student_email: str = fake_student.get("email")
    student_password: str = fake_student.get("password")

    admin_sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": admin_email, "password": admin_password},
    )

    student_sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": student_email, "password": student_password},
    )

    course_id: UUID = create_course.json()["data"]["id"]
    admin_access_token: str = admin_sign_in_res.json()["access_token"]
    student_access_token: str = student_sign_in_res.json()["access_token"]

    test_client.post(
        f"/api/v1/courses/{course_id}/enrollments/",
        headers={"Authorization": student_access_token},
    )

    res = test_client.get(
        f"/api/v1/admin/courses/{course_id}/enrollments/",
        headers={"Authorization": admin_access_token},
    )

    json_res = res.json()

    assert res.status_code == 200
    assert len(json_res["data"]) >= 1


@pytest.mark.asyncio
async def test_assign_admin_role(test_client, create_student, create_admin):
    email: str = fake_admin.get("email")
    password: str = fake_admin.get("password")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": email, "password": password},
    )

    student_id: UUID = create_student.json()["data"]["id"]
    access_token: str = sign_in_res.json()["access_token"]

    res = test_client.patch(
        f"/api/v1/admin/users/{student_id}/assign-admin-role/",
        headers={"Authorization": access_token},
    )

    json_res = res.json()

    assert res.status_code == 200
    assert json_res["data"]["role"] == UserRole.ADMIN


@pytest.mark.asyncio
async def test_assign_instructor_role(test_client, create_student, create_admin):
    email: str = fake_admin.get("email")
    password: str = fake_admin.get("password")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": email, "password": password},
    )

    student_id: UUID = create_student.json()["data"]["id"]
    access_token: str = sign_in_res.json()["access_token"]

    res = test_client.patch(
        f"/api/v1/admin/users/{student_id}/assign-instructor-role/",
        headers={"Authorization": access_token},
    )

    json_res = res.json()

    assert res.status_code == 200
    assert json_res["data"]["role"] == UserRole.ADMIN


@pytest.mark.asyncio
async def test_unauthenticated_admin(test_client):
    res = test_client.get("/api/v1/admin/students/")

    assert res.status_code == 401


@pytest.mark.asyncio
async def test_unauthorized_admin(test_client, create_student):
    email: str = fake_student.get("email")
    password: str = fake_student.get("password")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": email, "password": password},
    )

    access_token: str = sign_in_res.json()["access_token"]

    res = test_client.get(
        "/api/v1/admin/students/", headers={"Authorization": access_token}
    )

    assert res.status_code == 401


@pytest.mark.asyncio
async def test_user_not_found_admin(test_client, create_admin):
    email: str = fake_admin.get("email")
    password: str = fake_admin.get("password")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": email, "password": password},
    )

    access_token: str = sign_in_res.json()["access_token"]

    res = test_client.patch(
        f"/api/v1/admin/users/{uuid4()}]/assign-admin-role/",
        headers={"Authorization": access_token},
    )

    assert res.status_code == 404
