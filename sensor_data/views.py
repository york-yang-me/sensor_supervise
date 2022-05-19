from django.http import JsonResponse
from django.shortcuts import render

from sensor_data.models import Temperature
from sensor_data.serializers import TempSerializer
from rest_framework import generics


# Create your views here.
class TemperatureApi(generics.ListCreateAPIView):
    queryset = Temperature.objects.all()
    serializer_class = TempSerializer


def temperature(request):
    data = Temperature.objects.all()
    res = []
    if data:
        for i in data:
            tx = i.capHour
            ty = i.capTemperature
            res.append([tx, float(ty)])
    return render(request, 'temperature_index.html', locals())


def get_temperature(request):
    data = Temperature.objects.all()
    res = []
    if data:
        for i in data:
            tx = i.capHour
            ty = i.capTemperature
            res.append({"time": tx, "Temperature": float(ty)})
    return JsonResponse({'s1': res})
