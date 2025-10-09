from enum import StrEnum


class Methods(StrEnum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    DELETE = "DELETE"

class GoHighLevel(StrEnum):
    FROM_AIZEN = "From AIZen"
    ALREADY_BOOKED = "ALREADY BOOKED"
    APPOINTMENT_TITLE = "Booked by AIZen"
    