#django imports
from django.core import serializers
from django.http import HttpResponse, HttpRequest
# model imports
from app.models import Event
# backend imports
from mysite.qrgen import get_qrcode_from_response


def serve_events(request:HttpRequest) -> HttpResponse:
    """Returns a json list of all events that match arbitrary criteria. Use a 'filters' parameter in the URL to specify a list[str] of comma separated conditions, for example ?filters=pk=1,location="forum
    Events will be automatically filtered to ensure users can only fetch events they have access to."
    @param user's request
    @return a json list of events
    @author Seth Mallinson"""

    if request.method != "GET":
        return HttpResponse("Invalid request - should be GET", status=400)
    
    valid_events = Event.objects.all()
    # attempt to apply filters, if there are any. We do this by executing a filter operation for however many filter arguments were provided.
    conditions:list[str] = []

    # check if the user can view unapproved events or not, if not add a filter to strip these events.
    if "app.view_unapproved_events" not in request.user.get_all_permissions():
        conditions.append("approved=True")

    # attempt to fetch conditions from the GET parameters.
    try:
        conditions += request.GET["filters"].split(",")
    except:
        pass
    # attempt to apply each condition. Try-catch each attempt as user input conditions could throw an exception if invalid.
    for condition in conditions:
        try:
            local_vars = {"valid_events":valid_events}
            exec("valid_events = valid_events.filter(" + condition + ")", globals(), local_vars)
            valid_events = local_vars["valid_events"]
        except:
            pass
    data = serializers.serialize("json", valid_events)
    return HttpResponse(data, content_type="text/plain")

def qrgen(request: HttpRequest) -> HttpResponse:
    """Accepts a GET request with a 'url' argument, that argument will be processed into a QR code and a jpeg image returned to the frontend.

    @param: request - HttpRequest
    @author: Seth Mallinson
    """
    code_image = get_qrcode_from_response(request)
    if code_image is None:
        return HttpResponse("Invalid request. The qrgen expects a GET request with a 'url' parameter.")
    return HttpResponse(code_image, content_type="image/jpeg")