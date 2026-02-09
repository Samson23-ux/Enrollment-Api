fake_student: dict = {
    "name": "fake user",
    "email": "fakeuser@example.com",
    "nationality": "fakenationality",
    "password": "fakepassword"
}


fake_instructor: dict = {
    "name": "fake instructor",
    "email": "fakeinstructor@example.com",
    "nationality": "fakenationality",
    "password": "fakepassword"
}


fake_admin: dict = {
    "name": "fake admin",
    "email": "admin@example.com",
    "nationality": "fakenationality",
    "password": "fakepassword"
}


fake_course: dict = {
    "title": "fake_title",
    "description": "a fake course for tests",
    "code": "fakecode",
    "instructor": fake_instructor.get("name"),
    "capacity": 20,
    "duration": 2
}