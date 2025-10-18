
from django.shortcuts import render
from .models import Product
from django.db.models import Sum
import json
from django.db.models import Q

def home(request):
    products = Product.objects.all().order_by('-date')
    
    # Calculate statistics for the template
    total_products = products.count()
    low_stock_count = products.filter(remaining__lte=10).count()
    out_of_stock_count = products.filter(remaining=0).count()
    total_value = products.aggregate(total=Sum('total_price'))['total'] or 0
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(mrr_number__icontains=search_query)
        )
    
    # Handle sorting
    sort_by = request.GET.get('sort', '-date')
    valid_sort_fields = [
        'product_name', '-product_name', 
        'date', '-date', 
        'total_received', '-total_received', 
        'distributed', '-distributed',
        'remaining', '-remaining',
        'unit_price', '-unit_price',
        'total_price', '-total_price'
    ]
    
    if sort_by in valid_sort_fields:
        products = products.order_by(sort_by)
    
    # Handle filtering
    filter_by = request.GET.get('filter', 'all')
    if filter_by == 'low_stock':
        products = products.filter(remaining__lte=10)
    elif filter_by == 'out_of_stock':
        products = products.filter(remaining=0)
    
    context = {
        'products': products,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'total_value': total_value,
        'search_query': search_query,
        'sort_by': sort_by,
        'filter_by': filter_by,
    }
    return render(request, 'store/home.html', context)


def dashboard(request):
    products = Product.objects.all()

    total_received = products.aggregate(Sum('total_received'))['total_received__sum'] or 0
    total_distributed = products.aggregate(Sum('distributed'))['distributed__sum'] or 0
    total_remaining = products.aggregate(Sum('remaining'))['remaining__sum'] or 0
    total_value = products.aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Convert to JSON strings for JS
    product_names = json.dumps(list(products.values_list('product_name', flat=True)))
    remaining_data = json.dumps(list(products.values_list('remaining', flat=True)))
    distributed_data = json.dumps(list(products.values_list('distributed', flat=True)))

    context = {
        'products': products,
        'total_received': total_received,
        'total_distributed': total_distributed,
        'total_remaining': total_remaining,
        'total_value': total_value,
        'product_names': product_names,
        'remaining_data': remaining_data,
        'distributed_data': distributed_data,
    }
    return render(request, 'dashboard.html', context)

