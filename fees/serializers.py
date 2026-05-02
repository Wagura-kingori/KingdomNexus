from rest_framework import serializers
from .models import FeeStructure, Invoice

class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = ['id', 'name', 'amount']

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'student', 'fee_structure', 'amount', 'issued_date', 'due_date', 'paid']
