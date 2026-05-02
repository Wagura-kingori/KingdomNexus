from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, GalleryImage, Sermon, School,Donation, Event, Pastor, PrayerRequest, Student, Teacher, Achievement
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail, BadHeaderError

import traceback

# -----------------------------
# PRAYER REQUEST (AJAX handler)
# -----------------------------
@require_POST
def prayer_request(request):
    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip()
    subject = request.POST.get("subject", "").strip() or "Prayer Request from website"
    message = request.POST.get("message", "").strip()

    if not message:
        return JsonResponse({"error": "Message is required."}, status=400)

    # Save to DB
    pr = PrayerRequest.objects.create(
        name=name or "Anonymous",
        email=email or None,
        subject=subject,
        message=message
    )

    # Build email content
    site_name = getattr(settings, "SITE_NAME", "ACK Church")
    admin_email = getattr(settings, "CONTACT_EMAIL", settings.DEFAULT_FROM_EMAIL)
    mail_subject = f"[{site_name}] New Prayer Request: {pr.subject}"
    mail_body = f"""
A new prayer request was submitted on {pr.submitted_at:%Y-%m-%d %H:%M}.

Name: {pr.name}
Email: {pr.email or 'N/A'}
Subject: {pr.subject}

Message:
{pr.message}

-- end of message --
"""
    # Try to send notification email to church contact/admin
    try:
        send_mail(
            subject=mail_subject,
            message=mail_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=False,
        )
        pr.notified = True
        pr.save(update_fields=["notified"])
    except Exception:
        # don't break the flow for users, but log server side
        traceback.print_exc()

    return JsonResponse({"message": "Your prayer request has been received. We will pray for you."})




# -----------------------------
# EVENTS LIST + DETAIL
# -----------------------------
def events_list(request):
    events = Event.objects.filter(active=True).order_by("date")
    return render(request, "events.html", {"events": events})


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, "event_detail.html", {"event": event})


# -----------------------------
# PASTORAL TEAM PAGE
# -----------------------------
def pastoral_team(request):
    pastors = Pastor.objects.filter(active=True).order_by("name")
    return render(request, "pastoral_team.html", {"pastors": pastors})


# -----------------------------
# PROJECT DETAIL PAGE
# -----------------------------
def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, "project_detail.html", {"project": project})


def schools_list(request):
    schools = School.objects.all()
    return render(request, 'schools.html', {'schools': schools})


def home(request):
    projects = Project.objects.filter(active=True)[:4]
    gallery = GalleryImage.objects.all().order_by('-uploaded_at')[:6]
    sermons = Sermon.objects.all().order_by('-date')[:3]
    return render(request, 'home.html', {
    'projects': projects,
    'gallery': gallery,
    'sermons': sermons,
    })

def men_ministry(request):
    return render(request, 'ministries/men_ministry.html')

def women_ministry(request):
    return render(request, 'ministries/women_ministry.html')

def youth_ministry(request):
    return render(request, 'ministries/youth_ministry.html')

def children_ministry(request):
    return render(request, 'ministries/children_ministry.html')


def projects_list(request):
    projects = Project.objects.filter(active=True)
    return render(request, 'projects_list.html', {'projects': projects})


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'project_detail.html', {'project': project})


def gallery(request):
    images = GalleryImage.objects.all().order_by('-uploaded_at')
    return render(request, 'gallery.html', {'images': images})


def sermons(request):
    sermons = Sermon.objects.all().order_by('-date')
    
    return render(request, 'sermon.html', {'sermons': sermons})


# Simple contact page
def contact(request):
    return render(request, 'contact.html')



def schools_list(request):
    schools = School.objects.all()
    return render(request, 'schools.html', {'schools': schools})
# Single school detail
PAGINATE_BY = 10  # default items per page

def school_detail(request, pk):
    school = get_object_or_404(School, pk=pk)
    context = {
        'school': school,
        'student_count': school.students.count(),
        'teacher_count': school.teachers.count(),
        'achievement_count': school.achievements.count(),
    }
    return render(request, 'school_detail.html', context)


# Helper to return paginated JSON
def paginate_queryset_to_json(queryset, page, per_page, values_fields):
    paginator = Paginator(queryset, per_page)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    results = list(page_obj.object_list.values(*values_fields))
    return {
        'data': results,
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
        'total': paginator.count,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    }


def load_students(request, pk):
    school = get_object_or_404(School, pk=pk)
    q = request.GET.get('q', '').strip()
    class_level = request.GET.get('grade', '').strip()
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', PAGINATE_BY))

    qs = school.students.all()
    if q:
        qs = qs.filter(full_name__icontains=q)
    if class_level:
        qs = qs.filter(class_level__iexact=class_level)

    data = paginate_queryset_to_json(
        qs, page, per_page,
        values_fields=['id', 'full_name', 'admission_number', 'age', 'class_level', 'date_joined']
    )
    return JsonResponse(data)




def load_teachers(request, pk):
    school = get_object_or_404(School, pk=pk)
    q = request.GET.get('q', '').strip()
    subject = request.GET.get('subject', '').strip()
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', PAGINATE_BY))

    qs = school.teachers.all()
    if q:
        qs = qs.filter(full_name__icontains=q)
    if subject:
        qs = qs.filter(subject__icontains=subject)

    data = paginate_queryset_to_json(
        qs, page, per_page,
        values_fields=['id', 'full_name', 'staff_id', 'subject', 'hire_date']
    )
    return JsonResponse(data)


def load_achievements(request, pk):
    school = get_object_or_404(School, pk=pk)
    q = request.GET.get('q', '').strip()
    year = request.GET.get('year', '').strip()
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', PAGINATE_BY))

    qs = school.achievements.all()
    if q:
        qs = qs.filter(title__icontains=q)
    if year.isdigit():
        qs = qs.filter(year=int(year))

    data = paginate_queryset_to_json(
        qs, page, per_page,
        values_fields=['id', 'title', 'description', 'year']
    )
    return JsonResponse(data)

def newsletter_signup(request):
    return

def donate(request):
    return render(request, 'donate.html', {
        "PAYSTACK_PUBLIC_KEY": settings.PAYSTACK_PUBLIC_KEY
    })


def verify_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        reference = data.get("reference")

        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

        response = requests.get(url, headers=headers).json()

        if response.get("data", {}).get("status") == "success":
            info = response["data"]
            name = info["metadata"]["custom_fields"][0]["value"]
            email = info["customer"]["email"]
            amount = info["amount"] / 100

            Donation.objects.create(
                name=name,
                email=email,
                amount=amount,
                paystack_reference=reference
            )

            messages.success(request, f"Thank you {name}! Your donation of KES {amount:.2f} was successful.")
            return JsonResponse({"status": "success"})

        messages.error(request, "Payment verification failed.")
        return JsonResponse({"status": "failed"})