# Dayflow HRMS - Human Resource Management System

![Dayflow HRMS](https://img.shields.io/badge/Django-4.2-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)

**Every workday, perfectly aligned.** ✨

A comprehensive Human Resource Management System built with Django, HTML, and CSS. This system digitizes core HR operations including employee onboarding, profile management, attendance tracking, leave management, payroll visibility, and approval workflows.

## 📋 Features

### Authentication & Authorization
- ✅ **User Registration** - Sign up with employee ID, email, and role selection
- ✅ **Secure Login** - Email and password authentication
- ✅ **Role-Based Access Control** - Separate interfaces for Employees and Admin/HR

### Employee Features
- 👤 **Profile Management** - View and edit personal information
# Dayflow HRMS — Human Resource Management System

![Django](https://img.shields.io/badge/Django-4.2-green.svg) ![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)

Every workday, perfectly aligned. ✨

Lightweight, practical HRMS built on Django with features for employee profiles, attendance, leave management, and payroll visibility.

## Quick overview
- Authentication with OTP support
- Employee and Admin/HR role separation
- Attendance (check-in/check-out), leave application & approvals
- Payroll visibility and basic salary structure management

## Prerequisites
- Python 3.8+
- pip

## Setup (local development)
1. Clone or open this project folder.
2. Create & activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Apply database migrations:

```bash
python manage.py migrate
```

5. (Optional) Create a superuser:

```bash
python manage.py createsuperuser
```

6. Run the development server:

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Quick test data (optional)
Use the Django shell to create a simple admin and employee for quick testing:

```bash
python manage.py shell
```
use your emails for verification as we use gmail otp
Then paste:

```python
from hrms.models import CustomUser, EmployeeProfile

admin = CustomUser.objects.create_user(
    username='admin1', employee_id='HR00001', email='admin@dayflow.com', password='admin123', role='ADMIN', first_name='Admin'
)
EmployeeProfile.objects.create(user=admin, department='HR', position='Manager')

employee = CustomUser.objects.create_user(
    username='employee1', employee_id='E00001', email='employee@dayflow.com', password='employee123', role='EMPLOYEE', first_name='Jane'
)
EmployeeProfile.objects.create(user=employee, department='Engineering', position='Developer')
```

## Email testing (dev)
To see sent HTML emails in console, add this to your `settings.py` (development only):

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Trigger an action that sends email (login to receive OTP, assign a task, create a project) and check the server console for the styled HTML message.

## Project structure (important files)

```
dayflow_hrms/
├─ dayflow_hrms/        # Project settings & URLs
├─ hrms/                # Main app: models, views, forms, templates
├─ templates/           # Django templates (base, auth, admin, employee)
├─ static/              # Static assets (css, images, js)
├─ media/               # Uploaded files
├─ manage.py
└─ requirements.txt
```

## Common commands
- Run server: `python manage.py runserver`
- Make migrations: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`
