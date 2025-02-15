from pathlib import Path
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest
from mysite.qrgen import get_qrcode_from_response
from .forms import SignInForm, SignUpForm


def serve_events_txt(_request: HttpRequest) -> HttpResponse:
    file_path = Path.parent("templates/events.txt")
    try:
        with file_path.open("r") as file:
            content = file.read()
        return HttpResponse(content, content_type="text/plain")
    except FileNotFoundError:
        return HttpResponse("File not found", status=404)

def index(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")

def discover(request: HttpRequest) -> HttpResponse:
    return render(request, "discover.html")

def my_events(request: HttpRequest) -> HttpResponse:
    return render(request, "my_events.html")

def organise(request: HttpRequest) -> HttpResponse:
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

def qrgen(request: HttpRequest) -> HttpResponse:
    """Accepts a GET request with a 'url' argument, that argument will be processed into a QR code and a jpeg image returned to the frontend.

    @param: request - HttpRequest
    @author: Seth Mallinson
    """
    code_image = get_qrcode_from_response(request)
    if code_image is None:
        return HttpResponse("Invalid request. The qrgen expects a GET request with a 'url' parameter.")
    return HttpResponse(code_image, content_type="image/jpeg")
