import csv

from app.database.session import SessionLocal
from app.routes.data_import import bulk_insert_locations
from app.database.models import Location

from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from app.database.models import LocationType
from app.services.google_places_api import fetch_places


def fetch_and_populate_locations(
    location_types: list[LocationType], base_location: str, radius: float
) -> None:
    locations = []
    unique_names = set()

    csv_filename = "tube_stations.csv"

    with open(csv_filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Latitude", "Longitude", "Category"])

        for location_type in location_types:
            print(f"Fetching places of type: {location_type}")
            results = fetch_places(location_type, base_location, radius)

            for place in results:
                name, lat, lng, *_ = place

                if name not in unique_names:
                    unique_names.add(name)

                    writer.writerow(place)

                    locations.append(
                        Location(
                            name=name,
                            location_type=LocationType._value2member_map_.get(
                                location_type, LocationType.OTHER
                            ),
                            geom=from_shape(Point(lng, lat)),
                        )
                    )

        print(f"Finished saving {len(unique_names)} landmarks to csv.")

    # Save to DB.
    print(f"Saving landmarks to db.")
    db = SessionLocal()
    bulk_insert_locations(db, locations)
    db.close()
    print(f"Landmarks successfully saved to db!")
