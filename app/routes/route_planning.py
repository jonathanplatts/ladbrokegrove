from fastapi import HTTPException
import logging
import traceback
from app.schemas import RouteRequest, RouteResponse

from openai import OpenAI
import os
from dotenv import load_dotenv

from app.core.enums import LocationType
from app.core.prompts import generate_initial_prompt, generate_corrective_prompt
from app.services.route_planner import RoutePlannerLLM
from app.services.places_lookup import get_location_by_name, get_nearby_locations

import googlemaps

from sqlalchemy.orm import Session

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)


def handle_create_new_route(route_request: RouteRequest, db: Session) -> RouteResponse:
    try:
        # Check if the start point exists.
        start_location = get_location_by_name(db, route_request.start_location)
        if not start_location:
            raise HTTPException(
                status_code=404,
                detail=f"Start point '{route_request.start_location}' does not match any locations in the database!",
            )

        # If using GeoDB, need to get the nearest landmarks and their distances before prompting the LLM.
        if route_request.use_geo_database == True:
            # Fetch landmarks within (tour time / 30) km of start point.
            # This is the distance someone can walk, in half of the tour time, at 4 km/h, where tour time is in minutes.
            nearby_landmarks = get_nearby_locations(
                db=db,
                base_location=start_location,
                radius=(route_request.route_time / 30),
                excluded_types=[LocationType.SUBWAY_STATION],
                limit=25,
            )

            nearby_landmarks = [
                (landmark.name, landmark.distance) for landmark in nearby_landmarks
            ]
            prompt = generate_initial_prompt(
                start_location.name, float(route_request.route_time), nearby_landmarks
            )

        else:
            # Just generate the prompt without passing the landmark distances hint.
            prompt = generate_initial_prompt(
                start_location.name, float(route_request.route_time), False
            )

        print(f"Initial prompt - {prompt}")

        is_route_valid = False
        route_planner = RoutePlannerLLM(api_key=OPENAI_API_KEY)
        for i in range(route_request.max_attempts - 1):
            try:
                print("Calling LLM with prompt:")
                print(prompt)
                llm_response = route_planner.get_response(prompt)
                waypoints = llm_response.split(", ")

                # This will be needed to generate google maps URL.
                waypoints_plus_cities = [
                    f"{waypoint}, {route_request.city_name}" for waypoint in waypoints
                ]

                # Maps sanity-check.
                try:
                    route_duration, route_distance = (
                        get_route_duration_from_google_maps(
                            start_location.name, waypoints_plus_cities
                        )
                    )
                except Exception as e:
                    logging.error(f"Error getting route duration using Google Maps API")
                    raise e

                is_route_valid = validate_route(
                    route_request.route_time, route_duration, route_distance
                )

                attempts_needed = i + 1

                if is_route_valid:
                    print("Route validated - all good.")
                    break
                else:
                    print("Route needs refinement")
                    prompt = generate_corrective_prompt(
                        route_request.route_time, route_duration, route_distance
                    )  # Combine with validate_route?

            except Exception as e:
                logging.error(f"Error in route validation iteration {i+1}: {e}")
                logging.debug(traceback.format_exc())

        if not is_route_valid:
            # Check status code for this one.
            raise HTTPException(
                status_code=400,
                detail="Could not produce a valid route - please try again.",
            )

        print("Finished planning route - generating url.")
        google_maps_url = generate_maps_url(
            route_request.start_location, waypoints_plus_cities
        )

        route_response = {
            "google_maps_url": google_maps_url,
            "waypoints": waypoints,
            "attempts_needed": attempts_needed,
        }

        return route_response

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        logging.debug(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred. Please try again later.",
        )


def get_llm_response(prompt: str) -> str:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print(client)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            store=True,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.choices[0].message.content

    except Exception as e:
        print(e)
        raise e


def get_route_duration_from_google_maps(
    start_location: str, waypoints_plus_cities: list[str]
):
    try:
        gmaps = googlemaps.Client(key="AIzaSyCfroRLRD5haBZAfKThzlagmXsuHgSfqAg")
        logging.info("Initialized google maps client")

        start = f"{start_location}, London"
        end = f"{start_location}, London"

        directions = gmaps.directions(
            start,
            end,
            mode="walking",
            waypoints=waypoints_plus_cities,
            optimize_waypoints=False,  # waypoint order was determined by the LLM.
        )

        if not directions:
            raise HTTPException(status_code=404, detail="No route found")

        # Print the route for now.
        for i, leg in enumerate(directions[0]["legs"]):
            print(f"Leg {i+1}: {leg['start_address']} → {leg['end_address']}")
            print(
                f"Distance: {leg['distance']['text']}, Duration: {leg['duration']['text']}\n"
            )

        # Calculate distance and time to check.
        total_distance = 0
        total_duration = 0

        for leg in directions[0]["legs"]:
            total_distance += leg["distance"]["value"]
            total_duration += leg["duration"]["value"]

        # Convert distance to km and duration to minutes
        total_distance /= 1000
        total_duration /= 60

        return total_duration, total_distance

    # Handle any exceptions from google maps.

    except googlemaps.exceptions.ApiError as e:
        logging.error(f"Google Maps API error: {e}")
        raise HTTPException(
            status_code=502, detail="Google Maps API error. Please try again later."
        )

    except googlemaps.exceptions.Timeout as e:
        logging.error(f"Google Maps API request timed out: {e}")
        raise HTTPException(
            status_code=504,
            detail="Google Maps API request timed out. Please try again later.",
        )

    except googlemaps.exceptions.TransportError as e:
        logging.error(f"Network transport error with Google Maps API: {e}")
        raise HTTPException(
            status_code=503, detail="Network error while connecting to Google Maps API."
        )

    except googlemaps.exceptions.HTTPError as e:
        logging.error(f"HTTP error from Google Maps API: {e}")
        raise HTTPException(
            status_code=500, detail="Unexpected HTTP error from Google Maps API."
        )

    except KeyError as e:
        logging.error(f"Unexpected response structure from Google Maps API: {e}")
        raise HTTPException(
            status_code=500, detail="Unexpected response format from Google Maps API."
        )

    except Exception as e:
        logging.error(f"Unexpected error while fetching directions: {e}")
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching route data."
        )


def validate_route(
    requested_time: float, route_duration: float, route_distance: float
) -> bool:
    max_allowed_time = requested_time * 1.5
    max_allowed_distance = (requested_time * 1.5) * (4 / 60)
    print("validate route")
    print(max_allowed_time, max_allowed_distance)

    if route_duration > max_allowed_time or route_distance > max_allowed_distance:
        return False

    return True


def generate_maps_url(start_location: str, waypoints: list[str]) -> str:
    print("generate maps fn")
    print(start_location)
    print(waypoints)
    base_url = "https://www.google.com/maps/dir/?api=1"
    if len(waypoints) < 1:
        raise ValueError("Circular route must have at least one waypoint!")

    origin = destination = start_location

    waypoints_param = "|".join(waypoints) if waypoints else ""

    print(origin)
    print(destination)
    print(waypoints_param)

    print(f"waypoints param: {waypoints_param}")
    url = f"{base_url}&origin={origin}&destination={destination}&travelmode=walking"
    if waypoints_param:
        url += f"&waypoints={waypoints_param}"

    print(url)

    return url
