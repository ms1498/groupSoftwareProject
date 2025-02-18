import os
import json
#django imports
from django.shortcuts import render, redirect
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, User
from django.core import serializers
from django.http import HttpResponse, HttpRequest
# model imports
from app.models import Event, Location, SocietyRepresentative
# backend imports
from .forms import SignInForm, SignUpForm
from mysite.qrgen import get_qrcode_from_response


def serve_events(request:HttpRequest) -> HttpResponse:
    """Returns a list of all events that match arbitrary criteria. Use a 'filters' parameter in the URL to specify a list[str] of comma separated conditions, for example ?filters=pk=1,event_location="forum"
    @param user's request
    @return a json list of events
    @author Seth Mallinson"""

    if request.method == "GET":
        valid_events = Event.objects.all()
        # attempt to apply filters, if there are any. We do this by executing a filter operation for however many filter arguments were provided.
        try:
            conditions:list[str] = request.GET["filters"].split(",")
            for condition in conditions:
                local_vars = {"valid_events":valid_events}
                exec("valid_events = valid_events.filter(" + condition + ")", globals(), local_vars)
                valid_events = local_vars["valid_events"]
        except:
            pass
        data = serializers.serialize("json", valid_events)
        return HttpResponse(data, content_type="text/plain")
    else:
        return HttpResponse("Invalid request - should be GET", status=400)
    
def submit_event(request:HttpRequest) -> HttpResponse:
    """Include a json description of the event in the request body and it will be saved to the database.
    @param GET request
    @return response status
    @author Seth Mallinson"""

    if request.method == "POST":
        try:
            # convert organiser name to model object PK before deserialising
            dictionary:dict[str, any] = json.loads(str(request.body)[2:-1])
            dictionary["fields"].update({"organiser": SocietyRepresentative.objects.filter(user=User.objects.get(username=dictionary["fields"]["organiser"]))[0].pk})
            data = json.dumps(dictionary)
            # save the new event
            next(serializers.deserialize("json", "[" + data + "]")).save()
            return HttpResponse(status=200)
        except:
            return HttpResponse("Invalid request - error during deserialisation. A JSON definition of the event is expected. Got: " + str(request.body)[2:-1] + " \nmake sure that the user and location referenced by the event definition exist.", status=400)
    else:
        return HttpResponse("Invalid request - should be POST", status=400)