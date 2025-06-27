from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from core.models import Product, Cupon, CuponApplied
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import generics, filters, pagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from rest_framework.generics import RetrieveAPIView

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

import stripe
import os
from dotenv import load_dotenv
from django.conf import settings

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")


if not stripe.api_key:
    raise ValueError("Stripe API key is not set. Please ensure that the STRIPE_SECRET_KEY environment variable is configured.")



User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return JsonResponse({"detail": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        authenticated_user = authenticate(request, username=user.username, password=password)  

        if authenticated_user:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            user_data = CustomUserSerializer(user).data  

            return JsonResponse({
                "access": access_token,
                "refresh": str(refresh),
                "user": user_data
            }, status=status.HTTP_200_OK)

        return JsonResponse({"detail": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

    except User.DoesNotExist:
        return JsonResponse({"detail": "Invalid email or password"}, status=status.HTTP_404_NOT_FOUND)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class VerifyTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        user_data = CustomUserSerializer(user).data  

        return JsonResponse({
            "access": access_token,
            "refresh": str(refresh),
            "user": user_data
        }, status=status.HTTP_200_OK)



# Products 
class ProductPagination(pagination.PageNumberPagination):
    page_size = 40  # Adjust page size as needed
    page_size_query_param = "page_size"
    max_page_size = 100

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "category__name"]
    ordering_fields = ["price", "created_at", "stock_quantity"]
    ordering = ["-created_at"]  # Default ordering

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        category = request.query_params.get("category")
        if category:
            queryset = queryset.filter(category__name=category)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data).data  # Get default paginated response
            response["total_pages"] = self.paginator.page.paginator.num_pages  # Add total_pages
            return Response(response)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AllProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("id")  # Order by ID to maintain order
    serializer_class = AllProductSerializer
    pagination_class = ProductPagination


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "total_pages": self.paginator.page.paginator.num_pages,
            "count": self.paginator.page.paginator.count,
            "next": self.paginator.get_next_link(),
            "previous": self.paginator.get_previous_link(),
            "results": serializer.data
        })

class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.prefetch_related("gallery").all()
    serializer_class = ProductDetailsSerializer
    lookup_field = "id" 

    def get(self, request, *args, **kwargs):
        try:
            product = self.get_object()
            serializer = self.get_serializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemListView(generics.ListAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def apply_cupon(request):
    if request.method == 'POST':
        try:
            cupon_code = request.POST.get("cupon_code")
            total_amount = request.POST.get("total_amount")
            customer = request.POST.get("customer")
            try:
                customer = User.objects.get(id=customer)
            except User.DoesNotExist:
                return JsonResponse({"error": "Customer not found"}, status=status.HTTP_400_BAD_REQUEST)
            total_amount = float(total_amount)

            print(cupon_code, total_amount, customer)

            cupon = Cupon.objects.get(code=cupon_code, is_active=True)

            if total_amount < cupon.min_order_amount:
                return JsonResponse({"error": f"Total amount is less than the minimum order amount: {cupon.min_order_amount}"}, status=status.HTTP_400_BAD_REQUEST)
            if cupon.max_usage <= CuponApplied.objects.filter(cupon=cupon, user=customer).count():
                return JsonResponse({"error": f"You have reached the maximum usage limit for this coupon"}, status=status.HTTP_400_BAD_REQUEST)
            
            new_total_amount = total_amount - (total_amount * cupon.discount / 100)

            # CuponApplied.objects.create(
            #     cupon=cupon,
            #     user=customer,
            # )
            
            return JsonResponse({"message": f"Cupon applied successfully. You got {cupon.discount}% off", "total_amount": new_total_amount}, status=status.HTTP_200_OK)
        except Cupon.DoesNotExist:
            return JsonResponse({"error": "Invalid coupon code"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return JsonResponse({"error": "Customer not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED) 

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_product_stock(request):
    if request.method != "POST":
        return JsonResponse({"valid": False, "error": "Invalid request method."}, status=405)
    
    try:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        color = data.get("color")
        color = Color.objects.get(hex_code=color)
        quantity = data.get("quantity")

        print(product_id, color, quantity)

        product = Product.objects.get(id=product_id)
        product_image = ProductImage.objects.get(product=product, color=color)
        if product_image.stock > 0 and product_image.stock >= quantity:
            return JsonResponse({"valid": True, "stock": product_image.stock}, status=200)
        elif product_image.stock > 0 and product_image.stock < quantity:
            return JsonResponse({"valid": False, "error": f"Only {product_image.stock} {product_image.color.name} {product_image.product.name} left in stock."})
        else:
            return JsonResponse({"valid": False, "error": "This color is out of stock."}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({"valid": False, "error": "Product not found."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"valid": False, "error": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"valid": False, "error": f"An unexpected error occurred: {str(e)}"}, status=500)


# def product_reviews(request, product_id):
#     print(request.user)
#     if request.method == 'GET':
#         reviews = ProductReview.objects.filter(product_id=product_id)
#         serializer = ProductReviewSerializer(reviews, many=True)
#         return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
#     elif request.method == 'POST':
#         data = json.loads(request.body)
#         data["product"] = product_id
#         serializer = ProductReviewSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save(user=request.user)
#             return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
#         return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductReviewListView(generics.ListCreateAPIView):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return []  
        return [IsAuthenticated()] 

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        return ProductReview.objects.filter(product_id=product_id)  

    def create(self, request, *args, **kwargs):
        print("Received POST Data:", request.data)  # Print all request data

        product_id = self.kwargs.get("product_id")
        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        request.data["product"] = product_id
        request.data["user"] = request.user.id

        serializer = self.get_serializer(data=request.data)

        print("Serializer Data:", serializer.initial_data)  # Print serializer data
        
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    
from setting.models import CompanySetting
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_company_setting(request):
    company_setting = CompanySetting.objects.first()
    serializer = CompanySettingSerializer(company_setting)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
# @permission_classes([AllowAny])
def place_order(request):
    if request.method != "POST":
        return JsonResponse({"valid": False, "error": "Invalid request method."}, status=405)

    data = json.loads(request.body)
    is_registered = data.get("is_registered")
    orders = data.get("orders")
    order_info = data.get("order_info")
    billing_address = data.get("billing_address")
    coupon = data.get("coupon")

    if not orders or not isinstance(orders, list):
        return JsonResponse({"valid": False, "error": "Orders must be a non-empty list."})

    if not billing_address or not isinstance(billing_address, dict):
        return JsonResponse({"valid": False, "error": "Billing address is required."})

    if is_registered:
        if not request.user.is_authenticated:
            return JsonResponse({"valid": False, "error": "User not authenticated."})
        user = request.user
    else:

        if "email" in billing_address:
            email = billing_address["email"]
            username = email.split("@")[0] 
            base_username = username
            counter = 1

            # Ensure the username is unique
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            billing_address["username"] = username

        serializer = UserRegistrationSerializer(data=billing_address)
        if serializer.is_valid():
            serializer.save()
            user = serializer.instance

            password = billing_address.get("password")
            authenticated_user = authenticate(request, username=user.username, password=password)  

            if authenticated_user:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                user_data = CustomUserSerializer(user).data  

        else:
            error_messages = [
                f"{field}: {error}" for field, errors in serializer.errors.items() for error in errors
            ]
            return JsonResponse({"valid": False, "error": error_messages})

     # Update user billing details
    user.first_name = billing_address.get("first_name", user.first_name)
    user.last_name = billing_address.get("last_name", user.last_name)
    user.phone_number = billing_address.get("phone_number", user.phone_number)
    user.street_address = billing_address.get("street_address", user.street_address)
    user.city = billing_address.get("city", user.city)
    user.state = billing_address.get("state", user.state)
    user.save()
    
    # create order and order items. Also Validate coupon, tax, discount, product price, shipping fee, total amount
    try:
        company_setting = CompanySetting.objects.first()
        tax = company_setting.tax
        shipping_fee = company_setting.shipping_fee
    except AttributeError:
        return JsonResponse({"valid": False, "error": "Company settings not found."})

    
    # validate product price
    srv_subtotal = 0
    product_instances = {}

    try:
        for order in orders:
            product = Product.objects.get(id=order.get("product_id"))
            product_instances[order.get("product_id")] = product
            srv_subtotal += product.price * order.get("quantity")
    except ObjectDoesNotExist:
        return JsonResponse({"valid": False, "error": "One or more products are invalid."})


    # validate coupon
    cupon_instance = None
    if coupon:
        try:
            cupon_instance = Cupon.objects.get(code=coupon, is_active=True)

            if srv_subtotal < cupon_instance.min_order_amount:
                return JsonResponse({"valid": False, "error": f"Total must be at least {cupon_instance.min_order_amount} for this coupon."})

            if cupon_instance.max_usage <= CuponApplied.objects.filter(cupon=cupon_instance, user=user).count():
                return JsonResponse({"valid": False, "error": "Coupon usage limit reached."})

        except Cupon.DoesNotExist:
            return JsonResponse({"valid": False, "error": "Invalid coupon code."})


    # Calculate total price
    srv_total_price = srv_subtotal - (srv_subtotal * cupon_instance.discount / 100) if cupon_instance else srv_subtotal
    discount_amount = srv_subtotal - srv_total_price
    srv_tax = srv_total_price * tax / 100
    srv_shipping_cost = shipping_fee
    srv_total_price = srv_total_price + srv_tax + srv_shipping_cost
    
    # Save order and order items in a transaction
    try:
        with transaction.atomic():
            order_info = Order.objects.create(
                user=user,
                subtotal=srv_subtotal,
                coupon=cupon_instance,
                discount=discount_amount if cupon_instance else 0,
                tax=srv_tax,
                shipping_cost=srv_shipping_cost,
                total_price=srv_total_price,
                shipping_address=order_info.get("shipping_address"),
                payment_method=order_info.get("payment_method"),
            )

            if cupon_instance:
                CuponApplied.objects.create(cupon=cupon_instance, user=user)

            for order in orders:
                product = product_instances.get(order.get("product_id"))
                if not product:
                    return JsonResponse({"valid": False, "error": f"Product {order.get('product_id')} not found."})

                try:
                    color = Color.objects.get(hex_code=order.get("color"))
                    size = Size.objects.get(name=order.get("size"))
                    product_image = ProductImage.objects.get(product=product, color=color)
                except ObjectDoesNotExist:
                    return JsonResponse({"valid": False, "error": "Invalid color, size, or product image."})

                OrderItem.objects.create(
                    order=order_info,
                    product=product,
                    quantity=order.get("quantity"),
                    color=product_image.color,
                    size=size,
                    price_at_purchase=product.price,
                )

                product_image.stock -= order.get("quantity")
                product_image.save()

                product.total_units_sold += order.get("quantity")
                product.total_revenue += product.price * order.get("quantity")
                product.total_profit += (product.price - product.cost_price) * order.get("quantity")
                product.save()

    except Exception as e:
        return JsonResponse({"valid": False, "error": f"An unexpected error occurred: {str(e)}"}, status=500)

        

    response_data = {
        "valid": True, 
        "message": f"Order placed successfully. Your order ID is {order_info.order_id}", 
        "order_id": order_info.id,
    }

    if not is_registered:
        response_data["user_info"] = {
            "user": user_data,
            "access": access_token,
            "refresh": str(refresh),
        }

    return JsonResponse(response_data, status=status.HTTP_200_OK)

    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    print(serializer.data)  # Debugging output
    return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_items(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({"valid": False, "error": "Order not found."}, status=404)
    order_items = OrderItem.objects.filter(order=order)
    serializer = OrderItemSerializer(order_items, many=True)
    print(serializer.data)
    return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)





class CreateCheckoutSession(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            order_id = request.data.get("order_id")
            if not order_id:
                return JsonResponse({"error": "Order ID is required."}, status=400)

            order = Order.objects.get(id=order_id)

            # Retrieve order items
            order_items = OrderItem.objects.filter(order=order)

            # Construct line items for Stripe
            line_items = []
            for item in order_items:
                line_items.append({
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": item.product.name,  # Assuming product has a name attribute
                        },
                        "unit_amount": int(item.price_at_purchase * 100),  # Convert to cents
                    },
                    "quantity": item.quantity,
                })

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL,
                metadata={"order_id": order_id}
            )

            order.stripe_session = session.id
            order.save()  

            return JsonResponse({"session_id": session.id, "url": session.url})

        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found."}, status=404)
        except stripe.error.StripeError as e:
            return JsonResponse({"error": str(e)}, status=400)  
        except Exception as e:
            return JsonResponse({"error": "An unexpected error occurred: " + str(e)}, status=500)


import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def stripe_webhook(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    payload = request.body.decode("utf-8")
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    logger.info(f"Received webhook: {payload}")
    logger.info(f"Signature Header: {sig_header}")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return JsonResponse({"error": "Invalid signature"}, status=400)

    logger.info(f"Webhook event type: {event['type']}")

     # Handle events
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print(f"Payment successful: {session}")

        try:
            # Attempt to find the order using the session ID
            order = Order.objects.get(stripe_session=session["id"])
            order.payment_status = "paid"  # Update the payment status
            order.payment_method = "card"
            order.save()
            print(f"Order {order.id} payment status updated to 'paid'.")
        except Order.DoesNotExist:
            print(f"Order with stripe_session {session['id']} not found.")
            return JsonResponse({"error": "Order not found"}, status=404)


    return JsonResponse({'status': 'success'}, status=200)