from django.http import JsonResponse
from django.shortcuts import render

from sensor_data.models import DHT11Data
from sensor_data.serializers import DHT11DataSerializer
from rest_framework import generics


# Create your views here.
class DHT11Api(generics.ListCreateAPIView):
    queryset = DHT11Data.objects.all()
    serializer_class = DHT11DataSerializer


def dht11_data(request):
    data = DHT11Data.objects.all()
    res = []
    if data:
        for i in data:
            tx = i.capHour
            ty_1 = i.capTemperature
            ty_2 = i.capHumidity
            res.append([tx, float(ty_1), float(ty_2)])
    return render(request, 'dht11_index.html', locals())


def get_dht11_data(request):
    data = DHT11Data.objects.all()
    res = []
    if data:
        for i in data:
            tx = i.capHour
            ty_1 = i.capTemperature
            ty_2 = i.capHumidity
            res.append({"time": tx, "temperature": float(ty_1), "humidity": float(ty_2)})
    return JsonResponse({'res': res})


# def del_dht11_data(request):
#     data = DHT11Data.objects.get()
#     res = []
#     if data:
#         for i in data:
#             tx = i.capHour
#             ty_1 = i.capTemperature
#             ty_2 = i.capHumidity
#             res.append({"time": tx, "temperature": float(ty_1), "humidity": float(ty_2)})
#     return JsonResponse({'res': res})
