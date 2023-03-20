import requests
import structs
import datetime
import logging
import time
from typing import List

from functools import cache

formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler = logging.FileHandler('cineworld.log')
handler.setFormatter(formatter)
logger = logging.getLogger('cineworld')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

MAGIC_ID = '10108'

@cache
def get_all_venues(revision):
    until_date = (datetime.datetime.now().date() + datetime.timedelta(days=365)).isoformat()
    url = f'https://www.cineworld.co.uk/uk/data-api-service/v1/quickbook/{MAGIC_ID}/cinemas/with-event/until/{until_date}?attr=&lang=en_GB'
    headers = {
  'authority': 'www.cineworld.co.uk',
  'accept': 'application/json;charset=utf-8',
  'accept-language': 'ru,en;q=0.9',
  'referer': 'https://www.cineworld.co.uk/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    time.sleep(0.1)
    js = r.json()
    venues = []
    for item in js['body']['cinemas']:
        id_ = item['id']
        name = item['displayName']
        link = item['link']
        city = item['addressInfo']['city']
        postcode = item['addressInfo']['postalCode']
        address = item['address']
        lat = item['latitude']
        lon = item['longitude']
        venues.append(structs.Venue(id_, name, 'Cineworld', lat, lon, link, True))
    return venues

def get_venues():
    until_date = (datetime.datetime.now().date() + datetime.timedelta(days=365)).isoformat()
    url = f'https://www.cineworld.co.uk/uk/data-api-service/v1/quickbook/{MAGIC_ID}/cinemas/with-event/until/{until_date}?attr=&lang=en_GB'
    headers = {
  'authority': 'www.cineworld.co.uk',
  'accept': 'application/json;charset=utf-8',
  'accept-language': 'ru,en;q=0.9',
  'referer': 'https://www.cineworld.co.uk/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    js = r.json()
    venues = []
    for item in js['body']['cinemas']:
        id_ = item['id']
        name = item['displayName']
        venues.append((id_, name))
    return venues

@cache
def get_venue_dates(venue_id, revision):
    until_date = (datetime.datetime.now().date() + datetime.timedelta(days=365)).isoformat()
    url = f'https://www.cineworld.co.uk/uk/data-api-service/v1/quickbook/{MAGIC_ID}/dates/in-cinema/{venue_id}/until/{until_date}?attr=&lang=en_GB'
    headers = {
  'authority': 'www.cineworld.co.uk',
  'accept': 'application/json;charset=utf-8',
  'accept-language': 'ru,en;q=0.9',
  'referer': 'https://www.cineworld.co.uk/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    time.sleep(0.1)
    js = r.json()
    return js['body']['dates']

@cache
def get_film_events_json(venue_id, date, revision):
    url = f'https://www.cineworld.co.uk/uk/data-api-service/v1/quickbook/{MAGIC_ID}/film-events/in-cinema/{venue_id}/at-date/{date}?attr=&lang=en_GB'
    headers = {
  'authority': 'www.cineworld.co.uk',
  'accept': 'application/json;charset=utf-8',
  'accept-language': 'ru,en;q=0.9',
  'referer': 'https://www.cineworld.co.uk/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    time.sleep(0.1)
    return r.json()

def get_all_movies(revision):
    venues = get_all_venues(revision)
    movies_by_id = {}
    for venue in venues:
        logger.info(f"Processing venue {venue}")
        dates = get_venue_dates(venue.id_, revision)
        for date in dates:
            logger.info(f"Processing {venue.name} showings at {date}")
            js = get_film_events_json(venue.id_, date, revision)
            name_by_id = {}
            for item in js['body']['films']:
                id_ = item['id']
                name = item['name']
                logger.info(f"Processing {venue.name} movie {name} id={id_}")
                running_time = item['length']
                poster_link = item['posterLink']
                trailer_link = item['videoLink']
                link = item['link']
                release_year = item['releaseYear']
                name_by_id[id_] = name
                movies_by_id[id_] = structs.Movie(id_, name, 'Cineworld', link, True)
    movies = list(movies_by_id.values())
    logger.info(f"Got {len(movies)} movies from Cineworld")
    return movies

def get_showings_old(venue_id, date, revision):
    js = get_film_events_json(venue_id, date, revision)
    name_by_id = {}
    for item in js['body']['films']:
        id_ = item['id']
        name = item['name']
        name_by_id[id_] = name

    showings = []
    for item in js['body']['events']:
        movie_id = item['filmId']
        movie_name = name_by_id.get(movie_id)
        if not movie_id:
            logger.warning(f"Cannot file movie name for id={movie_id}. Skipping...")
            continue
        start_time = item['eventDateTime']
        showings.append((movie_name, start_time))
    return showings


def get_all_showings_old(revision, **args):
    assert(revision is not None)
    venues = get_venues()
    all_showings = []
    for venue_id, venue_name in venues:
        logger.info(f"Processing {venue_name}")
        # if 'London' not in venue_name:
            # continue
        dates = get_venue_dates(venue_id, revision)
        for date in dates:
            logger.info(f"Processing showings on {date} at {venue_name}")
            showings = get_showings(venue_id, date, revision)
            time.sleep(0.1)
            for movie_name, start_time in showings:
                start_time_local = datetime.datetime.fromisoformat(start_time)
                all_showings.append(structs.Showing(movie_name, venue_name, start_time_local, 'Cineworld'))
    return all_showings

def get_showings(venue_id, date, revision) -> List[structs.ShowingNew]:
    js = get_film_events_json(venue_id, date, revision)

    showings = []
    for item in js['body']['events']:
        id_ = item['id']
        movie_id = item['filmId']
        link = item['bookingLink']
        available = not item['soldOut']
        screen_name = item['auditorium']
        start_time = datetime.datetime.fromisoformat(item['eventDateTime'])
        showings.append(structs.ShowingNew(id_, movie_id, venue_id, start_time, 'Cineworld', link, available))
    return showings


def get_all_showings(revision, **kwargs):
    assert(revision is not None)
    venues = get_venues()
    all_showings = []
    for venue_id, venue_name in venues:
        logger.info(f"Processing {venue_name}")
        # if 'London' not in venue_name:
        #     continue
        dates = get_venue_dates(venue_id, revision)
        for date in dates:
            logger.info(f"Processing showings on {date} at {venue_name}")
            showings = get_showings(venue_id, date, revision)
            all_showings.extend(showings)
    logger.info(f"Got {len(all_showings)} showings from Cineworld")
    return all_showings

