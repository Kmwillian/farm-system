from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.finance_home, name='home'),
    
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.transaction_add, name='transaction_add'),
    path('transactions/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    
    path('reports/', views.reports, name='reports'),
    
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/add/', views.budget_add, name='budget_add'),
    path('budgets/<int:pk>/', views.budget_detail, name='budget_detail'),
]