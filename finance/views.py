from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from datetime import date, timedelta
from .models import Transaction, Budget


@login_required
def finance_home(request):
    """Finance dashboard with key metrics"""
    # Time periods
    today = date.today()
    this_month_start = today.replace(day=1)
    last_30_days = today - timedelta(days=30)
    
    # This month totals
    month_income = Transaction.objects.filter(
        transaction_type='income',
        date__gte=this_month_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    month_expense = Transaction.objects.filter(
        transaction_type='expense',
        date__gte=this_month_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Last 30 days totals
    income_30d = Transaction.objects.filter(
        transaction_type='income',
        date__gte=last_30_days
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    expense_30d = Transaction.objects.filter(
        transaction_type='expense',
        date__gte=last_30_days
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Recent transactions
    recent_transactions = Transaction.objects.all()[:10]
    
    # Pending payments (credit)
    pending = Transaction.objects.filter(payment_method='credit', transaction_type='income')
    
    context = {
        'month_income': month_income,
        'month_expense': month_expense,
        'month_profit': month_income - month_expense,
        'income_30d': income_30d,
        'expense_30d': expense_30d,
        'profit_30d': income_30d - expense_30d,
        'recent_transactions': recent_transactions,
        'pending_payments': pending,
    }
    return render(request, 'finance/home.html', context)


@login_required
def transaction_list(request):
    """List all transactions with filters"""
    trans_type = request.GET.get('type', '')
    category = request.GET.get('category', '')
    days = int(request.GET.get('days', 30))
    
    transactions = Transaction.objects.all()
    
    if trans_type:
        transactions = transactions.filter(transaction_type=trans_type)
    if category:
        transactions = transactions.filter(category=category)
    
    # Date filter
    if days:
        cutoff = date.today() - timedelta(days=days)
        transactions = transactions.filter(date__gte=cutoff)
    
    # Calculate totals
    totals = transactions.aggregate(
        total_income=Sum('amount', filter=Q(transaction_type='income')),
        total_expense=Sum('amount', filter=Q(transaction_type='expense')),
    )
    
    context = {
        'transactions': transactions[:100],
        'total_income': totals['total_income'] or 0,
        'total_expense': totals['total_expense'] or 0,
        'net_profit': (totals['total_income'] or 0) - (totals['total_expense'] or 0),
        'selected_type': trans_type,
        'selected_category': category,
        'days': days,
    }
    return render(request, 'finance/transaction_list.html', context)


@login_required
def transaction_add(request):
    """Add new transaction (income or expense)"""
    if request.method == 'POST':
        Transaction.objects.create(
            transaction_type=request.POST.get('transaction_type'),
            category=request.POST.get('category'),
            date=request.POST.get('date', date.today()),
            amount=request.POST.get('amount'),
            description=request.POST.get('description'),
            payment_method=request.POST.get('payment_method', 'cash'),
            party_name=request.POST.get('party_name', ''),
            reference=request.POST.get('reference', ''),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Transaction recorded!')
        return redirect('finance:transaction_list')
    
    # Pre-fill type if provided in URL
    initial_type = request.GET.get('type', '')
    context = {'initial_type': initial_type}
    return render(request, 'finance/transaction_form.html', context)


@login_required
def transaction_edit(request, pk):
    """Edit existing transaction"""
    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        transaction.transaction_type = request.POST.get('transaction_type')
        transaction.category = request.POST.get('category')
        transaction.date = request.POST.get('date')
        transaction.amount = request.POST.get('amount')
        transaction.description = request.POST.get('description')
        transaction.payment_method = request.POST.get('payment_method')
        transaction.party_name = request.POST.get('party_name', '')
        transaction.reference = request.POST.get('reference', '')
        transaction.notes = request.POST.get('notes', '')
        transaction.save()
        
        messages.success(request, 'Transaction updated!')
        return redirect('finance:transaction_list')
    
    context = {'transaction': transaction}
    return render(request, 'finance/transaction_form.html', context)


@login_required
def transaction_delete(request, pk):
    """Delete transaction"""
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted!')
        return redirect('finance:transaction_list')
    
    context = {'transaction': transaction}
    return render(request, 'finance/transaction_confirm_delete.html', context)


@login_required
def reports(request):
    """Financial reports and analytics"""
    # Time periods
    today = date.today()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    this_year = today.replace(month=1, day=1)
    
    # This month
    month_data = Transaction.objects.filter(date__gte=this_month).aggregate(
        income=Sum('amount', filter=Q(transaction_type='income')),
        expense=Sum('amount', filter=Q(transaction_type='expense')),
    )
    
    # Last month
    last_month_data = Transaction.objects.filter(
        date__gte=last_month,
        date__lt=this_month
    ).aggregate(
        income=Sum('amount', filter=Q(transaction_type='income')),
        expense=Sum('amount', filter=Q(transaction_type='expense')),
    )
    
    # This year
    year_data = Transaction.objects.filter(date__gte=this_year).aggregate(
        income=Sum('amount', filter=Q(transaction_type='income')),
        expense=Sum('amount', filter=Q(transaction_type='expense')),
    )
    
    # Income by category (this month)
    income_by_category = Transaction.objects.filter(
        transaction_type='income',
        date__gte=this_month
    ).values('category').annotate(total=Sum('amount')).order_by('-total')
    
    # Expense by category (this month)
    expense_by_category = Transaction.objects.filter(
        transaction_type='expense',
        date__gte=this_month
    ).values('category').annotate(total=Sum('amount')).order_by('-total')
    
    context = {
        'month_income': month_data['income'] or 0,
        'month_expense': month_data['expense'] or 0,
        'month_profit': (month_data['income'] or 0) - (month_data['expense'] or 0),
        
        'last_month_income': last_month_data['income'] or 0,
        'last_month_expense': last_month_data['expense'] or 0,
        'last_month_profit': (last_month_data['income'] or 0) - (last_month_data['expense'] or 0),
        
        'year_income': year_data['income'] or 0,
        'year_expense': year_data['expense'] or 0,
        'year_profit': (year_data['income'] or 0) - (year_data['expense'] or 0),
        
        'income_by_category': income_by_category,
        'expense_by_category': expense_by_category,
    }
    return render(request, 'finance/reports.html', context)


@login_required
def budget_list(request):
    """List all budgets"""
    budgets = Budget.objects.all()
    context = {'budgets': budgets}
    return render(request, 'finance/budget_list.html', context)


@login_required
def budget_add(request):
    """Create new budget"""
    if request.method == 'POST':
        Budget.objects.create(
            name=request.POST.get('name'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            target_income=request.POST.get('target_income', 0),
            target_expense=request.POST.get('target_expense', 0),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Budget created!')
        return redirect('finance:budget_list')
    
    return render(request, 'finance/budget_form.html')


@login_required
def budget_detail(request, pk):
    """View budget details with actual vs target"""
    budget = get_object_or_404(Budget, pk=pk)
    
    # Get transactions in budget period
    transactions = Transaction.objects.filter(
        date__gte=budget.start_date,
        date__lte=budget.end_date
    )
    
    context = {
        'budget': budget,
        'transactions': transactions,
    }
    return render(request, 'finance/budget_detail.html', context)