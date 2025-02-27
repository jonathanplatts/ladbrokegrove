from fastapi.encoders import jsonable_encoder

from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app.database.models import Location, LocationType


def handle_get_locations(db: Session, location_type: LocationType = None):
    query = db.query(Location)

    if location_type is not None:
        query = query.filter(Location.location_type == location_type)

    locations = query.all()

    # Serialize the geom objects so they can be returned as part of the response.
    results = []
    for loc in locations:
        results.append(
            {
                "id": loc.id,
                "name": loc.name,
                "location_type": loc.location_type.value,
                "latitude": to_shape(loc.geom).x,
                "longitude": to_shape(loc.geom).y,
            }
        )

    return jsonable_encoder(results)
