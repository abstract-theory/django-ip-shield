from django.db import models
from django.utils.timezone import now

class Log(models.Model):
    IpAddress = models.GenericIPAddressField()
    EventDate = models.DateTimeField(default=now)
    EventName = models.CharField(max_length=64)

class Blocked(models.Model):
    IpAddress = models.GenericIPAddressField()
    BlockDate = models.DateTimeField(default=now)
    EventName = models.CharField(max_length=64)


