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




def index(request):
    return render(request, "home.html")

def discover(request):
    return render(request, "discover.html")

def my_events(request):
    return render(request, "my-events.html")

def submit_event(request:HttpRequest):
    response = render(request, "submit-event.html")
    response["X-Content-Type-Options"] = "nosniff"
    return response

def organise(request):
    return render(request, "organise.html")

# Authentication section
def sign_in(request):
    """
     Takes the username and password and validates whether it matches a user in the system, if so it logs them in.
     @param     user's request
     @return    renders home + session logged in if successful, keeps rendering sign-in page if unsuccessful 
     @author    Maisie Marks
    """
    if request.method == "POST":
        form = SignInForm(request.POST)
        if form.is_valid() == True:
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user != None:
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'sign-in.html', {'form': form, 'error': 'Invalid username or password'})
    else:
        form = SignInForm()
    return render(request, 'sign-in.html', {'form': form})

def sign_out(request):
    """
     Logs the user out of the current session and redirects them to the homepage.
     @param     user's request
     @return    renders homepage
     @author    Maisie Marks
    """
    logout(request)
    return redirect('/app')

def sign_up(request):
    """
     Allows the user to sign-up and make an account on the webpage.
     @param     user's request
     @return    renders the sign-up page (showing currently logged in user), adding an account to the system.
     @author    Maisie Marks
    """
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid() == True :
            user = form.save()
            group = Group.objects.get(name='student')
            user.groups.add(group)      
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'sign-up.html', {'form': form})

def qrgen(request:HttpRequest) -> None:
    """Accepts a GET request with a 'url' argument, that argument will be processed into a QR code and a jpeg image returned to the frontend.\n
    @param: request - HttpRequest\n
    @author: Seth Mallinson"""
    code_image = get_qrcode_from_response(request)
    if code_image != None:
        return HttpResponse(code_image, content_type="image/jpeg")
    else:
        return HttpResponse("Invalid request. The qrgen expects a GET request with a 'url' parameter.")
