from django.urls import path

from sensor_data import views

urlpatterns = [
    path('', views.temperature, name='sensor_data.temperature'),
    path('temperature_api', views.TemperatureApi.as_view(), name='sensor_data.temperature_api'),
    path('get_temperature', views.get_temperature, name='sensor_data.get_temperature'),
]