from django.contrib import admin
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget
from django.db import models
from django.contrib.auth.admin import UserAdmin
from .models import *
import json

# Register your models here.
@admin.register(CompanySetting)
class CompanySettingAdmin(ModelAdmin):
    list_display = ("name", "address_line_1", "address_line_2", "phone", "email")
    search_fields = ("name",)
