import structs
import logging
import datetime
import re
import httplib
import subprocess
import time

from typing import List

formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler = logging.FileHandler('odeon.log')
handler.setFormatter(formatter)
logger = logging.getLogger('odeon')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def get_all_venues(revision, **kwargs) -> List[structs.Venue]:
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
    js = httplib.get_json(revision, url, headers)
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

def get_movie_image(revision: int, link: str):
    args = [
        'curl', '-s', '-L', link,
        '-H', "authority: www.odeon.co.uk",
        '-H', "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        '-H', "accept-language:ru,en;q=0.9",
        '-H', "cache-control:max-age=0",
        '-H', "sec-ch-ua:\"Not.A/Brand\";v=\"8\",\"Chromium\";v=\"114\",\"YaBrowser\";v=\"23\"",
        '-H', "sec-ch-ua-mobile:?1",
        '-H', "sec-ch-ua-platform:Android",
        '-H', "sec-fetch-dest:document",
        '-H', "sec-fetch-mode:navigate",
        '-H', "sec-fetch-site:none",
        '-H', "sec-fetch-user:?1",
        '-H', "upgrade-insecure-requests:1",
        '-H', "user-agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile \"Safari/537.36\""]
    o = subprocess.check_output(args)
    time.sleep(0.1)
    text = o.decode()
    for line in text.split('\n'):
        line = line.strip()
        if '<img' not in line:
            continue
        if 'class="v-image__img"' not in line:
            continue
        return line.split('src="', 1)[1].split('">')[0]
    logger.error(f"Cannot find image in {link}")
    return None


def get_all_movies(revision: int, **kwargs) -> List[structs.Movie]:
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
    js = httplib.get_json(revision, url, headers)
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
        normalized_name = re.sub('[^a-z0-9\-]', '', title.lower().replace(' ', '-'))
        link = f'https://www.odeon.co.uk/films/{normalized_name}/{id_}'
        #image_link = get_movie_image(revision, link)
        additional_info = {
            'synopsis': synopsis,
            #'image_link': image_link,
            'trailer_link': trailer_link,
        }
        movies.append(structs.Movie(id_, title, 'ODEON', link, True, additional_info))
    logger.info(f"Got {len(movies)} movies from ODEON")
    return movies


def get_all_showings(revision: int, **kwargs) -> List[structs.Showing]:
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
    js = httplib.get_json(revision, url, headers)
    all_showings = []
    for item in js:
        title = item['Title']
        movie_id = item['ID']
        logger.info(f"Processing movie {title}")
        if 'sessions' not in item:
            logger.error(f"No sessions for movie {title}")
            continue
        for session in item['sessions']:
            venue_id = session['CinemaId']
            logger.info(f"Processing {title} showings in {venue_id}")
            for showing in session['Showings']:
                id_ = showing['ID']
                start_time = datetime.datetime.fromisoformat(showing['Showtime'])
                screen_name = showing['ScreenName']
                link = f'https://www.odeon.co.uk/ticketing/seat-picker/?showtimeId={id_}'
                all_showings.append(structs.Showing(id_, movie_id, venue_id, start_time, 'ODEON', link, True))
    logger.info(f"Got {len(all_showings)} showings from ODEON")
    return all_showings
