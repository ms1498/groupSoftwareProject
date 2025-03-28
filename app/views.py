"""Views used to display content to the user based on their request."""
from datetime import datetime, timedelta
#django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.models import User # pylint: disable=imported-auth-user
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
# model imports
from app.models import Event, Booking, Student, SocietyRepresentative, Location, Badge, Award
# backend imports
from mysite.generators import get_qrcode_from_response
from mysite.algorithms import (
    get_event_search_priority,
    process_qrcode_scan, delete_account,
    apply_awards_after_attendance
)
from .forms import SignInForm, SignUpForm, CreateEventForm, UpdateEventForm, DeleteAccountForm

def index(request: HttpRequest) -> HttpResponse:
    """Display the home page."""
    qrcode_info = process_qrcode_scan(request)
    if qrcode_info and qrcode_info[0]:
        apply_awards_after_attendance(request)
    ordered_events = Event.objects.all().order_by("date")
    date_now = timezone.now().date()
    events = ordered_events.filter(approved="1",  date__date__gte=date_now)[:3]
    categories = [
        ["🤝", "End Poverty"],
        ["🌾", "End Hunger"],
        ["⚕️", "Good Health"],
        ["🎓", "Quality Education"],
        ["⚕️", "Gender Equality"],
        ["🚰", "Clean Water and Sanitation"],
        ["⚡", "Clean Energy"],
        ["📈", "Economic Growth"],
        ["⚖️", "Reducing Inequalities"],
        ["🏙️", "Sustainable Cities and Communities"],
        ["♻️", "Responsible Consumption"],
        ["🌍", "Protect the Planet"],
        ["☮️", "Peace and Justice"]
    ]
    return render(request, "home.html", {
        "events": events,
        "categories": categories,
        "qrcode_info":qrcode_info
    })

def discover(request: HttpRequest) -> HttpResponse:
    """Filter events based on user input.

    @author Tilly Searle
    @author Seth Mallinson
    """
    search_query = request.GET.get("search_query", "").lower()
    event_date = request.GET.get("event_date", "")
    category = request.GET.get("category", "")
    society = request.GET.get("society", "")

    society_rep = SocietyRepresentative.objects.all()
    events = Event.objects.all()
    events = events.filter(approved="1",  date__date__gte=timezone.now().date())

    #region Event filtering
    # Filter out events explicitly excluded by the user
    if category:
        events = events.filter(category=category)

    if event_date:
        events = events.filter(date__date=event_date)

    if society:
        society_obj = society_rep.filter(society_name=society).first()
        events = events.filter(organiser=society_obj)

    # Filter and sort by user search query - events will be removed if they have no relation to
    # the search, and remainders will be ordered by priority - a full name match is higher priority
    # than one word of the query matching for example.
    if search_query:
        # Temporary function to bind search query to the priority calculation
        def sorter(event: Event) -> int:
            return get_event_search_priority(event, search_query)

        # Filter out events with a priority of 0 (no relation to query)
        events = [event for event in events if sorter(event) > 0]

        # Sort remaining events
        events.sort(key=sorter, reverse=True)

    booked_events = set()
    can_be_unbooked = set()
    if request.user.is_authenticated and Student.objects.filter(user=request.user).exists():
        student = get_object_or_404(Student, user=request.user)
        filtered_bookings = Booking.objects.filter(student=student)
        current_time = timezone.make_aware(datetime.now(), timezone.get_current_timezone())
        can_be_unbooked = set(
            booking.event for booking in list(filtered_bookings)
            if current_time < booking.event.date - timedelta(minutes=5)
        )
        booked_events = set(filtered_bookings.values_list("event_id", flat=True))

    return render(request, "discover.html", {
        "events": events,
        "booked_events": booked_events,
        "can_be_unbooked": can_be_unbooked,
        "societies": society_rep,
    })

def discover_shortcut(request: HttpRequest, event_id: int) -> HttpResponse:
    """Take the user straight to discover page with the chosen event open.

    @author  Maisie Marks
    """
    events = Event.objects.all()
    events = events.filter(approved="1", date__date__gte=timezone.now().date())
    event = get_object_or_404(Event, id=event_id)
    society_rep = SocietyRepresentative.objects.all()

    search_query = event.name.lower()
    event_date = event.date
    category = event.category
    society = event.organiser.society_name

    #region Event filtering
    # Filter out events explicitly excluded by the user
    if category:
        events = events.filter(category=category)

    if event_date:
        events = events.filter(date__date=event_date)

    if society:
        events = events.filter(organiser=society_rep.filter(society_name=society).first())

    # Filter and sort by user search query - events will be removed if they have no relation to
    # the search, and remainders will be ordered by priority - a full name match is higher priority
    # than one word of the query matching for example.
    if search_query:
        # Temporary function to bind search query to the priority calculation
        def sorter(event: Event) -> int:
            return get_event_search_priority(event, search_query)

        # Filter out events with a priority of 0 (no relation to query)
        events = [event for event in events if sorter(event) > 0]

        # Sort remaining events
        events.sort(key=sorter, reverse=True)

    booked_events = set()
    can_be_unbooked = set()
    if request.user.is_authenticated and Student.objects.filter(user=request.user).exists():
        student = get_object_or_404(Student, user=request.user)
        filtered_bookings = Booking.objects.filter(student=student)
        current_time = timezone.make_aware(datetime.now(), timezone.get_current_timezone())
        can_be_unbooked = set(
            booking.event for booking in list(filtered_bookings)
            if current_time < booking.event.date - timedelta(minutes=5)
        )
        booked_events = set(filtered_bookings.values_list("event_id", flat=True))
    return render(request, "discover.html", {
        "events": events,
        "booked_events": booked_events,
        "can_be_unbooked": can_be_unbooked,
        "societys": society_rep,
    })

def category_shortcut(request: HttpRequest, category: str) -> HttpResponse:
    """Take the user straight to discover page with the chosen category.

    @author  Maisie Marks
    """
    # Get all currently approved events and their organisers
    events = Event.objects.all()
    events = events.filter(approved="1", date__date__gte=timezone.now().date())
    society_rep = SocietyRepresentative.objects.all()

    # Filter events by category type
    if category:
        events = events.filter(category=category)

    # Fetching user bookings to be rendered
    booked_events = set()
    if request.user.is_authenticated:
        try:
            student = Student.objects.get(user=request.user)
            filtered_bookings = Booking.objects.filter(student=student)
            booked_events = set(filtered_bookings.values_list("event_id", flat=True))
        except Student.DoesNotExist:
            pass
    return render(request, "discover.html", {
        "events": events,
        "booked_events": booked_events,
        "societys": society_rep,
    })

@login_required
def register_event(request: HttpRequest, event_id: int) -> HttpResponse:
    """Add an event to the booking table for the logged-in student.

    Only perform the booking if the event is not already booked.

    @author Tilly Searle
    """
    # Get the event - if it is not approved, do not allow the booking to take place
    event = get_object_or_404(Event, id=event_id)
    if not event.approved:
        return HttpResponse(status=403)
    # Get the student
    student = get_object_or_404(Student, user=request.user)

    # Check if the booking already exists
    if not Booking.objects.filter(student=student, event=event).exists():
        Booking.objects.create(student=student, event=event)
    return redirect("discover")

@login_required
def unregister_event(request: HttpRequest, event_id: int) -> HttpResponse:
    """Remove an event from the booking table for the logged-in student.

    Only perform the booking if the event is already booked.

    @author Maisie Marks
    """
    # Get the event
    event = get_object_or_404(Event, id=event_id)
    if not event.approved:
        return HttpResponse(status=403)
    # Get the student
    student = get_object_or_404(Student, user=request.user)
    # Check if the booking exists to be deleted
    bookings = Booking.objects.filter(student=student, event=event)
    if bookings.exists():
        for booking in bookings:
            booking.delete()
    return redirect("discover")

@login_required
@permission_required("app.approve_events", raise_exception=True)
def approval_page(request: HttpRequest) -> HttpResponse:
    """Show a list of unnapproved events.

    @author  Tilly Searle
    """
    events = Event.objects.all()
    events = events.filter(approved="0", rejected="0")

    return render(request, "approval.html", {"events": events})

@login_required
@permission_required("app.approve_events", raise_exception=True)
def approve_event(request: HttpRequest, event_id: int) -> HttpResponse:
    """Approve an event.

    Only moderators may approve events.

    @author Tilly Searle
    """
    # Get the event
    event = get_object_or_404(Event, id=event_id)

    event.approved = "1"
    event.save()
    events = Event.objects.filter(approved="0", rejected="0")

    return render(request, "approval.html", {"events": events})

@login_required
@permission_required("app.approve_events", raise_exception=True)
def reject_event(request: HttpRequest, event_id: int) -> HttpResponse:
    """Approve an event.

    Only moderators may approve events.

    @author Tilly Searle
    """
    # Get the event
    event = get_object_or_404(Event, id=event_id)

    event.rejected = "1"
    event.save()
    events = Event.objects.filter(approved="0", rejected="0")

    return render(request, "approval.html", {"events": events})

@login_required
@permission_required("app.create_events", raise_exception=True)
def organise(request: HttpRequest) -> HttpResponse:
    """Display a page for creating events.

    @author    Tricia Sibley
    """
    locations = Location.objects.all()  # Fetch locations for dropdown

    if request.method == "POST":
        form = CreateEventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)  # Prevent immediate saving
            event.organiser = get_object_or_404(SocietyRepresentative, user=request.user)

            # Ensure location exists before using it
            location_name = request.POST.get("location")
            event.location = get_object_or_404(Location, name=location_name)

            event.approved = False  # Auto-approve event
            event.rejected = False  # Auto-reject event
            event.expected_attendance = 0
            event.actual_attendance = 0
            event.save()

            return redirect("organise")  # Redirect to organise page
    else:
        form = CreateEventForm()

    user_society_rep = get_object_or_404(SocietyRepresentative, user=request.user).society_name
    potential_organisers = SocietyRepresentative.objects.filter(society_name=user_society_rep)
    valid_events = Event.objects.filter(organiser__in=potential_organisers)

    return render(request, "organise.html", {"form": form,
                                             "events": valid_events,
                                             "locations": locations})

@login_required
@permission_required("app.create_events", raise_exception=True)
def event_analytics(request: HttpRequest, event_id: int) -> HttpResponse:
    """Display a page for viewing event analytics.

    @author    Tilly Searle
    """
    user_society_rep = get_object_or_404(SocietyRepresentative, user=request.user)
    # Find all the organisers with the same society as the requesting user, and filter the events
    # we display to only include ones submitted by any of them.
    potential_organisers = list(
        SocietyRepresentative.objects.filter(society_name=user_society_rep.society_name)
    )

    # Fetch all locations for the dropdown
    locations = Location.objects.all()

    events = list(Event.objects.all())
    valid_events: list[Event] = []
    for event_iterator in events:
        if event_iterator.organiser in potential_organisers:
            valid_events.append(event_iterator)

    # Get the event requested, if it is in the valid events.
    event = [x for x in valid_events if x.organiser in potential_organisers and x.id == event_id]
    if len(event) == 0:
        raise PermissionDenied("You do not have permissions to access an event with the given ID.")
    event = event[0]

    return render(
        request, "events_analytics.html", {
        "locations": locations,
        "event": event,
        "events": valid_events,
    })


def edit_event(request: HttpRequest, event_id: int) -> HttpResponse:
    """Display a page for editing events.

    @author    Tilly Searle
    """
    user_society_rep = get_object_or_404(SocietyRepresentative, user=request.user)
    # Find all the organisers with the same society as the requesting user, and filter the events
    # we display to only include ones submitted by any of them.
    potential_organisers = list(
        SocietyRepresentative.objects.filter(society_name=user_society_rep.society_name)
    )

    # Fetch all locations for the dropdown
    locations = Location.objects.all()

    events = list(Event.objects.all())
    valid_events: list[Event] = []
    for event_iterator in events:
        if event_iterator.organiser in potential_organisers:
            valid_events.append(event_iterator)

    # Get the event requested, if it is in the valid events.
    event = [x for x in valid_events if x.organiser in potential_organisers and x.id == event_id]
    if len(event) == 0:
        raise PermissionDenied("You do not have permissions to access an event with the given ID.")
    event = event[0]
    # If the request method is POST, process the form data
    if request.method == "POST":
        form = UpdateEventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            event.approved = False
            event.save()
            return redirect("organise")
        print("Form errors:", form.errors)
        return render(request, "edit_event.html", {
            "form": form,
            "errors": form.errors,
            "locations": locations,
            "event": event,
            "events": valid_events,
        })
    form = UpdateEventForm(instance=event)
    return render(request, "edit_event.html", {
        "form": form,
        "locations": locations,
        "event": event,
        "events": valid_events,
    })

#region Authentication
def sign_in(request: HttpRequest) -> HttpResponse:
    """Take the username and password and check whether it matches a user in the system.

    If the match is successful, log in the user specified by the username.
    @param     user's request
    @return    renders home if successful, keeps rendering sign-in page if unsuccessful
    @author    Maisie Marks
    """
    if request.method == "POST":
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is None:
                return render(request, "sign_in.html", {
                    "form": form,
                    "error": "Invalid username or password",
                })
            login(request, user)
            if request.GET:
                next_page = request.GET.get("next", "home")
                return redirect(next_page)
            return redirect("home")
    else:
        form = SignInForm()
    return render(request, "sign_in.html", {"form": form})

def terms_and_conditions(request: HttpRequest) -> HttpResponse:
    """Allows users to look at the terms and conditions.

    @param     user's request
    @return    renders homepage
    @author    Tilly Searle
    """
    return render(request, "terms_and_conditions.html")

def sign_out(request: HttpRequest) -> HttpResponse:
    """Log the user out of the current session and redirect them to the homepage.

    @param     user's request
    @return    renders homepage
    @author    Maisie Marks
    """
    logout(request)
    return redirect("home")

def sign_in_as_another(request: HttpRequest) -> HttpResponse:
    """Log the user out of the current session and redirect them to the homepage.

    @param     user's request
    @return    renders homepage
    @author    Tilly Searle
    """
    logout(request)
    return redirect("sign-in")

def sign_up(request: HttpRequest) -> HttpResponse:
    """Allow the user to sign-up and make an account on the webpage.

    @param     user's request
    @return    render the sign-up page (showing current user), create an account.
    @author    Maisie Marks
    """
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Student.objects.create(user=user)
            login(request, user)
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "sign_up.html", {"form": form})

def password_reset(request: HttpRequest) -> HttpResponse:
    """Take the user's email and send them a link to a reset password form webpage.

    @param     user's email
    @return    email sent to the user if the email is found within the system.
    @author    Maisie Marks
    """
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                from_email=None,
                email_template_name="password_reset_email.html",
                subject_template_name="password_reset_subject.txt",
            )
            return redirect("password_reset_done")
    else:
        form = PasswordResetForm()
    return render(request, "password_reset_form.html", {"form": form})

def password_reset_done(request: HttpRequest) -> HttpResponse:
    """Display a page to show that an email request has been sent.

    @author    Maisie Marks
    """
    return render(request, "password_reset_done.html")

def password_reset_confirm(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    """Take the url made by token and base64 to create a password reset link form.

    @param     new password inputs to confirm password reset.
    @return    password successfully reset if new password meets requirements.
    @author    Maisie Marks
    """
    view = PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html")
    return view(request, uidb64=uidb64, token=token)

def password_reset_complete(request: HttpRequest) -> HttpResponse:
    """Take the url made by token and base64 to create a password reset link form.

    @return    the page that shows the user that the reset was successful.
    @author    Maisie Marks
    """
    return render(request, "password_reset_complete.html")

@login_required
def delete_account_confirm(request: HttpRequest) -> HttpResponse:
    """A confirmation page for deleting the user's account.
    @param     user's request
    @return    either re-renders the page with an error, or redirects to the home page
    @author    Seth Mallinson
    """
    if request.method == "POST":
        form = DeleteAccountForm(request.POST)
        if form.is_valid():
            # sign the user out, and then delete their account.
            user = request.user
            logout(request)
            delete_account(user)
            return redirect("home")
        errors = form.errors["__all__"]
        return render(request, "delete_account.html", {
            "form": DeleteAccountForm(),
            "errors": errors
        })
    return render(request, "delete_account.html", {"form": DeleteAccountForm(), "errors": {}})
#endregion

def generate_qr(request: HttpRequest) -> HttpResponse:
    """Generate a QR code from a given request.

    @return    An HTTP response containing the QR code.
    @author    Tilly Searle
    """
    # Get the QR code image data from the request
    qr_code_data = get_qrcode_from_response(request)

    if qr_code_data is None:
        return HttpResponse("Invalid request", status=400)

    # Return the QR code as an image in the HTTP response
    return HttpResponse(qr_code_data, content_type="image/jpeg")

def my_events(request: HttpRequest) -> HttpResponse:
    """Show the user's list of booked events.

    @author  Ruaidhrigh Plummer
    """
    if request.user.is_authenticated:
        try:
            student = Student.objects.get(user=request.user)
            bookings = Booking.objects.filter(student=student).order_by("event__date")
        except Student.DoesNotExist:
            bookings = Booking.objects.none()
    else:
        bookings = Booking.objects.none()

    return render(request, "my_events.html", {"bookings": bookings})

@login_required
def badge_list(request: HttpRequest) -> HttpResponse:
    """Show a list of all badges a user has earned.

    @author  Tilly Searle
    """
    student = get_object_or_404(Student, user=request.user)
    badges = Badge.objects.all()
    owned_badges = Award.objects.filter(student=student).values_list("badge_name", flat=True)

    return render(request, "badges.html", {"badges": badges,"owned_badges": owned_badges})

def leaderboard(request: HttpRequest) -> HttpResponse:
    """Display a leaderboard of students based on their points.

    @author  Lia Fisher
    """
    all_students = Student.objects.all().order_by("-points")
    badge_links = Award.objects.all()
    badges = Badge.objects.all()
    students = all_students[:10]
    top_ten = True
    rank = -1
    points = -1
    if request.user.is_authenticated:
        is_student = Student.objects.filter(user=request.user).exists()
        if is_student and Student.objects.get(user = request.user) not in students:
            top_ten = False
            current_student = Student.objects.get(user = request.user)
            points = current_student.points
            rank = all_students.filter(points__gte = current_student.points).count()
    return render(request, "leaderboard.html", {
        "students": students,
        "top_ten": top_ten,
        "rank": rank,
        "points": points,
        "badge_links": badge_links,
        "badges": badges
    })

@login_required
def user_data(request: HttpRequest) -> HttpResponse:
    """Display all data that relates to the user on request.
    
    @author Seth Mallinson
    """
    user: User = request.user
    student = Student.objects.filter(user=user).first()
    soc_rep = SocietyRepresentative.objects.filter(user=user).first()

    # Students may have bookings linked to them
    bookings = []
    points = None
    if student:
        bookings = Booking.objects.filter(student=student)
        points = student.points

    # Soc reps may have events linked to them
    events = []
    society_name = None
    if soc_rep:
        events = Event.objects.filter(organiser=soc_rep)
        society_name = soc_rep.society_name

    return render(request, "user_data.html", {
        "username": user.username,
        "email": user.email,
        "points": points,
        "society_name": society_name,
        "bookings": bookings,
        "events": events
    })
