import model
import sqlite3
import logging
import dataclasses

import structs

from typing import List
from typing import Tuple

@dataclasses.dataclass
class VenueDiff:
    deleted: List[structs.Venue]
    changed: List[Tuple[structs.Venue, structs.Venue]]
    added: List[structs.Venue]

@dataclasses.dataclass
class MovieDiff:
    deleted: List[structs.Movie]
    changed: List[Tuple[structs.Movie, structs.Movie]]
    added: List[structs.Movie]

@dataclasses.dataclass
class ShowingDiff:
    deleted: List[structs.ShowingNew]
    changed: List[Tuple[structs.ShowingNew, structs.ShowingNew]]
    added: List[structs.ShowingNew]

def get_all_revisions(con: sqlite3.Connection) -> List[int]:
    return model.get_all_revisions(con)

def _get_venue_diff(venues1: List[structs.Venue], venues2: List[structs.Venue], logger: logging.Logger) -> VenueDiff:
    def get_id(venue: structs.Venue):
        return (venue.network_name, venue.id_)
    ids1 = {get_id(venue): venue for venue in venues1}
    if len(ids1) != len(venues1):
        logger.warning(f"Revision has non-unique venue ids")

    ids2 = {get_id(venue): venue for venue in venues2}
    if len(ids2) != len(venues2):
        logger.warning(f"Revision has non-unique venue ids")
    
    deleted = []
    changed = []
    added = []

    for venue1 in venues1:
        id1 = get_id(venue1)
        venue2 = ids2.get(id1)
        if venue2 is None:
            deleted.append(venue1)
        elif venue1 != venue2:
            changed.append((venue1, venue2))

    for venue2 in venues2:
        id2 = get_id(venue2)
        venue1 = ids1.get(id2)
        if venue1 is None:
            added.append(venue2)
    
    return VenueDiff(deleted, changed, added)

def _get_movie_diff(movies1: List[structs.Movie], movies2: List[structs.Movie], logger: logging.Logger) -> MovieDiff:
    def get_id(movie: structs.Movie):
        return (movie.network_name, movie.id_)
    ids1 = {get_id(movie): movie for movie in movies1}
    if len(ids1) != len(movies1):
        logger.warning(f"Revision has non-unique movie ids")

    ids2 = {get_id(movie): movie for movie in movies2}
    if len(ids2) != len(movies2):
        logger.warning(f"Revision has non-unique movie ids")
    
    deleted = []
    changed = []
    added = []

    for movie1 in movies1:
        id1 = get_id(movie1)
        movie2 = ids2.get(id1)
        if movie2 is None:
            deleted.append(movie1)
        elif movie1 != movie2:
            changed.append((movie1, movie2))

    for movie2 in movies2:
        id2 = get_id(movie2)
        movie1 = ids1.get(id2)
        if movie1 is None:
            added.append(movie2)
    
    return MovieDiff(deleted, changed, added)

def _get_showing_diff(showings1: List[structs.ShowingNew], showings2: List[structs.ShowingNew], logger: logging.Logger) -> ShowingDiff:
    def get_id(showing: structs.ShowingNew):
        if showing.id_:
            return (showing.network_name, showing.id_, showing.venue_id, showing.movie_id)
        return (showing.network_name, showing.venue_id, showing.movie_id, showing.start_time_local)
    ids1 = {get_id(showing): showing for showing in showings1}
    if len(ids1) != len(showings1):
        logger.warning(f"Revision has non-unique showing ids")

    ids2 = {get_id(showing): showing for showing in showings2}
    if len(ids2) != len(showings2):
        logger.warning(f"Revision has non-unique showing ids")
    
    deleted = []
    changed = []
    added = []

    for showing1 in showings1:
        id1 = get_id(showing1)
        showing2 = ids2.get(id1)
        if showing2 is None:
            deleted.append(showing1)
        elif showing1 != showing2:
            changed.append((showing1, showing2))

    for showing2 in showings2:
        id2 = get_id(showing2)
        showing1 = ids1.get(id2)
        if showing1 is None:
            added.append(showing2)
    
    return ShowingDiff(deleted, changed, added)

def compare_revisions(con: sqlite3.Connection, rev1: int, rev2: int, logger: logging.Logger) -> Tuple[VenueDiff, MovieDiff, ShowingDiff]:
    logger.warning(f"Comparing revisions {rev1} and {rev2}")
    venues1 = model.get_venues(con, rev1)
    venues2 = model.get_venues(con, rev2)
    venue_diff = _get_venue_diff(venues1, venues2, logger)
    movies1 = model.get_movies(con, rev1)
    movies2 = model.get_movies(con, rev2)
    movie_diff = _get_movie_diff(movies1, movies2, logger)
    showings1 = model.get_showings(con, rev1)
    showings2 = model.get_showings(con, rev2)
    showing_diff = _get_showing_diff(showings1, showings2, logger)
    return venue_diff, movie_diff, showing_diff
