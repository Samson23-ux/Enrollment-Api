# Project Title 🎓
Enrollment API

## Description 📝

An enrollment API connecting interested students to their desired courses. Students can view and enroll in active courses, and instructors can view a list of enrolled courses and students, providing a smooth experience for both parties.

## Technology Stack 🛠️

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2C3E50?style=for-the-badge&logo=pydantic&logoColor=white)
![Postgres](https://img.shields.io/badge/Postgres-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)
![Sentry](https://img.shields.io/badge/Sentry-362D59?style=for-the-badge&logo=sentry&logoColor=white)

## Features ✨

- **RBAC** (students, instructors, admin)
- **Students**:
  - Create account and manage profile
  - View a list of courses and enroll in active courses
  - Manage enrolled courses
  - Unenroll from a course
- **Instructors**:
  - Manage courses
  - View a list of enrolled students
- **Admin**:
  - Manage course lifecycle and activity
  - View and manage list of students and instructors
  - View and manage list of courses and enrollments
  - Change roles

## Technical Highlights ⚙️

- **JWT** for authentication
- **Argon2** password hashing:
  - Memory hard
  - Good performance against ASIC and GPU attacks
  - Pepper and salt feature for better security and uniqueness in hashing value
  - Good configuration options
- **Sentry** for logging and monitoring
- **Rate limiting** with SlowAPI
- **Background processing** of tasks with Celery

## Ways to Run Application 🚀

### Prerequisites 📋
- Install Python 3.14. [Installation link](https://www.python.org/downloads/)
- Install and set up RabbitMQ on your machine. [Installation link](https://www.rabbitmq.com/docs/download)
- Install and set up PgAdmin. [Installation link](https://www.pgadmin.org/download/)

### Steps 🛠️

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd "Capstone-Project"
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Set the environment variables in the `env-demo.txt` file ([link to file](./env-demo.txt))

5. Create API database using PgAdmin.

6. Run Python script to initialize the database with roles and set admin details:
   ```bash
   python -m app.scripts.seed_data
   ```
7. Start Celery worker:
   ```bash
   celery -A app.tasks.celery_app worker -l info -P gevent
   ```
8. Start Celery beat:
   ```bash
   celery -A app.tasks.celery_app beat -l info
   ```
9. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```
10. Test API endpoints via docs:
    Open your browser and navigate to [http://localhost:8000/docs](http://localhost:8000/docs).

2. Test endpoints via live URL 🌐:
   **Note**: Some services are hosted on a free tier and may not be available after a few days.
   - Live URL: `<Insert live URL>`

## Testing 🧪

1. Run tests:
   ```bash
   pytest
   ```
2. Run tests with coverage:
   ```bash
   pytest --cov=.
   ```
3. Run a particular test module:
   ```bash
   pytest tests/<preferred_test_module.py>
   ```
4. Run a particular test function:
   ```bash
   pytest tests/<preferred_test_module.py>::<preferred_test_function>
   ```
