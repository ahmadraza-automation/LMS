# LMS — Learning Management System

A **Django-based Learning Management System** where instructors can create courses & lessons, and students can enroll and learn.

**Author:** [Ahmad Raza](https://github.com/ahmadraza-automation) — Python Automation Engineer & Django Expert

---

## Features

- Course management (Create, Read, Update)
- Lessons with YouTube embed support
- Student enrollment system
- Instructor & Student roles (via Django auth)
- Clean dashboard & course detail pages
- WhiteNoise for static files (deployment ready)

---

## Tech Stack

- **Python 3**
- **Django 6.x**
- SQLite (default) — easy to switch to PostgreSQL
- WhiteNoise
- Bootstrap-style templates

---

## Project Structure

```
LMS/
├── core/                 # Main Django project (settings, urls, wsgi)
├── courses/              # Main app (models, views, forms, urls)
├── templates/            # HTML templates
├── manage.py
├── requirements.txt
└── README.md
```

> Note: The repository also contains some experimental / older folders (`lms_core`, `my_ai_website`, `app`). The **active** project uses `core` + `courses`.

---

## Installation & Run (Local)

```bash
# Clone
git clone https://github.com/ahmadraza-automation/LMS.git
cd LMS

# Virtual environment
python -m venv env
# Windows
env\Scripts\activate
# Mac/Linux
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run
python manage.py runserver
```

Open: http://127.0.0.1:8000/

---

## Models Overview

| Model       | Description                                      |
|-------------|--------------------------------------------------|
| **Course**  | Title, description, instructor, price             |
| **Lesson**  | Belongs to course, title, video_url, content, order |
| **Enrollment** | Student enrolled in a course (unique constraint) |

---

## Deployment Notes

- `DEBUG = True` and `ALLOWED_HOSTS = ['*']` are currently set for easy testing.
- For production:
  - Set `DEBUG = False`
  - Use a strong `SECRET_KEY` from environment variables
  - Prefer PostgreSQL instead of SQLite
  - Configure proper `ALLOWED_HOSTS`

Ready for platforms like **Render**, **Railway**, or **PythonAnywhere**.

---

## Author

**Ahmad Raza**  
Python Automation Engineer | Django Expert | Playwright & Selenium Specialist  

- GitHub: [ahmadraza-automation](https://github.com/ahmadraza-automation)
- Portfolio: [Live Portfolio](https://ahmadraza-automation.github.io/Ahmad-Raza-Automation-Portfolio/)
- Email: arjafri347@gmail.com
