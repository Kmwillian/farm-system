from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import date, timedelta
from .models import Farm, CropSeason, CropInput, CropSale


@login_required
def crops_home(request):
    """Crops management overview"""
    farms = Farm.objects.all()
    
    # Active seasons
    active_seasons = CropSeason.objects.filter(status__in=['planned', 'planted'])
    
    # Harvest due soon (next 14 days)
    harvest_due = active_seasons.filter(
        expected_harvest_date__lte=date.today() + timedelta(days=14)
    )
    
    # Recent harvests (last 30 days)
    recent_harvests = CropSeason.objects.filter(
        status='harvested',
        actual_harvest_date__gte=date.today() - timedelta(days=30)
    )
    
    context = {
        'total_farms': farms.count(),
        'total_acres': farms.aggregate(Sum('size_acres'))['size_acres__sum'] or 0,
        'active_seasons': active_seasons.count(),
        'harvest_due': harvest_due,
        'recent_harvests': recent_harvests,
    }
    return render(request, 'crops/home.html', context)


@login_required
def farm_list(request):
    """List all farms"""
    farms = Farm.objects.all()
    context = {'farms': farms}
    return render(request, 'crops/farm_list.html', context)


@login_required
def farm_add(request):
    """Add new farm/plot"""
    if request.method == 'POST':
        Farm.objects.create(
            name=request.POST.get('name'),
            size_acres=request.POST.get('size_acres'),
            location=request.POST.get('location', ''),
            soil_type=request.POST.get('soil_type', ''),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Farm added successfully!')
        return redirect('crops:farm_list')
    
    return render(request, 'crops/farm_form.html')


@login_required
def farm_detail(request, pk):
    """View farm details and all seasons"""
    farm = get_object_or_404(Farm, pk=pk)
    seasons = farm.seasons.all()
    
    context = {
        'farm': farm,
        'seasons': seasons,
    }
    return render(request, 'crops/farm_detail.html', context)


@login_required
def season_list(request):
    """List all crop seasons with filters"""
    status = request.GET.get('status', '')
    crop_type = request.GET.get('crop_type', '')
    
    seasons = CropSeason.objects.select_related('farm')
    
    if status:
        seasons = seasons.filter(status=status)
    if crop_type:
        seasons = seasons.filter(crop_type=crop_type)
    
    context = {
        'seasons': seasons,
        'selected_status': status,
        'selected_crop': crop_type,
    }
    return render(request, 'crops/season_list.html', context)


@login_required
def season_add(request):
    """Add new crop season"""
    if request.method == 'POST':
        season = CropSeason.objects.create(
            farm_id=request.POST.get('farm'),
            crop_type=request.POST.get('crop_type'),
            crop_variety=request.POST.get('crop_variety', ''),
            planting_date=request.POST.get('planting_date'),
            expected_harvest_date=request.POST.get('expected_harvest_date'),
            area_planted_acres=request.POST.get('area_planted_acres'),
            expected_yield_kg=request.POST.get('expected_yield_kg') or None,
            status=request.POST.get('status', 'planned'),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Crop season added!')
        return redirect('crops:season_detail', pk=season.pk)
    
    farms = Farm.objects.all()
    context = {'farms': farms}
    return render(request, 'crops/season_form.html', context)


@login_required
def season_detail(request, pk):
    """View season details with inputs and sales"""
    season = get_object_or_404(CropSeason.objects.select_related('farm'), pk=pk)
    
    inputs = season.inputs.all()
    sales = season.sales.all()
    
    # Calculate totals
    total_input_cost = inputs.aggregate(Sum('cost'))['cost__sum'] or 0
    total_revenue = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    profit = total_revenue - total_input_cost
    
    context = {
        'season': season,
        'inputs': inputs,
        'sales': sales,
        'total_input_cost': total_input_cost,
        'total_revenue': total_revenue,
        'profit': profit,
    }
    return render(request, 'crops/season_detail.html', context)


@login_required
def season_edit(request, pk):
    """Edit crop season"""
    season = get_object_or_404(CropSeason, pk=pk)
    
    if request.method == 'POST':
        season.crop_type = request.POST.get('crop_type')
        season.crop_variety = request.POST.get('crop_variety', '')
        season.planting_date = request.POST.get('planting_date')
        season.expected_harvest_date = request.POST.get('expected_harvest_date')
        season.actual_harvest_date = request.POST.get('actual_harvest_date') or None
        season.area_planted_acres = request.POST.get('area_planted_acres')
        season.expected_yield_kg = request.POST.get('expected_yield_kg') or None
        season.actual_yield_kg = request.POST.get('actual_yield_kg') or None
        season.status = request.POST.get('status')
        season.notes = request.POST.get('notes', '')
        season.save()
        
        messages.success(request, 'Season updated!')
        return redirect('crops:season_detail', pk=season.pk)
    
    farms = Farm.objects.all()
    context = {'season': season, 'farms': farms}
    return render(request, 'crops/season_form.html', context)


@login_required
def input_add(request, season_id):
    """Add crop input (fertilizer, seeds, etc.)"""
    season = get_object_or_404(CropSeason, pk=season_id)
    
    if request.method == 'POST':
        CropInput.objects.create(
            season=season,
            input_type=request.POST.get('input_type'),
            date=request.POST.get('date', date.today()),
            description=request.POST.get('description'),
            quantity=request.POST.get('quantity'),
            cost=request.POST.get('cost'),
            supplier=request.POST.get('supplier', ''),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Input recorded!')
        return redirect('crops:season_detail', pk=season.pk)
    
    context = {'season': season}
    return render(request, 'crops/input_form.html', context)


@login_required
def sale_add(request, season_id):
    """Add crop sale"""
    season = get_object_or_404(CropSeason, pk=season_id)
    
    if request.method == 'POST':
        CropSale.objects.create(
            season=season,
            date=request.POST.get('date', date.today()),
            quantity_kg=request.POST.get('quantity_kg'),
            price_per_kg=request.POST.get('price_per_kg'),
            buyer=request.POST.get('buyer', ''),
            payment_status=request.POST.get('payment_status', 'paid'),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Sale recorded!')
        return redirect('crops:season_detail', pk=season.pk)
    
    context = {'season': season}
    return render(request, 'crops/sale_form.html', context)