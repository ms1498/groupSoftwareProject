"""Provide models to use for the database."""
from django.db import models
# pylint: disable=imported-auth-user
from django.contrib.auth.models import User, Permission
from mysite.generators import generate_random_key

class Student(models.Model):
    """Model for a Student user, who can sign up to events."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    class Meta:
        permissions = (("sign_up", "Can sign up for events"),)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        signup_perm = Permission.objects.get(codename="sign_up")
        self.user.user_permissions.add(signup_perm)

class Developer(models.Model):
    """Model for a Developer user, who can make system changes."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()

class SocietyRepresentative(models.Model):
    """Model for a Society Representative user, who can create events."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    society_name = models.CharField(max_length=50)
    class Meta:
        permissions = (
            ("create_events","Can create events"),
            ("generate_qr", "Can generate QR codes for events they are running"),
        )
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        create_perm = Permission.objects.get(codename="create_events")
        qr_perm = Permission.objects.get(codename="generate_qr")
        self.user.user_permissions.add(create_perm, qr_perm)

class Moderator(models.Model):
    """Model for a Moderator user, who can approve events."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    class Meta:
        permissions = (
            ("view_unapproved_events", "Can view currently unapproved events"),
            ("approve_events", "Can approve currently unapproved events"),
        )
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        view_perm = Permission.objects.get(codename="view_unapproved_events")
        approve_perm = Permission.objects.get(codename="approve_events")
        self.user.user_permissions.add(view_perm, approve_perm)

class Location(models.Model):
    """Model for a Location, which is a real-world site at which events can take place."""

    name = models.CharField(max_length=50, primary_key=True)
    address = models.CharField(max_length=255)

class Event(models.Model):
    """Model for an Event, which students can register for and attend."""

    start_key = models.CharField(max_length=7, default=generate_random_key)
    end_key = models.CharField(max_length=7, blank=True, default=generate_random_key)
    category = models.CharField(max_length=50)
    organiser = models.ForeignKey(SocietyRepresentative, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    expected_attendance = models.IntegerField(null=True)
    actual_attendance = models.IntegerField(null=True)
    maximum_attendance = models.IntegerField(null=True)
    approved = models.BooleanField(default=False)
    description = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to="event_images/", null=True, blank=True)

class Booking(models.Model):
    """Model for a Booking, which stores that a student has booked to attend an event."""

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    def update_expected_attendance(self):
        """Update the expected_attendance field of the linked event."""
        bookings = Booking.objects.all()
        bookings = bookings.filter(event=self.event)
        self.event.expected_attendance = bookings.count()
        self.event.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_expected_attendance()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.update_expected_attendance()
