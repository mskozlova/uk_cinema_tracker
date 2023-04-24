import datetime

import structs
import logging
import ast
import httplib
import re


formatter = logging.Formatter('%(asctime)s, %(name)s %(levelname)s %(message)s')
handler = logging.FileHandler('bfi.log')
handler.setFormatter(formatter)
logger = logging.getLogger('bfi')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def get_all_venues(**kwargs):
    return [
        structs.Venue("BFI Southbank", 'BFI Southbank', 'BFI', 51.5067731, -0.1151379, 'https://whatson.bfi.org.uk/Online/default.asp', True),
        structs.Venue("BFI IMAX", 'BFI IMAX', 'BFI', 51.5048807, -0.1136915, 'https://whatson.bfi.org.uk/imax/Online/default.asp', True),
    ]

def get_synopsis(revision: int, link: str):
    headers = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'Accept-Language': 'ru,en;q=0.9',
  'Cache-Control': 'max-age=0',
  'Connection': 'keep-alive',
  'Content-Type': 'application/x-www-form-urlencoded',
  'Origin': 'https://whatson.bfi.org.uk',
  'Referer': f'https://whatson.bfi.org.uk/Online/default.asp',
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
    text = httplib.get_text(revision, link, headers)
    fallback = None
    for line in text.split('\n'):
        line = line.strip()
        if 'og:description' in line:
            syn = line.split('content="', 1)[1].rsplit('"', 1)[0].strip()
            if len(syn) > 5:
                fallback = syn
        if 'Page__description' not in line:
            continue
        return line.split('>', 1)[1].rsplit('<', 1)[0]
    if fallback is None:
        logger.error(f"Cannot find synopsis in {link}")
    return fallback

def get_image(revision: int, link: str):
    headers = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'Accept-Language': 'ru,en;q=0.9',
  'Cache-Control': 'max-age=0',
  'Connection': 'keep-alive',
  'Content-Type': 'application/x-www-form-urlencoded',
  'Origin': 'https://whatson.bfi.org.uk',
  'Referer': f'https://whatson.bfi.org.uk/Online/default.asp',
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
    text = httplib.get_text(revision, link, headers)
    fallback = None
    for line in text.split('\n'):
        line = line.strip()
        if 'Media__image' not in line:
            continue
        image_url = line.split('class="Media__image" src="', 1)[1].rsplit('"', 1)[0]
        if image_url.startswith('/'):
            return 'https://whatson.bfi.org.uk' + image_url
        return image_url
    logger.error(f"Cannot find image in {link}")
    return None

def get_trailer(revision: int, link: str):
    headers = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'Accept-Language': 'ru,en;q=0.9',
  'Cache-Control': 'max-age=0',
  'Connection': 'keep-alive',
  'Content-Type': 'application/x-www-form-urlencoded',
  'Origin': 'https://whatson.bfi.org.uk',
  'Referer': f'https://whatson.bfi.org.uk/Online/default.asp',
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
    text = httplib.get_text(revision, link, headers)
    fallback = None
    for line in text.split('\n'):
        line = line.strip()
        if '"link": "https://youtu.be' not in line:
            continue
        return line.split('"link": "', 1)[1].rsplit('"', 1)[0]
    return None

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
            if 'default.asp?BOparam::WScontent::loadArticle::permalink=' in link_info:
                movie_id = link_info.split('BOparam::WScontent::loadArticle::permalink=')[1].split('&')[0]
                link = f'https://whatson.bfi.org.uk/{sub_url}Online/' + link_info
            else:
                movie_id = link_info.split('BOparam::WScontent::loadArticle::article_id=')[1].split('&')[0]
                link = f'https://whatson.bfi.org.uk/{sub_url}Online/default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=' + movie_id
            additional_info = {
                'synopsis': get_synopsis(revision, link),
                'image_link': get_image(revision, link),
                'trailer_link': get_trailer(revision, link),
            }
            movies_by_id[movie_id] = structs.Movie(movie_id, title, 'BFI', link, True, additional_info)
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
            if 'default.asp?BOparam::WScontent::loadArticle::permalink=' in link_info:
                movie_id = link_info.split('BOparam::WScontent::loadArticle::permalink=')[1].split('&')[0]
                link = f'https://whatson.bfi.org.uk/{sub_url}Online/' + link_info
            else:
                movie_id = link_info.split('BOparam::WScontent::loadArticle::article_id=')[1].split('&')[0]
            logger.info(f"Processing {title} in {venue_id} at {start_time}")
            showings.append(structs.Showing(id_, movie_id, venue_id, start_time, 'BFI', link, available))

    logger.info(f"Got {len(showings)} showings in BFI {sub_url} {venue_id}")
    return showings

def get_article_search_id(revision: int, url: str):
    headers = {
  'authority': 'www.bfi.org.uk',
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'ru,en;q=0.9',
  'cache-control': 'max-age=0',
  'referer': 'https://whatson.bfi.org.uk/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-site',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    text = httplib.get_text(revision, url, headers)
    for line in text.split('\n'):
        line = line.strip()
        if '<input type="hidden" name="BOparam::WScontent::search::article_search_id" value="' not in line:
            continue
        return line.split('value="')[1].split('"')[0]
    logger.error(f"Cannot find article_search_id for {url}: {text}")
    return None


def get_subsites(revision: int):
    urls_to_check = [
        'https://www.bfi.org.uk',
        'https://www.bfi.org.uk/bfi-festivals'
    ]
    headers = {
  'authority': 'www.bfi.org.uk',
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'ru,en;q=0.9',
  'cache-control': 'max-age=0',
  'referer': 'https://whatson.bfi.org.uk/',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': '"Android"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-site',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    }
    subsites = []
    for url in urls_to_check:
        text = httplib.get_text(revision, url, headers)
        matches = re.findall('(https://whatson.bfi.org.uk/\\S+/default.asp)', text)
        subsites.extend(matches)
    result = []
    for url in sorted(set(subsites)):
        article_search_id = get_article_search_id(revision, url)
        if not article_search_id:
            logger.error(f"Skipping {url} because of missing article_search_id")
            continue
        sub_url = url.split('https://whatson.bfi.org.uk/', 1)[1].rsplit('Online/default.asp', 1)[0]
        result.append({
            'sub_url': sub_url,
            'article_search_id': article_search_id,
            'venue_id': 'BFI IMAX' if 'imax' in sub_url else 'BFI Southbank',
        })
    return result


def get_all_movies(revision: int, **kwargs) -> structs.Showing:
    all_movies = []
    subsites = get_subsites(revision)
    for subsite in subsites:
        movies = get_movies_from_subsite(revision, subsite['sub_url'], subsite['venue_id'], subsite['article_search_id'])
        all_movies.extend(movies)
    logger.info(f"Got {len(all_movies)} movies from BFI")
    return all_movies


def get_all_showings(revision: int, **kwargs) -> structs.Showing:
    all_showings = []
    subsites = get_subsites(revision)
    for subsite in subsites:
        showings = get_showings_from_subsite(revision, subsite['sub_url'], subsite['venue_id'], subsite['article_search_id'])
        all_showings.extend(showings)
    logger.info(f"Got {len(all_showings)} showings from BFI")
    return all_showings
