from django.urls import path

from sensor_data import views

urlpatterns = [
    path('', views.dht11_data, name='sensor_data.dht11_data'),
    path('dht11_api', views.DHT11Api.as_view(), name='sensor_data.dht11_api'),
    path('get_dht11_data', views.get_dht11_data, name='sensor_data.get_dht11_data'),
]