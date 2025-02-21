from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey,
    Enum,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from app.database.session import Base
from app.core.enums import DistanceUnit, LocationType


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location_type = Column(Enum(LocationType), nullable=False)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)

    # (name, location_type) should be unique
    # i.e (London Bridge, subway_station) and (London Bridge, place_of_interest) is allowed.
    __table_args__ = (
        UniqueConstraint("name", "location_type", name="uq_location_name_type"),
    )


class Distance(Base):
    __tablename__ = "distances"

    id = Column(Integer, primary_key=True, index=True)
    origin_id = Column(
        Integer, ForeignKey("locations.id", ondelete="CASCADE"), index=True
    )
    destination_id = Column(
        Integer, ForeignKey("locations.id", ondelete="CASCADE"), index=True
    )
    distance = Column(Float, nullable=False)
    distance_unit = Column(Enum(DistanceUnit), nullable=False)

    origin = relationship("Location", foreign_keys=[origin_id])
    destination = relationship("Location", foreign_keys=[destination_id])

    __table_args__ = (
        UniqueConstraint("origin_id", "destination_id", name="uq_distance_pair"),
    )
