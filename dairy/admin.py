from django.contrib import admin
from .models import Animal, MilkProduction, HealthRecord, Pregnancy, FeedRecord


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['tag_number', 'name', 'animal_type', 'gender', 'status', 'date_acquired']
    list_filter = ['animal_type', 'gender', 'status']
    search_fields = ['tag_number', 'name', 'breed']
    date_hierarchy = 'date_acquired'


@admin.register(MilkProduction)
class MilkProductionAdmin(admin.ModelAdmin):
    list_display = ['animal', 'date', 'morning_liters', 'evening_liters', 'total_liters']
    list_filter = ['date']
    search_fields = ['animal__tag_number']
    date_hierarchy = 'date'


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ['animal', 'record_type', 'date', 'cost', 'next_due_date']
    list_filter = ['record_type', 'date']
    search_fields = ['animal__tag_number', 'description']
    date_hierarchy = 'date'


@admin.register(Pregnancy)
class PregnancyAdmin(admin.ModelAdmin):
    list_display = ['animal', 'breeding_date', 'expected_delivery', 'status', 'offspring_count']
    list_filter = ['status']
    search_fields = ['animal__tag_number']
    date_hierarchy = 'breeding_date'


@admin.register(FeedRecord)
class FeedRecordAdmin(admin.ModelAdmin):
    list_display = ['date', 'feed_type', 'quantity_kg', 'cost', 'supplier']
    list_filter = ['feed_type', 'date']
    search_fields = ['feed_type', 'supplier']
    date_hierarchy = 'date'