LADBROKE GROVE - CIRCULAR WALKS APP

Setup Instructions:

* Clone the repo

* Create a .env file with the following env variables
    SECRET_KEY  < generate your own >
    OPENAI_API_KEY  < go to platform.openai.com >
    GOOGLE_MAPS_API_KEY < go to developers.google.com>
    ACCESS_TOKEN_EXPIRE_MINUTES < set expiry time e.g 2880 (48h) >

* Run the app using:
    docker-compose up --build


Endpoints:

* You can see saved locations (GET /locations) and distances (GET /distances)
* To create walking routes, first get a JSON Web Token from /generate-token
* Then you can use routes/plan to plan new routes - a google maps link is returned, allowing you to view your custom circular walking route directly in google maps!