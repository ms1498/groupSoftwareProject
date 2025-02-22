from django.db import models
from django.contrib.auth.models import User
from mysite.keygen import generate_random_key

class Student(models.Model):
    user = models.OneToOneField(User)
    points = models.IntegerField()
    class Meta:
        permissions = [("sign_up", "Can sign up for events")]

class Developer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_superuser = True

class SocietyRepresentative(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    society_name = models.CharField(max_length=50)
    class Meta:
        permissions = [("create_events","Can create events")
                      ("generate_qr", "Can generate QR codes for events they are running")]

class Moderator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    class Meta:
        permissions = [("view_unapproved_events", "Can view currently unapproved events"),
                       ("approve_events", "Can approve currently unapproved events")]

class Location(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    address = models.CharField(max_length=255)

class Event(models.Model):
    startKey = models.CharField(max_length=7, default=generate_random_key(7))
    endKey = models.CharField(max_length=7, null=True, default=generate_random_key(7))
    eventType = models.CharField(max_length=50)
    organiser = models.ForeignKey(SocietyRepresentative, on_delete=models.CASCADE)
    eventDate = models.DateField()
    eventTime = models.TimeField()
    eventLocation = models.ForeignKey(Location, on_delete=models.CASCADE)
    expectedAttendance = models.IntegerField(null=True)
    actualAttendance = models.IntegerField(null=True)
    maximumAttendance = models.IntegerField(null=True)
    approved = models.BooleanField(default=False)

class Booking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)