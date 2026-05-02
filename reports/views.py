from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO

from students.models import Student
from exams.models import Exam, ExamResult


def report_card(request, student_id, exam_id):
    """Render HTML view of report card."""
    student = get_object_or_404(Student, id=student_id)
    exam = get_object_or_404(Exam, id=exam_id)
    results = ExamResult.get_student_results(student, exam)

    total = sum(r.score for r in results)
    average = total / results.count() if results.exists() else 0

    context = {
        "student": student,
        "exam": exam,
        "results": results,
        "total": total,
        "average": round(average, 2),
    }

    return render(request, "reports/report_card.html", context)


def render_to_pdf(template_src, context_dict, filename=None):
    """Rende a template to PDF using xhtml2pdf."""
    html = render_to_string(template_src, context_dict)
    result = BytesIO()
    pdf = pisa.CreatePDF(src=html, dest=result)

    if pdf.err:
        return HttpResponse("PDF generation error", status=500)

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    if filename:
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    else:
        response['Content-Disposition'] = 'inline; filename="document.pdf"'
    return response


def report_card_pdf(request, student_id, exam_id):
    """Generate pdf report card for a student."""
    student = get_object_or_404(Student, id=student_id)
    exam = get_object_or_404(Exam, id=exam_id)
    results = ExamResult.get_student_results(student, exam)

    total = sum(r.score for r in results)
    average = total / results.count() if results.exists() else 0

    context = {
        "student": student,
        "exam": exam,
        "results": results,
        "total": total,
        "average": round(average, 2),
    }

    filename = f"report_card_{student.id}_{exam.id}.pdf"
    return render_to_pdf("reports/report_card_pdf.html", context, filename)
