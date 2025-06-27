from django.contrib import admin
from .models import POS, POSItem

from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget
from django.db import models
from django.contrib.auth.admin import UserAdmin
from .models import *
import json

# Register your models here.
@admin.register(POS)
class POSAdmin(ModelAdmin):
    list_display = ("sale_date", "total_amount", "due_amount", "tax", "net_total", "status")
    list_filter = ("payment_method", "sale_date")
    search_fields = ("sale_date",)

@admin.register(POSItem)
class POSItemAdmin(ModelAdmin):
    list_display = ("pos", "product", "quantity", "sale_price", "discount", "total_price")
    search_fields = ("product__name",)