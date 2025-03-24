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
## Running the App (locally)
To run the app locally, run the command python manage.py runserver from the repository directory.
This will then give you a local URL to access the website from.

## Deploying the App (online)
Below is how we hosted our Uweave online. Though there are many ways to do this, this was our method of choice.

### Purchase a Domain
To host on a domain, you need to purchase a domain name, this can be from any domain registrar of your choosing, but we chose [Porkbun](https://porkbun.com/) for simplicity and affordability.

### Choose a Reverse Proxy
Proxies are a much better alternative to hosting fully-locally. Not only a workaround for hosting inaccessibility, (e.g. port forwarding and other router-related settings) but also offer protection against DDossing and IP privacy. We used [Cloudflare](https://www.cloudflare.com/) for this.

### Connect Your Domain to the Reverse Proxy
You will need to copy the nameservers given to you by your reverse proxy and paste them into your nameservers on the domain registrar. This can take up to 72 hours to take effect.

### Computer for Deployment
Once domain and reverse proxy are linked, you will need a computer to run your webserver. Connectors can be installed on Windows, Linux or Mac. We used (ubuntu)linux for simplicity to tunnel the traffic to and from the website and the server. Since we're using cloudflare, we also used their [Cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) daemon.

### Running the Webserver
You need to make some changes to settings.py before running the local webserver, replacing ``uweave.online`` with your domain name. :
```
DEBUG = False
ALLOWED_HOSTS = ["uweave.online", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = [
    "https://uweave.online",
]
```
Running the django server now should display your website on your purchased domain.

## Testing Basic Functionality
- To test registering for the website, click the black "Sign Up" button in the middle of the screen when logged out, enter some details, then click Sign Up.
- To test logging in to the website, click the "Sign In" button in the navbar when logged out, enter existing login details, then click Sign In.
- To test creating an event, log in as a Society Representative (username: artSoc password: pencilsAndPaint), click on either the Organise button in the navbar or the Create an Event button on the home page, then enter the event details and click Submit.
- To test registering for an event, log in as a Student (username: sampleStudent password: studentPassword), click on Discover Events, then click on an existing event, then click Register Here. 
- To test logging in as a moderator, use this login (username: tillysearle password: myPassword123), and you should be able to see the Approve Events button in the middle of the screen.
The `resources/` directory contains an example database, along with further information.

## Connecting to Our Domain
We host the application at https://uweave.online.
