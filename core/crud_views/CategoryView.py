from django.shortcuts import render, get_object_or_404, redirect
from ..decorators import *
from ..models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify

@admin_required
def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        slug = slugify(name)
        description = request.POST.get("description")
        logo = request.FILES.get("logo")

        if not name:
            messages.error(request, "Name field is required.")
            return redirect("core:category") 

        Category.objects.create(name=name, slug=slug, description=description, logo=logo)
        messages.success(request, "Category added successfully!")
    return redirect("core:category") 


def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    return JsonResponse({
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "logo_url": category.logo.url if category.logo else ""
    })

def update_category(request, category_id):
    if request.method == "POST":
        category = get_object_or_404(Category, id=category_id)
        name = request.POST.get("name")
        description = request.POST.get("description")
        logo = request.FILES.get("logo")

        if name:
            category.name = name
            category.slug = slugify(name)
            category.description = description
            if logo:
                category.logo = logo
            category.save()
            return JsonResponse({"status": "success", "message": "Category updated successfully!"})

        return JsonResponse({"status": "error", "message": "Name field is required."})

    return JsonResponse({"status": "error", "message": "Invalid request method."})

def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return JsonResponse({"status": "success", "message": "Category deleted successfully!"})
