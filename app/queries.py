import os
import json
#django imports
from django.shortcuts import render, redirect
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, User
from django.core import serializers
from django.http import HttpResponse, HttpRequest
# model imports
from app.models import Event, Location, SocietyRepresentative
# backend imports
from .forms import SignInForm, SignUpForm
from mysite.qrgen import get_qrcode_from_response


def serve_events(request:HttpRequest) -> HttpResponse:
    if request.method == "GET":
        data = serializers.serialize("json", Event.objects.all())
        file_path = os.path.join(os.path.dirname(__file__), 'templates', 'events.txt')
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return HttpResponse(content, content_type="text/plain")
        except FileNotFoundError:
            return HttpResponse("File not found", status=404)
    else:
        return HttpResponse("Invalid request - should be GET", status=400)
    
def submit_event(request:HttpRequest) -> HttpResponse:
    """Include a json description of the event in the request body and it will be saved to the database."""
    if User.objects.count() == 0:
        user:User = User.objects.create_user(username="temp", email="temp@temp.temp", password="temp")
    if SocietyRepresentative.objects.count() == 0:
        rep:SocietyRepresentative = SocietyRepresentative()
        rep.user = User.objects.get(username="temp")
        rep.societyName = "john society"
        rep.save()
    if Location.objects.count() == 0:
        location:Location = Location()
        location.name = "aaaaa"
        location.address = "woooooo"
        location.save()

    if request.method == "POST":
        try:
            data = json.loads(str(request.body)[2:-1])
            event:Event = Event()
            event.start_key = data["startKey"]
            event.end_key = data["endKey"]
            event.event_type = data["eventType"]
            event.organiser = SocietyRepresentative.objects.filter(user=User.objects.get(username="temp"))[0]
            event.event_date = data["eventDate"]
            event.event_time = data["eventTime"]
            event.event_location = Location.objects.filter(name=data["eventLocation"])[0]
            event.expected_attendance = data["expectedAttendance"]
            event.actual_attendance = data["actualAttendance"]
            event.maximum_attendance = data["actualAttendance"]
            event.approved = data["approved"]
            event.save()
            return HttpResponse(status=200)
        except:
            return HttpResponse("Invalid request - bad message body. A JSON definition of the event is expected. Got: " + str(request.body)[2:-1], status=400)
    else:
        return HttpResponse("Invalid request - should be POST", status=400)