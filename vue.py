import requests
import time
import datetime

import structs
import logging
import httplib

from typing import List


formatter = logging.Formatter('%(asctime)s, %(name)s %(levelname)s %(message)s')
handler = logging.FileHandler('vue.log')
handler.setFormatter(formatter)
logger = logging.getLogger('vue')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

def get_venue_location(revision, venue_link_name):
    url = f'https://www.myvue.com/cinema/{venue_link_name}/getting-here'
    headers = {
  'authority': 'www.myvue.com' ,
  'accept': '*/*' ,
  'accept-language': 'ru,en;q=0.9' ,
  'referer': 'https://www.myvue.com/' ,
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"' ,
  'sec-ch-ua-mobile': '?1' ,
  'sec-ch-ua-platform': '"Android"' ,
  'sec-fetch-dest': 'empty' ,
  'sec-fetch-mode': 'cors' ,
  'sec-fetch-site': 'same-origin' ,
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36' ,
    }
    for _ in range(10):
        fake_revision = revision + _ # To avoid caching
        text = httplib.get_text(fake_revision, url, headers)
        logger.info(f'Got get directions HTML for {venue_link_name}: {text}')
        lines = [x for x in text.split('\n') if 'Get directions' in x and 'q=' in x]
        logger.info(f'Got lines with directions for {venue_link_name}: {lines}')
        if lines:
            line = lines[0]
            lat, lon = map(float, line.split('q=')[1].split('"')[0].split(','))
            return lat, lon
        time.sleep(5.0)
    raise Exception(f'Cannot find directions to {venue_link_name} VUE cinema')

def get_all_venues(revision: int, **kwargs) -> List[structs.Venue]:
    url = 'https://www.myvue.com/api/microservice/showings/cinemas'
    headers = {
  'authority': 'www.myvue.com' ,
  'accept': '*/*' ,
  'accept-language': 'ru,en;q=0.9' ,
  'referer': 'https://www.myvue.com/cinema/westfield-stratford-city/whats-on' ,
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"' ,
  'sec-ch-ua-mobile': '?1' ,
  'sec-ch-ua-platform': '"Android"' ,
  'sec-fetch-dest': 'empty' ,
  'sec-fetch-mode': 'cors' ,
  'sec-fetch-site': 'same-origin' ,
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36' ,
  'x-requested-with': 'XMLHttpRequest' ,
    }
    js = httplib.get_json(revision, url, headers)
    all_venues = []
    if 'result' not in js:
        logger.error("No result in venues response")
        return []
    for item in js['result']:
        for cinema in item['cinemas']:
            id_ = cinema['cinemaId']
            name = cinema['cinemaName']
            link_name = cinema['whatsOnUrl'].split('/')[4]
            lat = lon = None
            link = f'https://www.myvue.com/cinema/{link_name}/about'
            all_venues.append(structs.Venue(id_, name, 'VUE', lat, lon, link, True))
    return all_venues

def get_venue_ids(revision: int):
    url = 'https://www.myvue.com/data/locations/'
    headers = {
  'authority': 'www.myvue.com' ,
  'accept': '*/*' ,
  'accept-language': 'ru,en;q=0.9' ,
  'referer': 'https://www.myvue.com/cinema/westfield-stratford-city/whats-on' ,
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"' ,
  'sec-ch-ua-mobile': '?1' ,
  'sec-ch-ua-platform': '"Android"' ,
  'sec-fetch-dest': 'empty' ,
  'sec-fetch-mode': 'cors' ,
  'sec-fetch-site': 'same-origin' ,
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36' ,
  'x-requested-with': 'XMLHttpRequest' ,
    }
    js = httplib.get_json(revision, url, headers)
    ids = set()
    names = {}
    venues = []
    for item in js['venues']:
        for cinema in item['cinemas']:
            id_ = cinema['id']
            name = cinema['search_term']
            ids.add(id_)
            names[id_] = name
            venues.append((id_, name))
    return venues

def get_all_movies(revision: int, **kwargs) -> List[structs.Movie]:
    url = 'https://www.myvue.com/api/microservice/showings/films'
    headers = {
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'Referer': 'https://www.myvue.com/whats-on',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?1',
  'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
  'sec-ch-ua-platform': '"Android"',
    }
    js = httplib.get_json(revision, url, headers)
    movies = []
    if 'result' not in js or not js['result']:
        logger.error("No result in movies response")
        return []
    for item in js['result']:
        id_ = item['filmId']
        title = item['filmTitle']
        poster_link = item['posterImageSrc']
        synopsis = item['synopsisShort']
        release_date = item['releaseDate']
        running_time = item['runningTime']
        director = item['director']
        cast = item['cast']
        link = item['filmUrl']
        available = item['hasSessions']
        additional_info = {
            'synopsis': synopsis,
            'image_link': poster_link,
        }
        movies.append(structs.Movie(id_, title, 'VUE', link, available, additional_info))
    logger.info(f"Got {len(movies)} movies from VUE")
    return movies

def get_movie_ids(revision: int):
    url = 'https://www.myvue.com/data/filmswithshowings/'
    headers = {
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'Referer': 'https://www.myvue.com/whats-on',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?1',
  'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
  'sec-ch-ua-platform': '"Android"',
    }
    js = httplib.get_json(revision, url, headers)
    ids = set()
    titles = {}
    movies = []
    for item in js['films']:
        id_ = item['id']
        title = item['title']
        ids.add(id_)
        titles[id_] = title
        movies.append((id_, title))
    return movies
    

def get_movie_showings(revision: int, venue_id):
    url = f'https://www.myvue.com/api/microservice/showings/cinemas/{venue_id}/films'
    headers = {
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'Referer': 'https://www.myvue.com/film/insidious-the-red-door/times',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?1',
  'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
  'sec-ch-ua-platform': '"Android"',
    }
    js = httplib.get_json(revision, url, headers)
    showings = []
    if 'result' not in js:
        logger.error("No result in showings response")
        return []
    for item in js['result']:
        movie_id = item['filmId']
        for showing_group in item['showingGroups']:
            date = showing_group['date']
            for showing in showing_group['sessions']:
                start_time = showing['startTime']
                price = showing['formattedPrice']
                id_ = showing['sessionId']
                link = f'https://www.myvue.com' + showing['bookingUrl']
                available = showing['isBookingAvailable']
                showings.append(structs.Showing(id_, movie_id, venue_id, build_datetime(date, start_time), 'VUE', link, available))
    return showings

def build_datetime(date, time):
    return datetime.datetime.strptime(f'{date} {time}', '%Y-%m-%d %I:%M %p')

def get_all_showings(revision: int, **kwargs) -> List[structs.Showing]:
    return []
    venues = get_all_venues(revision)

    all_showings = []

    for venue in venues:
        venue_name = venue.name
        venue_id = venue.id_
        logger.info(f"Processing {venue_name}")
        showings = get_movie_showings(revision, venue_id)
        all_showings.extend(showings)
    return all_showings
