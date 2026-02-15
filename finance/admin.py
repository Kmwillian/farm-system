from django.contrib import admin
from .models import Transaction, Budget


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'transaction_type', 'category', 'amount', 'party_name', 'payment_method']
    list_filter = ['transaction_type', 'category', 'payment_method', 'date']
    search_fields = ['description', 'party_name', 'reference']
    date_hierarchy = 'date'


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'target_income', 'target_expense']
    search_fields = ['name']
    date_hierarchy = 'start_date'