from django.urls import path
from . import views
from .crud_views import CategoryView

app_name = "core"

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    
    path('products/', views.product, name="product"),

    path('category/', views.category, name="category"),
    path('add-category/', CategoryView.add_category, name="add_category"),

    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
]
