import structs
import sqlite3
import datetime
import json

from typing import List
from typing import Optional


def save_showings(con: sqlite3.Connection, showings: List[structs.Showing], revision: int):
    data = [(s.id_.strip(), s.movie_id.strip(), s.venue_id.strip(), s.start_time_local.isoformat(), s.network_name, s.link, s.available, revision) for s in showings]
    con.executemany('INSERT INTO showings(id, movie_id, venue_id, start_time_local, network_name, link, available, revision) '
                    'VALUES(?, ?, ?, ?, ?, ?, ?, ?)',
                    data)
    con.commit()
    print(f'Saved {len(showings)} showings')

def save_venues(con: sqlite3.Connection, venues: List[structs.Venue], revision: int):
    data = [(v.id_.strip(), v.name.strip(), v.network_name, v.lat, v.lon, v.link, v.available, revision) for v in venues]
    con.executemany('INSERT INTO venues(id, name, network_name, lat, lon, link, available, revision) '
                    'VALUES(?, ?, ?, ?, ?, ?, ?, ?)',
                    data)
    con.commit()
    print(f'Saved {len(venues)} venues')

def save_movies(con: sqlite3.Connection, movies: List[structs.Movie], revision: int):
    def _get_additional_info(m):
        if m.additional_info is None:
            return None
        return json.dumps(m.additional_info)
    data = [(m.id_.strip(), m.title.strip(), m.network_name, m.link, m.available, _get_additional_info(m), revision) for m in movies]
    con.executemany('INSERT INTO movies(id, title, network_name, link, available, additional_info, revision) '
                    'VALUES(?, ?, ?, ?, ?, ?, ?)',
                    data)
    con.commit()
    print(f'Saved {len(movies)} movies')

def get_all_revisions(con: sqlite3.Connection) -> List[int]:
    res = con.execute("select distinct revision from (select distinct revision from movies union all select distinct revision from venues union all select distinct revision from showings) order by revision")
    return [x[0] for x in res.fetchall()]

def get_venues(con: sqlite3.Connection, revision: int) -> List[structs.Venue]:
    res = con.execute("select id, name, network_name, lat, lon, link, available from venues where revision = ?", (revision,))
    return [structs.Venue(x[0], x[1], x[2], x[3], x[4], x[5], x[6]) for x in res.fetchall()]

def get_movies(con: sqlite3.Connection, revision: int) -> List[structs.Movie]:
    res = con.execute("select id, title, network_name, link, available, additional_info from movies where revision = ?", (revision,))
    return [structs.Movie(x[0], x[1], x[2], x[3], x[4], None if x[5] is None else json.loads(x[5])) for x in res.fetchall()]

def get_showings(con: sqlite3.Connection, revision: int) -> List[structs.Showing]:
    res = con.execute("select id, movie_id, venue_id, start_time_local, network_name, link, available from showings where revision = ?", (revision,))
    return [structs.Showing(x[0], x[1], x[2], x[3], x[4], x[5], x[6]) for x in res.fetchall()]

def search_showings(con: sqlite3.Connection, revision: int, search_query: Optional[str]) -> List[structs.Showing]:
    if not search_query:
        return get_showings(con, revision)
    res = con.execute("select id, movie_id, venue_id, start_time_local, s.network_name, s.link, s.available from showings as s left join movies as m on s.network_name = m.network_name and s.movie_id = m.id where s.revision = ? and m.revision = ? and lower(m.title) like ?", (revision, revision, '%'+search_query+'%'))
    return [structs.Showing(x[0], x[1], x[2], datetime.datetime.fromisoformat(x[3]), x[4], x[5], x[6]) for x in res.fetchall()]
