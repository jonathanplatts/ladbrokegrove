from enum import Enum as PyEnum


class DistanceUnit(PyEnum):
    METERS = "m"
    KM = "km"
    MILES = "mi"


class TimeUnit(PyEnum):
    HOUR = "hr"
    MINUTE = "min"
    SECOND = "s"


class LocationType(PyEnum):
    SUBWAY_STATION = "subway_station"  # American names come from Google Places API.
    TOURIST_ATTRACTION = "tourist_attraction"
    MUSEUM = "museum"
    PARK = "park"
    CHURCH = "church"
    ART_GALLERY = "art_gallery"
    HISTORICAL_LANDMARK = "historical_landmark"
    PLACE_OF_WORSHIP = "place_of_worship"
    CITY_HALL = "city_hall"
    LIBRARY = "library"
    UNIVERSITY = "university"
    TRAIN_STATION = "train_station"
    BRIDGE = "bridge"
    STADIUM = "stadium"
    MARKET = "market"
    VIEWPOINT = "viewpoint"
    OBSERVATORY = "observatory"
    LANDMARK = "landmark"
    POINT_OF_INTEREST = "point_of_interest"
    OTHER = "other"
