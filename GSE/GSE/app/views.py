from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse


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
