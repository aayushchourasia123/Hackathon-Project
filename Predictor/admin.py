from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'type', 'amount', 'nameOrig', 'nameDest', 'isFraud', 'timestamp']
    list_filter = ['type', 'isFraud', 'isFlaggedFraud', 'timestamp']
    search_fields = ['nameOrig', 'nameDest']
    readonly_fields = ['transaction_id', 'timestamp']
    ordering = ['-timestamp']
