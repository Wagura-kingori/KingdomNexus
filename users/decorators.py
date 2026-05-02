from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def super_admin_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                messages.error(request, "You are not allowed to access this page.")
                return redirect("home")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
