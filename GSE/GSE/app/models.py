from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User)
    points = models.IntegerField()

class Developer(models.Model):
    user = models.OneToOneField(User)

class SocietyRepresentative(models.Model):
    user = models.OneToOneField(User)
    societyName = models.CharField(max_length=50)

class Moderator(models.Model):
    user = models.OneToOneField(User)

class Event(models.Model):
    eventType = models.CharField(max_length=50)
    organiser = models.ForeignKey(SocietyRepresentative, on_delete=models.CASCADE)
    eventDate = models.DateField()
    eventTime = models.TimeField()
    eventLocation = models.ForeignKey(Location, on_delete=models.CASCADE)
    expectedAttendance = models.IntegerField(null=True)
    actualAttendance = models.IntegerField(null=True)
    maximumAttendance = models.IntegerField(null=True)

class Location(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    address = models.CharField(max_length=255)