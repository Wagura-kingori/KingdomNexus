from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from .models import Employee, SalaryComponent, PayrollPeriod, Payslip, PayslipLine, Payment
from .forms import (
    EmployeeForm, SalaryComponentForm, PayrollPeriodForm,
    PaymentForm, EmployeeComponentForm
)
from django.db import transaction
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from .decorators import payroll_required
from django.utils import timezone


# ----------------------------
# PDF helper
# ----------------------------
def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF")
    return response


@login_required
def payslip_pdf(request, pk):
    payslip = get_object_or_404(
        Payslip,
        pk=pk,
        employee__school=request.user.payrollprofile.school
    )
    context = {"payslip": payslip}
    return render_to_pdf("payroll/payslip_pdf.html", context)


# ----------------------------
# TAX CALCULATION
# ----------------------------
def calculate_tax(gross: Decimal) -> Decimal:
    gross = Decimal(gross)
    tax = Decimal('0')
    remaining = gross

    if remaining > 100000:
        remaining -= 100000
        slab = min(remaining, Decimal('100000'))
        tax += slab * Decimal('0.10')
        remaining -= slab
        if remaining > 0:
            tax += remaining * Decimal('0.20')

    return tax.quantize(Decimal('0.01'))


# ----------------------------
# EMPLOYEES (SCHOOL LOCKED)
# ----------------------------
@login_required
@payroll_required
def employees_list(request):
    employees = Employee.objects.filter(
        school=request.user.payrollprofile.school
    ).order_by('name')

    return render(request, 'payroll/employees_list.html', {'employees': employees})


@login_required
@payroll_required
def employee_form(request, pk=None):
    emp = None
    if pk:
        emp = get_object_or_404(
            Employee,
            pk=pk,
            school=request.user.payrollprofile.school
        )

    form = EmployeeForm(request.POST or None, instance=emp)

    if request.method == 'POST' and form.is_valid():
        employee = form.save(commit=False)
        employee.school = request.user.payrollprofile.school
        employee.save()
        return redirect('payroll:employees')

    return render(request, 'payroll/employee_form.html', {'form': form})


# ----------------------------
# COMPONENTS & PERIODS
# ----------------------------
@login_required
@payroll_required
def components_list(request):
    return render(
        request,
        'payroll/components_list.html',
        {'components': SalaryComponent.objects.all()}
    )


@login_required
@payroll_required
def payroll_periods(request):
    periods = PayrollPeriod.objects.all().order_by('-start_date')
    return render(request, 'payroll/periods_list.html', {'periods': periods})


@login_required
@payroll_required
def payroll_period_form(request, pk=None):
    p = get_object_or_404(PayrollPeriod, pk=pk) if pk else None
    form = PayrollPeriodForm(request.POST or None, instance=p)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('payroll:periods')

    return render(request, 'payroll/period_form.html', {'form': form})


# ----------------------------
# PAYROLL PROCESSING (SCHOOL SAFE)
# ----------------------------
@login_required
@payroll_required
def process_payroll(request, period_id):
    period = get_object_or_404(PayrollPeriod, pk=period_id)

    employees = Employee.objects.filter(
        active=True,
        school=request.user.payrollprofile.school
    )

    with transaction.atomic():
        for emp in employees:
            payslip, _ = Payslip.objects.get_or_create(
                employee=emp,
                period=period
            )
            payslip.lines.all().delete()

            gross = Decimal('0')
            total_ded = Decimal('0')

            for ec in emp.custom_components.all():
                if ec.component.kind == 'earning':
                    gross += ec.amount
                    PayslipLine.objects.create(
                        payslip=payslip,
                        component=ec.component,
                        amount=ec.amount
                    )
                else:
                    total_ded += ec.amount
                    PayslipLine.objects.create(
                        payslip=payslip,
                        component=ec.component,
                        amount=ec.amount,
                        is_deduction=True
                    )

            tax = calculate_tax(gross)
            if tax > 0:
                total_ded += tax
                PayslipLine.objects.create(
                    payslip=payslip,
                    component=None,
                    amount=tax,
                    is_deduction=True
                )

            payslip.gross = gross
            payslip.total_deductions = total_ded
            payslip.net_pay = gross - total_ded
            payslip.processed = True
            payslip.save()

        period.processed = True
        period.processed_on = timezone.now()
        period.save()

    messages.success(request, "Payroll processed successfully.")
    return redirect(reverse('payroll:periods'))


# ----------------------------
# PAYSLIPS (LOCKED)
# ----------------------------
@login_required
@permission_required('payroll.view_payslip', raise_exception=True)
def payslips_list(request, period_id=None):
    qs = Payslip.objects.filter(
        employee__school=request.user.payrollprofile.school
    )

    if period_id:
        qs = qs.filter(period_id=period_id)

    return render(request, 'payroll/payslips_list.html', {'payslips': qs})


@login_required
def payslip_detail(request, pk):
    payslip = get_object_or_404(
        Payslip,
        pk=pk,
        employee__school=request.user.payrollprofile.school
    )
    return render(request, 'payroll/payslip_detail.html', {'payslip': payslip})
