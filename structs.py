import dataclasses
import datetime
from typing import Optional

@dataclasses.dataclass
class Venue:
    id_: str
    name: str
    network_name: str
    lat: Optional[float]
    lon: Optional[float]
    link: Optional[str]
    available: bool = True

@dataclasses.dataclass
class Movie:
    id_: str
    title: str
    network_name: str
    link: Optional[str]
    available: bool = True

@dataclasses.dataclass
class Showing:
    id_: str
    movie_id: str
    venue_id: str
    start_time_local: datetime.datetime
    network_name: str
    link: Optional[str]
    available: bool = True
