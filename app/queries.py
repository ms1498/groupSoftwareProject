from django.http import HttpResponse, HttpRequest
# backend imports
from mysite.qrgen import get_qrcode_from_response

def qrgen(request: HttpRequest) -> HttpResponse:
    """Accepts a GET request with a 'url' argument, that argument will be processed into a QR code and a jpeg image returned to the frontend.

    @param: request - HttpRequest
    @author: Seth Mallinson
    """
    code_image = get_qrcode_from_response(request)
    if code_image is None:
        return HttpResponse("Invalid request. The qrgen expects a GET request with a 'url' parameter.")
    return HttpResponse(code_image, content_type="image/jpeg")