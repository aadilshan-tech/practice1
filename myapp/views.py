from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, Prefetch, Exists, OuterRef
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from .models import VehicleModel, Part, PartStock


def home(request):
    """Home page with quick stats"""
    total_vehicles = VehicleModel.objects.filter(is_active=True).count()
    total_parts_in_stock = PartStock.objects.filter(quantity__gt=0).count()
    
    context = {
        'total_vehicles': total_vehicles,
        'total_parts_in_stock': total_parts_in_stock,
    }
    return render(request, 'myapp/home.html', context)


def vehicle_list(request):
    """Display all active vehicle models with available parts count"""
    vehicle_type = request.GET.get('type', '')
    manufacturer = request.GET.get('manufacturer', '')
    
    vehicles = VehicleModel.objects.filter(is_active=True).annotate(
        available_parts_count=Count(
            'parts',
            filter=Q(parts__is_active=True, parts__stock__quantity__gt=0)
        )
    )
    
    # Apply filters
    if vehicle_type:
        vehicles = vehicles.filter(vehicle_type=vehicle_type)
    if manufacturer:
        vehicles = vehicles.filter(manufacturer__icontains=manufacturer)
    
    # Get unique manufacturers for filter
    manufacturers = VehicleModel.objects.filter(is_active=True).values_list(
        'manufacturer', flat=True
    ).distinct().order_by('manufacturer')
    
    context = {
        'vehicles': vehicles,
        'manufacturers': manufacturers,
        'selected_type': vehicle_type,
        'selected_manufacturer': manufacturer,
    }
    return render(request, 'myapp/vehicles.html', context)


def parts_list(request, vehicle_slug):
    """Display all available parts for a specific vehicle model"""
    vehicle = get_object_or_404(VehicleModel, slug=vehicle_slug, is_active=True)
    
    category = request.GET.get('category', '')
    
    # Only show parts that are active and have stock > 0
    # CRITICAL: Use select_related to avoid N+1 queries
    parts = Part.objects.filter(
        vehicle_model=vehicle,
        is_active=True,
        stock__quantity__gt=0
    ).select_related('stock', 'vehicle_model').order_by('category', 'name')
    
    if category:
        parts = parts.filter(category__icontains=category)
    
    # Get unique categories for this vehicle (only for parts with stock)
    categories = Part.objects.filter(
        vehicle_model=vehicle,
        is_active=True,
        stock__quantity__gt=0
    ).values_list('category', flat=True).distinct().order_by('category')
    
    context = {
        'vehicle': vehicle,
        'parts': parts,
        'categories': categories,
        'selected_category': category,
    }
    return render(request, 'myapp/parts.html', context)


def part_detail(request, vehicle_slug, part_slug):
    """Display detailed information about a specific part"""
    vehicle = get_object_or_404(VehicleModel, slug=vehicle_slug, is_active=True)
    
    # CRITICAL FIX: Always use select_related to fetch stock in same query
    part = get_object_or_404(
        Part.objects.select_related('stock', 'vehicle_model'),
        vehicle_model=vehicle,
        slug=part_slug,
        is_active=True
    )
    
    # FIXED: Robust stock check using the model method
    stock_available = part.is_in_stock()
    stock_quantity = part.get_stock_quantity()
    
    # Debug logging (remove in production)
    print(f"DEBUG: Part={part.name}, Stock Available={stock_available}, Quantity={stock_quantity}")
    
    # If no stock, show out of stock page
    if not stock_available:
        context = {
            'part': part,
            'vehicle': vehicle,
            'stock_quantity': 0,
        }
        return render(request, 'myapp/part_not_available.html', context)
    
    # Get related parts from the same category (with stock)
    related_parts = Part.objects.filter(
        vehicle_model=vehicle,
        category=part.category,
        is_active=True,
        stock__quantity__gt=0
    ).exclude(id=part.id).select_related('stock', 'vehicle_model')[:4]
    
    context = {
        'vehicle': vehicle,
        'part': part,
        'related_parts': related_parts,
        'stock_quantity': stock_quantity,
    }
    return render(request, 'myapp/part_detail.html', context)


def search(request):
    """Search for parts across all vehicles"""
    query = request.GET.get('q', '').strip()
    results = []
    
    if query and len(query) >= 3:
        # Search in part names, categories, and vehicle models
        # CRITICAL: Use select_related to avoid N+1 queries
        results = Part.objects.filter(
            Q(name__icontains=query) |
            Q(category__icontains=query) |
            Q(part_number__icontains=query) |
            Q(vehicle_model__name__icontains=query) |
            Q(vehicle_model__manufacturer__icontains=query),
            is_active=True,
            stock__quantity__gt=0
        ).select_related('vehicle_model', 'stock').distinct()[:50]
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'myapp/search.html', context)


# AJAX endpoints for stock management
@staff_member_required
@require_POST
def increase_stock(request, stock_id):
    """AJAX view to increase stock by 1"""
    try:
        stock = get_object_or_404(PartStock, pk=stock_id)
        stock.quantity += 1
        stock.save()
        return JsonResponse({
            'success': True,
            'new_quantity': stock.quantity,
            'message': f'Increased stock for {stock.part.name}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@staff_member_required
@require_POST
def decrease_stock(request, stock_id):
    """AJAX view to decrease stock by 1"""
    try:
        stock = get_object_or_404(PartStock, pk=stock_id)
        if stock.quantity > 0:
            stock.quantity -= 1
            stock.save()
            return JsonResponse({
                'success': True,
                'new_quantity': stock.quantity,
                'message': f'Decreased stock for {stock.part.name}'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Stock is already 0'
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)