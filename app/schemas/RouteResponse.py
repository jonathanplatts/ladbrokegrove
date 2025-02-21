from pydantic import BaseModel


class RouteResponse(BaseModel):
    google_maps_url: str
    waypoints: list[str]
    attempts_needed: int
