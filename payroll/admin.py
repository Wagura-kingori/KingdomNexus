from django.contrib import admin
from .models import Employee, SalaryComponent, PayrollPeriod, Payslip, PayslipLine, Payment

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('staff_id','name','job_title','active')

@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ('name','kind','default_amount')

@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ('name','start_date','end_date','processed')

class PayslipLineInline(admin.TabularInline):
    model = PayslipLine
    extra = 0

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ('employee','period','gross','net_pay','processed')
    inlines = [PayslipLineInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payslip','amount','method','paid_on')
