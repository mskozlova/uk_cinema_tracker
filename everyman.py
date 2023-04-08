import requests
import structs
import datetime
import logging
import time
import json
import collections

from typing import List
from typing import Set
from typing import Dict

formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler = logging.FileHandler('everyman.log')
handler.setFormatter(formatter)
logger = logging.getLogger('everyman')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def get_all_movies(**kwargs) -> List[structs.Movie]:
    url = 'https://cms-assets.webediamovies.pro/prod/everyman/64d73c13bc78e7607dd0f957/public/page-data/sq/d/4272676115.json'
    headers = {
  'authority': 'cms-assets.webediamovies.pro',
  'accept': '*/*',
  'accept-language': 'ru,en;q=0.9',
  'origin': 'https://www.everymancinema.com',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'cross-site',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    time.sleep(0.1)
    js = r.json()
    movies = []
    for item in js['data']['allMovie']['nodes']:
        id_ = item['id']
        title = item['title']
        link = 'https://www.everymancinema.com' + item['path']
        cast = item['casting']
        director = item['direction']
        poster_link = item['poster']
        release_date = item['release']
        running_time = item['runtime']
        synopsis = item['synopsis']
        trailer_link = item['trailer']
        movies.append(structs.Movie(id_, title, 'Everyman', link, True))
    logger.info(f"Got {len(movies)} movies from Everyman")
    return movies

def get_movies_by_venue_id() -> Dict[str, Set[str]]:
    url = 'https://cms-assets.webediamovies.pro/prod/everyman/64d73c13bc78e7607dd0f957/public/page-data/sq/d/4272676115.json'
    headers = {
  'authority': 'cms-assets.webediamovies.pro',
  'accept': '*/*',
  'accept-language': 'ru,en;q=0.9',
  'origin': 'https://www.everymancinema.com',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'cross-site',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    time.sleep(0.1)
    js = r.json()
    movies_by_theatre = collections.defaultdict(set)
    for item in js['data']['allMovie']['nodes']:
        id_ = item['id']
        for theatre_item in item['theaters']:
            venue_id = theatre_item['theater']['id']
            movies_by_theatre[venue_id].add(id_)
    return movies_by_theatre


def get_all_venues(**kwargs) -> List[structs.Venue]:
    url = 'https://cms-assets.webediamovies.pro/prod/everyman/64d73c13bc78e7607dd0f957/public/page-data/sq/d/2826555639.json'
    headers = {
  'authority': 'cms-assets.webediamovies.pro',
  'accept': '*/*',
  'accept-language': 'ru,en;q=0.9',
  'origin': 'https://www.everymancinema.com',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'cross-site',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    time.sleep(0.1)
    js = r.json()
    venues = []
    for item in js['data']['allTheater']['nodes']:
        id_ = item['id']
        name = item['name']
        city = item['practicalInfo']['location']['city']
        postcode = item['practicalInfo']['location']['zip']
        available = not item['practicalInfo']['closed']
        lat = item['practicalInfo']['coordinates']['latitude']
        lon = item['practicalInfo']['coordinates']['longitude']
        normalized_name = city + " " + name.replace(city, '')
        link = 'https://www.everymancinema.com' + item['path'].replace('/theaters/', '/venues-list/')
        logger.info(f'Processing venue id={id_} name={name} city={city} normalized name={normalized_name}')
        venues.append(structs.Venue(id_, name, 'Everyman', lat, lon, link, available))
    return venues


def get_all_showings(**kwargs) -> List[structs.ShowingNew]:
    url = 'https://www.everymancinema.com/api/gatsby-source-boxofficeapi/schedule'
    headers = {
  'authority': 'www.everymancinema.com',
  'accept': '*/*',
  'accept-language': 'ru,en;q=0.9',
  'content-type': 'text/plain;charset=UTF-8',
  'origin': 'https://www.everymancinema.com',
  'referer': 'https://www.everymancinema.com/film-listing/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    venues = get_all_venues(**kwargs)
    venue_name_by_id = {venue.id_: venue.name for venue in venues}
    movies = get_all_movies(**kwargs)
    movies_by_venue_id = get_movies_by_venue_id()
    movie_name_by_id = {movie.id_: movie.title for movie in movies}
    from_dt = (datetime.datetime.now().date() - datetime.timedelta(days=1)).isoformat() + "T03:00:00"
    to_dt = (datetime.datetime.now().date() + datetime.timedelta(days=365)).isoformat() + "T03:00:00"
    for venue in venues:
        venue_id = venue.id_
        venue_name = venue.name
        data = {
            "theaters": [{"id": venue_id, "timeZone":"Europe/London"}],
            "movieIds": [id_ for id_ in movies_by_venue_id[venue_id]],
            "from": from_dt,
            "to": to_dt,
        }
        data_str = json.dumps(data, separators=(',', ':'))
        logger.info(f"Posting data: {data_str}")
        r = requests.post(url, data=data_str, headers=headers)
        time.sleep(0.1)
        js = r.json()
        all_showings = []
        for venue_id, item in js.items():
            venue_name = venue_name_by_id.get(venue_id)
            if not venue_name:
                logger.warning(f"Cannot find venue with id={venue_id}. Skipping...")
                continue
            for movie_id, schedule_item in item['schedule'].items():
                movie_name = movie_name_by_id.get(movie_id)
                if not movie_name:
                    logger.warning(f"Cannot find movie name with id={movie_id}. Skipping...")
                    continue
                for _, showings in schedule_item.items():
                    for showing in showings:
                        id_ = showing['id']
                        start_time = datetime.datetime.fromisoformat(showing['startsAt'])
                        link = showing['data']['ticketing'][0]['urls'][0]
                        all_showings.append(structs.ShowingNew(id_, movie_id, venue_id, start_time, 'Everyman', link, True))
    logger.info(f"Got {len(all_showings)} showings from Everyman")
    return all_showings
