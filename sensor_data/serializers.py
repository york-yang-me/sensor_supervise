from rest_framework import serializers
from sensor_data.models import DHT11Data


class DHT11DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DHT11Data
        fields = ['capTime', 'capHour', 'capTemperature', 'capHumidity']
