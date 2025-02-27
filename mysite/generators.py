"""Handle the generation of event QR codes."""
from __future__ import annotations
import secrets
from typing import TYPE_CHECKING
from io import BytesIO
import qrcode

if TYPE_CHECKING:
    from django.http import HttpRequest

def generate_random_key(length: int = 7) -> str:
    """Generate an alphanumeric key of the specified length randomly.

    @param: length - the length of the key.
    @returns: the key (str).
    @author: Seth Mallinson
    """
    characters: str = "abcdefghijklmnopqrstuvwxyz0123456789"
    key: str = ""
    for _ in range(length):
        key += secrets.choice(characters)
    return key

def get_qrcode_from_response(request: HttpRequest) -> bytes | None:
    """Validate then encapsulate the request's GET parameter in a QR code.

    The QR code is returned as a jpeg image, stored as bytes.

    @param: request - HttpRequest
    @returns: Either a bytes object, or None if the request was invalid.
    @author: Seth Mallinson
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    try:
        if request.method != "GET":
            return None
        qr.add_data(request.GET["url"])
        qr.make(fit=True)
    except KeyError:
        return None

    # This image should be in a jpeg format that can be sent to the server and embedded.
    img = qr.make_image(fill_color="black", back_color="white", format="jpeg")

    # save the image, but to memory rather than an actual file location.
    with BytesIO() as stream:
        img.save(stream, format="jpeg")
        img_data = stream.getvalue()

    return img_data
