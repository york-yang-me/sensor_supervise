from django.contrib import admin

# Register your models here.

# Register your models here.
from .models import *


class DHT11DataAdmin(admin.ModelAdmin):
    list_display = ('id', 'capTime', 'capHour', 'capTemperature', 'capHumidity')


admin.site.register(DHT11Data, DHT11DataAdmin)
