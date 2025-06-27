from django.urls import path
from .views import *

app_name = "pos"

urlpatterns = [
    path('', pos, name='pos'),
    path('verify_product_size_color/', verify_product_color_size, name='verify_product_color_size'),
    path('verify_product_stock/', verify_product_stock, name='verify_product_stock'),
    path('checkout/', checkout, name='checkout'),
    path('invoice/<int:pos_id>/', invoice, name='invoice'),
]

