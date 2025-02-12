from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpRequest

from mysite.qrgen import get_qrcode_from_response


def index(request:HttpRequest):
    return render(request, "home.html")

def qrgen(request:HttpRequest):
    """Accepts a GET request with a 'url' argument, that argument will be processed into a QR code and a jpeg image returned to the frontend."""
    code_image = get_qrcode_from_response(request)
    if code_image != None:
        return HttpResponse(code_image, content_type="image/jpeg")
    else:
        return HttpResponse("Invalid request. The qrgen expects a GET request with a 'url' parameter.")