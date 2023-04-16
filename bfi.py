import datetime

import structs
import logging
import ast
import httplib


formatter = logging.Formatter('%(asctime)s, %(name)s %(levelname)s %(message)s')
handler = logging.FileHandler('bfi.log')
handler.setFormatter(formatter)
logger = logging.getLogger('bfi')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

SUBSITES = [
    {
        'sub_url': '',
        'article_search_id': '25E7EA2E-291F-44F9-8EBC-E560154FDAEB',
        'venue_id': "BFI Southbank",
    },
    {
        'sub_url': 'imax/',
        'article_search_id': '49C49C83-6BA0-420C-A784-9B485E36E2E0',
        'venue_id': "BFI IMAX",
    },
]

def get_all_venues(**kwargs):
    return [
        structs.Venue("BFI Southbank", 'BFI Southbank', 'BFI', 51.5067731, -0.1151379, 'https://whatson.bfi.org.uk/Online/default.asp', True),
        structs.Venue("BFI IMAX", 'BFI IMAX', 'BFI', 51.5048807, -0.1136915, 'https://whatson.bfi.org.uk/imax/Online/default.asp', True),
    ]

def get_movies_from_subsite(revision: int, sub_url: str, venue_id: str, article_search_id: str):
    url = f'https://whatson.bfi.org.uk/{sub_url}Online/default.asp'
    headers = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'Accept-Language': 'ru,en;q=0.9',
  'Cache-Control': 'max-age=0',
  'Connection': 'keep-alive',
  'Content-Type': 'application/x-www-form-urlencoded',
  'Origin': 'https://whatson.bfi.org.uk',
  'Referer': f'https://whatson.bfi.org.uk/{sub_url}Online/default.asp',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-User': '?1',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
    }
    text = httplib.post_with_text_response(revision, url, f'BOparam%3A%3AWScontent%3A%3Asearch%3A%3Aarticle_search_id={article_search_id}&doWork%3A%3AWScontent%3A%3Asearch=1', headers)
    inside = False
    logger.info(f"HTML: {text}")

    movies_by_id = {}

    for line in text.split('\n'):
        if 'searchResults :' in line:
            inside = True
            continue
        if inside:
            if line == '  ],':
                break
            logger.info(f"Parsing {line}")
            parts = ast.literal_eval(line.strip().rstrip(','))
            # hh =  [ "Id", "Object Type", "Type", "Category", "Name", "Description", "Short Description", "-", "- time", "- date", "- month", "- year", "End Date", "On Sale Date", "Sales Status", "Availability", "Available Number", "Keywords", "Additional Info", "Group", "Image 1", "Image 2", "image1_alt_text", "image2_alt_text", "thumbnail", "Data 1", "Data 2", "Data 3", "Data 4", "Data 5", "Data 6", "Data 7", "Data 8", "Data 9", "Data 10", "Data 11", "Data 12", "Data 13", "Data 14", "Data 15", "Data 16", "filter1", "filter2", "filter3", "filter4", "filter_parent1", "filter_child2", "filter_parent2", "filter_child1", "multifilter1", "multifilter2", "Organization Short Description", "Sales Type", "Options", "Street", "City", "Province / State", "Postal Code", "Country", "Longitude", "Latitude", "Venue ID", "Venue Name", "Venue Description", "Venue Short Description", "Venue Group", "Venue Data 1", "Venue Data 2", "Venue Data 3", "Venue Data 4", "Venue Data 5", "Venue Data 6", "Venue Data 7", "Venue Data 8", "Venue Data 9", "Venue Data 10", "Venue Data 11", "Venue Data 12", "Venue Type", "Series Name", "Minimum Price", "Maximum Price", "Upsell Article", "Add-on Article", "email", "e_address1", "e_address2", "e_address3", "customer_id", "tracking_code", "twitter_search_term", "external_reference_code", "access", "Venue Organization Id", "Meta Description", "" ]
            title = parts[5]
            link_info = parts[18]
            if not link_info:
                logger.warning(f"Cannot find link info in line: {line}. Skipping...")
                continue
            movie_id = link_info.split('BOparam::WScontent::loadArticle::article_id=')[1].split('&')[0]
            link = f'https://whatson.bfi.org.uk/{sub_url}Online/default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=' + movie_id
            movies_by_id[movie_id] = structs.Movie(movie_id, title, 'BFI', link, True)
    movies = list(movies_by_id.values())
    logger.info(f"Got {len(movies)} movies from BFI {sub_url} {venue_id}")
    return movies

def get_showings_from_subsite(revision: int, sub_url: str, venue_id: str, article_search_id: str):
    url = f'https://whatson.bfi.org.uk/{sub_url}Online/default.asp'
    headers = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'Accept-Language': 'ru,en;q=0.9',
  'Cache-Control': 'max-age=0',
  'Connection': 'keep-alive',
  'Content-Type': 'application/x-www-form-urlencoded',
  'Origin': 'https://whatson.bfi.org.uk',
  'Referer': f'https://whatson.bfi.org.uk/{sub_url}Online/default.asp',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-User': '?1',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
    }
    text = httplib.post_with_text_response(revision, url, f'BOparam%3A%3AWScontent%3A%3Asearch%3A%3Aarticle_search_id={article_search_id}&doWork%3A%3AWScontent%3A%3Asearch=1', headers)
    inside = False
    logger.info(f"HTML: {text}")

    showings = []

    for line in text.split('\n'):
        if 'searchResults :' in line:
            inside = True
            continue
        if inside:
            if line == '  ],':
                break
            logger.info(f"Parsing {line}")
            parts = ast.literal_eval(line.strip().rstrip(','))
            id_ = parts[0]
            title = parts[5]
            start_time = datetime.datetime.fromisoformat(f"{parts[11]}-{int(parts[10])+1:02}-{int(parts[9]):02}T{parts[8]}:00")
            if '2' in parts[53]:
                link = f'https://whatson.bfi.org.uk/{sub_url}Online/mapSelect.asp?BOparam::WSmap::loadMap::performance_ids={id_}'
            else:
                link = f'https://whatson.bfi.org.uk/{sub_url}Online/seatSelect.asp?BOparam::WSmap::loadMap::performance_ids={id_}'
            available = int(parts[16]) > 0
            price = parts[80] # min
            price = parts[81] # max
            link_info = parts[18]
            if not link_info:
                logger.warning(f"Cannot find link info in line: {line}. Skipping...")
                continue
            movie_id = link_info.split('BOparam::WScontent::loadArticle::article_id=')[1].split('&')[0]
            logger.info(f"Processing {title} in {venue_id} at {start_time}")
            showings.append(structs.Showing(id_, movie_id, venue_id, start_time, 'BFI', link, available))

    logger.info(f"Got {len(showings)} showings in BFI {sub_url} {venue_id}")
    return showings

def get_all_movies(revision: int, **kwargs) -> structs.Showing:
    all_movies = []
    for subsite in SUBSITES:
        movies = get_movies_from_subsite(revision, subsite['sub_url'], subsite['venue_id'], subsite['article_search_id'])
        all_movies.extend(movies)
    logger.info(f"Got {len(all_movies)} movies from BFI")
    return all_movies


def get_all_showings(revision: int, **kwargs) -> structs.Showing:
    all_showings = []
    for subsite in SUBSITES:
        showings = get_showings_from_subsite(revision, subsite['sub_url'], subsite['venue_id'], subsite['article_search_id'])
        all_showings.extend(showings)
    logger.info(f"Got {len(all_showings)} showings from BFI")
    return all_showings
