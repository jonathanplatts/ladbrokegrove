from typing import List, Optional
from app.database.models import Location


def generate_initial_prompt(
    landmark_name: str,
    route_time: float,
    nearby_landmarks: Optional[List[Location]] = None,
) -> str:
    """Generates a prompt to pass to OpenAI model."""
    prompt = f"""
    You are a tour guide. Come up with a {str(route_time)}-minute walking tour, with carefully spaced stops for the user to look at landmarks.
    Constraints:
    * The tour should start and end at {landmark_name} station in London.
    * You should allow for a few minutes at each stop and assume an average walking pace of
    4 km/h. 
    * The person taking the tour does not want to spend money or go inside places extensively, it is just a walking tour
    to see as much as possible from the street. Therefore, focus on scenic routes such as riverside paths, parks and pedestrian-friendly streets.
    * The tour must not go over {str(route_time)} minutes and should avoid doubling back.
    * Therefore, no leg of the route should take more than {str(route_time / 2)} minutes.
    * No waypoint should be further than the distance covered at 4 km/h in {str(route_time / 2)} minutes.
    * There should be no more than 10 waypoints.

    Output:
    * Return only a single-line comma-separated list of waypoints, with no additional text or explanations.
    * The waypoints should be in the order in which the user will visit them.
    Example:
    'Big Ben, Westminster Abbey, St James' Park.'
    """

    if nearby_landmarks:
        landmark_table = "\n".join(
            [
                f"{i+1}. {name.ljust(40)} {round(distance, 2)} m"
                for i, (name, distance) in enumerate(nearby_landmarks)
            ]
        )
        subprompt = f"""
        To help you find a route, here is a table of the 25 landmarks closest to the start point, and their distances from the start point:
        | #  | Landmark Name                         | Distance (meters) |
        |----|--------------------------------------|------------------|
        {landmark_table}
        """

        prompt += subprompt

    return prompt


def generate_corrective_prompt(
    requested_time: float, route_duration: float, route_distance: float
) -> str:
    return f"""Google maps says the route you provided takes {route_duration} minutes and is a distance of {route_distance} km.
    This is too long - the route should be completed in {str(requested_time)} minutes.
    Take the shortest route you've found so far, and *adapt* it to make it shorter, do not modify the entire route.
    This may include removing waypoints.
    Output:
    * Return only a single-line comma-separated list of waypoints, with no additional text or explanations.
    * The waypoints should be in the order in which the user will visit them.
    Example:
    'Big Ben, Westminster Abbey, St James' Park.'"""
