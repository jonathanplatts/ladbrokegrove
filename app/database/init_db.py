from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from app.database.session import Base, engine


def initialize_postgis_and_indexes(engine):
    with engine.connect() as connection:
        try:
            # Enable PostGIS Extension
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))

            # Create spatial index for the locations table
            connection.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_locations_geom ON locations USING GIST(geom);"
                )
            )

            connection.commit()
            print("PostGIS initialized and spatial index created.")
        except ProgrammingError as e:
            print(f"Error initializing PostGIS: {e}")


def initialize_db():
    Base.metadata.create_all(bind=engine)
    initialize_postgis_and_indexes(engine)
