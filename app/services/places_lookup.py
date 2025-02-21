from sqlalchemy.orm import Session
from sqlalchemy import not_
from app.database.models import Location, LocationType
from geoalchemy2.functions import ST_DWithin, ST_DistanceSphere
from typing import List, Optional


def get_tube_stations(db: Session):
    return (
        db.query(Location)
        .filter(Location.location_type == LocationType.SUBWAY_STATION)
        .all()
    )


def get_location_by_name(db: Session, location_name: str):
    return db.query(Location).filter(Location.name == location_name).first()


def get_nearby_locations(
    db: Session,
    base_location: Location,
    radius: float,
    excluded_types: List[LocationType],
    limit: Optional[int] = None,
) -> List[Location]:

    query = (
        db.query(
            Location.id,
            Location.name,
            ST_DistanceSphere(base_location.geom, Location.geom).label("distance"),
        )
        .filter(
            ST_DWithin(base_location.geom, Location.geom, radius),
            not_(Location.location_type.in_(excluded_types)),
        )
        .order_by(ST_DistanceSphere(base_location.geom, Location.geom))
    )

    if limit:
        query = query.limit(limit)

    return query.all()
