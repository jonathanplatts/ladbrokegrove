import typer
from app.database.session import Base, engine, SessionLocal

from app.services.data_import import fetch_and_populate_locations
from app.services.places_lookup import get_tube_stations, get_nearby_locations
from app.database.models import Location, LocationType, Distance, DistanceUnit
from app.database.init_db import initialize_db

app = typer.Typer()

CENTRAL_LONDON_COORDS = "51.5074,-0.1278"

# Reminder: run these from docker container...
# docker exec -it fastapi_backend bash
# python cli.py <populate-tube-stations> # Note formatting


@app.command()
def create_tables():
    try:
        print("Creating tables...")
        initialize_db()
        print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")


@app.command()
def populate_tube_stations():
    try:
        db = SessionLocal()

        base_location = CENTRAL_LONDON_COORDS
        radius = 5000  # 5km
        location_types = ["subway_station"]

        fetch_and_populate_locations(location_types, base_location, radius)

        db.close()
        typer.echo("Tube stations populated successfully.")
    except Exception as e:
        print(f"Error populating tube stations: {e}")


@app.command()
def populate_landmarks():
    try:
        db = SessionLocal()

        base_location = CENTRAL_LONDON_COORDS
        radius = 5000  # 5km
        location_types = [
            "tourist_attraction",
            "museum",
            "park",
            "church",
            "art_gallery",
            "historical_landmark",
            "place_of_worship",
            "city_hall",
            "library",
            "university",
            "train_station",
            "bridge",
            "stadium",
            "market",
            "viewpoint",
            "observatory",
            "landmark",
            "point_of_interest",
        ]

        fetch_and_populate_locations(location_types, base_location, radius)

        db.close()
        typer.echo("Landmarks populated successfully.")
    except Exception as e:
        print(f"Error populating landmarks: {e}")


@app.command()
def populate_distance_table():
    # Initially, populate all distances from landmarks of type subway_station.
    try:
        print("Populating distances table...")
        db = SessionLocal()
        tube_stations = get_tube_stations(db)

        radius = 3000  # Look within a 3km radius.

        for station in tube_stations:
            # Get all landmarks within the specified distance, excluding other tube stations.
            nearby_locations = get_nearby_locations(
                db, station, radius, [LocationType.SUBWAY_STATION]
            )

            print(f"Nearby locs: {nearby_locations}")

            distances_to_add = [
                Distance(
                    origin_id=station.id,
                    destination_id=loc_id,
                    distance=distance,
                    distance_unit=DistanceUnit.METERS,
                )
                for loc_id, loc_name, distance in nearby_locations
            ]

            db.bulk_save_objects(distances_to_add)
            db.commit()
            print("Distances added successfully!")

        db.close()

    except Exception as e:
        print(f"Error computing distances: {e}")


@app.command()
def clear_distances_table():
    confirm = typer.confirm(
        """
        Warning: this command deletes *all* calculated distances from the db, and is irreversible.
        Are you sure you want to proceed?"""
    )

    if not confirm:
        typer.echo("Clear distances operation cancelled.")
        raise typer.Abort()

    try:
        db = SessionLocal()
        db.query(Distance).delete()
        db.commit()
        db.close()
        typer.echo("Distance data deleted successfully.")
    except Exception as e:
        print(f"Error clearing distances db: {e}")


@app.command()
def clear_landmarks_table():
    confirm = typer.confirm(
        """
        Warning: this command deletes *all* landmarks from the db, and is irreversible.
        Are you sure you want to proceed?"""
    )

    if not confirm:
        typer.echo("Clear landmarks operation cancelled.")
        raise typer.Abort()

    try:
        db = SessionLocal()
        db.query(Location).delete()
        db.commit()
        db.close()
        typer.echo("Locations deleted successfully.")
    except Exception as e:
        print(f"Error clearing landmarks db: {e}")


if __name__ == "__main__":
    app()
