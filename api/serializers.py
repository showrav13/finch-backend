# serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from core.models import *

User = get_user_model()


# User Authentication and authrorizaiton

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'phone_number', 'street_address', 'city', 'state')

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number', ''),
            street_address=validated_data.get('street_address', ''),
            city=validated_data.get('city', ''),
            state=validated_data.get('state', ''),
        )   
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role  
        return token

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role', 'phone_number', 'street_address', 'city', 'state', 'is_active', 'is_verified']


# Products

class ProductSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(source="id", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    currency = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "_id", "name", "slug", "is_featured", "price", 
            "stock_quantity",
            "category_name", 'currency', "image", "created_at"
        ]

    def get_currency(self, obj):
        return "$"

class AllProductSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(source="id", read_only=True)
    category_name = serializers.CharField(source="category.name")
    currency = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            "_id", "name", "slug", "is_featured", "price", 
            "stock_quantity",
            "category_name", 'currency', "image", "created_at"
        ]
    
    def get_currency(self, obj):
        return "$"
    
    def get_images(self, obj):
        return [obj.image.url] if obj.image else []  # Assuming a single main image, modify if multiple

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["id", "name", "hex_code"]

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ["id", "name"]

class ProductDetailsSerializer(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name") 
    size = SizeSerializer(many=True, read_only=True) 
    gallery = ProductImageSerializer(many=True, read_only=True)
    colors = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "is_featured",
            "price",
            "discount",
            "discounted_price",
            "barcode",
            "stock_quantity",
            "stock_status",
            "size",
            "colors",
            "category_name",
            "seo_title",
            "seo_description",
            "seo_keywords",
            "category",
            "tags",
            'currency',
            "image", 
            "gallery", 
            "created_at",
            "updated_at",
        ]
    def get_currency(self, obj):
        return "$"
    
    def get_colors(self, obj):
        """
        Extracts unique colors from related ProductImage objects.
        """
        colors = set()
        for image in obj.gallery.all():  # Ensure gallery is correctly related
            if image.color:  # Check if color exists (if ForeignKey)
                colors.add((image.color.id, image.color.name, image.color.hex_code, image.image.url))
        
        return [{"id": c[0], "name": c[1], "hex_code": c[2], 'image': c[3]} for c in colors]


# Menu item
class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "logo", "parent", "description"]


class CuponAppliedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuponApplied
        fields = "__all__"

from setting.models import CompanySetting

class CompanySettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySetting
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name")
    color_name = serializers.CharField(source="color.name")
    size_name = serializers.CharField(source="size.name")

    class Meta:
        model = OrderItem
        fields = "__all__"  

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"

class ProductReviewSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()  # Add a custom field for username

    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'username', 'rating', 'review', 'created_at']  # Use 'username' instead of 'user'

    def get_username(self, obj):
        return obj.user.username if obj.user else None  # Return the username of the user
    
    def create(self, validated_data):
        request = self.context.get('request')
        review = ProductReview.objects.create(
            user=request.user,
            **validated_data
        )
        return review