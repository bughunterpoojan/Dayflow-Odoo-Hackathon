"""
Database models for the HRMS application.
Includes CustomUser, EmployeeProfile, Attendance, LeaveRequest, and Payroll models.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import datetime, timedelta
import json


class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds employee_id, role, email verification, and profile picture.
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Admin / HR Officer'),
        ('EMPLOYEE', 'Employee'),
    ]
    
    employee_id = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='EMPLOYEE')
    email_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    # Override email to make it required and unique
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return f"{self.employee_id} - {self.get_full_name()}"
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'ADMIN'
    
    def is_employee(self):
        """Check if user has employee role"""
        return self.role == 'EMPLOYEE'
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class EmployeeProfile(models.Model):
    """
    Employee profile with personal details, job details, and salary structure.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Details (stored as JSON for flexibility)
    personal_details = models.JSONField(default=dict, blank=True, help_text="Address, emergency contacts, etc.")
    
    # Job Details
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    date_joined = models.DateField(default=timezone.now)
    employment_type = models.CharField(max_length=50, default='Full-time', 
                                      choices=[('Full-time', 'Full-time'), ('Part-time', 'Part-time'), ('Contract', 'Contract')])
    
    # Salary Structure (stored as JSON)
    salary_structure = models.JSONField(default=dict, blank=True, 
                                       help_text="Base salary, allowances, deductions")
    
    # Documents
    documents = models.FileField(upload_to='documents/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"
    
    def get_tenure(self):
        """Calculate years of service"""
        delta = timezone.now().date() - self.date_joined
        years = delta.days // 365
        months = (delta.days % 365) // 30
        return f"{years} years, {months} months"
    
    def get_base_salary(self):
        """Get base salary from salary structure"""
        return self.salary_structure.get('base_salary', 0)
    
    class Meta:
        verbose_name = 'Employee Profile'
        verbose_name_plural = 'Employee Profiles'


class Attendance(models.Model):
    """
    Attendance tracking with check-in/check-out and status.
    """
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('HALF_DAY', 'Half-day'),
        ('LEAVE', 'Leave'),
    ]
    
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    check_in_time = models.TimeField(blank=True, null=True)
    check_out_time = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ABSENT')
    remarks = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'date']
        ordering = ['-date']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date} - {self.status}"
    
    def calculate_hours_worked(self):
        """Calculate total hours worked"""
        if self.check_in_time and self.check_out_time:
            check_in = datetime.combine(self.date, self.check_in_time)
            check_out = datetime.combine(self.date, self.check_out_time)
            delta = check_out - check_in
            hours = delta.total_seconds() / 3600
            return round(hours, 2)
        return 0
    
    def is_full_day(self):
        """Check if attendance is full day (>= 8 hours)"""
        hours = self.calculate_hours_worked()
        return hours >= 8


class LeaveRequest(models.Model):
    """
    Leave request with approval workflow.
    """
    LEAVE_TYPE_CHOICES = [
        ('PAID', 'Paid Leave'),
        ('SICK', 'Sick Leave'),
        ('UNPAID', 'Unpaid Leave'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    remarks = models.TextField(blank=True, null=True, help_text="Reason for leave")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    admin_comments = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True, 
                                   related_name='approved_leaves')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.leave_type} - {self.status}"
    
    def get_duration(self):
        """Calculate leave duration in days"""
        delta = self.end_date - self.start_date
        return delta.days + 1


class Payroll(models.Model):
    """
    Payroll records for employees.
    """
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payrolls')
    month = models.IntegerField(validators=[MinValueValidator(1)])
    year = models.IntegerField(validators=[MinValueValidator(2020)])
    
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    generated_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'month', 'year']
        ordering = ['-year', '-month']
        verbose_name = 'Payroll'
        verbose_name_plural = 'Payroll Records'
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.month}/{self.year}"
    
    def calculate_net_salary(self):
        """Calculate net salary"""
        self.net_salary = self.base_salary + self.allowances - self.deductions
        return self.net_salary
    
    def save(self, *args, **kwargs):
        """Override save to auto-calculate net salary"""
        self.calculate_net_salary()
        super().save(*args, **kwargs)
