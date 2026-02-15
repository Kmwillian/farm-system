from django.urls import path
from . import views

app_name = 'dairy'

urlpatterns = [
    path('', views.dairy_home, name='home'),
    path('animals/', views.animal_list, name='animal_list'),
    path('animals/add/', views.animal_add, name='animal_add'),
    path('animals/<int:pk>/', views.animal_detail, name='animal_detail'),
    path('animals/<int:pk>/edit/', views.animal_edit, name='animal_edit'),
    
    path('milk/add/', views.milk_production_add, name='milk_add'),
    path('milk/', views.milk_production_list, name='milk_list'),
    
    path('health/<int:animal_id>/add/', views.health_record_add, name='health_add'),
    
    path('pregnancy/<int:animal_id>/add/', views.pregnancy_add, name='pregnancy_add'),
    path('pregnancy/<int:pk>/update/', views.pregnancy_update, name='pregnancy_update'),
    
    path('feed/add/', views.feed_record_add, name='feed_add'),
    path('feed/', views.feed_record_list, name='feed_list'),
]