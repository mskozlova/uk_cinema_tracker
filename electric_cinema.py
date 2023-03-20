import requests
import structs
import datetime
import logging
import time

formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler = logging.FileHandler('electric_cinema.log')
handler.setFormatter(formatter)
logger = logging.getLogger('electric_cinema')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

def get_venue_location(link_name):
    url = f'https://www.electriccinema.co.uk/wp-json/superwire/v1/path/cinemas/{link_name}/contact/'
    headers = {
    'authority': 'www.electriccinema.co.uk',
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9',
    'referer': 'https://www.electriccinema.co.uk/programme/by-film/',
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
    for item in js['body']:
        if item['objectType'] != 'contact-map':
            continue
        return item['map']['lat'], item['map']['lng']
    raise Exception(f"Cannot find location for {link_name}: {js}")


def get_all_venues(**kwargs):
    url = 'https://www.electriccinema.co.uk/data/0000000000000.json'
    headers = {
    'authority': 'www.electriccinema.co.uk',
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9',
    'referer': 'https://www.electriccinema.co.uk/programme/by-film/',
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
    for item in js['cinemas'].values():
        id_ = str(item['id'])
        name = item['title']
        link = 'https://www.electriccinema.co.uk' + item['link']
        link_name = item['link'].strip('/').split('/')[1]
        lat, lon = get_venue_location(link_name)
        address = item['address']
        venues.append(structs.Venue(id_, name, 'Electric Cinema', lat, lon, link, True))
    return venues

def get_all_movies(**args):
    url = 'https://www.electriccinema.co.uk/data/0000000000000.json'
    headers = {
    'authority': 'www.electriccinema.co.uk',
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9',
    'referer': 'https://www.electriccinema.co.uk/programme/by-film/',
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
    movies = []
    for id_, item in js['films'].items():
        title = item['title']
        poster_link = item['image']
        link = 'https://www.electriccinema.co.uk' + item['link']
        synopsis = item['short_synopsis']
        release_date = item['premiere']
        director = item['director']
        movies.append(structs.Movie(id_, title, 'Electric Cinema', link, True))
    logger.info(f"Got {len(movies)} movies from Electric Cinema")
    return movies


def get_all_showings_old(**args):
    url = 'https://www.electriccinema.co.uk/data/0000000000000.json'
    headers = {
    'authority': 'www.electriccinema.co.uk',
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9',
    'referer': 'https://www.electriccinema.co.uk/programme/by-film/',
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
    venues_name_by_id = {}
    for item in js['cinemas'].values():
        id_ = item['id']
        name = item['title']
        venues_name_by_id[id_] = name
    film_names_by_id = {}
    for id_, item in js['films'].items():
        title = item['title']
        film_names_by_id[id_] = title
        logger.info(f"Processing movie id={id_} title={title}")
    all_showings = []
    for item in js['screenings'].values():
        film_id = str(item['film'])
        film_name = film_names_by_id.get(film_id)
        if not film_name:
            logger.warning(f"Cannot find movie with id={film_id}. Skipping...")
            continue
        venue_id = item['cinema']
        venue_name = venues_name_by_id.get(venue_id)
        if not venue_name:
            logger.warning(f'Cannot find venue with id={venue_id}. Skipping...')
            continue
        start_time = datetime.datetime.fromisoformat(item['d'] + "T" + item['t'])
        logger.info(f"Processing showing of {film_name} in {venue_name} at {start_time}")
        all_showings.append(structs.Showing(film_name, venue_name, start_time, 'Electric Cinema'))
    return all_showings


def get_all_showings(**args):
    url = 'https://www.electriccinema.co.uk/data/0000000000000.json'
    headers = {
    'authority': 'www.electriccinema.co.uk',
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9',
    'referer': 'https://www.electriccinema.co.uk/programme/by-film/',
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
    all_showings = []
    for item in js['screenings'].values():
        id_ = str(item['id'])
        film_id = str(item['film'])
        venue_id = str(item['cinema'])
        start_time = datetime.datetime.fromisoformat(item['d'] + "T" + item['t'])
        available = item['bookable']
        if available or item['link']:
            link = 'https://www.electriccinema.co.uk' + item['link']
        else:
            link = None
        logger.info(f"Processing showing {id_} of {film_id} in {venue_id} at {start_time}")
        all_showings.append(structs.ShowingNew(id_, film_id, venue_id, start_time, 'Electric Cinema', link, available))
    logger.info(f"Got {len(all_showings)} showings from Electric Cinema")
    return all_showings