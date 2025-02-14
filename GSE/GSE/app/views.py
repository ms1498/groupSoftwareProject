from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpRequest
from mysite.qrgen import get_qrcode_from_response

import os

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
    return render(request, "myEvents.html")

def organise(request):
    return render(request, "organise.html")

def signIn(request):
    return render(request, "signIn.html")

def signUp(request):
    return render(request, "signUp.html")

def qrgen(request:HttpRequest) -> None:
    """Accepts a GET request with a 'url' argument, that argument will be processed into a QR code and a jpeg image returned to the frontend.\n
    @param: request - HttpRequest\n
    @author: Seth Mallinson"""
    code_image = get_qrcode_from_response(request)
    if code_image != None:
        return HttpResponse(code_image, content_type="image/jpeg")
    else:
        return HttpResponse("Invalid request. The qrgen expects a GET request with a 'url' parameter.")
