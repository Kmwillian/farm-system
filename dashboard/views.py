from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from datetime import date, timedelta

from dairy.models import Animal, MilkProduction, HealthRecord, Pregnancy
from crops.models import CropSeason
from finance.models import Transaction


@login_required
def dashboard(request):
    """Main dashboard - farm overview"""
    today = date.today()
    this_month = today.replace(day=1)
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    
    # === LIVESTOCK SUMMARY ===
    total_cows = Animal.objects.filter(animal_type='cow', status='active').count()
    total_sheep = Animal.objects.filter(animal_type='sheep', status='active').count()
    
    # Today's milk
    today_milk = MilkProduction.objects.filter(date=today).aggregate(
        total=Sum('morning_liters') + Sum('evening_liters')
    )['total'] or 0
    
    # Last 7 days milk
    milk_7d = MilkProduction.objects.filter(date__gte=last_7_days).aggregate(
        total=Sum('morning_liters') + Sum('evening_liters')
    )['total'] or 0
    
    # === CROPS SUMMARY ===
    active_crops = CropSeason.objects.filter(status__in=['planned', 'planted']).count()
    
    # Harvest due soon (next 14 days)
    harvest_due = CropSeason.objects.filter(
        status__in=['planted'],
        expected_harvest_date__lte=today + timedelta(days=14),
        expected_harvest_date__gte=today
    )
    
    # === FINANCE SUMMARY ===
    # This month
    month_income = Transaction.objects.filter(
        transaction_type='income',
        date__gte=this_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    month_expense = Transaction.objects.filter(
        transaction_type='expense',
        date__gte=this_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Last 30 days
    income_30d = Transaction.objects.filter(
        transaction_type='income',
        date__gte=last_30_days
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    expense_30d = Transaction.objects.filter(
        transaction_type='expense',
        date__gte=last_30_days
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # === ALERTS & REMINDERS ===
    # Health checkups due
    health_due = HealthRecord.objects.filter(
        next_due_date__lte=today + timedelta(days=7),
        next_due_date__gte=today
    ).select_related('animal')[:5]
    
    # Pregnancies due soon
    pregnancies_due = Pregnancy.objects.filter(
        expected_delivery__lte=today + timedelta(days=14),
        expected_delivery__gte=today,
        status__in=['bred', 'confirmed', 'due_soon']
    ).select_related('animal')[:5]
    
    # Recent activity
    recent_transactions = Transaction.objects.all()[:5]
    recent_milk = MilkProduction.objects.select_related('animal')[:5]
    
    context = {
        # Livestock
        'total_cows': total_cows,
        'total_sheep': total_sheep,
        'today_milk': today_milk,
        'milk_7d': milk_7d,
        
        # Crops
        'active_crops': active_crops,
        'harvest_due': harvest_due,
        
        # Finance
        'month_income': month_income,
        'month_expense': month_expense,
        'month_profit': month_income - month_expense,
        'income_30d': income_30d,
        'expense_30d': expense_30d,
        'profit_30d': income_30d - expense_30d,
        
        # Alerts
        'health_due': health_due,
        'pregnancies_due': pregnancies_due,
        
        # Recent activity
        'recent_transactions': recent_transactions,
        'recent_milk': recent_milk,
    }
    
    return render(request, 'dashboard/home.html', context)