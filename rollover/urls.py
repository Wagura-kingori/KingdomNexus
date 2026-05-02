
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from users.views import UserViewSet
from students.views import StudentViewSet, ClassGradeViewSet, SectionViewSet, ParentProfileViewSet
from academics.views import SubjectViewSet, EnrollmentViewSet
from attendance.views import AttendanceRecordViewSet
from fees.views import FeeStructureViewSet, InvoiceViewSet
from django.conf.urls.static import static
#from accounts.views import school_login
from django.contrib.auth.views import LogoutView





router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'students', StudentViewSet)
router.register(r'classgrades', ClassGradeViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'parents', ParentProfileViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'attendance', AttendanceRecordViewSet)
router.register(r'feestructures', FeeStructureViewSet)
router.register(r'invoices', InvoiceViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path("api/", include("made_aesy.api_urls")),
    path('', include('made_aesy.urls')),
    path('', include('users.urls')),
    path('students/', include('students.urls', namespace='students')),
    path('academics/', include('academics.urls', namespace='academics')),
    path("exams/", include("exams.urls", namespace='exams')),
    path("timetable/", include("timetable.urls", namespace="timetable")),
    path("reports/", include("reports.urls", namespace="reports")),
    path('attendance/', include('attendance.urls', namespace='attendance')),
    path('fees/', include('fees.urls', namespace='fees')),
    path('messaging/', include('messaging.urls', namespace='messaging')),
    path('assets/', include('assets.urls',namespace='assets')),
    path("profile/", include("profiles.urls",namespace="profiles")),
    path('transport/', include('transport.urls', namespace='transport')),
    path("teacher/", include("teachers.urls",namespace='teacher')),
    path("parent/", include("parent.urls", namespace="parent")),
    path('hostell/', include('hostell.urls',namespace='hostell')),
    path('payroll/', include('payroll.urls', namespace='payroll')),
    path("schools/", include("schools.urls",namespace='schools')),
    


    #path('accounts/', include('django.contrib.auth.urls')),
    #path("login/", school_login, name="login"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),




]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
