from django import forms
from .models import FeeStructure, StudentFee, Payment


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['classroom', 'term', 'amount']


class StudentFeeForm(forms.ModelForm):
    class Meta:
        model = StudentFee
        fields = ['student', 'fee_structure', 'total_amount']


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['student_fee', 'amount', 'method']
