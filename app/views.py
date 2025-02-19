import os
#django imports
from pathlib import Path
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.core import serializers
from django.http import HttpResponse, HttpRequest
# model imports
from app.models import Event
# backend imports
from .forms import SignInForm, SignUpForm
from mysite.qrgen import get_qrcode_from_response
from .forms import SignInForm, SignUpForm, CreateEventForm

import os

def index(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")

def discover(request: HttpRequest) -> HttpResponse:
    return render(request, "discover.html")

def my_events(request: HttpRequest) -> HttpResponse:
    return render(request, "my_events.html")

def organise(request: HttpRequest) -> HttpResponse:
    """Take data from the event creation form, and uses it to create and save an event.

    @author    Tricia Sibley
    """
    if request.method == "POST":
        form = CreateEventForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            return render(request, "organise.html", {"form": form, "errors": form.errors})
    else:
        form = CreateEventForm()
    return render(request, "organise.html")

# Authentication section
def sign_in(request: HttpRequest) -> HttpResponse:
    """Takes the username and password and validates whether it matches a user in the system, if so it logs them in.

    @param     user's request
    @return    renders home + session logged in if successful, keeps rendering sign-in page if unsuccessful
    @author    Maisie Marks
    """
    if request.method == "POST":
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is None:
                return render(request, "sign_in.html", {"form": form, "error": "Invalid username or password"})
            login(request, user)
            return redirect("home")
    else:
        form = SignInForm()
    return render(request, "sign_in.html", {"form": form})

def sign_out(request: HttpRequest) -> HttpResponse:
    """Logs the user out of the current session and redirects them to the homepage.

    @param     user's request
    @return    renders homepage
    @author    Maisie Marks
    """
    logout(request)
    return redirect("/app")

def sign_up(request: HttpRequest) -> HttpResponse:
    """Allows the user to sign-up and make an account on the webpage.

    @param     user's request
    @return    renders the sign-up page (showing currently logged in user), adding an account to the system.
    @author    Maisie Marks
    """
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name="student")
            user.groups.add(group)
            login(request, user)
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "sign_up.html", {"form": form})

