from pydantic import BaseModel
from typing import Optional

from app.core.constants import DEFAULT_NUMBER_LLM_CALLS


class RouteRequest(BaseModel):
    city_name: str
    route_time: int
    start_location: str
    max_attempts: Optional[int] = DEFAULT_NUMBER_LLM_CALLS
    use_geo_database: Optional[bool] = False
