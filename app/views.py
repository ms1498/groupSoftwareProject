import os
#django imports
from pathlib import Path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import Group
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.core import serializers
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.decorators import login_required
# model imports
from app.models import Event, Booking, Student
# backend imports
from .forms import SignInForm, SignUpForm, BookingForm
from mysite.qrgen import get_qrcode_from_response
from .forms import SignInForm, SignUpForm, CreateEventForm

import os

def index(request: HttpRequest) -> HttpResponse:
    events = Event.objects.all()
    return render(request, "home.html", {"events":events})


def discover(request: HttpRequest) -> HttpResponse:
    """Filters events based on user input

    @author  Tilly Searle
    """
    search_query = request.GET.get("search_query", "")
    event_date = request.GET.get("event_date", "")
    category = request.GET.get("category", "")
    society = request.GET.get("society", "")

    events = Event.objects.all()

    if search_query:
        events = events.filter(name__icontains=search_query)

    events = events.filter(approved="1")
    if category:
        events = events.filter(category=category)

    if event_date:
        events = events.filter(date__date=event_date)

    if category:
        events = events.filter(category=category)

    if society:
        events = events.filter(organiser__society_name=society)

    return render(request, "discover.html", {"events": events})


@login_required
def register_event(request, event_id):
    """ Adds events to the booking table for the logged-in student.

    @author Tilly Searle
    """
    # Get the event
    event = get_object_or_404(Event, id=event_id)
    student = get_object_or_404(Student, user=request.user)
    Booking.objects.create(student=student, event=event)

    events = Event.objects.all()
    events = events.filter(approved="1")

    return render(request, "discover.html", {"events": events})  


def my_events(request: HttpRequest) -> HttpResponse:
    return render(request, "my_events.html")


def organise(request: HttpRequest) -> HttpResponse:
    """Take data from the event creation form, and uses it to create and save an event.

    @author    Tricia Sibley
    """
    if request.method == "POST":
        form = CreateEventForm(request.POST, request.FILES)
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
    return redirect("home")

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

def password_reset(request: HttpRequest) -> HttpResponse:
    """Takes the user's email, sending them a link to a reset password form webpage.
    @param     user's email
    @return    email sent to the user if the email is found within the system.
    @author    Maisie Marks
    """
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                from_email=None,
                email_template_name='password_reset_email.html',
                subject_template_name='password_reset_subject.txt',
            )
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset_form.html', {'form': form})

def password_reset_done(request: HttpRequest) -> HttpResponse:
    """Page to show that an email request has been sent
    @author    Maisie Marks
    """
    return render(request, 'password_reset_done.html')

def password_reset_confirm(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    """Takes the necessary url made by token and base64 to create a password reset link form.
    @param     new password inputs to confirm password reset.
    @return    password successfully reset if new password meets requirements.
    @author    Maisie Marks
    """
    return PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html')(request, uidb64=uidb64, token=token)

def password_reset_complete(request: HttpRequest) -> HttpResponse:
    return render(request, 'password_reset_complete.html')