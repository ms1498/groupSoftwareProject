from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField()

class Developer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class SocietyRepresentative(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    societyName = models.CharField(max_length=50)

class Moderator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Location(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    address = models.CharField(max_length=255)

class Event(models.Model):
    startKey = models.CharField(max_length=7)
    endKey = models.CharField(max_length=7, null=True)
    eventType = models.CharField(max_length=50)
    organiser = models.ForeignKey(SocietyRepresentative, on_delete=models.CASCADE)
    eventDate = models.DateField()
    eventTime = models.TimeField()
    eventLocation = models.ForeignKey(Location, on_delete=models.CASCADE)
    expectedAttendance = models.IntegerField(null=True)
    actualAttendance = models.IntegerField(null=True)
    maximumAttendance = models.IntegerField(null=True)
    approved = models.BooleanField(default=False)