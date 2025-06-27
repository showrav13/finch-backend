from django.urls import path
from .views import *

app_name = "api"

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('verify-token/', VerifyTokenView.as_view(), name='verify-token'),

    path("filter-products/", ProductListView.as_view(), name="product-list"),
    path('products/', AllProductListView.as_view(), name='all-products'),
    path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),

    path('product-reviews/<int:product_id>/', ProductReviewListView.as_view(), name='product-reviews'),

    path('category/', CategoryListView.as_view(), name='category-list'),
    path('menu-items/', MenuItemListView.as_view(), name='menu-items'),

    path('apply-cupon/', apply_cupon, name='apply-cupon'),
    path('verify-product-stock/', verify_product_stock, name='verify-product-stock'),

    path('get-company-setting/', get_company_setting, name='get-company-setting'),
    path('place-order/', place_order, name='place-order'),

    path('stripe-webhook/', stripe_webhook, name='stripe-webhook'),
    path("create-checkout-session/", CreateCheckoutSession.as_view(), name="create-checkout-session"),

    path('get-orders/', get_orders, name='get-orders'),
    path('get-order-items/<int:order_id>/', get_order_items, name='get-order-items'),
]

