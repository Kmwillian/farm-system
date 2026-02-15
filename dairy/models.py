from django.db import models
from django.utils import timezone
from datetime import date, timedelta


class Animal(models.Model):
    """Base model for livestock (cows and sheep)"""
    ANIMAL_TYPES = (
        ('cow', 'Cow'),
        ('sheep', 'Sheep'),
    )
    
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('deceased', 'Deceased'),
    )
    
    animal_type = models.CharField(max_length=10, choices=ANIMAL_TYPES)
    tag_number = models.CharField(max_length=50, unique=True, help_text="Unique ID/Tag")
    name = models.CharField(max_length=100, blank=True, help_text="Optional name")
    breed = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    date_acquired = models.DateField(default=timezone.now)
    acquisition_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to='animals/', blank=True, null=True)
    
    # Breeding information
    mother_tag = models.CharField(max_length=50, blank=True, help_text="Mother's tag number")
    father_tag = models.CharField(max_length=50, blank=True, help_text="Father's tag number")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_animal_type_display()} - {self.tag_number} ({self.name or 'Unnamed'})"
    
    def age_in_months(self):
        """Calculate age in months"""
        if self.date_of_birth:
            today = date.today()
            months = (today.year - self.date_of_birth.year) * 12
            months += today.month - self.date_of_birth.month
            return max(0, months)
        return None
    
    def is_mature(self):
        """Check if animal is mature for breeding (cows: 15+ months, sheep: 7+ months)"""
        age = self.age_in_months()
        if age is None:
            return False
        if self.animal_type == 'cow':
            return age >= 15
        elif self.animal_type == 'sheep':
            return age >= 7
        return False


class MilkProduction(models.Model):
    """Daily milk production record"""
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='milk_records')
    date = models.DateField(default=timezone.now)
    morning_liters = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="Morning milking")
    evening_liters = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="Evening milking")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ['animal', 'date']
    
    def __str__(self):
        return f"{self.animal.tag_number} - {self.date} - {self.total_liters}L"
    
    @property
    def total_liters(self):
        """Total milk for the day"""
        return self.morning_liters + self.evening_liters


class HealthRecord(models.Model):
    """Health, vaccination, and veterinary records"""
    RECORD_TYPES = (
        ('vaccination', 'Vaccination'),
        ('treatment', 'Treatment'),
        ('checkup', 'Checkup'),
        ('injury', 'Injury'),
        ('other', 'Other'),
    )
    
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='health_records')
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES)
    date = models.DateField(default=timezone.now)
    description = models.TextField(help_text="What was done/observed")
    veterinarian = models.CharField(max_length=100, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    next_due_date = models.DateField(null=True, blank=True, help_text="Next vaccination/checkup date")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.animal.tag_number} - {self.get_record_type_display()} - {self.date}"
    
    def is_due_soon(self):
        """Check if next appointment is due within 7 days"""
        if self.next_due_date:
            return self.next_due_date <= date.today() + timedelta(days=7)
        return False


class Pregnancy(models.Model):
    """Track breeding and pregnancy cycles"""
    STATUS_CHOICES = (
        ('bred', 'Recently Bred'),
        ('confirmed', 'Pregnancy Confirmed'),
        ('due_soon', 'Due Soon'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed/Aborted'),
    )
    
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='pregnancies')
    breeding_date = models.DateField(default=timezone.now)
    bull_tag = models.CharField(max_length=50, blank=True, help_text="Bull/Ram tag number")
    expected_delivery = models.DateField(null=True, blank=True)
    actual_delivery = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='bred')
    offspring_count = models.IntegerField(default=0, help_text="Number of calves/lambs")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-breeding_date']
    
    def __str__(self):
        return f"{self.animal.tag_number} - Bred: {self.breeding_date}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate expected delivery date"""
        if self.breeding_date and not self.expected_delivery:
            # Cows: 283 days, Sheep: 150 days
            if self.animal.animal_type == 'cow':
                self.expected_delivery = self.breeding_date + timedelta(days=283)
            elif self.animal.animal_type == 'sheep':
                self.expected_delivery = self.breeding_date + timedelta(days=150)
        super().save(*args, **kwargs)
    
    def is_due_within_week(self):
        """Check if delivery is expected within 7 days"""
        if self.expected_delivery and self.status in ['bred', 'confirmed', 'due_soon']:
            return self.expected_delivery <= date.today() + timedelta(days=7)
        return False


class FeedRecord(models.Model):
    """Track feeding and expenses"""
    date = models.DateField(default=timezone.now)
    feed_type = models.CharField(max_length=100, help_text="e.g., Hay, Concentrate, Silage")
    quantity_kg = models.DecimalField(max_digits=8, decimal_places=2, help_text="Quantity in kg")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.feed_type} - {self.date} - {self.quantity_kg}kg"