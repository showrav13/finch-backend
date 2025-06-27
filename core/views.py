from django.shortcuts import render, get_object_or_404, redirect
from .decorators import admin_required, sales_rep_required, customer_required, staff_required
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse

from pos.models import POS

from django.db.models import Sum, Count


# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin() or request.user.is_sales_rep():
            return redirect('core:dashboard')
        elif request.user.is_customer():
            return redirect('core:login')  # Assuming you have a customer dashboard


    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                next_url = request.GET.get('next', None)
                if next_url:
                    return redirect(next_url)
                
                if user.is_admin() or user.is_sales_rep():
                    return redirect('core:dashboard')
                elif user.is_customer():
                    return redirect('core:login')
                
    return render(request, 'account/login.html')

def logout_view(request):
    logout(request)
    return redirect('core:login')

def custom_admin_dashboard(request):
    return render(request, 'custom_admin_dashboard.html')

@staff_required
def dashboard(request):
    # total orders
    total_orders = Order.objects.all().count()
    pending_orders = Order.objects.filter(order_status='pending').count()
    confirmed_orders = Order.objects.filter(order_status='confirmed').count()
    
    # total customers
    total_customers = User.objects.filter(role='customer').count()
    # total products
    total_products = Product.objects.all().count()
    # total categories
    total_categories = Category.objects.all().count()   
    # sum of total pos sales
    total_pos_sales = POS.objects.all().aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    # sum of total ecommerce sale
    total_ecom_sales = Order.objects.all().aggregate(Sum('total_price'))['total_price__sum'] or 0
    # active coupons
    active_coupons = Cupon.objects.filter(is_active=True).count()
    #total revenue 
    total_revenue = Product.objects.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0
    #total profit
    total_profit = Product.objects.aggregate(Sum('total_profit'))['total_profit__sum'] or 0
    #total due
    total_due = POS.objects.all().aggregate(Sum('due_amount'))['due_amount__sum'] or 0

    recent_orders = Order.objects.all().order_by('-id')[:5]
    recent_pos_sales = POS.objects.all().order_by('-id')[:5]

    top_products = Product.objects.all().order_by('-total_views')[:7]

    # visitors group by country
    visitor_country = VisitorSession.objects.values('country').annotate(count=Count('country')).order_by('-count')[:7]

    # stock alert products
    stock_alert_products = Product.objects.filter(stock_quantity__lte=20)    

    context = {
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_products': total_products,
        'total_categories': total_categories,
        'total_pos_sales': total_pos_sales,
        'total_ecom_sales': total_ecom_sales,
        'active_coupons': active_coupons,
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'total_due': total_due,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,

        'recent_orders': recent_orders,
        'recent_pos_sales': recent_pos_sales,

        'top_products': top_products,
        'visitor_country': visitor_country,

        'stock_alert_products': stock_alert_products,
    }



    return render(request, 'dashboard.html', context) 

def product(request):
    return render(request, 'product.html')

def category(request):
    category_list = Category.objects.all().order_by('-id')
    paginator = Paginator(category_list, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'category.html', {'page_obj': page_obj})
