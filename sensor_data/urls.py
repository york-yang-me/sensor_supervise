from django.conf.urls import url
from sensor_data import views

urlpatterns = [
    url(r'^$', views.temperature, name='sensor_data.temperature'),
    url(r'^temperature_api', views.TemperatureApi.as_view(), name='sensor_data.temperature_api'),
    url(r'^get_temperature', views.get_temperature, name='sensor_data.get_temperature'),
]