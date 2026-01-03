"""
View functions for the HRMS application.
Includes authentication, employee dashboard, admin dashboard, and all feature views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta, date

from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .models import CustomUser, EmployeeProfile, Attendance, LeaveRequest, Payroll
from .forms import AddUserForm, LoginForm, EmployeeProfileForm, LeaveRequestForm, AttendanceForm, SalaryStructureForm
from .decorators import admin_required, employee_required


# ==================== Authentication Views ====================

@login_required
@admin_required
def add_user_view(request):
    """Admin add user view with auto-generated ID"""
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data['role']
            
            # Generate Employee ID
            prefix = 'HR' if role == 'ADMIN' else 'E'
            
            # Find last ID with this prefix
            last_user = CustomUser.objects.filter(employee_id__startswith=prefix).order_by('-employee_id').first()
            
            if last_user:
                try:
                    last_number = int(last_user.employee_id[len(prefix):])
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1
            else:
                new_number = 1
                
            user.employee_id = f"{prefix}{str(new_number).zfill(5)}"
            user.email_verified = True # Admin created users are verified
            user.save()
            
            # Create EmployeeProfile for the user
            EmployeeProfile.objects.create(
                user=user,
                department='Not Assigned',
                position='Not Assigned'
            )
            
            messages.success(request, f'User created! Please complete their profile details.')
            return redirect('edit_employee', employee_id=user.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddUserForm()
    
    return render(request, 'admin/add_user.html', {'form': form})


def login_view(request):
    """User login view - Phase 1: Validate credentials and send OTP"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                user = CustomUser.objects.get(email=email)
                authenticated_user = authenticate(request, username=user.username, password=password)
                
                if authenticated_user is not None:
                    # Generate OTP and store user ID in session
                    otp = authenticated_user.generate_otp()
                    request.session['otp_user_id'] = authenticated_user.id
                    
                    # Send OTP via email
                    subject = 'Your Dayflow HRMS Login OTP'
                    message = f'Your OTP for logging into Dayflow HRMS is: {otp}\n\nThis code will expire in 10 minutes.'
                    
                    try:
                        send_mail(subject, message, None, [authenticated_user.email])
                        messages.info(request, 'An OTP has been sent to your email. Please enter it below.')
                        return redirect('otp_verify')
                    except Exception as e:
                        messages.error(request, f'Error sending OTP email: {str(e)}')
                else:
                    messages.error(request, 'Invalid email or password.')
            except CustomUser.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


def otp_verify_view(request):
    """OTP verification view - Phase 2: Validate OTP and log in"""
    user_id = request.session.get('otp_user_id')
    
    if not user_id:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('login')
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found. Please log in again.')
        return redirect('login')
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '')
        
        if user.otp and user.otp_expiry and timezone.now() <= user.otp_expiry:
            if user.otp == entered_otp:
                # Clear OTP and session
                user.otp = None
                user.otp_expiry = None
                user.save()
                del request.session['otp_user_id']
                
                # Log the user in
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
        else:
            messages.error(request, 'OTP has expired. Please log in again.')
            del request.session['otp_user_id']
            return redirect('login')
    
    return render(request, 'auth/otp_verify.html', {'user_email': user.email})



@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Main dashboard - redirects based on user role"""
    if request.user.is_admin():
        return redirect('admin_dashboard')
    else:
        return redirect('employee_dashboard')


# ==================== Employee Views ====================

@login_required
@employee_required
def employee_dashboard_view(request):
    """Employee dashboard with quick-access cards"""
    employee = request.user
    
    # Get recent attendance
    recent_attendance = Attendance.objects.filter(employee=employee).order_by('-date')[:7]
    
    # Get pending leave requests
    pending_leaves = LeaveRequest.objects.filter(employee=employee, status='PENDING').count()
    
    # Get latest payroll
    latest_payroll = Payroll.objects.filter(employee=employee).first()
    
    # Check if already checked in today
    today = timezone.now().date()
    today_attendance = Attendance.objects.filter(employee=employee, date=today).first()
    
    context = {
        'employee': employee,
        'recent_attendance': recent_attendance,
        'pending_leaves': pending_leaves,
        'latest_payroll': latest_payroll,
        'today_attendance': today_attendance,
    }
    
    return render(request, 'employee/dashboard.html', context)


@login_required
def view_profile_view(request):
    """View employee profile"""
    profile = get_object_or_404(EmployeeProfile, user=request.user)
    
    context = {
        'profile': profile,
        'user': request.user,
    }
    
    return render(request, 'employee/profile_view.html', context)


@login_required
def edit_profile_view(request):
    """Edit employee profile (limited fields for employees)"""
    profile = get_object_or_404(EmployeeProfile, user=request.user)
    
    if request.method == 'POST':
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            request.user.profile_picture = request.FILES['profile_picture']
            request.user.save()
        
        # Handle phone update
        if 'phone' in request.POST:
            request.user.phone = request.POST.get('phone')
            request.user.save()
        
        # Handle address update (stored in personal_details JSON)
        if 'address' in request.POST:
            profile.personal_details['address'] = request.POST.get('address')
            profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('view_profile')
    
    context = {
        'profile': profile,
        'user': request.user,
    }
    
    return render(request, 'employee/profile_edit.html', context)


# ==================== Attendance Views ====================

@login_required
def employee_attendance_view(request):
    """Employee's own attendance view"""
    employee = request.user
    
    # Get date range from query params or default to current month
    today = timezone.now().date()
    start_date = request.GET.get('start_date', today.replace(day=1))
    end_date = request.GET.get('end_date', today)
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get attendance records
    attendance_records = Attendance.objects.filter(
        employee=employee,
        date__range=[start_date, end_date]
    ).order_by('-date')
    
    context = {
        'attendance_records': attendance_records,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'employee/attendance.html', context)


@login_required
def check_in_view(request):
    """Employee check-in endpoint"""
    if request.method == 'POST':
        employee = request.user
        today = timezone.now().date()
        current_time = timezone.now().time()
        
        # Check if already checked in today
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={'check_in_time': current_time, 'status': 'PRESENT'}
        )
        
        if not created and attendance.check_in_time:
            messages.warning(request, 'You have already checked in today.')
        else:
            attendance.check_in_time = current_time
            attendance.status = 'PRESENT'
            attendance.save()
            messages.success(request, f'Checked in successfully at {current_time.strftime("%I:%M %p")}')
    
    return redirect('employee_dashboard')


@login_required
def check_out_view(request):
    """Employee check-out endpoint"""
    if request.method == 'POST':
        employee = request.user
        today = timezone.now().date()
        current_time = timezone.now().time()
        
        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
            
            if not attendance.check_in_time:
                messages.error(request, 'Please check in first.')
            elif attendance.check_out_time:
                messages.warning(request, 'You have already checked out today.')
            else:
                attendance.check_out_time = current_time
                
                # Update status based on hours worked
                hours = attendance.calculate_hours_worked()
                if hours >= 8:
                    attendance.status = 'PRESENT'
                elif hours >= 4:
                    attendance.status = 'HALF_DAY'
                else:
                    attendance.status = 'ABSENT'
                
                attendance.save()
                messages.success(request, f'Checked out successfully at {current_time.strftime("%I:%M %p")}. Hours worked: {hours}')
        except Attendance.DoesNotExist:
            messages.error(request, 'Please check in first.')
    
    return redirect('employee_dashboard')


# ==================== Leave Views ====================

@login_required
def apply_leave_view(request):
    """Employee leave application"""
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = request.user
            leave_request.status = 'PENDING'
            leave_request.save()
            
            messages.success(request, 'Leave request submitted successfully!')
            return redirect('leave_history')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LeaveRequestForm()
    
    return render(request, 'employee/apply_leave.html', {'form': form})


@login_required
def leave_history_view(request):
    """Employee's leave history"""
    leave_requests = LeaveRequest.objects.filter(employee=request.user).order_by('-created_at')
    
    context = {
        'leave_requests': leave_requests,
    }
    
    return render(request, 'employee/leave_history.html', context)


# ==================== Payroll Views ====================

@login_required
def employee_payroll_view(request):
    """Employee payroll view (read-only)"""
    payroll_records = Payroll.objects.filter(employee=request.user).order_by('-year', '-month')
    
    context = {
        'payroll_records': payroll_records,
    }
    
    return render(request, 'employee/payroll.html', context)


# ==================== Admin Views ====================

@login_required
@admin_required
def admin_dashboard_view(request):
    """Admin/HR dashboard"""
    # Get statistics
    total_employees = CustomUser.objects.filter(role='EMPLOYEE').count()
    pending_leaves = LeaveRequest.objects.filter(status='PENDING').count()
    
    # Today's attendance
    today = timezone.now().date()
    todays_attendance = Attendance.objects.filter(date=today)
    present_count = todays_attendance.filter(status='PRESENT').count()
    
    # Recent leave requests
    recent_leaves = LeaveRequest.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_employees': total_employees,
        'pending_leaves': pending_leaves,
        'present_count': present_count,
        'recent_leaves': recent_leaves,
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
@admin_required
def employee_list_view(request):
    """Admin view all employees and admins"""
    employees = CustomUser.objects.all().select_related('profile').order_by('-date_joined')
    
    context = {
        'employees': employees,
    }
    
    return render(request, 'admin/employee_list.html', context)


@login_required
@admin_required
def view_employee_detail_view(request, employee_id):
    """Admin view specific employee details"""
    employee = get_object_or_404(CustomUser, id=employee_id)
    profile = get_object_or_404(EmployeeProfile, user=employee)
    
    # Get employee statistics
    total_attendance = Attendance.objects.filter(employee=employee).count()
    present_days = Attendance.objects.filter(employee=employee, status='PRESENT').count()
    leave_requests = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')[:5]
    
    context = {
        'employee': employee,
        'profile': profile,
        'total_attendance': total_attendance,
        'present_days': present_days,
        'leave_requests': leave_requests,
    }
    
    return render(request, 'admin/employee_detail.html', context)


@login_required
@admin_required
def edit_employee_view(request, employee_id):
    """Admin edit employee details (full access)"""
    employee = get_object_or_404(CustomUser, id=employee_id)
    profile = get_object_or_404(EmployeeProfile, user=employee)
    
    if request.method == 'POST':
        # Update user fields
        employee.first_name = request.POST.get('first_name', employee.first_name)
        employee.last_name = request.POST.get('last_name', employee.last_name)
        employee.email = request.POST.get('email', employee.email)
        employee.phone = request.POST.get('phone', employee.phone)
        employee.save()
        
        # Update profile fields
        profile.department = request.POST.get('department', profile.department)
        profile.position = request.POST.get('position', profile.position)
        profile.employment_type = request.POST.get('employment_type', profile.employment_type)
        
        if request.POST.get('date_joined'):
            profile.date_joined = request.POST.get('date_joined')
        
        profile.save()
        
        messages.success(request, 'Employee details updated successfully!')
        return redirect('view_employee_detail', employee_id=employee_id)
    
    context = {
        'employee': employee,
        'profile': profile,
    }
    
    return render(request, 'admin/employee_edit.html', context)


@login_required
@admin_required
def admin_attendance_view(request):
    """Admin view all employees' attendance"""
    # Get date range
    today = timezone.now().date()
    start_date = request.GET.get('start_date', today.replace(day=1))
    end_date = request.GET.get('end_date', today)
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get attendance records
    attendance_records = Attendance.objects.filter(
        date__range=[start_date, end_date]
    ).select_related('employee').order_by('-date', 'employee__employee_id')
    
    context = {
        'attendance_records': attendance_records,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'admin/attendance_records.html', context)


@login_required
@admin_required
def admin_leave_list_view(request):
    """Admin view all leave requests"""
    status_filter = request.GET.get('status', 'all')
    
    if status_filter == 'all':
        leave_requests = LeaveRequest.objects.all()
    else:
        leave_requests = LeaveRequest.objects.filter(status=status_filter.upper())
    
    leave_requests = leave_requests.select_related('employee').order_by('-created_at')
    
    context = {
        'leave_requests': leave_requests,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin/leave_approvals.html', context)


@login_required
@admin_required
def approve_leave_view(request, leave_id):
    """Admin approve leave request"""
    if request.method == 'POST':
        leave_request = get_object_or_404(LeaveRequest, id=leave_id)
        leave_request.status = 'APPROVED'
        leave_request.approved_by = request.user
        leave_request.admin_comments = request.POST.get('comments', '')
        leave_request.save()
        
        # Mark attendance as LEAVE for the date range
        current_date = leave_request.start_date
        while current_date <= leave_request.end_date:
            Attendance.objects.update_or_create(
                employee=leave_request.employee,
                date=current_date,
                defaults={'status': 'LEAVE'}
            )
            current_date += timedelta(days=1)
        
        messages.success(request, 'Leave request approved successfully!')
    
    return redirect('admin_leave_list')


@login_required
@admin_required
def reject_leave_view(request, leave_id):
    """Admin reject leave request"""
    if request.method == 'POST':
        leave_request = get_object_or_404(LeaveRequest, id=leave_id)
        leave_request.status = 'REJECTED'
        leave_request.approved_by = request.user
        leave_request.admin_comments = request.POST.get('comments', '')
        leave_request.save()
        
        messages.success(request, 'Leave request rejected.')
    
    return redirect('admin_leave_list')


@login_required
@admin_required
def admin_payroll_list_view(request):
    """Admin view payroll for all employees"""
    # Get month/year filter
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    month = int(request.GET.get('month', current_month))
    year = int(request.GET.get('year', current_year))
    
    payroll_records = Payroll.objects.filter(month=month, year=year).select_related('employee')
    
    context = {
        'payroll_records': payroll_records,
        'month': month,
        'year': year,
    }
    
    return render(request, 'admin/payroll_management.html', context)


@login_required
@admin_required
def admin_update_salary_view(request, employee_id):
    """Admin update employee salary structure"""
    employee = get_object_or_404(CustomUser, id=employee_id)
    profile = get_object_or_404(EmployeeProfile, user=employee)
    
    if request.method == 'POST':
        form = SalaryStructureForm(request.POST)
        if form.is_valid():
            # Update salary structure in profile
            profile.salary_structure = {
                'base_salary': float(form.cleaned_data['base_salary']),
                'allowances': float(form.cleaned_data.get('allowances', 0)),
                'deductions': float(form.cleaned_data.get('deductions', 0)),
            }
            profile.save()
            
            messages.success(request, 'Salary structure updated successfully!')
            return redirect('view_employee_detail', employee_id=employee_id)
    else:
        # Populate form with existing data
        initial_data = {
            'base_salary': profile.salary_structure.get('base_salary', 0),
            'allowances': profile.salary_structure.get('allowances', 0),
            'deductions': profile.salary_structure.get('deductions', 0),
        }
        form = SalaryStructureForm(initial=initial_data)
    
    context = {
        'form': form,
        'employee': employee,
    }
    
    return render(request, 'admin/salary_structure_edit.html', context)


@login_required
@admin_required
def admin_generate_payroll_view(request):
    """Admin generate payroll for current month"""
    if request.method == 'POST':
        month = int(request.POST.get('month', timezone.now().month))
        year = int(request.POST.get('year', timezone.now().year))
        
        # Generate payroll for all employees
        employees = CustomUser.objects.filter(role='EMPLOYEE').select_related('profile')
        generated_count = 0
        
        for employee in employees:
            salary_structure = employee.profile.salary_structure
            
            # Skip if no salary structure defined
            if not salary_structure or 'base_salary' not in salary_structure:
                continue
            
            # Create or update payroll
            payroll, created = Payroll.objects.update_or_create(
                employee=employee,
                month=month,
                year=year,
                defaults={
                    'base_salary': salary_structure.get('base_salary', 0),
                    'allowances': salary_structure.get('allowances', 0),
                    'deductions': salary_structure.get('deductions', 0),
                }
            )
            generated_count += 1
        
        messages.success(request, f'Payroll generated for {generated_count} employees!')
        return redirect('admin_payroll_list')
    
    return redirect('admin_payroll_list')
