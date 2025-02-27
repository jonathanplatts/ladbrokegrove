from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy.orm import Session

from app.database.models import Location
from app.database.models import LocationType


def insert_location(
    db: Session,
    location_name: str,
    location_type: LocationType,
    latitude: float,
    longitude: float,
) -> Location:
    geom = from_shape(Point(longitude, latitude), srid=4326)
    new_location = Location(name=location_name, location_type=location_type, geom=geom)
    db.add(new_location)
    db.commit()
    db.refresh(new_location)

    return new_location


def bulk_insert_locations(db: Session, locations: list[dict]) -> None:
    if not locations:
        return

    db.add_all(
        [
            location if isinstance(location, Location) else Location(**location)
            for location in locations
        ]
    )
    db.commit()
