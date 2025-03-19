"""Algorithms where it was thought too messy to define them elsewhere."""


from datetime import timedelta, datetime
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
    """Delete a given user's account, along with all data related to them.
    
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
    
    @param request:   the user's request
    @author:          Seth Mallinson
    """
    # pylint: disable=too-many-locals
    student = Student.objects.get(user=request.user)
    all_bookings = Booking.objects.filter(student=student)
    attended_bookings = all_bookings.exclude(attended=Booking.AttendanceStatus.ABSENT)
    already_awarded = [award.badge_name for award in Award.objects.filter(student=student)]
    new_awards: list[Award] = []

    def at_least_x_events(x: int) -> bool:
        return attended_bookings.count() >= x

    def at_least_x_events_one_soc(x: int) -> bool:
        counts = {}
        for booking in attended_bookings:
            society = booking.event.organiser.society_name
            if society in counts:
                counts.update({society : counts[society] + 1})
            else:
                counts.update({society : 1})
        return any(count >= x for count in counts.values())

    def events_from_at_least_x_socs(x: int) -> bool:
        socs = set(booking.event.organiser.society_name for booking in attended_bookings)
        return len(socs) >= x

    def events_at_at_least_x_locations(x: int) -> bool:
        locs = set(booking.event.location.name for booking in attended_bookings)
        return len(locs) >= x

    def all_event_categories() -> bool:
        categories = [
            "End Poverty",
            "End Hunger",
            "Good Health",
            "Quality Education",
            "Gender Equality",
            "Clean Water and Sanitation",
            "Clean Energy",
            "Economic Growth",
            "Reducing Inequalities",
            "Sustainable Cities and Communities",
            "Responsible Consumption",
            "Protect the Planet",
            "Peace and Justice"
        ]
        booked_categories = set(booking.event.category for booking in attended_bookings)
        return all(category in booked_categories for category in categories)

    def at_least_x_outdoor_events(_: int) -> bool:
        # to do: actually create some outdoor locations.
        # This badge is currently unattainable.
        return False

    def at_least_x_week_streak(x: int) -> bool:
        this_week_start = datetime.today() - timedelta(days=datetime.today().weekday())
        this_week_start = timezone.make_aware(this_week_start, timezone.get_current_timezone())
        week_starts = [this_week_start - timedelta(days=i*7) for i in range(x+1)]
        event_dates = [booking.event.date for booking in attended_bookings]
        streak = True
        for i in range(1, len(week_starts)):
            if not any(week_starts[i] <= date <= week_starts[i-1] for date in event_dates):
                streak = False
        return streak

    def top_x_on_leaderboard(x: int, badge_name: str) -> bool:
        # notice: we don't have a model representing the leaderboard. Thus, the method of using
        # it here (basically just assembling it) would not scale well with large numbers of users.
        leaderboard = list(Student.objects.all())
        leaderboard.sort(key=lambda x: x.points, reverse=True)
        # Similarly we must remove the badge another student may have here.
        if student in leaderboard[0:5] and len(leaderboard) > x:
            badge = Badge.objects.get(badge_name=badge_name)
            # The badge might not exist if badge rules have been altered etc.
            # There is also the caveat that a badge may not remove correctly if its leaderboard
            # requirements are changed. Such cases need to be handled elsewhere.
            to_be_removed = Award.objects.filter(student=leaderboard[x], badge_name=badge).first()
            if to_be_removed:
                to_be_removed.delete()
        return student in leaderboard[0:5]

    conditions = {
        # Attend one event
        "Getting Started": [],
        # Attend five events
        "On a Roll": [lambda: at_least_x_events(5)],
        # Attend ten events
        "Locked In": [lambda: at_least_x_events(10)],
        # Attend five events from one society
        "Loyalist": [lambda: at_least_x_events_one_soc(5)],
        # Attend events from five different societies
        "All-Rounder": [lambda: events_from_at_least_x_socs(5)],
        # Attend events at five different locations
        "Explorer": [lambda: events_at_at_least_x_locations(5)],
        # Attend an event from every category
        "Variety is the Spice of Life": [all_event_categories],
        # Attend an event that takes place outside
        "Outdoorsy": [lambda: at_least_x_outdoor_events(1)],
        # Attend an event in two consecutive weeks
        "Reliable": [lambda: at_least_x_week_streak(2)],
        # Attend an event in three consecutive weeks
        "Dedicated": [lambda: at_least_x_week_streak(3)],
        # Top 5 on the leaderboard
        "Sustainability Superstar": [lambda: top_x_on_leaderboard(5, "Sustainability Superstar")],
        # Top of the leaderboard
        "The Best.": [lambda: top_x_on_leaderboard(1, "The Best.")]
    }

    for item in conditions.items():
        if item[0] not in already_awarded:
            if all(condition() for condition in item[1]):
                badge = Badge.objects.get(badge_name=item[0])
                new_awards.append(Award(student=student, badge_name=badge))

    # Save any new badges
    for award in new_awards:
        award.save()
