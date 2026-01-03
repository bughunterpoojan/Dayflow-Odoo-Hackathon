"""
Django forms for the HRMS application.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, EmployeeProfile, LeaveRequest, Attendance, Payroll


class SignUpForm(UserCreationForm):
    """
    User registration form with employee_id, email, role selection.
    """
    employee_id = forms.CharField(max_length=20, required=True, 
                                  widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Employee ID'}))
    email = forms.EmailField(required=True, 
                            widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}))
    first_name = forms.CharField(max_length=30, required=True,
                                 widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True,
                                widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}))
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True,
                            widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = CustomUser
        fields = ['employee_id', 'email', 'first_name', 'last_name', 'username', 'password1', 'password2', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Confirm Password'})


class LoginForm(forms.Form):
    """
    User login form with email and password.
    """
    email = forms.EmailField(required=True,
                            widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}))
    password = forms.CharField(required=True,
                              widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))


class EmployeeProfileForm(forms.ModelForm):
    """
    Employee profile edit form.
    Employees can edit limited fields (address, phone, profile picture).
    Admins can edit all fields.
    """
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))
    
    class Meta:
        model = EmployeeProfile
        fields = ['department', 'position', 'employment_type', 'date_joined']
        widgets = {
            'department': forms.TextInput(attrs={'class': 'form-input'}),
            'position': forms.TextInput(attrs={'class': 'form-input'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'date_joined': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


class LeaveRequestForm(forms.ModelForm):
    """
    Leave application form for employees.
    """
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'remarks']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Reason for leave'}),
        }


class AttendanceForm(forms.ModelForm):
    """
    Attendance form for admin to manually add/edit attendance.
    """
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'check_in_time', 'check_out_time', 'status', 'remarks']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'check_in_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }


class SalaryStructureForm(forms.Form):
    """
    Form for admin to update employee salary structure.
    """
    base_salary = forms.DecimalField(max_digits=10, decimal_places=2, required=True,
                                    widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Base Salary'}))
    allowances = forms.DecimalField(max_digits=10, decimal_places=2, required=False, initial=0,
                                   widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Allowances'}))
    deductions = forms.DecimalField(max_digits=10, decimal_places=2, required=False, initial=0,
                                   widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Deductions'}))
