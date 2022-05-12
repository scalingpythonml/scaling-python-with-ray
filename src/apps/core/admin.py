from django.contrib import admin

# Register your models here.
from apps.core.models import BlockedNumber, Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("serial_number", "used")


@admin.register(BlockedNumber)
class BlockedNumbersAdmin(admin.ModelAdmin):
    list_display = ("number",)
