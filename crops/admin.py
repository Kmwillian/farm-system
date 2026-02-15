from django.contrib import admin
from .models import Farm, CropSeason, CropInput, CropSale


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ['name', 'size_acres', 'location']
    search_fields = ['name', 'location']


@admin.register(CropSeason)
class CropSeasonAdmin(admin.ModelAdmin):
    list_display = ['crop_type', 'farm', 'planting_date', 'expected_harvest_date', 'status']
    list_filter = ['crop_type', 'status']
    search_fields = ['crop_type', 'farm__name']
    date_hierarchy = 'planting_date'


@admin.register(CropInput)
class CropInputAdmin(admin.ModelAdmin):
    list_display = ['season', 'input_type', 'description', 'date', 'cost']
    list_filter = ['input_type', 'date']
    search_fields = ['description', 'season__crop_type']
    date_hierarchy = 'date'


@admin.register(CropSale)
class CropSaleAdmin(admin.ModelAdmin):
    list_display = ['season', 'date', 'quantity_kg', 'total_amount', 'payment_status']
    list_filter = ['payment_status', 'date']
    search_fields = ['buyer', 'season__crop_type']
    date_hierarchy = 'date'