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

    # Not logged in = fail
    if not request.user.is_authenticated:
        return (False, "You must be signed in to register attendance.")
    student = get_object_or_404(Student, user=request.user)

    # No matching event = fail
    if event_end:
        valid_events = Event.objects.filter(pk=event_id, end_key=key)
        points_reward: int = 10
    else:
        valid_events = Event.objects.filter(pk=event_id, start_key=key)
        points_reward: int = 15
    if len(valid_events) == 0:
        return (False, "No event with matching key exists.")
    event = valid_events.first()

    # User not booked for the event = fail
    booking = Booking.objects.filter(student=student, event=event).first()
    if booking is None:
        return (False, "You are not booked for this event.")

    # Event not begun = fail
    if timezone.now() + timedelta(minutes=5) < event.date:
        return (False, "This event has not started yet.")

    # User already scanned this code = fail
    if (event_end and booking.end_attendance) or ((not event_end) and booking.start_attendance):
        return (False, "You have already attended this event.")

    # Register the student's attendance
    if ((not booking.start_attendance) and (not booking.end_attendance)):
        # Field may be null - is this really a good idea?
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
    student.points += points_reward
    student.save()
    return (True, "🎉 Thank You for Attending! 🎉")
