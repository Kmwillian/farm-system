from django.db import models
from django.utils import timezone


class Transaction(models.Model):
    """Universal transaction model for all income and expenses"""
    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    
    CATEGORIES = (
        # Income categories
        ('milk_sale', 'Milk Sale'),
        ('crop_sale', 'Crop Sale'),
        ('animal_sale', 'Animal Sale'),
        ('other_income', 'Other Income'),
        
        # Expense categories
        ('feed', 'Animal Feed'),
        ('veterinary', 'Veterinary/Health'),
        ('seeds', 'Seeds'),
        ('fertilizer', 'Fertilizer'),
        ('pesticide', 'Pesticide'),
        ('labor', 'Labor/Wages'),
        ('transport', 'Transport'),
        ('equipment', 'Equipment/Tools'),
        ('utilities', 'Utilities'),
        ('other_expense', 'Other Expense'),
    )
    
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ('credit', 'Credit/Pending'),
    )
    
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=30, choices=CATEGORIES)
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=300)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    party_name = models.CharField(max_length=200, blank=True, help_text="Buyer/Seller/Supplier name")
    reference = models.CharField(max_length=100, blank=True, help_text="Receipt/Invoice number")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        symbol = '+' if self.transaction_type == 'income' else '-'
        return f"{symbol}KSh {self.amount} - {self.get_category_display()} ({self.date})"


class Budget(models.Model):
    """Monthly or seasonal budgets"""
    name = models.CharField(max_length=200, help_text="e.g., 'January 2025' or 'Maize Season 2025'")
    start_date = models.DateField()
    end_date = models.DateField()
    target_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    target_expense = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name
    
    def actual_income(self):
        """Calculate actual income in period"""
        return Transaction.objects.filter(
            transaction_type='income',
            date__gte=self.start_date,
            date__lte=self.end_date
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0
    
    def actual_expense(self):
        """Calculate actual expenses in period"""
        return Transaction.objects.filter(
            transaction_type='expense',
            date__gte=self.start_date,
            date__lte=self.end_date
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0
    
    def actual_profit(self):
        """Calculate actual profit"""
        return self.actual_income() - self.actual_expense()
    
    def expected_profit(self):
        """Calculate expected profit"""
        return self.target_income - self.target_expense