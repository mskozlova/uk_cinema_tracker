import sqlite3

from urllib.parse import urlparse
from urllib.parse import parse_qs
import compare
import model
import collections

def generate_diff_page(path: str, logger):
    o = urlparse(path)
    q = parse_qs(o.query)
    rev1 = None
    rev2 = None
    if 'rev1' in q and 'rev2' in q:
        rev1 = int(q['rev1'][0])
        rev2 = int(q['rev2'][0])

    with sqlite3.connect('movies.db') as con:
        all_revisions = compare.get_all_revisions(con)
        if not rev1:
            rev1 = all_revisions[-1] if all_revisions else 1
        if not rev2:
            rev2 = all_revisions[-1] if all_revisions else 1
        venue_diff, movie_diff, showing_diff = compare.compare_revisions(con, rev1, rev2, logger)
    
    summary = f"""
    <p>
    Venues: added {len(venue_diff.added)}, deleted {len(venue_diff.deleted)}, changed {len(venue_diff.changed)}
    </p>
    <p>
    Movies: added {len(movie_diff.added)}, deleted {len(movie_diff.deleted)}, changed {len(movie_diff.changed)}
    </p>
    <p>
    Showings: added {len(showing_diff.added)}, deleted {len(showing_diff.deleted)}, changed {len(showing_diff.changed)}
    </p>
    """

    added_venues_html_p = "\n".join([f'<p>{venue}</p>' for venue in venue_diff.added])
    added_venues_html = f"""
    <h3>Added venues</h3>
    {added_venues_html_p}
    """ if added_venues_html_p else ""

    deleted_venues_html_p = "\n".join([f'<p>{venue}</p>' for venue in venue_diff.deleted])
    deleted_venues_html = f"""
    <h3>Deleted venues</h3>
    {deleted_venues_html_p}
    """ if deleted_venues_html_p else ""

    changed_venues_html_p = "\n".join([f'<p>{venue1}</p><p>{venue2}</p><br/>' for venue1, venue2 in venue_diff.changed])
    changed_venues_html = f"""
    <h3>Changed venues</h3>
    {changed_venues_html_p}
    """ if changed_venues_html_p else ""

    added_movies_html_p = "\n".join([f'<p>{movie}</p>' for movie in movie_diff.added])
    added_movies_html = f"""
    <h3>Added movies</h3>
    {added_movies_html_p}
    """ if added_movies_html_p else ""

    deleted_movies_html_p = "\n".join([f'<p>{movie}</p>' for movie in movie_diff.deleted])
    deleted_movies_html = f"""
    <h3>Deleted movies</h3>
    {deleted_movies_html_p}
    """ if deleted_movies_html_p else ""

    changed_movies_html_p = "\n".join([f'<p>{movie1}</p><p>{movie2}</p><br/>' for movie1, movie2 in movie_diff.changed])
    changed_movies_html = f"""
    <h3>Changed movies</h3>
    {changed_movies_html_p}
    """ if changed_movies_html_p else ""

    added_showings_html_p = "\n".join([f'<p>{showing}</p>' for showing in showing_diff.added])
    added_showings_html = f"""
    <h3>Added showings</h3>
    {added_showings_html_p}
    """ if added_showings_html_p else ""

    deleted_showings_html_p = "\n".join([f'<p>{showing}</p>' for showing in showing_diff.deleted])
    deleted_showings_html = f"""
    <h3>Deleted showings</h3>
    {deleted_showings_html_p}
    """ if deleted_showings_html_p else ""

    changed_showings_html_p = "\n".join([f'<p>{showing1}</p><p>{showing2}</p><br/>' for showing1, showing2 in showing_diff.changed])
    changed_showings_html = f"""
    <h3>Changed showings</h3>
    {changed_showings_html_p}
    """ if changed_showings_html_p else ""

    options1 = "".join([f'<option value="{rev}" {"selected" if rev == rev1 else ""}>{rev}</option>' for rev in all_revisions])
    options2 = "".join([f'<option value="{rev}" {"selected" if rev == rev2 else ""}>{rev}</option>' for rev in all_revisions])
    script = """
    <script type="text/javascript">
    var update_link = function() {
        var rev1 = document.getElementById('rev1').value;
        var rev2 = document.getElementById('rev2').value;
        document.getElementById('go_link').href = '/compare?rev1=' + rev1 + '&rev2=' + rev2;
    };
    </script>
    """
    dropdown = f"""
    <select id="rev1" onchange="update_link()">
        {options1}
    </select>
    <select id="rev2" onchange="update_link()">
        {options2}
    </select>
    """

    link = f"""
    <a id="go_link" href="/compare?rev1={rev1}&rev2={rev2}">Go</a>
    """

    text = f"""
    <html>
    <head>
    {script}
    </head>
    <h1>Compare revisions</h1>
    {dropdown}
    {link}
    <h3>Summary</h3>
    {summary}
    {added_venues_html}
    {deleted_venues_html}
    {changed_venues_html}

    {added_movies_html}
    {deleted_movies_html}
    {changed_movies_html}

    {added_showings_html}
    {deleted_showings_html}
    {changed_showings_html}
    </html>
    """

    return text

def generate_venues_page(path: str, logger):
    o = urlparse(path)
    q = parse_qs(o.query)
    rev = None
    if 'rev' in q:
        rev = int(q['rev'][0])

    with sqlite3.connect('movies.db') as con:
        if not rev:
            all_revisions = model.get_all_revisions(con)
            rev = all_revisions[-1] if all_revisions else 1
        venues = model.get_venues(con, rev)
    
    by_networks = collections.defaultdict(list)
    for venue in venues:
        by_networks[venue.network_name].append(venue)
    
    venues_html = ''
    for network_name in sorted(by_networks.keys()):
        venues_html += f'<h2>{network_name}</h2>'
        for venue in sorted(by_networks[network_name], key=lambda x: x.name):
            venues_html += f'<h3>{venue.name}</h3>'
            if venue.link:
                venues_html += f'<p><a href="{venue.link}">Link</a></p>'
            if venue.lat and venue.lon:
                venues_html += f'<p><a href="https://google.co.uk/maps?q={venue.lat},{venue.lon}">Get directions</a></p>'

    text = f"""
    <html>
    <h1>Venues</h1>
    {venues_html}
    </html>
    """

    return text


def generate_movies_page(path: str, logger):
    o = urlparse(path)
    q = parse_qs(o.query)
    rev = None
    if 'rev' in q:
        rev = int(q['rev'][0])

    with sqlite3.connect('movies.db') as con:
        if not rev:
            all_revisions = model.get_all_revisions(con)
            rev = all_revisions[-1] if all_revisions else 1
        movies = model.get_movies(con, rev)
    
    by_networks = collections.defaultdict(list)
    for movie in movies:
        by_networks[movie.network_name].append(movie)
    
    movies_html = ''
    for network_name in sorted(by_networks.keys()):
        movies_html += f'<h2>{network_name}</h2>'
        for movie in sorted(by_networks[network_name], key=lambda x: x.title):
            movies_html += f'<h3>{movie.title}</h3>'
            if movie.link:
                movies_html += f'<p><a href="{movie.link}">Link</a></p>'

    text = f"""
    <html>
    <h1>Movies</h1>
    {movies_html}
    </html>
    """

    return text

def generate_search_showings_page(path: str, logger):
    o = urlparse(path)
    q = parse_qs(o.query)
    rev = None
    if 'rev' in q:
        rev = int(q['rev'][0])
    
    search_query = None
    if 'search_query' in q:
        search_query = q['search_query'][0]

    with sqlite3.connect('movies.db') as con:
        if not rev:
            all_revisions = model.get_all_revisions(con)
            rev = all_revisions[-1] if all_revisions else 1
        showings = model.search_showings(con, rev, search_query)
        movies = model.get_movies(con, rev)
        venues = model.get_venues(con, rev)
    
    movie_by_id = {movie.id_: movie for movie in movies}
    venue_by_id = {(venue.network_name, venue.id_): venue for venue in venues}
    
    by_date_and_venue = collections.defaultdict(lambda: collections.defaultdict(list))
    for showing in showings:
        by_date_and_venue[showing.start_time_local.date()][(showing.network_name, showing.venue_id)].append(showing)
    
    showings_html = ''
    for date in sorted(by_date_and_venue.keys()):
        showings_html += f'<h2>{date}</h2>'
        for venue_id in sorted(by_date_and_venue[date].keys()):
            venue = venue_by_id.get(venue_id)
            if not venue:
                logger.warning(f"Cannot find venue with id={venue_id}. Skipping...")
                continue
            showings_html += f'<h3>{venue.network_name} - {venue.name}</h3>'
            by_movie = collections.defaultdict(list)
            for showing in by_date_and_venue[date][venue_id]:
                by_movie[showing.movie_id].append(showing)
            for movie_id in sorted(by_movie.keys(), key=lambda x: movie_by_id[x].title if x in movie_by_id else ''):
                movie = movie_by_id.get(movie_id)
                if not movie:
                    logger.warning(f"Cannot find movie with id={movie_id}. Skipping...")
                    continue
                showings_html += f'<h4>{movie.title}</h4>'
                for showing in by_movie[movie_id]:
                    time = showing.start_time_local.isoformat().split('T')[1]
                    showings_html += f'<a href={showing.link}>{time}</a>' + "&nbsp;"


    text = f"""
    <html>
    <h1>Showings</h1>
    {showings_html}
    </html>
    """

    return text