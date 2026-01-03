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
- 📅 **Attendance Tracking** - Check-in/Check-out functionality with daily and weekly views
- 🏖️ **Leave Management** - Apply for leave (Paid, Sick, Unpaid) and track status
- 💰 **Payroll Access** - View salary details (read-only)

### Admin/HR Features
- 👥 **Employee Management** - View, add, and edit employee details
- 📊 **Attendance Monitoring** - View attendance for all employees with filtering
- ✅ **Leave Approvals** - Review and approve/reject leave requests
- 💵 **Payroll Management** - Update salary structures and generate payroll
- 📈 **Dashboard Analytics** - Quick stats and overview

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

First, install pip if you don't have it:
```bash
sudo apt update
sudo apt install python3-pip -y
```

Then install the required packages:
```bash
cd /home/poojan/coding/gcet*odoo/dayflow_hrms
pip3 install -r requirements.txt
```

### Step 2: Database Setup

Create the database tables:
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### Step 3: Create an Admin User

Create a superuser for the Django admin panel:
```bash
python3 manage.py createsuperuser
```

### Step 4: Create Sample Data (Optional)

You can use the Django shell to create sample employees:
```bash
python3 manage.py shell
```

Then run:
```python
from hrms.models import CustomUser, EmployeeProfile

# Create an admin user
admin = CustomUser.objects.create_user(
    username='admin1',
    employee_id='EMP001',
    email='admin@dayflow.com',
    password='admin123',
    role='ADMIN',
    first_name='John',
    last_name='Admin',
    email_verified=True
)

# Create admin profile
EmployeeProfile.objects.create(
    user=admin,
    department='Administration',
    position='HR Manager',
    salary_structure={'base_salary': 80000, 'allowances': 10000, 'deductions': 5000}
)

# Create an employee user
employee = CustomUser.objects.create_user(
    username='employee1',
    employee_id='EMP002',
    email='employee@dayflow.com',
    password='employee123',
    role='EMPLOYEE',
    first_name='Jane',
    last_name='Doe',
    email_verified=True
)

# Create employee profile
EmployeeProfile.objects.create(
    user=employee,
    department='Engineering',
    position='Software Developer',
    salary_structure={'base_salary': 60000, 'allowances': 8000, 'deductions': 3000}
)

exit()
```

### Step 5: Run the Development Server

```bash
python3 manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

## 🎨 Design Features

- **Modern UI** - Clean, professional design with vibrant gradients
- **Glassmorphism Effects** - Beautiful card designs with backdrop blur
- **Dark Mode Support** - Toggle between light and dark themes
- **Smooth Animations** - Micro-animations for better user experience
- **Responsive Design** - Works on all screen sizes
- **Premium Typography** - Using Inter font from Google Fonts

## 📱 Usage

### For Employees

1. **Sign Up** - Register with your employee ID and email
2. **Login** - Access your dashboard
3. **Check In/Out** - Mark your attendance daily
4. **Apply for Leave** - Submit leave requests
5. **View Profile** - Check your job details and salary
6. **View Attendance** - Track your attendance history
7. **View Payroll** - See your salary details

### For Admin/HR

1. **Login** - Access the admin dashboard
2. **Manage Employees** - Add, edit, view employee details
3. **Track Attendance** - Monitor attendance for all employees
4. **Approve Leaves** - Review and approve/reject leave requests
5. **Manage Payroll** - Update salary structures and generate payroll
6. **View Analytics** - Quick overview of HR metrics

## 📂 Project Structure

```
dayflow_hrms/
├── dayflow_hrms/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── hrms/                  # Main application
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   ├── forms.py          # Django forms
│   ├── urls.py           # URL routing
│   ├── decorators.py     # Access control
│   └── admin.py          # Admin interface
├── templates/            # HTML templates
│   ├── base.html
│   ├── auth/            # Login, signup
│   ├── employee/        # Employee dashboard & features
│   └── admin/           # Admin dashboard & features
├── static/              # Static files
│   └── css/
│       └── styles.css   # Modern CSS styles
├── media/               # User uploads
├── manage.py
└── requirements.txt
```

## 🔐 Default Test Credentials

If you created sample data in Step 4:

**Admin/HR User:**
- Email: `admin@dayflow.com`
- Password: `admin123`

**Employee User:**
- Email: `employee@dayflow.com`
- Password: `employee123`

## 🛠️ Technology Stack

- **Backend**: Django 4.2
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (development)
- **Styling**: Custom CSS with modern design patterns

## 📋 Requirements Covered

✅ Authentication & Authorization (Sign Up/Sign In)  
✅ Role-based access (Employee vs Admin/HR)  
✅ Employee Dashboard with quick-access cards  
✅ Admin Dashboard with statistics  
✅ Employee Profile Management  
✅ Attendance tracking (Check-in/Check-out)  
✅ Daily and weekly attendance views  
✅ Leave management (Apply, Approve/Reject)  
✅ Leave types (Paid, Sick, Unpaid)  
✅ Payroll/Salary Management  
✅ Admin payroll controls  

## 🎯 Future Enhancements

- 📧 Email & notification alerts
- 📊 Analytics & reports dashboard
- 📄 PDF salary slips and attendance reports
- 📱 Mobile app integration
- 🔔 Real-time notifications

## 👨‍💻 Development

To contribute or modify:

1. Make changes to the code
2. Run migrations if models changed:
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```
3. Test your changes
4. Restart the development server

## 📝 License

This project is created for educational purposes.

## 🤝 Support

For issues or questions, please contact your system administrator.

---

**Dayflow HRMS** - Making HR management effortless! 🌊
