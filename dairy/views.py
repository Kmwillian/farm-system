from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from datetime import date, timedelta
from .models import Animal, MilkProduction, HealthRecord, Pregnancy, FeedRecord


@login_required
def dairy_home(request):
    """Dairy management home - overview of all livestock"""
    animals = Animal.objects.filter(status='active')
    cows = animals.filter(animal_type='cow')
    sheep = animals.filter(animal_type='sheep')
    
    # Get today's milk production
    today = date.today()
    today_milk = MilkProduction.objects.filter(date=today).aggregate(
        total=Sum('morning_liters') + Sum('evening_liters')
    )['total'] or 0
    
    # Upcoming health reminders
    upcoming_health = HealthRecord.objects.filter(
        next_due_date__lte=today + timedelta(days=7),
        next_due_date__gte=today
    ).select_related('animal')[:5]
    
    # Pregnancies due soon
    pregnancies_due = Pregnancy.objects.filter(
        expected_delivery__lte=today + timedelta(days=14),
        status__in=['bred', 'confirmed', 'due_soon']
    ).select_related('animal')
    
    context = {
        'total_cows': cows.count(),
        'total_sheep': sheep.count(),
        'total_animals': animals.count(),
        'today_milk': today_milk,
        'upcoming_health': upcoming_health,
        'pregnancies_due': pregnancies_due,
    }
    return render(request, 'dairy/home.html', context)


@login_required
def animal_list(request):
    """List all animals with filters"""
    animal_type = request.GET.get('type', '')
    status = request.GET.get('status', 'active')
    
    animals = Animal.objects.all()
    
    if animal_type:
        animals = animals.filter(animal_type=animal_type)
    if status:
        animals = animals.filter(status=status)
    
    context = {
        'animals': animals,
        'selected_type': animal_type,
        'selected_status': status,
    }
    return render(request, 'dairy/animal_list.html', context)


@login_required
def animal_add(request):
    """Add new animal"""
    if request.method == 'POST':
        animal = Animal(
            animal_type=request.POST.get('animal_type'),
            tag_number=request.POST.get('tag_number'),
            name=request.POST.get('name', ''),
            breed=request.POST.get('breed', ''),
            gender=request.POST.get('gender'),
            date_of_birth=request.POST.get('date_of_birth') or None,
            acquisition_cost=request.POST.get('acquisition_cost', 0),
            mother_tag=request.POST.get('mother_tag', ''),
            father_tag=request.POST.get('father_tag', ''),
            notes=request.POST.get('notes', ''),
        )
        
        if 'photo' in request.FILES:
            animal.photo = request.FILES['photo']
        
        animal.save()
        messages.success(request, f'Animal {animal.tag_number} added successfully!')
        return redirect('dairy:animal_detail', pk=animal.pk)
    
    return render(request, 'dairy/animal_form.html')


@login_required
def animal_detail(request, pk):
    """View animal details with all records"""
    animal = get_object_or_404(Animal, pk=pk)
    
    # Recent milk production (last 7 days for cows)
    milk_records = []
    if animal.animal_type == 'cow' and animal.gender == 'female':
        milk_records = animal.milk_records.all()[:7]
    
    health_records = animal.health_records.all()[:10]
    pregnancies = animal.pregnancies.all()[:5]
    
    # Calculate total milk (last 30 days)
    thirty_days_ago = date.today() - timedelta(days=30)
    total_milk_30d = animal.milk_records.filter(
        date__gte=thirty_days_ago
    ).aggregate(
        total=Sum('morning_liters') + Sum('evening_liters')
    )['total'] or 0
    
    context = {
        'animal': animal,
        'milk_records': milk_records,
        'health_records': health_records,
        'pregnancies': pregnancies,
        'total_milk_30d': total_milk_30d,
    }
    return render(request, 'dairy/animal_detail.html', context)


@login_required
def animal_edit(request, pk):
    """Edit animal information"""
    animal = get_object_or_404(Animal, pk=pk)
    
    if request.method == 'POST':
        animal.tag_number = request.POST.get('tag_number')
        animal.name = request.POST.get('name', '')
        animal.breed = request.POST.get('breed', '')
        animal.gender = request.POST.get('gender')
        animal.date_of_birth = request.POST.get('date_of_birth') or None
        animal.status = request.POST.get('status')
        animal.mother_tag = request.POST.get('mother_tag', '')
        animal.father_tag = request.POST.get('father_tag', '')
        animal.notes = request.POST.get('notes', '')
        
        if 'photo' in request.FILES:
            animal.photo = request.FILES['photo']
        
        animal.save()
        messages.success(request, f'Animal {animal.tag_number} updated successfully!')
        return redirect('dairy:animal_detail', pk=animal.pk)
    
    context = {'animal': animal}
    return render(request, 'dairy/animal_form.html', context)


@login_required
def milk_production_add(request):
    """Add milk production record"""
    if request.method == 'POST':
        animal_id = request.POST.get('animal')
        animal = get_object_or_404(Animal, pk=animal_id)
        
        # Check if record exists for today
        record_date = request.POST.get('date', date.today())
        existing = MilkProduction.objects.filter(animal=animal, date=record_date).first()
        
        if existing:
            # Update existing record
            existing.morning_liters = request.POST.get('morning_liters', 0)
            existing.evening_liters = request.POST.get('evening_liters', 0)
            existing.notes = request.POST.get('notes', '')
            existing.save()
            messages.success(request, 'Milk record updated!')
        else:
            # Create new record
            MilkProduction.objects.create(
                animal=animal,
                date=record_date,
                morning_liters=request.POST.get('morning_liters', 0),
                evening_liters=request.POST.get('evening_liters', 0),
                notes=request.POST.get('notes', ''),
            )
            messages.success(request, 'Milk record added!')
        
        return redirect('dairy:milk_list')
    
    # Get milking cows only
    cows = Animal.objects.filter(
        animal_type='cow',
        gender='female',
        status='active'
    )
    
    context = {'cows': cows}
    return render(request, 'dairy/milk_form.html', context)


@login_required
def milk_production_list(request):
    """List milk production records"""
    # Filter options
    days = int(request.GET.get('days', 7))
    animal_id = request.GET.get('animal', '')
    
    records = MilkProduction.objects.select_related('animal')
    
    if animal_id:
        records = records.filter(animal_id=animal_id)
    
    # Last N days
    cutoff_date = date.today() - timedelta(days=days)
    records = records.filter(date__gte=cutoff_date)
    
    # Calculate totals
    totals = records.aggregate(
        total_morning=Sum('morning_liters'),
        total_evening=Sum('evening_liters'),
    )
    total_liters = (totals['total_morning'] or 0) + (totals['total_evening'] or 0)
    
    cows = Animal.objects.filter(animal_type='cow', gender='female', status='active')
    
    context = {
        'records': records[:30],
        'total_liters': total_liters,
        'days': days,
        'cows': cows,
        'selected_animal': animal_id,
    }
    return render(request, 'dairy/milk_list.html', context)


@login_required
def health_record_add(request, animal_id):
    """Add health/vaccination record"""
    animal = get_object_or_404(Animal, pk=animal_id)
    
    if request.method == 'POST':
        HealthRecord.objects.create(
            animal=animal,
            record_type=request.POST.get('record_type'),
            date=request.POST.get('date', date.today()),
            description=request.POST.get('description'),
            veterinarian=request.POST.get('veterinarian', ''),
            cost=request.POST.get('cost', 0),
            next_due_date=request.POST.get('next_due_date') or None,
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Health record added!')
        return redirect('dairy:animal_detail', pk=animal.pk)
    
    context = {'animal': animal}
    return render(request, 'dairy/health_form.html', context)


@login_required
def pregnancy_add(request, animal_id):
    """Add pregnancy record"""
    animal = get_object_or_404(Animal, pk=animal_id)
    
    if request.method == 'POST':
        Pregnancy.objects.create(
            animal=animal,
            breeding_date=request.POST.get('breeding_date', date.today()),
            bull_tag=request.POST.get('bull_tag', ''),
            status=request.POST.get('status', 'bred'),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Pregnancy record added!')
        return redirect('dairy:animal_detail', pk=animal.pk)
    
    context = {'animal': animal}
    return render(request, 'dairy/pregnancy_form.html', context)


@login_required
def pregnancy_update(request, pk):
    """Update pregnancy status"""
    pregnancy = get_object_or_404(Pregnancy, pk=pk)
    
    if request.method == 'POST':
        pregnancy.status = request.POST.get('status')
        pregnancy.actual_delivery = request.POST.get('actual_delivery') or None
        pregnancy.offspring_count = request.POST.get('offspring_count', 0)
        pregnancy.notes = request.POST.get('notes', '')
        pregnancy.save()
        messages.success(request, 'Pregnancy updated!')
        return redirect('dairy:animal_detail', pk=pregnancy.animal.pk)
    
    context = {'pregnancy': pregnancy}
    return render(request, 'dairy/pregnancy_form.html', context)


@login_required
def feed_record_add(request):
    """Add feed purchase record"""
    if request.method == 'POST':
        FeedRecord.objects.create(
            date=request.POST.get('date', date.today()),
            feed_type=request.POST.get('feed_type'),
            quantity_kg=request.POST.get('quantity_kg'),
            cost=request.POST.get('cost', 0),
            supplier=request.POST.get('supplier', ''),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Feed record added!')
        return redirect('dairy:feed_list')
    
    return render(request, 'dairy/feed_form.html')


@login_required
def feed_record_list(request):
    """List feed records"""
    records = FeedRecord.objects.all()[:30]
    
    # Calculate totals for last 30 days
    thirty_days_ago = date.today() - timedelta(days=30)
    totals = FeedRecord.objects.filter(date__gte=thirty_days_ago).aggregate(
        total_cost=Sum('cost'),
        total_quantity=Sum('quantity_kg'),
    )
    
    context = {
        'records': records,
        'total_cost_30d': totals['total_cost'] or 0,
        'total_quantity_30d': totals['total_quantity'] or 0,
    }
    return render(request, 'dairy/feed_list.html', context)