from rest_framework import viewsets
from .models import FeeStructure, Invoice
from .serializers import FeeStructureSerializer, InvoiceSerializer
from rest_framework.permissions import IsAuthenticated

class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAuthenticated]

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

from django.shortcuts import render, redirect, get_object_or_404
from .models import FeeStructure, StudentFee, Payment
from .forms import FeeStructureForm, StudentFeeForm, PaymentForm


def fee_structure_list(request):
    structures = FeeStructure.objects.all()
    return render(request, 'fees/fee_structure_list.html', {'structures': structures})


def fee_structure_form(request):
    form = FeeStructureForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('fee_structure_list')
    return render(request, 'fees/fee_structure_form.html', {'form': form})


def student_fees_list(request):
    fees = StudentFee.objects.all()
    return render(request, 'fees/student_fees_list.html', {'fees': fees})


def student_fee_form(request):
    form = StudentFeeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        student_fee = form.save(commit=False)
        student_fee.balance = student_fee.total_amount
        student_fee.save()
        return redirect('student_fees_list')
    return render(request, 'fees/student_fee_form.html', {'form': form})


def payment_list(request):
    payments = Payment.objects.all()
    return render(request, 'fees/payment_list.html', {'payments': payments})


def payment_form(request):
    form = PaymentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('payment_list')
    return render(request, 'fees/payment_form.html', {'form': form})
