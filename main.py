import vue
import odeon
import cineworld
import picturehouse
import bfi
import curzon
import electric_cinema
import everyman
import sqlite3
import datetime
import concurrent.futures

import model 
import logging
import time

logging.basicConfig(filename='main.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger()

def main():
    con = sqlite3.connect('movies.db')

    revision = int(datetime.datetime.now().timestamp() * 1000000)

    def create_get_all_task(module):
        kwargs = {'revision': revision}
        def task():
            st = time.time()
            venues = module.get_all_venues(**kwargs)
            movies = module.get_all_movies(**kwargs)
            showings = module.get_all_showings(**kwargs)
            logger.info(f"Finished everything for {module} in {time.time() - st} seconds")
            return venues, movies, showings
        return task

    tasks = [
        create_get_all_task(vue),
        create_get_all_task(odeon),
        create_get_all_task(cineworld),
        create_get_all_task(picturehouse),
        create_get_all_task(bfi),
        create_get_all_task(curzon),
        create_get_all_task(electric_cinema),
        create_get_all_task(everyman),
    ]

    all_venues = []
    all_movies = []
    all_showings = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        running_tasks = [executor.submit(task) for task in tasks]
        while running_tasks:
            failed, running_tasks = concurrent.futures.wait(running_tasks, return_when=concurrent.futures.FIRST_EXCEPTION, timeout=3.0)
            for task in failed:
                logger.error(f"Exception: {task.exception()}", exc_info=task.exception())
                task.result()
                exit(1)

            done, running_tasks = concurrent.futures.wait(running_tasks, return_when=concurrent.futures.FIRST_COMPLETED, timeout=3.0)
            for task in done:
                venues, movies, showings = task.result()
                all_venues.extend(venues)
                all_movies.extend(movies)
                all_showings.extend(showings)


    model.save_venues(con, all_venues, revision)
    model.save_movies(con, all_movies, revision)
    model.save_showings(con, all_showings, revision)

    con.close()

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        logger.error("Exception in the main: ", exc_info=exc)
        raise
