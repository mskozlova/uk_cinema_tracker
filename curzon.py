import requests
import time
import datetime

import structs
import logging
import json
import collections
from functools import cache
from typing import List


formatter = logging.Formatter('%(asctime)s, %(name)s %(levelname)s %(message)s')
handler = logging.FileHandler('curzon.log')
handler.setFormatter(formatter)
logger = logging.getLogger('curzon')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


@cache
def get_token(revision):
    url = 'https://www.curzon.com/films/'
    headers = {
  'authority': 'www.curzon.com',
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'ru,en;q=0.9',
  'referer': 'https://www.curzon.com/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    logger.info(f"HTML: {r.text}")
    line = [x for x in r.text.split('\n') if '"authToken"' in x][0]
    return json.loads(line[line.index('{'):line.rindex('}')+1])['api']['authToken']

def get_all_movies(revision, *args):
    token = get_token(revision)
    url = 'https://vwc.curzon.com/WSVistaWebClient/ocapi/v1/films'
    headers = {
  'authority': 'vwc.curzon.com',
  'accept': 'application/json',
  'accept-language': 'ru,en;q=0.9',
  'authorization': f'Bearer {token}',
  'origin': 'https://www.curzon.com',
  'referer': 'https://www.curzon.com/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    js = r.json()
    movies = []
    for item in js['films']:
        id_ = item['id']
        title = item['title']['text']
        synopsis = item['synopsis']['text']
        release_date = item['releaseDate']
        running_time = item['runtimeInMinutes']
        trailer_link = item['trailerUrl']
        cast = item['castAndCrew']
        link = f'https://www.curzon.com/films/{id_}/'
        movies.append(structs.Movie(id_, title, 'Curzon', link, True))
    logger.info(f"Got {len(movies)} movies from Curzon")
    return movies

def get_all_movies_old(token):
    url = 'https://vwc.curzon.com/WSVistaWebClient/ocapi/v1/films'
    headers = {
  'authority': 'vwc.curzon.com',
  'accept': 'application/json',
  'accept-language': 'ru,en;q=0.9',
  'authorization': f'Bearer {token}',
  'origin': 'https://www.curzon.com',
  'referer': 'https://www.curzon.com/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    js = r.json()
    movies = []
    for item in js['films']:
        id_ = item['id']
        title = item['title']['text']
        movies.append((id_, title))
    return movies

def get_venue_location(link):
    url = link
    headers = {
  'authority': 'www.curzon.com',
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'ru,en;q=0.9',
  'referer': 'https://www.curzon.com/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    time.sleep(0.1)
    logger.info(f"Got HTML from {link}: {r.text}")
    lines = [x for x in r.text.split('\n') if 'get directions' in x.lower() and 'google.' in x and '/maps' in x]
    logger.info(f"Got direction lines from {link}: {lines}")
    parts = lines[0].split('/@')[1].split(',')
    return float(parts[0]), float(parts[1])


def get_all_venues(revision=None, token=None, **args):
    if not token:
        token = get_token(revision)
    url = 'https://vwc.curzon.com/WSVistaWebClient/ocapi/v1/sites'
    headers = {
  'authority': 'vwc.curzon.com',
  'accept': 'application/json',
  'accept-language': 'ru,en;q=0.9',
  'authorization': f'Bearer {token}',
  'origin': 'https://www.curzon.com',
  'referer': 'https://www.curzon.com/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    time.sleep(0.1)
    js = r.json()
    venues = []
    for item in js['sites']:
        id_ = item['id']
        name = item['name']['text']
        link_name = name.lower().replace(' ', '-')
        city = item['contactDetails']['address']['line2']
        postcode = item['contactDetails']['address']['city']
        link = f'https://www.curzon.com/venues/{link_name}/'
        if item['location']:
            lat = item['location']['latitude']
            lon = item['location']['longitude']
        else:
            lat, lon = get_venue_location(link)
        venues.append(structs.Venue(id_, name, 'Curzon', lat, lon, link, True))
    return venues

def get_all_venues_old(token):
    url = 'https://vwc.curzon.com/WSVistaWebClient/ocapi/v1/sites'
    headers = {
  'authority': 'vwc.curzon.com',
  'accept': 'application/json',
  'accept-language': 'ru,en;q=0.9',
  'authorization': f'Bearer {token}',
  'origin': 'https://www.curzon.com',
  'referer': 'https://www.curzon.com/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    js = r.json()
    venues = []
    for item in js['sites']:
        id_ = item['id']
        name = item['name']['text']
        venues.append((id_, name))
    return venues

def get_all_dates(token):
    url = 'https://vwc.curzon.com/WSVistaWebClient/ocapi/v1/film-screening-dates'
    headers = {
  'authority': 'vwc.curzon.com',
  'accept': 'application/json',
  'accept-language': 'ru,en;q=0.9',
  'authorization': f'Bearer {token}',
  'origin': 'https://www.curzon.com',
  'referer': 'https://www.curzon.com/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    js = r.json()
    sites_by_date = collections.defaultdict(set)
    films_by_date = collections.defaultdict(set)
    for item in js['filmScreeningDates']:
        date = item['businessDate']
        for screening_item in item['filmScreenings']:
            films_by_date[date].add(screening_item['filmId'])
            for site_item in screening_item['sites']:
                sites_by_date[date].add(site_item['siteId'])
    return sites_by_date, films_by_date

def get_all_showings_old(revision, **args):
    token = get_token(revision)
    venues = get_all_venues_old(token)
    movies = get_all_movies(token)
    sites_by_date, films_by_date = get_all_dates(token)
    movie_name_by_id = {id_: name for id_, name in movies}
    venue_name_by_id = {id_: name for id_, name in venues}
    dates = set(sites_by_date.keys()) & set(films_by_date.keys())
    all_showings = []
    for date in dates:
        url = f'https://vwc.curzon.com/WSVistaWebClient/ocapi/v1/showtimes/by-business-date/{date}?'
        for movie_id in films_by_date[date]:
            url += f"filmIds={movie_id}&"
        for venue_id in sites_by_date[date]:
            url += f"siteIds={venue_id}&"
        url = url[:-1]
        headers = {
    'authority': 'vwc.curzon.com',
    'accept': 'application/json',
    'accept-language': 'ru,en;q=0.9',
    'authorization': f'Bearer {token}',
    'origin': 'https://www.curzon.com',
    'referer': 'https://www.curzon.com/',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        }
        r = requests.get(url, headers=headers)
        time.sleep(0.1)
        js = r.json()
        for item in js['showtimes']:
            logger.info(f"Processing showtime: {item}")
            movie_id = item['filmId']
            movie_name = movie_name_by_id.get(movie_id)
            if not movie_name:
                logger.warning(f"Cannot find movie name for id={movie_id}")
                continue
            venue_id = item['siteId']
            venue_name = venue_name_by_id.get(venue_id)
            if not venue_name:
                logger.warning(f"Cannot find venue name for id={venue_id}")
                continue
            start_time = datetime.datetime.fromisoformat(item['schedule']['startsAt'].split('+')[0])
            all_showings.append(structs.Showing(movie_name, venue_name, start_time, 'Curzon'))
    logger.info(f"Got {len(all_showings)} showings from Curzon")
    return all_showings


def get_all_showings(revision, **args) -> List[structs.ShowingNew]:
    token = get_token(revision)
    sites_by_date, films_by_date = get_all_dates(token)
    dates = set(sites_by_date.keys()) & set(films_by_date.keys())
    all_showings = []
    for date in dates:
        url = f'https://vwc.curzon.com/WSVistaWebClient/ocapi/v1/showtimes/by-business-date/{date}?'
        for movie_id in films_by_date[date]:
            url += f"filmIds={movie_id}&"
        for venue_id in sites_by_date[date]:
            url += f"siteIds={venue_id}&"
        url = url[:-1]
        headers = {
    'authority': 'vwc.curzon.com',
    'accept': 'application/json',
    'accept-language': 'ru,en;q=0.9',
    'authorization': f'Bearer {token}',
    'origin': 'https://www.curzon.com',
    'referer': 'https://www.curzon.com/',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        }
        r = requests.get(url, headers=headers)
        time.sleep(0.1)
        js = r.json()
        for item in js['showtimes']:
            logger.info(f"Processing showtime: {item}")
            id_ = item['id']
            movie_id = item['filmId']
            venue_id = item['siteId']
            start_time = datetime.datetime.fromisoformat(item['schedule']['startsAt'].split('+')[0])
            link = f'https://www.curzon.com/ticketing/seats/{id_}/'
            available = not item['isSoldOut']
            screen_name = item['screenId']
            all_showings.append(structs.ShowingNew(id_, movie_id, venue_id, start_time, 'Curzon', link, available))
    logger.info(f"Got {len(all_showings)} showings from Curzon")
    return all_showings
