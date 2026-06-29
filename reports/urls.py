from django.urls import path
from .views import report_card, report_card_pdf

app_name = "reports"   

urlpatterns = [
    path("<int:student_id>/<int:exam_id>/", report_card, name="report_card"),
    path("<int:student_id>/<int:exam_id>/pdf/", report_card_pdf, name="report_card_pdf"),
]