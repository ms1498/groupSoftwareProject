"""Test cases for the app."""

from datetime import datetime
from zoneinfo import ZoneInfo
from uuid import uuid4
from django.test import TestCase
from django.http import HttpRequest
# pylint: disable=imported-auth-user
from django.contrib.auth.models import User
import cv2
import numpy as np
from mysite.generators import get_qrcode_from_response
from mysite.algorithms import get_event_search_priority
from .models import Event, SocietyRepresentative

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
