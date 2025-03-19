# UWeave

## System Requirements
- See requirements.txt
- If the included requirements are not present on your device, use pip install
- Before running any migrations, please make sure to replace any db.sqlite3 file in the repository directory with the one from the ELE submission zip file, as this contains the sample data required for testing.
- Before running the app, from the repository directory, be sure to run the following commands to ensure all migrations are made properly:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --run-syncdb
```
## Running the App
To run the app locally, run the command python manage.py runserver from the repository directory.
This will then give you a local URL to access the website from.

## Testing Basic Functionality
- To test registering for the website, click the black "Sign Up" button in the middle of the screen when logged out, enter some details, then click Sign Up.
- To test logging in to the website, click the "Sign In" button in the navbar when logged out, enter existing login details, then click Sign In.
- To test creating an event, log in as a Society Representative (username: artSoc password: pencilsAndPaint), click on either the Organise button in the navbar or the Create an Event button on the home page, then enter the event details and click Submit.
- To test registering for an event, log in as a Student (username: sampleStudent password: studentPassword), click on Discover Events, then click on an existing event, then click Register Here. 
- To test logging in as a moderator, use this login (username: tillysearle password: myPassword123), and you should be able to see the Approve Events button in the middle of the screen.
The `resources/` directory contains an example database, along with further information.

