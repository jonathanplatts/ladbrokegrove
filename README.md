LADBROKE GROVE - CIRCULAR WALKS APP

Purpose of the app:

This is a prototype, WIP app that allows you to create a circular walking route from *any tube station in zone 1*
of London, and then get a google maps URL that will open the found route in google maps walking mode.
The idea is that the route is scenic and passes as many landmarks as possible that the user can just admire
(i.e not things they need to go in to for long periods or spend lots of money on).

I'm in the process of developing a very simple React Native frontend that will allow you to enter the city, start 
location and time (e.g 45 mins, 1h30) and then allow the user to open the route in Google Maps (or potentially
to see the google maps route within the app).

Note the constraints - London only currently - and just zone 1 - I've not populated the db with stations further out,
as the testing needed is more extensive (there just isn't the high density of landmarks in zones 3/4/5).

SETUP INSTRUCTIONS:

* Clone the repo

* Create a .env file with the env variables from .env.example, these must include:
    SECRET_KEY  < generate your own >
    ACCESS_TOKEN_EXPIRE_MINUTES < set expiry time e.g 2880 (48h) >
    DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, DB_PORT - for the Postgres database.
    OPENAI_API_KEY  < go to platform.openai.com >
    GOOGLE_MAPS_API_KEY < go to developers.google.com>
    

* Run the app using:
    docker-compose up --build

* Data (locations/landmarks/distances) can be populated using the commands in cli.py
* The commands to run, in order, are:

docker exec -it fastapi_backend bash
python cli.py create-tables
python cli.py populate-tube-stations
python cli.py populate-landmarks
python cli.py populate-distance-table

(Script coming soon...)

ENDPOINTS:

* You can see saved locations (GET /locations) and distances (GET /distances)
* To create walking routes, first get a JSON Web Token from /generate-token
* Then you can use routes/plan to plan new routes - a google maps link is returned, allowing you to view your custom circular walking route directly in google maps!


GETTING A TOKEN:

* Send a GET request to /generate-token and a bearer access token will be returned.

CREATING A WALKING ROUTE:

* Make a POST request to /routes/plan endpoint, example request body below:

{
	"city_name": "London", # Note - only supports London zone 1 currently
    "route_time": 45, # Minutes
    "start_location": "Russell Square",
	"number_of_attempts": 10, # Max attempts allowed
	"use_geo_database": true # Whether the LLM is given info from the built-in geo database
}

* This will return a google_maps_url, the waypoints, and the number of attempts it took.
* You will likely find that using the geodb gives a much greater success rate with fewer attempts.