from django import forms
from .models import Employee, SalaryComponent, PayrollPeriod, Payslip, PayslipLine, Payment,EmployeeComponent

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['user','staff_id','name','email','phone','job_title','date_joined','active']

class SalaryComponentForm(forms.ModelForm):
    class Meta:
        model = SalaryComponent
        fields = ['name','kind','default_amount']

class PayrollPeriodForm(forms.ModelForm):
    class Meta:
        model = PayrollPeriod
        fields = ['name','start_date','end_date']

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payslip','amount','method','reference','paid_on']
class EmployeeComponentForm(forms.ModelForm):
    class Meta:
        model = EmployeeComponent
        fields = ['employee','component','amount']
