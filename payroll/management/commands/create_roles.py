# payroll/management/commands/create_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# mapping: group -> list of (app_label, model_name, perms_list)
ROLE_MAP = {
    "Admins": [
        # empty: we'll grant all payroll app perms below; superusers can be used instead
    ],
    "Teacher": [
        ("students", "student", ["view", "change"]),
        ("academics", "subject", ["view", "change"]),
        ("exams", "examresult", ["add", "change", "view"]),
        ("attendance", "attendancerecord", ["add", "change", "view"]),
        ("reports", "report", ["view"]),  # optional
    ],
    "PayrollManager": [
        ("payroll", "employee", ["add", "change", "view"]),
        ("payroll", "salarycomponent", ["add", "change", "view"]),
        ("payroll", "payrollperiod", ["add", "change", "view"]),
        ("payroll", "payslip", ["view", "change"]),
        ("payroll", "payment", ["add", "change", "view"]),
        ("payroll", "employeecomponent", ["add", "change", "view"]),  # if present
    ],
    "Parent": [
        ("students", "student", ["view"]),
        ("fees", "invoice", ["view"]),
        ("exams", "examresult", ["view"]),
        ("attendance", "attendancerecord", ["view"]),
    ],
}

class Command(BaseCommand):
    help = "Create default role groups and assign recommended permissions. Skips missing models."

    def handle(self, *args, **options):
        for group_name, perms in ROLE_MAP.items():
            group, created = Group.objects.get_or_create(name=group_name)
            self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Found'} group: {group_name}"))

            for app_label, model_name, perm_kinds in perms:
                for kind in perm_kinds:
                    codename = f"{kind}_{model_name}"
                    try:
                        ct = ContentType.objects.get(app_label=app_label, model=model_name)
                    except ContentType.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"ContentType not found: {app_label}.{model_name} — skipping {codename}"))
                        continue
                    try:
                        perm = Permission.objects.get(content_type=ct, codename=codename)
                        group.permissions.add(perm)
                        self.stdout.write(self.style.NOTICE(f"Added {codename} to {group_name}"))
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Permission not found: {codename} (app:{app_label} model:{model_name})"))

        # Optionally: give Admins all permissions (careful)
        admin_group, _ = Group.objects.get_or_create(name="Admins")
        all_perms = Permission.objects.all()
        admin_group.permissions.set(all_perms)
        self.stdout.write(self.style.SUCCESS("Assigned ALL permissions to Admins group"))

        self.stdout.write(self.style.SUCCESS("Roles creation completed."))
