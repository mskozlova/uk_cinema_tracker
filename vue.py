import requests
import time
import datetime

import structs
import logging

from typing import List


formatter = logging.Formatter('%(asctime)s, %(name)s %(levelname)s %(message)s')
handler = logging.FileHandler('vue.log')
handler.setFormatter(formatter)
logger = logging.getLogger('vue')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

def get_venue_location(venue_link_name):
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
        r = requests.get(url, headers=headers)
        time.sleep(0.1)
        logger.info(f'Got get directions HTML for {venue_link_name}: {r.text}')
        lines = [x for x in r.text.split('\n') if 'Get directions' in x and 'q=' in x]
        logger.info(f'Got lines with directions for {venue_link_name}: {lines}')
        if lines:
            line = lines[0]
            lat, lon = map(float, line.split('q=')[1].split('"')[0].split(','))
            return lat, lon
        time.sleep(5.0)
    raise Exception(f'Cannot find directions to {venue_link_name} VUE cinema')

def get_all_venues(**kwargs) -> List[structs.Venue]:
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
    r = requests.get(url, headers=headers)
    time.sleep(0.1)
    js = r.json()
    all_venues = []
    for item in js['venues']:
        for cinema in item['cinemas']:
            id_ = cinema['id']
            name = cinema['search_term']
            available = not cinema['hidden']
            link_name = cinema['link_name']
            lat, lon = get_venue_location(link_name)
            link = f'https://www.myvue.com/cinema/{link_name}/about'
            all_venues.append(structs.Venue(id_, name, 'VUE', lat, lon, link, available))
    return all_venues

def get_venue_ids():
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
    r = requests.get(url, headers=headers)
    js = r.json()
    ids = set()
    names = {}
    venues = []
    for item in js['venues']:
        for cinema in item['cinemas']:
            id_ = cinema['id']
            name = cinema['search_term']
            #print(name, id_)
            ids.add(id_)
            names[id_] = name
            venues.append((id_, name))
    return venues

def get_all_movies(**kwargs) -> List[structs.Movie]:
    url = 'https://www.myvue.com/data/filmswithshowings/'
    headers = {
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'Referer': 'https://www.myvue.com/whats-on',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?1',
  'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
  'sec-ch-ua-platform': '"Android"',
    }
    r = requests.get(url, headers=headers)
    js = r.json()
    movies = []
    for item in js['films']:
        del item['showings']
        id_ = item['id']
        title = item['title']
        poster_link = item['image_poster']
        synopsis = item['synopsis_short']
        release_date = item['info_release']
        running_time = item['info_runningtime']
        director = item['info_director']
        cast = item['info_cast']
        link = 'https://www.myvue.com' + item['filmlink']
        trailer_link = item['video']
        available = not item['hidden']
        movies.append(structs.Movie(id_, title, 'VUE', link, available))
    logger.info(f"Got {len(movies)} from VUE")
    return movies

def get_movie_ids():
    url = 'https://www.myvue.com/data/filmswithshowings/'
    headers = {
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'Referer': 'https://www.myvue.com/whats-on',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?1',
  'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
  'sec-ch-ua-platform': '"Android"',
    }
    r = requests.get(url, headers=headers)
    js = r.json()
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
    

def get_movie_showings(movie_id, venue_id):
    url = f'https://www.myvue.com/data/showings/{movie_id}/{venue_id}'
    headers = {
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'Referer': 'https://www.myvue.com/film/insidious-the-red-door/times',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?1',
  'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
  'sec-ch-ua-platform': '"Android"',
    }
    r = requests.get(url, headers=headers)
    time.sleep(0.1)
    js = r.json()
    showings = []
    for item in js['showings']:
        date = item['date_time']
        for time_item in item['times']:
            start_time = time_item['time']
            screen_name = time_item['screen_name']
            screen_type = time_item['screen_type']
            # time_item['hidden'] or time_item['disabled']
            price = time_item['default_price']
            id_ = time_item['session_id']
            link = f'https://www.myvue.com/book-tickets/summary/{venue_id}/{movie_id}/{id_}'
            showings.append(structs.Showing(id_, movie_id, venue_id, build_datetime(date, start_time), 'VUE', link, True))
    return showings

def build_datetime(date, time):
    return datetime.datetime.strptime(f'{date} {time}', '%Y-%m-%d %I:%M %p')

def get_all_showings(**kwargs) -> List[structs.Showing]:
    movies = get_movie_ids()
    venues = get_venue_ids()

    all_showings = []

    for venue_id, venue_name in venues:
        logger.info(f"Processing {venue_name}")
        ###########
        # if 'London' not in venue_name:
        #     continue
        ###########
        for movie_id, movie_name in movies:
            showings = get_movie_showings(movie_id, venue_id)
            all_showings.extend(showings)
    return all_showings
