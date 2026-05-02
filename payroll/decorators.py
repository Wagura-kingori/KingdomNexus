from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin

# --- role checks using user.role field ---

def is_teacher(user):
    return user.is_authenticated and (
        user.is_superuser or user.role == "teacher"
    )

def is_payroll_manager(user):
    return user.is_authenticated and (
        user.is_superuser or user.role == "payroll"
    )

def is_parent(user):
    return user.is_authenticated and (
        user.is_superuser or user.role == "parent"
    )

def is_admin(user):
    return user.is_authenticated and (
        user.is_superuser or user.role in ("admin", "superadmin")
    )

# --- function view decorators ---
teacher_required      = user_passes_test(is_teacher,         login_url='/login/')
payroll_required      = user_passes_test(is_payroll_manager, login_url='/login/')
parent_required       = user_passes_test(is_parent,          login_url='/login/')
admin_required        = user_passes_test(is_admin,           login_url='/login/')

# --- class based view mixins ---
class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_teacher(self.request.user)

class PayrollRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_payroll_manager(self.request.user)

class ParentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_parent(self.request.user)

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_admin(self.request.user)