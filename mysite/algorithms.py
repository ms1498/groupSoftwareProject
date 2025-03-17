"""Algorithms where it was thought too messy to define them elsewhere."""


from datetime import timedelta
from django.contrib.auth.models import User # pylint: disable=imported-auth-user
from django.utils import timezone
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from app.models import Event, Student, SocietyRepresentative, Booking, Award, Badge

def get_event_search_priority(event: Event, search_query: str) -> int:
    """Get the priority of an event (paired with a user query) for ordering search results.

    @param      event - the event to calculate the priority of.
    @param      search_query - the user's search query to match against.
    @return     the priority of the event as an integer, from 0-5.
    @author     Seth Mallinson
    @author     Tricia Sibley
    """
    society_name = event.organiser.society_name.lower()
    event_name = event.name.lower()
    search_query = search_query.lower()

    # Query matches event name exactly.
    if search_query == event_name:
        return 5

    # Query is in event name.
    if search_query in event_name:
        return 4

    # Query is in event description.
    if search_query in event.description.lower():
        return 3

    # At least one word in the user's query is in the event name.
    if any(query in event_name for query in search_query.split(" ")):
        return 2

    # Query is in society name.
    if search_query in society_name:
        return 1

    return 0

def process_qrcode_scan(request: HttpRequest) -> tuple[bool, str] | None:
    """Validate a user's request to register attendance for an event, and register their attendance
    and reward them points if valid.
    
    @param:     request - the HttpRequest
    @returns:   a tuple containing whether the operation was successful and a string to be displayed
                to the user. Returns None instead if the request was not related to a QR code scan.
    @author:    Seth Mallinson
    """
    try:
        event_id: int = int(request.GET["id"])
        event_end: bool = int(request.GET["end"])
        key: str = request.GET["key"]
    except KeyError:
        return None

    # check if the requested user is a student here
    student = Student.objects.filter(user=request.user).first()
    if student is None:
        error = "You must be signed in as a student to register attendance."
    else:
        error = validate_checkin_request(event_id, event_end, key, student)

    if error is None:
        student = get_object_or_404(Student, user=request.user)
        if event_end:
            event = Event.objects.filter(pk=event_id, end_key=key).first()
        else:
            event = Event.objects.filter(pk=event_id, start_key=key).first()
        booking = Booking.objects.filter(student=student, event=event).first()
        # Register the student's attendance
        if booking.attended == Booking.AttendanceStatus.ABSENT:
            # Field may be null - was that really a good idea?
            if event.actual_attendance:
                event.actual_attendance += 1
            else:
                event.actual_attendance = 1
        update_booking_status(booking, event_end)

        # This is a good student. They get points. Yay.
        if event_end:
            student.points += 10
        else:
            student.points += 15
        student.save()
        return (True, "🎉 Thank You for Attending! 🎉")
    return (False, error)

def validate_checkin_request(event_id: int, is_end: bool, key: str, student: Student) -> str | None:
    """If the request is invalid, this finds out why and returns the error.
    
    @param:     event_id - the id of the event.
    @param:     is_end - is this the QR code that should be scanned at the end of the event?
    @param:     key - the key from the request.
    @param:     student - the Student making the request.
    @returns:   a string of the error that was found, or None.
    @author:    Seth Mallinson
    """
    # No matching event = fail
    if is_end:
        event = Event.objects.filter(pk=event_id, end_key=key).first()
    else:
        event = Event.objects.filter(pk=event_id, start_key=key).first()
    if event is None:
        return "No event with matching key exists."

    # User not booked for the event = fail
    booking = Booking.objects.filter(student=student, event=event).first()
    if booking is None:
        return "You are not booked for this event."

    # Event not begun = fail
    if timezone.now() + timedelta(minutes=5) < event.date:
        return "This event has not started yet."

    # User already scanned this code = fail
    will_attend_twice = (
        booking.attended == Booking.AttendanceStatus.ATTENDED
        or booking.attended == Booking.AttendanceStatus.START and not is_end
        or booking.attended == Booking.AttendanceStatus.END and is_end
    )
    if will_attend_twice:
        return "You have already attended this event."
    return None

def update_booking_status(booking: Booking, is_end: bool) -> None:
    """Updates the "attended" field of a booking based on whether the code being scanned is the
    one for the end, or not.
    @param:     booking - the Booking
    @param:     is_end - whether this is the event end QR code or not
    @author:    Seth Mallinson
    """
    now_attended_start = (
        booking.attended == Booking.AttendanceStatus.START
        or not is_end
    )
    attended_end = (
        booking.attended == Booking.AttendanceStatus.END
        or is_end
    )
    if now_attended_start and attended_end:
        booking.attended = Booking.AttendanceStatus.ATTENDED
    elif now_attended_start:
        booking.attended = Booking.AttendanceStatus.START
    else:
        booking.attended = Booking.AttendanceStatus.END
    booking.save()

def delete_account(user: User) -> None:
    """Deletes the account of a given user and all data related to them.
    
    @param user:    the account
    @author         Seth Mallinson
    """
    # If the user is a student, we need to delete all bookings and awards related to them.
    student = Student.objects.filter(user=user).first()
    if student:
        related_bookings = Booking.objects.filter(student=student)
        for booking in related_bookings:
            booking.delete()
        related_awards = Award.objects.filter(student=student)
        for award in related_awards:
            award.delete()
    # If the user is a society representative, we need to delete all events organised by them.
    society_representative = SocietyRepresentative.objects.filter(user=user).first()
    if society_representative:
        related_events = Event.objects.filter(organiser=society_representative)
        for event in related_events:
            event.delete()

    # Delete the account.
    user.delete()

def apply_awards_after_attendance(request: HttpRequest) -> None:
    """A function to determine whether the user now meets the criteria for any badges to be
    awarded, and awards those badges to them. This function assumes that it is being called
    after the request has already been validated as a valid event attendance registration.
    
    @request:   the user's request
    @author:    Seth Mallinson
    """

    event = Event.objects.get(id=int(request.GET["id"]))
    student = Student.objects.get(user=request.user)
    booking = Booking.objects.get(student=student, event=event)
    already_awarded = [award.badge_name for award in Award.objects.filter(student=student)]
    new_awards: list[Award] = []

    def at_least_x_events(x: int) -> bool:
        return len([booking for booking in Booking.objects.filter(student=student)
                if booking.AttendanceStatus != Booking.AttendanceStatus.ABSENT]) >= x

    def test1():
        return
    def test1():
        return
    def test1():
        return
    def test1():
        return
    def test1():
        return
    def test1():
        return
    def test1():
        return
    def test1():
        return
    def test1():
        return
    def test1():
        return
    def test1():
        return
    def test1():
        return
    def test1():
        return
    def test1():
        return
    def test1():
        return
    conditions = {
        # attend at least one event
        "Getting Started": [],
        # attend at least five events
        "On a Roll": [lambda: at_least_x_events(5)],
        # attend at least ten events
        "Locked In": [lambda: at_least_x_events(10)],
    }

    for badge_name in conditions.keys():
        if badge_name not in already_awarded:
            if False not in [condition for condition in conditions[badge_name]]:
                badge = Badge.objects.get(badge_name=badge_name)
                new_awards.append(Award(student=student, badge_name=badge))


    # Save any new badges
    for award in new_awards:
        award.save()
