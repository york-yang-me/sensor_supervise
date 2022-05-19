from rest_framework import serializers
from sensor_data.models import Temperature


class TempSerializer(serializers.ModelSerializer):
    class Meta:
        model = Temperature
        fields = ['capTime', 'capHour', 'capTemperature']
