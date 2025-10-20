from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render
from .models import Product
from django.db.models import Sum
import json
from django.db.models import Q
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required 






@login_required(login_url='login')
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

@login_required(login_url='login')
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



def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name").strip()
        username = request.POST.get("username")
        email = request.POST.get("email").strip()
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        terms = request.POST.get("terms")

       
        if not all([full_name, email, password, confirm_password]):
            messages.error(request, "All fields are required.")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Enter a valid email address.")
            return redirect("register")

       

        if User.objects.filter(username=username).exists():
            messages.error(request, "An account with this username already exists.")
            return redirect("register")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect("register")

        # Create user
        user = User.objects.create_user(
            
            username=username,
            email=email,
            password=password,
            first_name=full_name
        )
        user.is_active=False
        user.save()
        

        messages.success(request, "Your account has been created successfully! You can now login.")
        return redirect("login")

    return render(request, "auth/register.html")


def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username_or_email", "").strip()
        password = request.POST.get("password", "")
        remember_me = request.POST.get("remember_me")  # ✅ get checkbox value

        if not username_or_email or not password:
            messages.error(request, "Both fields are required.")
            return redirect("login")

        # Find user by email or username
        user_obj = None
        if "@" in username_or_email:
            user_obj = User.objects.filter(email=username_or_email).first()
        else:
            user_obj = User.objects.filter(username=username_or_email).first()

        if not user_obj:
            messages.error(request, "Invalid username/email or password.")
            return redirect("login")

        if not user_obj.is_active:
            messages.error(request, "Your account is inactive. Please contact support.")
            return redirect("login")

        # Authenticate user
        user = authenticate(request, username=user_obj.username, password=password)
        if user:
            login(request, user)

            # Set session expiry
            if remember_me:
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
            else:
                request.session.set_expiry(0)  # Browser close

            messages.success(request, f"Welcome back, {user.first_name}!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username/email or password.")
            return redirect("login")

    return render(request, "auth/login.html")

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')
    
