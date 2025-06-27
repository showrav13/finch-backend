from django.contrib import admin
from core.models import Category, Tag, Size, Color, Product, ProductReview, ProductImage
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget
from django.db import models
from django.contrib.auth.admin import UserAdmin
from .models import *
import json
from django.utils.html import format_html
from django import forms

# class CustomAdminMixin:
#     def get_model_perms(self, request):
#         """
#         Ensures that the model appears under the custom app label `product_management`
#         in Django Admin.
#         """
#         return super().get_model_perms(request)

#     def has_module_permission(self, request):
#         """
#         Override the module name to `product_management` in the admin panel.
#         """
#         return True

#     @property
#     def app_label(self):
#         return "product_management"

# @admin.register(Category)
# class CategoryAdmin(CustomAdminMixin, ModelAdmin):
#     list_display = ("name", "slug", "parent")
#     search_fields = ("name", "slug")
#     prepopulated_fields = {"slug": ("name",)}
#     formfield_overrides = {
#         models.TextField: {"widget": WysiwygWidget()},
#     }

# @admin.register(Tag)
# class TagAdmin(CustomAdminMixin, ModelAdmin):
#     list_display = ("name", "slug")
#     search_fields = ("name", "slug")
#     prepopulated_fields = {"slug": ("name",)}

# @admin.register(Size)
# class SizeAdmin(CustomAdminMixin, ModelAdmin):
#     list_display = ('name',)
#     search_fields = ('name',)
#     ordering = ('name',)

# @admin.register(Color)
# class ColorAdmin(ModelAdmin):
#     list_display = ('name', 'hex_code')
#     search_fields = ('name', 'hex_code')
#     ordering = ('name',)


# class ProductImageForm(forms.ModelForm):
#     class Meta:
#         model = ProductImage
#         fields = '__all__'
#         widgets = {
#             'stock': forms.NumberInput(attrs={
#                 'style': 'color: #c9cdd3; background-color: #111827; width: 70px; text-align: center; font-weight: bold; border-radius: 5px; padding: 5px; border: 1px solid #ccc;'
#             }),
#             'color': forms.Select(attrs={
#                 'style': 'color: #c9cdd3; background-color: #111827; width: auto; text-align: center; font-weight: bold; border-radius: 5px; padding: 5px; border: 1px solid #ccc;'
#             })
#         }
    
#     def clean_color(self):
#         color = self.cleaned_data.get('color')
#         if not color:
#             raise forms.ValidationError("This field is required.")
#         return color


# # Inline admin for ProductImage
# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 0
#     form = ProductImageForm
#     fields = ('image', 'image_preview', 'color', 'stock',)  
#     readonly_fields = ('image_preview',) 
    

#     def image_preview(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;"/>', obj.image.url)
#         return "No Image"

#     image_preview.short_description = "Preview"


# class ProductAdmin(ModelAdmin):
#     list_display = ('name', 'price', 'sku', 'is_featured', 'stock_quantity', 'category', 'created_at')
#     search_fields = ('name', 'sku', 'barcode', 'category__name')
#     list_filter = ('category', 'created_at')

#     readonly_fields = ('total_units_sold', 'total_revenue', 'total_profit', 'created_at', 'updated_at', 'total_views')

#     inlines = [ProductImageInline]

#     def get_fieldsets(self, request, obj=None):
#         """ Exclude 'barcode' and 'sku' fields when adding a new product. """
#         if obj is None:  # If adding a new product
#             return (
#                 (None, {
#                     'fields': ('name', 'slug', 'description', 'is_featured')
#                 }),
#                 ('Sales & Inventory', {
#                     'fields': (
#                         ('cost_price', 'price', 'discount'),  # Pricing fields
#                         ('stock_quantity', 'total_views'),    # Current status
#                         ('total_units_sold', 'total_revenue'),  # Sales metrics
#                         ('total_profit',),  # Financial outcome
#                     ),
#                     'classes': ('collapse',),
#                     'description': 'Product pricing, inventory, and performance metrics'
#                 }),
#                 ('SEO', {
#                     'fields': ('seo_title', 'seo_description', 'seo_keywords')
#                 }),
#                 ('Relations', {
#                     'fields': ('category', 'tags', 'size')
#                 }),
#                 ('Media', {
#                     'fields': ('image',)
#                 }),
#             )
#         return (
#                 (None, {
#                     'fields': ('name', 'slug', 'description', 'is_featured')
#                 }),
#                 ('Sales & Inventory', {
#                     'fields': (
#                         ('cost_price', 'price', 'discount'),  # Pricing fields
#                         ('stock_quantity', 'total_views'),    # Current status
#                         ('total_units_sold', 'total_revenue'),  # Sales metrics
#                         ('total_profit',),  # Financial outcome
#                     ),
#                     'classes': ('collapse',),
#                     'description': 'Product pricing, inventory, and performance metrics'
#                 }),
#                 ('SEO', {
#                     'fields': ('seo_title', 'seo_description', 'seo_keywords')
#                 }),
#                 ('Barcode', {
#                     'fields': ('sku','barcode')
#                 }),
#                 ('Relations', {
#                     'fields': ('category', 'tags', 'size')
#                 }),
#                 ('Media', {
#                     'fields': ('image',)
#                 }),
#             ) 

#     formfield_overrides = {
#         models.TextField: {'widget': WysiwygWidget},  
#         models.JSONField: {'widget': ArrayWidget},   
#     }

# admin.site.register(Product, ProductAdmin)


# @admin.register(ProductReview)
# class ProductReviewAdmin(ModelAdmin):
#     list_display = ("product", "user", "rating", "created_at")
#     search_fields = ("product__name", "user__username")