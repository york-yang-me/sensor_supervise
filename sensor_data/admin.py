from django.contrib import admin

# Register your models here.

# Register your models here.
from .models import *


class TemperatureAdmin(admin.ModelAdmin):
    list_display = ('id', 'capTime', 'capHour', 'capTemperature')


admin.site.register(Temperature, TemperatureAdmin)
