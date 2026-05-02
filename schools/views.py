from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.decorators import super_admin_required
from .models import School
from .forms import SchoolForm
from django.shortcuts import render, get_object_or_404




@login_required
def school_dashboard(request, pk):
    school = get_object_or_404(School, pk=pk)

    #  usr must belong to this school (unless superadmin)
    if request.user.role != "superadmin" and request.user.school != school:
        return render(request, "403.html", status=403)

    context = {
        "school": school,
    }
    return render(request, "schools/school_dashboard.html", context)


@login_required
@super_admin_required
def setup_dashboard(request):
    schools = School.objects.all()
    return render(request, "schools/setup_dashboard.html", {
        "schools": schools
    })


@login_required
@super_admin_required
def add_school(request):
    form = SchoolForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("schools:setup_dashboard")

    return render(request, "schools/add_school.html", {
        "form": form
    })
