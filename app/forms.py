from .models import Event, Booking, Location
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class SignInForm(forms.Form):
    """The template for the sign-in form.

    @param username    The username.
    @param password    The password.
    @return            Contains the sign in form template to render to the screen.
    @author            Maisie Marks
    """

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class SignUpForm(UserCreationForm):
    """The template for the sign-up form.

    @param username:   The username
    @param email:      The email address
    @param password1:  The password
    @param password2:  The password again for further validation
    @return            The form for the sign up template
    @author            Maisie Marks
    """

    email = forms.EmailField(required=True)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

class CreateEventForm(forms.ModelForm):
    """Form for creating events.

    @param name:        The name of the event
    @param date:        The date and time of the event
    @param category:    The category of the event
    @param description: A description of the event
    @param image:       An image to display representing the event
    @param location:    The location of the event
    @author             Tricia Sibley
    """

    class Meta:
        model = Event
        fields = ("name", "date", "category", "description", "location", "image")
    
    # Ensure location field uses a ModelChoiceField
    location = forms.ModelChoiceField(queryset= Location.objects.all(), empty_label="Choose a location")

class BookingForm(forms.ModelForm):
    """Form for booking a place at an event.
    
    @param event:       An approved event from the database
    @author             Tilly Searle"""
    event = forms.ModelChoiceField(queryset=Event.objects.filter(approved=True), required=True)
    class Meta:
        model = Booking
        # the user will select the event they're interested in
        fields = ("event",)