from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

import os
<<<<<<< Updated upstream
=======

def serve_events_txt(request):
    file_path = os.path.join(os.path.dirname(__file__), 'templates', 'events.txt')
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return HttpResponse(content, content_type="text/plain")
    except FileNotFoundError:
        return HttpResponse("File not found", status=404)
>>>>>>> Stashed changes

def serve_events_txt(request):
    file_path = os.path.join(os.path.dirname(__file__), 'templates', 'events.txt')
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return HttpResponse(content, content_type="text/plain")
    except FileNotFoundError:
        return HttpResponse("File not found", status=404)
    
def index(request):
    return render(request, "home.html")

def discover(request):
    return render(request, "discover.html")

def myEvents(request):
    return render(request, "my-events.html")

def organise(request):
    return render(request, "organise.html")

def signIn(request):
    return render(request, "sign-in.html")

def signUp(request):
    return render(request, "sign-up.html")
