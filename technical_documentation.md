Here's info on the structure of the project. Most of it is in app/, but generators.py and algorithms.py are in the mysite directory, where the justification is that they don't have any references to the frontend in them. Many of the files are quite self explanatory in their function but they will be listed here:
app/*.html - HTML files for different pages.
app/\__init__.py - Django needs this.
app/admin.py - registers database models so that the admin panel can manipulate them.
app/forms.py - stores all of the form objects to be served and interpreted to and from the frontend.
app/models.py - stores all of the models which define the structure of the relational database.
app/queries.py - URLs that can be queried to retrieve some specific resource from the server.
app/tests.py - unit tests for the system.
app/urls.py - defines all valid url patterns for the system, aside from the admin panel.
app/views.py - the frontend of the backend, this defines the server response to every url pattern.
mysite/\__init__.py - Django needs this.
mysite/algorithms.py - significant chunks of code that are referenced elsewhere but stored here for neatness.
mysite/asgi.py - Django needs this.
mysite/generators.py - distinct from algorithms.py in that it stores functions with "gen" in their name.
mysite/settings.py - Django requires this to declare project settings.
mysite/urls.py - encapsulates the content of app/urls.py along with the admin panel.
mysite/wsgi.py - Django needs this.

Files typically have more granular documentation within them.

There were definitely a lot of important design decisions, but that is terribly broad. Here's some subset of them:
We decided to use QR codes to enforce location based engagement.
We decided to enforce event approval by moderators.
We decided to only allow Student accounts to attend events.
