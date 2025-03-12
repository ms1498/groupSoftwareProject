"""Test cases for the app."""

from django.test import TestCase
from django.http import HttpRequest
import cv2
import numpy
from mysite.generators import get_qrcode_from_response

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
        qr_image = numpy.frombuffer(get_qrcode_from_response(self.request), numpy.uint8)
        decoded_image = cv2.imdecode(qr_image, flags=cv2.IMREAD_COLOR_BGR)
        url, _, _ = self.qr_reader.detectAndDecode(decoded_image)
        self.assertEqual(url, self.target_url)
