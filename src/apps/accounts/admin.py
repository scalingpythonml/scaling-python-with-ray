# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.forms import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "full_name")
    ordering = ("email",)
