from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField()

class Developer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class SocietyRepresentative(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    society_name = models.CharField(max_length=50)

class Moderator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Location(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    address = models.CharField(max_length=255)

class Event(models.Model):
    start_key = models.CharField(max_length=7)
    end_key = models.CharField(max_length=7, null=True)
    category = models.CharField(max_length=50)
    organiser = models.ForeignKey(SocietyRepresentative, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    expected_attendance = models.IntegerField(null=True)
    actual_attendance = models.IntegerField(null=True)
    maximum_attendance = models.IntegerField(null=True)
    approved = models.BooleanField(default=False)
    description = models.CharField(max_length=500, null=True)
    image = models.ImageField(blank=True)