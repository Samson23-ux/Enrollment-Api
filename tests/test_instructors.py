import pytest
from uuid import UUID

from tests.fake_data import fake_instructor, fake_admin, fake_student


@pytest.mark.asyncio
async def test_get_instructor_courses(async_client, create_course):
    course, instructor = create_course
    admin_email: str = fake_admin.get("email")
    admin_password: str = fake_admin.get("password")

    # sign in as admin
    admin_sign_in_res = await async_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": admin_email, "password": admin_password},
    )

    instructor_id: UUID = instructor.json()["data"]["id"]
    admin_access_token: str = admin_sign_in_res.json()["access_token"]

    # assign instructor role to instructor user
    await async_client.patch(
        f"/api/v1/admin/users/{instructor_id}/assign-instructor-role/",
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )

    instructor_email: str = fake_instructor.get("email")
    instructor_password: str = fake_instructor.get("password")

    # sign in as instructor
    instructor_sign_res = await async_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": instructor_email, "password": instructor_password},
    )

    instructor_access_token: str = instructor_sign_res.json()["access_token"]

    # get instructor courses
    res = await async_client.get(
        "/api/v1/users/instructor/me/courses/",
        headers={"Authorization": f"Bearer {instructor_access_token}"},
    )

    assert res.status_code == 200


# needs admin assign instructor role - complete later
@pytest.mark.asyncio
async def test_get_course_students(async_client, create_student, create_course):
    course, instructor = create_course
    admin_email: str = fake_admin.get("email")
    admin_password: str = fake_admin.get("password")

    # sign in as admin
    admin_sign_in_res = await async_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": admin_email, "password": admin_password},
    )

    student_email: str = fake_student.get("email")
    student_password: str = fake_student.get("password")

    # sign in as student
    student_sign_in_res = await async_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": student_email, "password": student_password},
    )

    instructor_id: UUID = instructor.json()["data"]["id"]
    course_id = course.json()["data"]["id"]
    admin_access_token: str = admin_sign_in_res.json()["access_token"]

    # assign instructor role to instructor user
    await async_client.patch(
        f"/api/v1/admin/users/{instructor_id}/assign-instructor-role/",
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )

    student_access_token: str = student_sign_in_res.json()["access_token"]

    # enroll student for the created course
    await async_client.post(
        f"/api/v1/courses/{course_id}/enrollments/",
        headers={"Authorization": f"Bearer {student_access_token}"},
    )

    instructor_email: str = fake_instructor.get("email")
    instructor_password: str = fake_instructor.get("password")

    # sign in as instructor
    instructor_sign_res = await async_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": instructor_email, "password": instructor_password},
    )

    instructor_access_token: str = instructor_sign_res.json()["access_token"]

    # get students for instructor's course
    res = await async_client.get(
        f"/api/v1/users/instructor/me/courses{course_id}/students/",
        headers={"Authorization": f"Bearer {instructor_access_token}"},
    )

    assert res.status_code == 200
