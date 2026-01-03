"""
URL configuration for the HRMS application.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('login/otp/', views.otp_verify_view, name='otp_verify'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Admin User Management
    path('admin/add-user/', views.add_user_view, name='add_user'),
    
    # Employee Dashboard
    path('employee/dashboard/', views.employee_dashboard_view, name='employee_dashboard'),
    path('employee/profile/', views.view_profile_view, name='view_profile'),
    path('employee/profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # Employee Attendance
    path('employee/attendance/', views.employee_attendance_view, name='employee_attendance'),
    path('employee/check-in/', views.check_in_view, name='check_in'),
    path('employee/check-out/', views.check_out_view, name='check_out'),
    
    # Employee Leave
    path('employee/leave/apply/', views.apply_leave_view, name='apply_leave'),
    path('employee/leave/history/', views.leave_history_view, name='leave_history'),
    
    # Employee Payroll
    path('employee/payroll/', views.employee_payroll_view, name='employee_payroll'),
    
    # Admin Dashboard
    path('admin/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin/employees/', views.employee_list_view, name='employee_list'),
    path('admin/employee/<int:employee_id>/', views.view_employee_detail_view, name='view_employee_detail'),
    path('admin/employee/<int:employee_id>/edit/', views.edit_employee_view, name='edit_employee'),
    
    # Admin Attendance
    path('admin/attendance/', views.admin_attendance_view, name='admin_attendance'),
    
    # Admin Leave
    path('admin/leave/', views.admin_leave_list_view, name='admin_leave_list'),
    path('admin/leave/<int:leave_id>/approve/', views.approve_leave_view, name='approve_leave'),
    path('admin/leave/<int:leave_id>/reject/', views.reject_leave_view, name='reject_leave'),
    
    # Admin Payroll
    path('admin/payroll/', views.admin_payroll_list_view, name='admin_payroll_list'),
    path('admin/employee/<int:employee_id>/salary/', views.admin_update_salary_view, name='admin_update_salary'),
    path('admin/payroll/generate/', views.admin_generate_payroll_view, name='admin_generate_payroll'),
]
