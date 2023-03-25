import requests
import structs
import logging
import datetime
import time
import re

from typing import List

formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler = logging.FileHandler('odeon.log')
handler.setFormatter(formatter)
logger = logging.getLogger('odeon')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

def get_all_venues(**kwargs):
    url = 'https://odeon-vwc.webtrends-optimize.workers.dev/CinemasSchedule'
    headers = {
  'authority': 'odeon-vwc.webtrends-optimize.workers.dev',
  'accept': 'application/json',
  'accept-language': 'ru,en;q=0.9',
  'origin': 'https://www.odeon.co.uk',
  'referer': 'https://www.odeon.co.uk/',
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
    for item in js:
        id_ = item['ID']
        city = item['City']
        name = item['Name']
        normalized_name = city + " " + name.replace(city, '')
        lat = float(item['Latitude'])
        lon = float(item['Longitude'])
        link = 'https://www.odeon.co.uk/cinemas/' + name.lower().replace(' ', '-') + '/'
        venues.append(structs.Venue(id_, normalized_name, 'ODEON', lat, lon, link, True))
    return venues

def get_venues():
    url = 'https://odeon-vwc.webtrends-optimize.workers.dev/CinemasSchedule'
    headers = {
  'authority': 'odeon-vwc.webtrends-optimize.workers.dev',
  'accept': 'application/json',
  'accept-language': 'ru,en;q=0.9',
  'origin': 'https://www.odeon.co.uk',
  'referer': 'https://www.odeon.co.uk/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'cross-site',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    js = r.json()
    venues = []
    for item in js:
        id_ = item['ID']
        city = item['City']
        name = item['Name']
        normalized_name = city + " " + name.replace(city, '')
        logger.info(f"Processing venue id={id_} name={name} from {city}. Normalized name is {normalized_name}")
        venues.append((id_, normalized_name))
    return venues

def get_all_movies(**kwargs) -> List[structs.Movie]:
    url = 'https://odeon-vwc.webtrends-optimize.workers.dev/FilmsSchedule'
    headers = {
  'authority': 'odeon-vwc.webtrends-optimize.workers.dev',
  'accept': 'application/json',
  'accept-language': 'ru,en;q=0.9',
  'origin': 'https://www.odeon.co.uk',
  'referer': 'https://www.odeon.co.uk/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'cross-site',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    js = r.json()
    movies = []
    for item in js:
        id_ = item['ID']
        title = item['Title']
        logger.info(f"Processing movie {title}")
        del item['sessions']
        synopsis = item['Synopsis']
        running_time = item['RunTime']
        release_date = item['OpeningDate'] # ?
        trailer_link = item['TrailerUrl']
        poster_link = item['GraphicUrl']
        normalized_name = re.sub('[^a-z0-9\-]', '', title.lower().replace(' ', '-'))
        link = f'https://www.odeon.co.uk/films/{normalized_name}/{id_}'
        movies.append(structs.Movie(id_, title, 'ODEON', link, True))
    logger.info(f"Got {len(movies)} movies from ODEON")
    return movies

def get_all_showings_old(**kwargs) -> List[structs.Showing]:
    venues = get_venues()
    name_by_id = {id_: name for id_, name in venues}
    url = 'https://odeon-vwc.webtrends-optimize.workers.dev/FilmsSchedule'
    headers = {
  'authority': 'odeon-vwc.webtrends-optimize.workers.dev',
  'accept': 'application/json',
  'accept-language': 'ru,en;q=0.9',
  'origin': 'https://www.odeon.co.uk',
  'referer': 'https://www.odeon.co.uk/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'cross-site',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    js = r.json()
    all_showings = []
    for item in js:
        title = item['Title']
        logger.info(f"Processing movie {title}")
        for session in item['sessions']:
            venue_id = session['CinemaId']
            venue_name = name_by_id.get(venue_id)
            if not venue_name:
                logger.warning(f"Cannot find venue with id={venue_id}. Skipping...")
                continue
            logger.info(f"Processing {title} showings in {venue_name}")
            for showing in session['Showings']:
                time = datetime.datetime.fromisoformat(showing['Showtime'])
                all_showings.append(structs.Showing(title, venue_name, time, 'ODEON'))
    return all_showings

def get_all_showings(**kwargs) -> List[structs.ShowingNew]:
    url = 'https://odeon-vwc.webtrends-optimize.workers.dev/FilmsSchedule'
    headers = {
  'authority': 'odeon-vwc.webtrends-optimize.workers.dev',
  'accept': 'application/json',
  'accept-language': 'ru,en;q=0.9',
  'origin': 'https://www.odeon.co.uk',
  'referer': 'https://www.odeon.co.uk/',
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
    all_showings = []
    for item in js:
        title = item['Title']
        movie_id = item['ID']
        logger.info(f"Processing movie {title}")
        for session in item['sessions']:
            venue_id = session['CinemaId']
            logger.info(f"Processing {title} showings in {venue_id}")
            for showing in session['Showings']:
                id_ = showing['ID']
                start_time = datetime.datetime.fromisoformat(showing['Showtime'])
                screen_name = showing['ScreenName']
                link = f'https://www.odeon.co.uk/ticketing/seat-picker/?showtimeId={id_}'
                all_showings.append(structs.ShowingNew(id_, movie_id, venue_id, start_time, 'ODEON', link, True))
    logger.info(f"Got {len(all_showings)} showings from ODEON")
    return all_showings
