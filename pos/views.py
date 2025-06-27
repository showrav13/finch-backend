from django.shortcuts import render, get_object_or_404
from core.models import *
from django.core.paginator import Paginator
from django.http import JsonResponse
from pos.models import POS, PAYMENT_METHOD, POSItem

import json
from decimal import Decimal

from django.db import transaction, IntegrityError



from setting.models import CompanySetting

# Create your views here.
def pos(request):
    # Get all categories and customers
    categories = Category.objects.all()
    customers = User.objects.filter(role='customer')

    # Handle the AJAX request
    if request.method == "POST":
        category_filter = request.POST.get('category', '')
        customer_filter = request.POST.get('customer', '')
        search_query = request.POST.get('search', '')

        # Filter products based on category, customer, and search query
        products = Product.objects.all().order_by('-id')

        if category_filter:
            products = products.filter(category__id=category_filter)
        # if customer_filter:
        #     products = products.filter(customer__id=customer_filter)
        # if search_query:
        #     products = products.filter(name__icontains=search_query)

        if search_query:
            products = products.filter(models.Q(name__icontains=search_query) | models.Q(sku__icontains=search_query))


        # Paginate filtered products (12 per page)
        paginator = Paginator(products, 4)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Prepare data for the response
        product_data = []
        for product in page_obj:

            product_images = ProductImage.objects.filter(product=product)
            colors = [
                {'color_name': image.color.name, 'color_hex': image.color.hex_code, 'image_url': image.image.url}
                for image in product_images if image.color
            ]
            sizes = [size.name for size in product.size.all()]

            product_data.append({
                'id': product.id,
                'name': product.name,
                'category': product.category.name,
                'price': product.price,
                'stock_quantity': product.stock_quantity,
                'image_url': product.image.url,
                'colors': colors,
                'sizes': sizes,
                'sku'  : product.sku
            })

        # Return the filtered products and pagination data in JSON format
        return JsonResponse({
            'products': product_data,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'num_pages': page_obj.paginator.num_pages,
            'current_page': page_obj.number,
        })



    # Default rendering (no AJAX request)
    products = Product.objects.all().order_by('-id')
    paginator = Paginator(products, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    company_setting = CompanySetting.objects.first()
    payment_methods = PAYMENT_METHOD

    # Prepare products and their default images for rendering
    default_product_data = []
    for product in page_obj:
        # Fetch all ProductImages related to the product
        product_images = ProductImage.objects.filter(product=product)
        colors = [
            {'color_name': image.color.name, 'color_hex': image.color.hex_code, 'image_url': image.image.url}
            for image in product_images if image.color
        ]
        sizes = [size.name for size in product.size.all()]

        default_product_data.append({
            'id': product.id,
            'name': product.name,
            'category': product.category.name,
            'price': product.price,
            'stock_quantity': product.stock_quantity,
            'image': product.image,  # Default image for product
            'colors': colors,  # List of colors and their corresponding images
            'sizes': sizes,
            'sku': product.sku
        })

    context = {
        'products': default_product_data,
        'page_obj': page_obj, 
        'categories': categories,
        'customers': customers,
        'company_setting': company_setting,
        'payment_methods': payment_methods,
    }
    return render(request, 'pos.html', context)



from django.core.exceptions import ObjectDoesNotExist


def verify_product_color_size(request):
    if request.method != "POST":
        return JsonResponse({"valid": False, "error": "Invalid request method."}, status=405)

    try:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        color = data.get("color")
        size = data.get("size")

        if not product_id or not color or not size:
            return JsonResponse({"valid": False, "error": "Missing required fields."}, status=400)

        product = Product.objects.get(id=product_id)

        valid_color_combination = ProductImage.objects.filter(
            product=product,
            color__hex_code=color,
            stock__gt=0
        ).exists()

        valid_size_combination = product.size.filter(name=size).exists()

        if valid_color_combination and valid_size_combination:
            return JsonResponse({"valid": True})

        if not valid_color_combination and not valid_size_combination:
            error_message = "Invalid color and size combination."
        elif not valid_color_combination:
            error_message = "Invalid color combination."
        else:
            error_message = "Invalid size combination."

        return JsonResponse({"valid": False, "error": error_message}, status=400)

    except ObjectDoesNotExist:
        return JsonResponse({"valid": False, "error": "Product not found."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"valid": False, "error": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"valid": False, "error": f"An unexpected error occurred: {str(e)}"}, status=500)

# verify product stock through product image
def verify_product_stock(request):
    if request.method != "POST":
        return JsonResponse({"valid": False, "error": "Invalid request method."}, status=405)
    
    try:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        color = data.get("color")
        color = Color.objects.get(hex_code=color)

        product = Product.objects.get(id=product_id)
        product_image = ProductImage.objects.get(product=product, color=color)
        if product_image.stock > 0:
            return JsonResponse({"valid": True, "stock": product_image.stock})
        else:
            return JsonResponse({"valid": False, "error": "Product is out of stock."}, status=400)
    except ObjectDoesNotExist:
        return JsonResponse({"valid": False, "error": "Product not found."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"valid": False, "error": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"valid": False, "error": f"An unexpected error occurred: {str(e)}"}, status=500)


def checkout(request):
    if request.method != "POST":
        return JsonResponse({"valid": False, "error": "Invalid request method."}, status=405)

    try:
        data = json.loads(request.body)
        customer_get = data.get("customer")
        total_paid = data.get("totalPaid")
        payment_method = data.get("paymentMethod")
        note = data.get("note")
        cart = data.get("cart")

        if not cart:
            return JsonResponse({"valid": False, "error": "Cart is empty."}, status=400)

        # Fetch customer if provided
        customer = None
        if customer_get:
            try:
                customer = User.objects.get(id=customer_get)
            except ObjectDoesNotExist:
                # return JsonResponse({"valid": False, "error": "Customer not found."}, status=400)
                pass

        # Get tax from company settings
        company_settings = CompanySetting.objects.first()
        tax = company_settings.tax if company_settings else 0

        # Calculate subtotal and total
        subtotal = 0
        for item in cart:
            try:
                product = Product.objects.get(id=item.get("id"))
            except ObjectDoesNotExist:
                return JsonResponse({"valid": False, "error": f"Product with ID {item.get('id')} not found."}, status=400)

            subtotal += product.price * item.get("quantity", 0)

        tax_amount = (subtotal * tax) / 100
        total = subtotal + tax_amount
        due = Decimal(str(total)) - Decimal(str(total_paid or 0))

        if due < 0:
            due = 0

        with transaction.atomic():  # Ensures all database operations happen together
            pos = POS.objects.create(
                user=customer,
                total_amount=total,
                sub_total=subtotal,
                due_amount=due,
                tax=tax,
                discount=0,
                payment_method=payment_method,
                notes=note
            )

            for item in cart:
                try:
                    product = Product.objects.get(id=item.get("id"))
                    color = Color.objects.get(hex_code=item.get("color"))
                    size = Size.objects.get(name=item.get("size"))
                except ObjectDoesNotExist:
                    return JsonResponse({"valid": False, "error": "Invalid product, color, or size."}, status=400)

                POSItem.objects.create(
                    pos=pos,
                    product=product,
                    quantity=item.get("quantity"),
                    sale_price=product.price,
                    discount=0,
                    total_price=product.price * item.get("quantity"),
                    color=color,
                    size=size
                )

            # Decrease product stock
            for item in cart:
                try:
                    product = Product.objects.get(id=item.get("id"))
                    color = Color.objects.get(hex_code=item.get("color"))
                    product_image = ProductImage.objects.get(product=product, color=color)

                    if product_image.stock < item.get("quantity"):
                        return JsonResponse(
                            {"valid": False, "error": f"Insufficient stock for {product.name} ({color.hex_code})."},
                            status=400
                        )

                    product_image.stock -= item.get("quantity")
                    product_image.save()

                    product.total_units_sold += item.get("quantity")
                    product.total_revenue += product.price * item.get("quantity")
                    product.total_profit += (product.price - product.cost_price) * item.get("quantity")
                    product.save()

                except ObjectDoesNotExist:
                    return JsonResponse({"valid": False, "error": "Product or color not found."}, status=400)

        return JsonResponse({"valid": True, "pos_id": pos.id})

    except json.JSONDecodeError:
        return JsonResponse({"valid": False, "error": "Invalid JSON format."}, status=400)
    except IntegrityError:
        return JsonResponse({"valid": False, "error": "Database integrity error. Possible stock constraint issue."}, status=400)
    except Exception as e:
        return JsonResponse({"valid": False, "error": str(e)}, status=500)


def invoice(request, pos_id):
    # handle error for pos_id not found 
    try:
        pos = POS.objects.get(id=pos_id)
        company_setting = CompanySetting.objects.first()
    except ObjectDoesNotExist:
        return render(request, '404.html')
    return render(request, 'invoice.html', {"pos": pos, "company": company_setting})

def page_404(request):
    return render(request, '404.html')