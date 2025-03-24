"""Test cases for the app."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from uuid import uuid4
from django.test import TestCase
from django.http import HttpRequest
# pylint: disable=imported-auth-user
from django.contrib.auth.models import User
import cv2
import numpy as np
from mysite.generators import get_qrcode_from_response
from mysite.algorithms import get_event_search_priority, validate_checkin_request
from .models import Event, SocietyRepresentative, Student, Booking

class QRFromRequestTestCase(TestCase):
    """Test generating QR codes from requests.

    @author Tricia Sibley
    """

    def setUp(self) -> None:
        """Set up the test with a URL, a request, and a reader."""
        self.target_url = "http://127.0.0.1:8000/home?id=20&end=1&key=9qu1b3j"
        self.request = HttpRequest()
        self.request.method = "GET"
        self.request.GET["url"] = self.target_url
        self.qr_reader = cv2.QRCodeDetector()

    def test_get_qrcode_from_response(self) -> None:
        """Test if the generated QR code contains the target URL."""
        qr_image = np.frombuffer(get_qrcode_from_response(self.request), np.uint8)
        decoded_image = cv2.imdecode(qr_image, flags=cv2.IMREAD_COLOR_BGR)
        url, _, _ = self.qr_reader.detectAndDecode(decoded_image)
        self.assertEqual(url, self.target_url)

class EventSearchTestCase(TestCase):
    """Test the event search system.

    @author Tricia Sibley
    """

    def setUp(self) -> None:
        """Create some events to sort."""
        event_data = (
            ("whole test query", "", "", 5),
            ("whole test query extra", "", "", 4),
            ("", "whole test query", "", 3),
            ("whole other idea", "", "", 2),
            ("", "", "whole test query", 1),
            ("", "", "", 0),
        )
        self.test_events = []
        for data in event_data:
            user = User.objects.create(username=uuid4())
            rep = SocietyRepresentative.objects.create(user=user, society_name=data[2])
            date = datetime.now(tz=ZoneInfo("Europe/London"))
            event = Event.objects.create(
                name=data[0],
                description=data[1],
                date=date,
                organiser=rep,
            )
            self.test_events.append((event, data[3]))

    def test_get_priority(self) -> None:
        """Test if the event priority calculation produces expected results."""
        query = "whole test query"
        for event, priority in self.test_events:
            self.assertEqual(get_event_search_priority(event, query), priority)

class CheckInTestCase(TestCase):
    """Test the checkin system.

    @author Tricia Sibley
    """

    def setUp(self) -> None:
        """Create some sample events to check into, and book them to a student."""
        rep_user = User.objects.create(username=uuid4())
        student_user = User.objects.create(username=uuid4())
        rep = SocietyRepresentative.objects.create(user=rep_user, society_name="a")
        self.student = Student.objects.create(user=student_user)
        date = datetime.now(tz=ZoneInfo("Europe/London"))
        early = date + timedelta(minutes=10)

        self.good = Event.objects.create(name="a", description="a", date=date, organiser=rep)
        Booking.objects.create(student=self.student, event=self.good)

        self.too_early = Event.objects.create(name="a", description="a", date=early, organiser=rep)
        Booking.objects.create(student=self.student, event=self.too_early)

        self.unbooked = Event.objects.create(name="a", description="a", date=date, organiser=rep)

        self.already_a = Event.objects.create(name="a", description="a", date=date, organiser=rep)
        Booking.objects.create(
            student=self.student, event=self.already_a, attended=Booking.AttendanceStatus.ATTENDED
        )
        self.already_s = Event.objects.create(name="a", description="a", date=date, organiser=rep)
        Booking.objects.create(
            student=self.student, event=self.already_s, attended=Booking.AttendanceStatus.START
        )
        self.already_e = Event.objects.create(name="a", description="a", date=date, organiser=rep)
        Booking.objects.create(
            student=self.student, event=self.already_e, attended=Booking.AttendanceStatus.END
        )

    def test_validate_checkin_request(self) -> None:
        """Test if the correct response is given for different checkin conditions."""
        self.assertIsNone(
            validate_checkin_request(self.good.id, False, self.good.start_key, self.student)
        )
        self.assertIsNone(
            validate_checkin_request(self.good.id, True, self.good.end_key, self.student)
        )
        self.assertEqual(
            validate_checkin_request(self.good.id, True, "aaaaaaa", self.student),
            "No event with matching key exists.",
        )
        self.assertEqual(
            validate_checkin_request(self.good.id, True, self.good.start_key, self.student),
            "No event with matching key exists.",
        )
        self.assertEqual(
            validate_checkin_request(self.good.id, False, self.good.end_key, self.student),
            "No event with matching key exists.",
        )
        self.assertEqual(
            validate_checkin_request(self.too_early.id, True, self.too_early.end_key, self.student),
            "This event has not started yet.",
        )
        self.assertEqual(
            validate_checkin_request(self.unbooked.id, True, self.unbooked.end_key, self.student),
            "You are not booked for this event.",
        )
        self.assertEqual(
            validate_checkin_request(self.already_a.id, True, self.already_a.end_key, self.student),
            "You have already attended this event.",
        )
        self.assertEqual(
            validate_checkin_request(
                self.already_s.id, False, self.already_s.start_key, self.student,
            ),
            "You have already attended this event.",
        )
        self.assertEqual(
            validate_checkin_request(
                self.already_e.id, True, self.already_e.end_key, self.student,
            ),
            "You have already attended this event.",
        )
        self.assertIsNone(
            validate_checkin_request(
                self.already_s.id, True, self.already_s.end_key, self.student,
            ),
        )
