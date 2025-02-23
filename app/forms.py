from .models import Event, Booking
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

    @author            Tricia Sibley
    """

    class Meta:
        model = Event
        fields = ("name", "date", "category", "description", "image")

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['event']  # Only need to choose the event

    event = forms.ModelChoiceField(queryset=Event.objects.all(), required=True)