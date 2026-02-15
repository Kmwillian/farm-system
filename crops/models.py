from django.db import models
from django.utils import timezone
from datetime import date


class Farm(models.Model):
    """Farm location/plot"""
    name = models.CharField(max_length=200, help_text="Farm name or location")
    size_acres = models.DecimalField(max_digits=8, decimal_places=2, help_text="Size in acres")
    location = models.CharField(max_length=300, blank=True, help_text="Address or GPS coordinates")
    soil_type = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.size_acres} acres)"


class CropSeason(models.Model):
    """Planting season/cycle for a specific crop"""
    CROP_CHOICES = (
        ('sugarcane', 'Sugarcane'),
        ('maize', 'Maize'),
        ('beans', 'Beans'),
        ('vegetables', 'Vegetables'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('planned', 'Planned'),
        ('planted', 'Planted/Growing'),
        ('harvested', 'Harvested'),
        ('failed', 'Failed/Lost'),
    )
    
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='seasons')
    crop_type = models.CharField(max_length=50, choices=CROP_CHOICES)
    crop_variety = models.CharField(max_length=100, blank=True, help_text="Specific variety name")
    
    # Dates
    planting_date = models.DateField()
    expected_harvest_date = models.DateField(help_text="Estimated harvest date")
    actual_harvest_date = models.DateField(null=True, blank=True)
    
    # Area and yield
    area_planted_acres = models.DecimalField(max_digits=8, decimal_places=2)
    expected_yield_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_yield_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-planting_date']
    
    def __str__(self):
        return f"{self.get_crop_type_display()} - {self.farm.name} ({self.planting_date.year})"
    
    def days_to_harvest(self):
        """Calculate days remaining until expected harvest"""
        if self.status == 'harvested':
            return 0
        today = date.today()
        delta = (self.expected_harvest_date - today).days
        return max(0, delta)
    
    def is_harvest_due(self):
        """Check if harvest is due within 7 days"""
        return 0 <= self.days_to_harvest() <= 7


class CropInput(models.Model):
    """Track inputs like seeds, fertilizer, pesticides"""
    INPUT_TYPES = (
        ('seeds', 'Seeds/Seedlings'),
        ('fertilizer', 'Fertilizer'),
        ('pesticide', 'Pesticide/Herbicide'),
        ('water', 'Irrigation Water'),
        ('labor', 'Labor'),
        ('other', 'Other'),
    )
    
    season = models.ForeignKey(CropSeason, on_delete=models.CASCADE, related_name='inputs')
    input_type = models.CharField(max_length=20, choices=INPUT_TYPES)
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=200, help_text="Brand/name of product")
    quantity = models.CharField(max_length=100, help_text="e.g., 50 kg, 10 liters, 5 days")
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_input_type_display()} - {self.description} ({self.date})"


class CropSale(models.Model):
    """Record crop sales/revenue"""
    season = models.ForeignKey(CropSeason, on_delete=models.CASCADE, related_name='sales')
    date = models.DateField(default=timezone.now)
    quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_kg = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    buyer = models.CharField(max_length=200, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=(('paid', 'Paid'), ('pending', 'Pending'), ('partial', 'Partial')),
        default='paid'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.season.crop_type} Sale - {self.quantity_kg}kg - {self.date}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate total amount"""
        self.total_amount = self.quantity_kg * self.price_per_kg
        super().save(*args, **kwargs)