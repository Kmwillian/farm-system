from django.urls import path
from . import views

app_name = 'crops'

urlpatterns = [
    path('', views.crops_home, name='home'),
    
    path('farms/', views.farm_list, name='farm_list'),
    path('farms/add/', views.farm_add, name='farm_add'),
    path('farms/<int:pk>/', views.farm_detail, name='farm_detail'),
    
    path('seasons/', views.season_list, name='season_list'),
    path('seasons/add/', views.season_add, name='season_add'),
    path('seasons/<int:pk>/', views.season_detail, name='season_detail'),
    path('seasons/<int:pk>/edit/', views.season_edit, name='season_edit'),
    
    path('seasons/<int:season_id>/input/add/', views.input_add, name='input_add'),
    path('seasons/<int:season_id>/sale/add/', views.sale_add, name='sale_add'),
]