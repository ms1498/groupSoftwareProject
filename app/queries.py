import os
#django imports
from django.shortcuts import render, redirect
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.core import serializers
from django.http import HttpResponse, HttpRequest
# model imports
from app.models import Event
# backend imports
from .forms import SignInForm, SignupForm
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
    if request.method == "POST":
        try:
            event:Event = serializers.deserialize("json", str(request.body))[0]
            event.save()
        except:
            return HttpResponse("Invalid request - bad message body. A JSON definition of the event is expected. Got: " + str(request.body), status=400)
    else:
        return HttpResponse("Invalid request - should be POST", status=400)