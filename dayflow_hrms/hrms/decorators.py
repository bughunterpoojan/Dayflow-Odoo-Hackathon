"""
Custom decorators for role-based access control.
"""

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from functools import wraps


def admin_required(view_func):
    """
    Decorator to restrict view to Admin/HR users only.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin():
            return redirect('employee_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def employee_required(view_func):
    """
    Decorator to restrict view to Employee users only.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_employee():
            return redirect('admin_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
