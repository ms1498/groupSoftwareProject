"""Stores queries that can be executed from the frontend."""
from django.http import HttpResponse, HttpRequest
# backend imports
from mysite.generators import get_qrcode_from_response

def qrgen(request: HttpRequest) -> HttpResponse:
    """Generate a QR code from a GET request with a 'url' argument.

    That argument will be processed into a QR code, returned as a JPEG image.

    @param: request - HttpRequest
    @author: Seth Mallinson
    """
    code_image = get_qrcode_from_response(request)
    if code_image is None:
        return HttpResponse("Invalid request. Expected a GET request with a 'url' parameter.")
    return HttpResponse(code_image, content_type="image/jpeg")
