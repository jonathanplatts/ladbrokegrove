from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.database.models import Distance, DistanceUnit
from geoalchemy2.shape import to_shape


def handle_get_distances(db: Session):
    query = db.query(Distance)

    distances = query.all()

    # Serialize.
    results = []
    for distance in distances:
        results.append(
            {
                "id": distance.id,
                "origin_id": distance.origin_id,
                "origin_name": distance.origin.name if distance.origin else None,
                "origin_latitude": (
                    to_shape(distance.origin.geom).x if distance.origin else None
                ),
                "origin_longitude": (
                    to_shape(distance.origin.geom).y if distance.origin else None
                ),
                "destination_id": distance.destination_id,
                "destination_name": (
                    distance.destination.name if distance.destination else None
                ),
                "destination_latitude": (
                    to_shape(distance.destination.geom).x
                    if distance.destination
                    else None
                ),
                "destination_longitude": (
                    to_shape(distance.destination.geom).y
                    if distance.destination
                    else None
                ),
                "distance": distance.distance,
                "distance_unit": distance.distance_unit.value,
            }
        )

    return jsonable_encoder(results)
