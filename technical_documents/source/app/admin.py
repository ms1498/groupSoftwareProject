"""Configures the admin interface, registering models."""
from django.contrib import admin
from .models import Booking, SocietyRepresentative, Student, Developer, Moderator
from .models import Location, Event, Badge, Award

# registering models
admin.site.register(Booking)
admin.site.register(Student)
admin.site.register(Developer)
admin.site.register(SocietyRepresentative)
admin.site.register(Moderator)
admin.site.register(Location)
admin.site.register(Event)
admin.site.register(Badge)
admin.site.register(Award)
