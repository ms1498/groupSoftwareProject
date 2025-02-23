from django.db import models
from django.contrib.auth.models import User
from mysite.keygen import generate_random_key

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    class Meta:
        permissions = [("sign_up", "Can sign up for events")]

class Developer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_superuser = True
    class Meta:
        permissions = [("create_events","Can create events"),
                      ("generate_qr", "Can generate QR codes for events they are running")]

class SocietyRepresentative(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    society_name = models.CharField(max_length=50)
    class Meta:
        permissions = [("create_events","Can create events"),
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
    start_key = models.CharField(max_length=7, default=generate_random_key)
    end_key = models.CharField(max_length=7, null=True, default=generate_random_key)
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
    image = models.ImageField(upload_to="event_images/", null=True, blank=True)

class Booking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
