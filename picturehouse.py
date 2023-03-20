import requests
import time
import datetime

import structs
import logging
import re


formatter = logging.Formatter('%(asctime)s, %(name)s %(levelname)s %(message)s')
handler = logging.FileHandler('picturehouse.log')
handler.setFormatter(formatter)
logger = logging.getLogger('picturehouse')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

def get_token():
    url = 'https://www.picturehouses.com/whats-on'
    headers = {
  'authority': 'www.picturehouses.com',
  'accept': '*/*',
  'accept-language': 'ru,en;q=0.9',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'origin': 'https://www.picturehouses.com',
  'referer': 'https://www.picturehouses.com/whats-on',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
  'x-requested-with': 'XMLHttpRequest',
    }
    r = requests.get(url, headers=headers)
    logger.info(f"Set-cookie header is: {r.headers['set-cookie']}")
    cookie = [x for x in r.headers['set-cookie'].split(' ') if x.startswith('laravel_session=')][0]
    lines = [x for x in r.text.split('\n') if '_token' in x]
    logger.info(f"Lines with token: {lines}")
    token = [x for x in r.text.split('\n') if '_token: "' in x][0].strip().split('"')[1]
    return cookie, token

def get_all_venues(**kwargs):
    cookie, token = get_token()
    url = 'https://www.picturehouses.com/ajax-cinema-list'
    headers = {
  'authority': 'www.picturehouses.com',
  'accept': '*/*',
  'accept-language': 'ru,en;q=0.9',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'origin': 'https://www.picturehouses.com',
  'referer': 'https://www.picturehouses.com/whats-on',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
  'x-requested-with': 'XMLHttpRequest',
  'cookie': cookie,
    }
    r = requests.post(url, data=f"_token={token}", headers=headers)
    js = r.json()
    venues = []
    for item in js['cinema_list']:
        venue_id = item['cinema_id']
        venue_name = item['name']
        city = item['address2']
        postcode = item['city']
        if 'coming soon' in venue_name.lower():
            lat = None
            lon = None
            available = False
        else:
            lat = float(item['latitude'])
            lon = float(item['longitude'])
            available = bool(item['is_active'])
        normalized_name = city + " " + venue_name.replace(city, '')
        link = 'https://www.picturehouses.com/cinema/' + item['slug']
        logger.info(f"Processing venue id={venue_id} name={venue_name} in {city}. Normalized name is {normalized_name}")
        venues.append(structs.Venue(venue_id, normalized_name, 'Picturehouse', lat, lon, link, available))
    return venues

def get_venues():
    cookie, token = get_token()
    url = 'https://www.picturehouses.com/ajax-cinema-list'
    headers = {
  'authority': 'www.picturehouses.com',
  'accept': '*/*',
  'accept-language': 'ru,en;q=0.9',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'origin': 'https://www.picturehouses.com',
  'referer': 'https://www.picturehouses.com/whats-on',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
  'x-requested-with': 'XMLHttpRequest',
  'cookie': cookie,
    }
    r = requests.post(url, data=f"_token={token}", headers=headers)
    js = r.json()
    venues = []
    for item in js['cinema_list']:
        venue_id = item['cinema_id']
        city = item['address2']
        venue_name = item['name']
        normalized_name = city + " " + venue_name.replace(city, '')
        logger.info(f"Processing venue id={venue_id} name={venue_name} in {city}. Normalized name is {normalized_name}")
        venues.append((venue_id, normalized_name))
    return venues

def get_all_movies(**kwargs):
    url = 'https://www.picturehouses.com/api/scheduled-movies-ajax'
    headers = {
  'authority': 'www.picturehouses.com',
  'accept': '*/*',
  'accept-language': 'ru,en;q=0.9',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'origin': 'https://www.picturehouses.com',
  'referer': 'https://www.picturehouses.com/whats-on',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
  'x-requested-with': 'XMLHttpRequest',
    }
    r = requests.post(url, data='cinema_id=', headers=headers)
    js = r.json()
    movies = []
    for item in js['movies']:
        id_ = item['ID']
        another_id = item['ScheduledFilmId']
        title = item['Title']
        logger.info(f"Processing showings of {title}")
        venue_id = item['CinemaId']
        trailer_link = item['TrailerUrl']
        poster_link = item['image_url']
        normalized_name = re.sub('[^a-z0-9\-]', '', title.lower().replace(' ', '-'))
        link = f'https://www.picturehouses.com/movie-details/{venue_id}/{another_id}/{normalized_name}'
        movies.append(structs.Movie(id_, title, 'Picturehouse', link, True))
    logger.info(f"Got {len(movies)} movies from Picturehouse")
    return movies

def get_all_showings_old(**kwargs):
    venues = get_venues()
    venue_name_by_id = {id_: name for (id_, name) in venues}
    url = 'https://www.picturehouses.com/api/scheduled-movies-ajax'
    headers = {
  'authority': 'www.picturehouses.com',
  'accept': '*/*',
  'accept-language': 'ru,en;q=0.9',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'origin': 'https://www.picturehouses.com',
  'referer': 'https://www.picturehouses.com/whats-on',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
  'x-requested-with': 'XMLHttpRequest',
    }
    r = requests.post(url, data='cinema_id=', headers=headers)
    js = r.json()
    all_showings = []
    for item in js['movies']:
        title = item['Title']
        logger.info(f"Processing showings of {title}")
        for showtime in item['show_times']:
            venue_id = showtime['CinemaId']
            venue_name = venue_name_by_id.get(venue_id)
            if not venue_name:
                logger.warning(f"Cannot find venue with id={venue_id}. Skipping...")
                continue
            start_time = datetime.datetime.fromisoformat(showtime['Showtime'])
            all_showings.append(structs.Showing(title, venue_name, start_time, 'Picturehouse'))
    return all_showings
    
def get_all_showings(**kwargs):
    venues = get_venues()
    venue_name_by_id = {id_: name for (id_, name) in venues}
    url = 'https://www.picturehouses.com/api/scheduled-movies-ajax'
    headers = {
  'authority': 'www.picturehouses.com',
  'accept': '*/*',
  'accept-language': 'ru,en;q=0.9',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'origin': 'https://www.picturehouses.com',
  'referer': 'https://www.picturehouses.com/whats-on',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
  'x-requested-with': 'XMLHttpRequest',
    }
    r = requests.post(url, data='cinema_id=', headers=headers)
    time.sleep(0.1)
    js = r.json()
    all_showings = []
    for item in js['movies']:
        title = item['Title']
        movie_id = item['ID']
        logger.info(f"Processing showings of {title}")
        for showtime in item['show_times']:
            id_ = showtime['SessionId']
            screen_name = showtime['ScreenName']
            venue_id = showtime['CinemaId']
            link = f'https://ticketing.picturehouses.com/Ticketing/visSelectTickets.aspx?cinemacode={venue_id}&txtSessionId={id_}&visLang=1'
            start_time = datetime.datetime.fromisoformat(showtime['Showtime'])
            # available - showtime[SoldoutStatus]
            all_showings.append(structs.ShowingNew(id_, movie_id, venue_id, start_time, 'Picturehouse', link, True))
    logger.info(f"Got {len(all_showings)} showings from Picturehouse")
    return all_showings