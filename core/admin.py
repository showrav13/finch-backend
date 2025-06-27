from django.contrib.auth.models import User
from django.contrib import admin
# admin.site.unregister(User)

from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget
from django.db import models
from django.contrib.auth.admin import UserAdmin
from .models import *
import json

from django.utils.html import format_html
from django import forms
from django.contrib.auth.forms import UserCreationForm



class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'style': 'color: #c9cdd3; background-color: #111827; width: 100%; text-align: left; font-weight: normal; border-radius: 5px; padding: 8px; border: 1px solid #374151;',
            'class': 'unfold-input'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'style': 'color: #c9cdd3; background-color: #111827; width: 100%; text-align: left; font-weight: normal; border-radius: 5px; padding: 8px; border: 1px solid #374151;',
            'class': 'unfold-input'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'style': 'color: #c9cdd3; background-color: #111827; width: 100%; text-align: left; font-weight: normal; border-radius: 5px; padding: 8px; border: 1px solid #374151;',
                'class': 'unfold-input'
            }),
            'email': forms.EmailInput(attrs={
                'style': 'color: #c9cdd3; background-color: #111827; width: 100%; text-align: left; font-weight: normal; border-radius: 5px; padding: 8px; border: 1px solid #374151;',
                'class': 'unfold-input'
            })
        }

@admin.register(User)
class CustomUserAdmin(ModelAdmin, UserAdmin):
    add_form = CustomUserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_verified', 'role')
    list_filter = ('is_staff', 'is_active', 'role')
    search_fields = ('username', 'email')
    ordering = ('username',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'street_address', 'city', 'state')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def get_queryset(self, request):
        """Ensure only the default view shows all users."""
        return super().get_queryset(request)

@admin.register(MenuItem)
class MenuItemAdmin(ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "parent")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget()},
    }

@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Size)
class SizeAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Color)
class ColorAdmin(ModelAdmin):
    list_display = ('name', 'hex_code')
    search_fields = ('name', 'hex_code')
    ordering = ('name',)

# @admin.register(Product)
# class ProductAdmin(ModelAdmin):
#     list_display = ("name", "price", "stock_quantity", "category", "brand", "discounted_price")
#     list_filter = ("category", "brand", "created_at")
#     search_fields = ("name", "slug", "barcode")
#     prepopulated_fields = {"slug": ("name",)}
#     formfield_overrides = {
#         models.JSONField: {"widget": ArrayWidget()},
#         models.TextField: {"widget": WysiwygWidget()},
#     }

# @admin.register(ProductVariant)
# class ProductVariantAdmin(ModelAdmin):
#     list_display = ("product", "name", "value")
#     search_fields = ("product__name", "name", "value")

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = '__all__'
        widgets = {
            'stock': forms.NumberInput(attrs={
                'style': 'color: #c9cdd3; background-color: #111827; width: 70px; text-align: center; font-weight: bold; border-radius: 5px; padding: 5px; border: 1px solid #ccc;'
            }),
            'color': forms.Select(attrs={
                'style': 'color: #c9cdd3; background-color: #111827; width: auto; text-align: center; font-weight: bold; border-radius: 5px; padding: 5px; border: 1px solid #ccc;'
            }),
        }
    
    def clean_color(self):
        color = self.cleaned_data.get('color')
        if not color:
            raise forms.ValidationError("This field is required.")
        return color


# # Inline admin for ProductImage
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    form = ProductImageForm
    fields = ('image', 'image_preview', 'color', 'stock',)  
    readonly_fields = ('image_preview',) 
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;"/>', obj.image.url)
        return "No Image"

    image_preview.short_description = "Preview"

from django.forms.widgets import CheckboxSelectMultiple
from django_select2.forms import Select2MultipleWidget  # Use Select2 for multi-select dropdown



class ProductAdmin(ModelAdmin):
    list_display = ('name', 'price', 'sku', 'is_featured', 'stock_quantity', 'category', 'created_at')
    search_fields = ('name', 'sku', 'barcode', 'category__name')
    list_filter = ('category', 'created_at')

    readonly_fields = ('total_units_sold', 'total_revenue', 'total_profit', 'created_at', 'updated_at', 'total_views')

    inlines = [ProductImageInline]

    def get_fieldsets(self, request, obj=None):
        """ Exclude 'barcode' and 'sku' fields when adding a new product. """
        if obj is None:  # If adding a new product
            return (
                (None, {
                    'fields': ('name', 'slug', 'description', 'is_featured')
                }),
                ('Sales & Inventory', {
                    'fields': (
                        ('cost_price', 'price', 'discount'),  # Pricing fields
                        ('stock_quantity', 'total_views'),    # Current status
                        ('total_units_sold', 'total_revenue'),  # Sales metrics
                        ('total_profit',),  # Financial outcome
                    ),
                    'classes': ('collapse',),
                    'description': 'Product pricing, inventory, and performance metrics'
                }),
                ('SEO', {
                    'fields': ('seo_title', 'seo_description', 'seo_keywords')
                }),
                ('Relations', {
                    'fields': ('category', 'tags', 'size')
                }),
                ('Media', {
                    'fields': ('image',)
                }),
            )
        return (
                (None, {
                    'fields': ('name', 'slug', 'description', 'is_featured')
                }),
                ('Sales & Inventory', {
                    'fields': (
                        ('cost_price', 'price', 'discount'),  # Pricing fields
                        ('stock_quantity', 'total_views'),    # Current status
                        ('total_units_sold', 'total_revenue'),  # Sales metrics
                        ('total_profit',),  # Financial outcome
                    ),
                    'classes': ('collapse',),
                    'description': 'Product pricing, inventory, and performance metrics'
                }),
                ('SEO', {
                    'fields': ('seo_title', 'seo_description', 'seo_keywords')
                }),
                ('Barcode', {
                    'fields': ('sku','barcode')
                }),
                ('Relations', {
                    'fields': ('category', 'tags', 'size')
                }),
                ('Media', {
                    'fields': ('image',)
                }),
            ) 

    formfield_overrides = {
        models.TextField: {'widget': WysiwygWidget},  
        models.JSONField: {'widget': ArrayWidget},   
    }



    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """ Override the default widget for many-to-many fields with custom styling. """
        if db_field.name == 'size' or db_field.name == 'tags':  
            kwargs['widget'] = Select2MultipleWidget(attrs={
                'data-placeholder': 'Select sizes',
                'style': 'background-color: #000000; color: #ffffff; border-radius: 6px; padding: 5px;'  # Dark bg, light text
            })
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    
    class Media:
        css = {
            'all': ('custom_admin/style.css',)  # Load custom CSS
        }


admin.site.register(Product, ProductAdmin)


@admin.register(ProductReview)
class ProductReviewAdmin(ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    search_fields = ("product__name", "user__username")
    



# admin.site.register(ProductImage)


# @admin.register(ProductImage)
# class ProductImageAdmin(ModelAdmin):
#     list_display = ("product", "image", "alt_text")
#     search_fields = ("product__name", "alt_text")



# @admin.register(Wishlist)
# class WishlistAdmin(ModelAdmin):
#     list_display = ("user", "product", "created_at")
#     search_fields = ("user__username", "product__name")

# @admin.register(Cart)
# class CartAdmin(ModelAdmin):
#     list_display = ("user", "created_at")
#     search_fields = ("user__username",)

# @admin.register(CartItem)
# class CartItemAdmin(ModelAdmin):
#     list_display = ("cart", "product", "quantity", "total_price")
#     search_fields = ("cart__user__username", "product__name")



class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = '__all__'
        widgets = {
            'product': forms.Select(attrs={'style': 'color: #c9cdd3; background-color: #111827; width: auto; text-align: center; font-weight: bold; border-radius: 5px; padding: 5px; border: 1px solid #ccc;'}),
            'quantity': forms.NumberInput(attrs={'style': 'color: #c9cdd3; background-color: #111827; width: 50px; text-align: center; font-weight: bold; border-radius: 5px; padding: 5px; border: 1px solid #ccc;'}),
            'color': forms.Select(attrs={'style': 'color: #c9cdd3; background-color: #111827; width: auto; text-align: center; font-weight: bold; border-radius: 5px; padding: 5px; border: 1px solid #ccc;'}),
            'size': forms.Select(attrs={'style': 'color: #c9cdd3; background-color: #111827; width: 80px; text-align: center; font-weight: bold; border-radius: 5px; padding: 5px; border: 1px solid #ccc;'}),
            'price_at_purchase': forms.NumberInput(attrs={'style': 'color: #c9cdd3; background-color: #111827; width: 100px; text-align: center; font-weight: bold; border-radius: 5px; padding: 5px; border: 1px solid #ccc;'}),
        }

class OrderItemInline(admin.TabularInline):  
    model = OrderItem
    extra = 0  
    readonly_fields = ('product', "quantity", 'color', 'size', 'price_at_purchase')
    can_delete = False 
    can_add = False  
    form = OrderItemForm
@admin.register(Order)
class OrderAdmin(ModelAdmin):  # Using Unfold's ModelAdmin
    list_display = ("user", "order_id", "order_status", "total_price", "payment_status", "created_at")
    list_filter = ("order_status", "payment_status", "created_at")
    search_fields = ("user__username", "order_id")
    inlines = [OrderItemInline]  # Add the inline here

# @admin.register(OrderItem)
# class OrderItemAdmin(ModelAdmin):
#     list_display = ("order", "product", "quantity", "price_at_purchase", "total_price")
#     search_fields = ("order__user__username", "product__name")




# @admin.register(Invoice)
# class InvoiceAdmin(ModelAdmin):
#     list_display = ("invoice_number", "order", "issued_date", "due_date")
#     search_fields = ("invoice_number", "order__user__username")

# @admin.register(ProductAnalytics)
# class ProductAnalyticsAdmin(ModelAdmin):
#     list_display = ("product", "views", "purchases")
#     search_fields = ("product__name",)


@admin.register(Cupon)
class CuponAdmin(ModelAdmin):
    list_display = ("code", "discount", "is_active", "created_at", "updated_at")
    search_fields = ("code",)


# @admin.register(CuponApplied)
# class CuponAppliedAdmin(ModelAdmin):
#     list_display = ("user", "cupon", "created_at")
#     search_fields = ("user__username", "cupon__code")



@admin.register(VisitorSession)
class VisitorSessionAdmin(ModelAdmin):
    list_display = ("ip_address", "country", "session_key")
    search_fields = ("ip_address", "country", "session_key")


def order_badge_callback(request):
    return Order.objects.count() 

