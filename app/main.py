from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth import create_access_token, verify_token
from app.config import setup_cors
from app.database.session import get_db
from app.database.models import LocationType
from app.rate_limit import limiter, get_user_key
from app.routes.route_planning import handle_create_new_route
from app.routes.locations import handle_get_locations
from app.routes.distances import handle_get_distances
from app.schemas.RouteRequest import RouteRequest
from app.schemas.RouteResponse import RouteResponse

from datetime import timedelta
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from shapely.geometry import Point
from typing import Optional

app = FastAPI()

# Rate limiter.
app.add_middleware(SlowAPIMiddleware)
app.state.limiter = limiter

# CORS middleware.
setup_cors(app)


@app.get("/")
@limiter.limit("30/minute")
def read_root(request: Request):
    return {"message": "Hello, FastAPI!"}


@app.get("/locations/{location_type:int}")
@app.get("/locations")
@limiter.limit("30/minute")
def get_locations(
    request: Request,
    db: Session = Depends(get_db),
    location_type_int: Optional[int] = None,
):
    location_type = None
    if location_type_int is not None:
        try:
            location_type = LocationType(location_type_int)
        except ValueError:
            return {"error": "Invalid location type passed"}

    return handle_get_locations(db, location_type)


@app.get("/distances")
@limiter.limit("30/minute")
def get_distances(request: Request, db: Session = Depends(get_db)):
    return handle_get_distances(db)


@app.post("/routes/plan", response_model=RouteResponse)
@limiter.limit("10/minute", key_func=get_user_key)
def create_new_route(
    request: RouteRequest,
    db: Session = Depends(get_db),
    user_data: dict = Depends(verify_token),
):
    try:
        return handle_create_new_route(request, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@limiter.limit("30/minute")
@app.post("/generate-token")
async def generate_token(request: Request):
    access_token = create_access_token(
        data={"sub": "authorized_user"}, expires_delta=timedelta(hours=48)
    )
    return {"access_token": access_token, "token_type": "bearer"}
