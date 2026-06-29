from rest_framework import viewsets
from .models import Subject, Enrollment
from .serializers import SubjectSerializer, EnrollmentSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SubjectForm, EnrollmentForm
from django.contrib import messages
from schools.models import School
from rest_framework import generics
from .serializers import SubjectSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

def manage_subjects(request, school_id):
    school = get_object_or_404(School, id=school_id)
    subjects = Subject.objects.filter(school=school).order_by("name")

    #instantiating the form for the template
    form = SubjectForm()

    # Inline save request (from JS)
    if request.method == "POST":
        # Inline save
        if "save_subject" in request.POST:
            subject_id = request.POST.get("subject_id")
            name = request.POST.get("name", "").strip()
            code = request.POST.get("code", "").strip()
            subject = get_object_or_404(Subject, id=subject_id, school=school)
            if name:
                subject.name = name
                subject.code = code
                subject.save()
                messages.success(request, f"Subject '{name}' updated successfully.")
            else:
                messages.error(request, "Subject name cannot be empty.")
            return redirect(request.path)

        # Inline delete
        if "delete_subject" in request.POST:
            subject_id = request.POST.get("subject_id")
            subject = get_object_or_404(Subject, id=subject_id, school=school)
            subject.delete()
            messages.success(request, f"Subject '{subject.name}' deleted successfully.")
            return redirect(request.path)

        # Standard add form submission
        form = SubjectForm(request.POST)
        if form.is_valid():
            new_subject = form.save(commit=False)
            new_subject.school = school
            new_subject.save()
            messages.success(request, f"Subject '{new_subject.name}' added successfully.")
            return redirect(request.path)
        else:
            messages.error(request, "Error adding subject. Please check the form.")

    return render(request, "academics/manage_subjects.html", {
        "school": school,
        "subjects": subjects,
        "form": form, 
    })

def subjects_list(request):
    subjects = Subject.objects.all()
    return render(request, 'academics/subjects_list.html', {'subjects': subjects})




def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect('subjects_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'academics/subjects_form.html', {'form': form})


# ---------------------- ENROLLMENTS ----------------------

def enrollments_list(request):
    enrollments = Enrollment.objects.all()
    return render(request, 'academics/enrollments_list.html', {'enrollments': enrollments})


def enrollment_create(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('enrollments_list')
    else:
        form = EnrollmentForm()
    return render(request, 'academics/enrollments_form.html', {'form': form})


def enrollment_edit(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    if request.method == 'POST':
        form = EnrollmentForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            return redirect('enrollments_list')
    else:
        form = EnrollmentForm(instance=enrollment)
    return render(request, 'academics/enrollments_form.html', {'form': form})


class SubjectListAPIView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]
    