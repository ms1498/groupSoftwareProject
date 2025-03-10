"""Algorithms for general use."""


from datetime import timedelta
from django.utils import timezone
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from app.models import Event, Student, Booking

def get_event_search_priority(data: list[Event | str | int]) -> int:
    """Get the priority of an event (paired with a user query) for ordering search results.
    The priority passed in is modified in-place.
    
    @param: data - a list containing an event, the user's query (str) and the event's priority.
    @returns: the priority of the event as an integer, from 0-4.
    @author: Seth Mallinson
    """
    event = data[0]
    search_query = data[1]
    # if there is no search query, no ordering needs to be applied by us.
    if not search_query:
        data[2] = 0
        return 0

    society_name = event.organiser.society_name
    # Query is in event name.
    if search_query in event.name.lower():
        data[2] = 0
        return 0
    # Query is in event description.
    if search_query in event.description.lower():
        data[2] = 1
        return 1
    # True if at least one word in the user's query is in the event name.
    if any(query in event.name.lower() for query in search_query.split(" ")):
        data[2] = 2
        return 2
    # Query is in society name.
    if search_query in society_name.lower():
        data[2] = 3
        return 3
    data[2] = 4
    return 4

def process_qrcode_scan(request: HttpRequest) -> tuple[bool, str] | None:
    """Validate a user's request to register attendance for an event, and register their attendance
    and reward them points if valid.
    
    @param: request - the HttpRequest
    @returns: a tuple containing whether the operation was successful and a string to be displayed
              to the user. Returns None instead if the request was not related to a QR code scan.
    @author: Seth Mallinson
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
        event = Event.objects.filter(pk=event_id, end_key=key).first()
        booking = Booking.objects.filter(student=student, event=event).first()
        # Register the student's attendance
        if ((not booking.start_attendance) and (not booking.end_attendance)):
            # Field may be null - was that really a good idea?
            if event.actual_attendance:
                event.actual_attendance += 1
            else:
                event.actual_attendance = 1
        if event_end:
            booking.end_attendance = True
        else:
            booking.start_attendance = True
        booking.save()

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
    
    @param: event_id - the id of the event.
    @param: is_end - is this the QR code that should be scanned at the end of the event?
    @param: key - the key from the request.
    @param: student - the Student making the request.
    @returns: a string of the error that was found, or None.
    @author: Seth Mallinson
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
    if (is_end and booking.end_attendance) or ((not is_end) and booking.start_attendance):
        return "You have already attended this event."
    return None
