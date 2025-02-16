from __future__ import annotations
from typing import TYPE_CHECKING
from io import BytesIO
import qrcode

if TYPE_CHECKING:
    from django.http import HttpRequest

def get_qrcode_from_response(request: HttpRequest) -> bytes | None:
    """Validates then encapsulates the request's GET parameter in a QR code and returns this as a jpeg image, stored as bytes.

    @param: request - HttpRequest\n
    @returns: Either a bytes object, or None if the request was invalid.\n
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
    except:
        return None

    # this image should be in a jpeg format that can just be sent to the server and embedded, I think...
    img = qr.make_image(fill_color="black", back_color="white", format="jpeg")

    # save the image, but to memory rather than an actual file location.
    with BytesIO() as stream:
        img.save(stream, format="jpeg")
        img_data = stream.getvalue()

    # a temp test to check that the data formed a coherent image
    #img.save("./test_valid.jpeg", format="jpeg")
    #with open("./test_raw.jpeg", "wb") as file:
    #    file.write(img_data)

    return img_data
