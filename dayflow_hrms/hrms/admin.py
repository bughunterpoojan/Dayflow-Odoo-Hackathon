"""
Django admin configuration for HRMS models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, EmployeeProfile, Attendance, LeaveRequest, Payroll


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser"""
    list_display = ['employee_id', 'username', 'email', 'role', 'email_verified', 'is_active']
    list_filter = ['role', 'email_verified', 'is_active', 'is_staff']
    search_fields = ['employee_id', 'username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Employee Information', {'fields': ('employee_id', 'role', 'phone', 'profile_picture', 'email_verified')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Employee Information', {'fields': ('employee_id', 'email', 'role')}),
    )


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    """Admin interface for EmployeeProfile"""
    list_display = ['user', 'department', 'position', 'employment_type', 'date_joined']
    list_filter = ['department', 'employment_type', 'date_joined']
    search_fields = ['user__employee_id', 'user__first_name', 'user__last_name', 'department', 'position']
    date_hierarchy = 'date_joined'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin interface for Attendance"""
    list_display = ['employee', 'date', 'check_in_time', 'check_out_time', 'status']
    list_filter = ['status', 'date']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']
    date_hierarchy = 'date'
    ordering = ['-date']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    """Admin interface for LeaveRequest"""
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status', 'leave_type', 'start_date']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    """Admin interface for Payroll"""
    list_display = ['employee', 'month', 'year', 'base_salary', 'net_salary', 'generated_date']
    list_filter = ['year', 'month']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']
    ordering = ['-year', '-month']
