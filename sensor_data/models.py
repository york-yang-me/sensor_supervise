from django.db import models


# Create your models here.
class DHT11Data(models.Model):
    capTime = models.DateTimeField(auto_now_add=False)
    capHour = models.IntegerField(default=0)
    capTemperature = models.CharField(max_length=10)
    capHumidity = models.CharField(max_length=10)

    def __str__(self):
        return self.capTemperature, self.capHumidity
