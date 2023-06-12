import logging
import sqlite3
import model
import dataclasses
import json
import gzip
from vendor import jinja2
from vendor.jinja2 import Environment, PackageLoader, select_autoescape

logging.basicConfig(filename='generate_bundle.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger()

DIR = '/home/basil8/deploy/movies'

def main():
    with sqlite3.connect('movies.db') as con:
        all_revisions = model.get_all_revisions(con)
        rev = all_revisions[-1] if all_revisions else 1
        venues = model.get_venues(con, rev)
        movies = model.get_movies(con, rev)
        showings = model.get_showings(con, rev)
    venues_dicts = [dataclasses.asdict(venue) for venue in venues if venue.available]
    with open(f'{DIR}/venues.json', 'w') as f:
        json.dump(venues_dicts, f)
    movies_dicts = [dataclasses.asdict(movie) for movie in movies if movie.available]
    with open(f'{DIR}/movies.json', 'w') as f:
        json.dump(movies_dicts, f)
    showings_dicts = [dataclasses.asdict(showing) for showing in showings]
    showings_text = json.dumps(showings_dicts)
    gzipped = gzip.compress(showings_text.encode(), 5)
    with open(f'{DIR}/showings.json.gz', 'wb') as f:
        f.write(gzipped)
    env = Environment(
        loader=PackageLoader("generate_bundle"),
        autoescape=select_autoescape(),
        undefined=jinja2.StrictUndefined,
    )
    venues_html = env.get_template("venues.html").render()
    with open(f'{DIR}/venues.html', 'w') as f:
        f.write(venues_html)
    movies_html = env.get_template("movies.html").render()
    with open(f'{DIR}/movies.html', 'w') as f:
        f.write(movies_html)
    showings_html = env.get_template("showings.html").render()
    with open(f'{DIR}/showings.html', 'w') as f:
        f.write(showings_html)

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        logger.error("Exception in the main: ", exc_info=exc)
        raise
