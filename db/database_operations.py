# db/database_operations.py
from contextlib import contextmanager
import sqlite3
import os
from datetime import datetime
import json
import re

from config.logger import log_error, log_info, log_warning

database_path = os.path.expanduser("~/.local/share/amdb/assets/movies.db")


def log_error_with_context(context, error_message):
    log_error(f"{context}: {error_message}")

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = sqlite3.connect(database_path)
        yield conn
    except sqlite3.Error as e:
        log_error(f"Database connection error: {e}")
    finally:
        if conn:
            conn.close()

def fetch_all(cursor, query, params=()):
    cursor.execute(query, params)
    return cursor.fetchall()

def fetch_one(cursor, query, params=()):
    cursor.execute(query, params)
    return cursor.fetchone()

def execute_query(cursor, query, params=()):
    cursor.execute(query, params)

def insert_with_commit(cursor, query, params=()):
    cursor.execute(query, params)
    return cursor.lastrowid

def get_or_create_id(cursor, table, column, value):
    cursor.execute(f"SELECT id FROM {table} WHERE {column} = ?", (value,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute(f"INSERT INTO {table} ({column}) VALUES (?)", (value,))
        return cursor.lastrowid

def rating_percent(ratings):
    ratings_chunks = re.findall(r'{(.*?)}', str(ratings))
    imdb_percent, metacritic_percent, rottentomatoes_percent = None, None, None
    for chunk in ratings_chunks:
        chunk = chunk.replace("'", "\"")
        rating_data = json.loads("{" + chunk + "}")
        source = rating_data["Source"]
        value_str = rating_data["Value"]
        cleaned_value = re.sub(r'[%/].*', '', value_str)
        cleaned_value = re.sub(r'[^0-9]', '', cleaned_value)
        if cleaned_value:
            rating_value = int(cleaned_value)
            if source == "Internet Movie Database":
                imdb_percent = rating_value
            elif source == "Rotten Tomatoes":
                metacritic_percent = rating_value
            elif source == "Metacritic":
                rottentomatoes_percent = rating_value
    return imdb_percent, metacritic_percent, rottentomatoes_percent

def add_new_movie(movie_data, poster_path, path):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Extract ratings
            imdb_rating, rottentomatoes_rating, metacritic_rating = rating_percent(movie_data.get('Ratings', []))

            # Calculate average rating
            ratings = [r for r in [imdb_rating, rottentomatoes_rating, metacritic_rating] if r is not None]
            average_rating = int(sum(ratings) / len(ratings)) if ratings else None

            # Insert into movies table
            last_inserted_row_id = insert_with_commit(cursor, '''
                INSERT INTO movies (imdb_id, title, year, rated, released, runtime, plot, plot_toggle, awards, 
                imdb_rating, rotten_tomatoes_rating, metacritic_rating, type, production, poster_path, path, 
                watched, u_rate, last_verified, has_parts, average_rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                movie_data.get('imdbID', ''),
                movie_data.get('Title', ''),
                movie_data.get('Year', None),
                get_or_create_id(cursor, 'ratings', 'rating', movie_data.get('Rated', '')),
                movie_data.get('Released', ''),
                movie_data.get('Runtime', ''),
                movie_data.get('Plot', ''),
                0,
                movie_data.get('Awards', ''),
                imdb_rating,
                rottentomatoes_rating,
                metacritic_rating,
                movie_data.get('Type', ''),
                movie_data.get('Production', ''),
                poster_path,
                path,
                0,
                0,
                datetime.now().strftime('%Y-%m-%d'),
                0,
                average_rating
            ))
            last_inserted_row_id = cursor.lastrowid

            # Insert into related tables
            related_tables = {
                'Genre': ('movie_genres', 'genres', 'genre', 'genre_id'),
                'Language': ('movie_languages', 'languages', 'language', 'language_id'),
                'Country': ('movie_countries', 'countries', 'country', 'country_id'),
                'Director': ('movie_directors', 'directors', 'name', 'director_id'),
                'Writer': ('movie_writers', 'writers', 'name', 'writer_id'),
                'Actors': ('movie_actors', 'actors', 'name', 'actor_id')
            }

            for key, (movie_table, main_table, column, fk_column) in related_tables.items():
                for item in movie_data.get(key, '').split(', '):
                    item_id = get_or_create_id(cursor, main_table, column, item)
                    execute_query(cursor, f'''
                        INSERT INTO {movie_table} (movie_id, {fk_column})
                        VALUES (?, ?)
                    ''', (last_inserted_row_id, item_id))

            conn.commit()
            log_info(f"Successfully added movie: {movie_data.get('Title', '')}")
            return last_inserted_row_id
    except sqlite3.Error as e:
        log_error_with_context("add_new_movie", f"Failed to add movie {movie_data.get('Title', '')}. Error: {e}")

def add_series_parts(movie_id, parts):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            for part_path in parts:
                cursor.execute("INSERT INTO movie_parts (movie_id, file_path) VALUES (?, ?)",
                               (movie_id, part_path.strip()))
            conn.commit()
    except sqlite3.Error as e:
        log_error_with_context("add_series_parts", f"Failed to add series part(s). Error: {e}")

def get_movies(details, keywords, tab, limit, offset, sort_method, descending, fields='all'):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Define the fields to select based on the argument
            if fields == 'list':
                select_fields = """
                    movies.id, movies.title, movies.year, GROUP_CONCAT(DISTINCT genres.genre) AS genre, 
                    movies.poster_path, movies.path, movies.watched, movies.keyword_scrape_date, 
                    movies.last_verified, movies.has_parts
                """
            elif fields == 'grid':
                select_fields = """
                    movies.id, movies.title, movies.year, GROUP_CONCAT(DISTINCT genres.genre) AS genre, 
                    movies.poster_path
                """
            else:  # Default to 'all' fields
                select_fields = """
                    movies.*, GROUP_CONCAT(DISTINCT directors.name) AS directors,
                    GROUP_CONCAT(DISTINCT writers.name) AS writers,
                    GROUP_CONCAT(DISTINCT actors.name) AS actors,
                    GROUP_CONCAT(DISTINCT languages.language) AS languages,
                    GROUP_CONCAT(DISTINCT countries.country) AS countries,
                    GROUP_CONCAT(DISTINCT genres.genre) AS genres
                """

            query = f"""
                SELECT {select_fields}
                FROM movies
                LEFT JOIN ratings ON movies.rated = ratings.id
                LEFT JOIN movie_directors ON movies.id = movie_directors.movie_id
                LEFT JOIN directors ON movie_directors.director_id = directors.id
                LEFT JOIN movie_writers ON movies.id = movie_writers.movie_id
                LEFT JOIN writers ON movie_writers.writer_id = writers.id
                LEFT JOIN movie_actors ON movies.id = movie_actors.movie_id
                LEFT JOIN actors ON movie_actors.actor_id = actors.id
                LEFT JOIN movie_languages ON movies.id = movie_languages.movie_id
                LEFT JOIN languages ON movie_languages.language_id = languages.id
                LEFT JOIN movie_countries ON movies.id = movie_countries.movie_id
                LEFT JOIN countries ON movie_countries.country_id = countries.id
                LEFT JOIN movie_genres ON movies.id = movie_genres.movie_id
                LEFT JOIN genres ON movie_genres.genre_id = genres.id
                WHERE 1=1
            """
            params = []

            # Apply search criteria filters
            for key, value in details.items():
                if key == 'watched':
                    query += " AND movies.watched = ?"
                    params.append(value)
                elif key == 'rating':
                    query += " AND movies.average_rating >= ?"
                    params.append(value)
                elif key == 'title':
                    query += " AND movies.title LIKE ?"
                    params.append(f"%{value}%")
                elif key == 'director':
                    query += " AND directors.name LIKE ?"
                    params.append(f"%{value}%")
                elif key == 'writer':
                    query += " AND writers.name LIKE ?"
                    params.append(f"%{value}%")
                elif key == 'actors':
                    query += " AND actors.name LIKE ?"
                    params.append(f"%{value}%")
                elif key == 'language':
                    query += " AND languages.language LIKE ?"
                    params.append(f"%{value}%")
                elif key == 'country':
                    query += " AND countries.country LIKE ?"
                    params.append(f"%{value}%")
                elif key == 'selected_rated':
                    query += " AND ratings.rating IN ({})".format(','.join(['?'] * len(value)))
                    params.extend(value)
                elif key in ['range_min', 'range_max', 'year']:
                    if key == 'range_min':
                        query += " AND movies.year >= ?"
                        params.append(value)
                    elif key == 'range_max':
                        query += " AND movies.year <= ?"
                        params.append(value)
                    elif key == 'year':
                        query += " AND movies.year = ?"
                        params.append(value)

            # Apply genres_included filter
            if 'genres_included' in details:
                genres_included = details['genres_included']
                for genre in genres_included:
                    query += f"""
                        AND movies.id IN (
                            SELECT movie_id
                            FROM movie_genres
                            JOIN genres ON movie_genres.genre_id = genres.id
                            WHERE genres.genre LIKE ?
                        )
                    """
                    params.append(f"%{genre}%")

            # Apply genres_excluded filter
            if 'genres_excluded' in details:
                genres_excluded = details['genres_excluded']
                for genre in genres_excluded:
                    query += f"""
                        AND movies.id NOT IN (
                            SELECT movie_id
                            FROM movie_genres
                            JOIN genres ON movie_genres.genre_id = genres.id
                            WHERE genres.genre LIKE ?
                        )
                    """
                    params.append(f"%{genre}%")

            # Apply alphabetic tab filter
            if tab and tab != 'All':
                if tab == '0-9':
                    query += " AND movies.title GLOB '[0-9]*'"
                elif tab == '#':
                    query += " AND movies.title GLOB '[^A-Za-z0-9]*'"
                else:
                    query += " AND movies.title LIKE ?"
                    params.append(f"{tab}%")

            # Apply keywords filter
            if keywords:
                subquery = f"""
                        SELECT movie_id FROM movie_keywords WHERE keyword_id IN (
                            SELECT id FROM keywords WHERE keyword IN ({','.join(['?'] * len(keywords))})
                        )
                    """
                query += f" AND movies.id IN ({subquery})"
                params.extend(keywords)

            query += """
                GROUP BY movies.id
            """

            # Apply sorting
            sort_columns = ['movies.id', 'movies.title', 'movies.year']  # Update with the actual columns you use
            sort_column = sort_columns[sort_method] if 0 <= sort_method < len(sort_columns) else 'movies.title'
            order = 'DESC' if descending.lower() == 'true' else 'ASC'
            query += f" ORDER BY {sort_column} {order}"

            # Add limit and offset for pagination
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            movies = fetch_all(cursor, query, params)
            conn.commit()
            return movies
    except sqlite3.Error as e:
        log_error_with_context("get_movies", f"Failed to get movie data. Error: {e}")

def get_full_movie_data(movie_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    movies.imdb_id,
                    movies.title,
                    movies.year,
                    ratings.rating,
                    movies.released,
                    movies.poster_path,
                    GROUP_CONCAT(DISTINCT genres.genre) AS genre,
                    movies.runtime,
                    GROUP_CONCAT(DISTINCT directors.name) AS directors,
                    GROUP_CONCAT(DISTINCT writers.name) AS writers,
                    GROUP_CONCAT(DISTINCT actors.name) AS actors,
                    GROUP_CONCAT(DISTINCT languages.language) AS languages,
                    GROUP_CONCAT(DISTINCT countries.country) AS countries,
                    movies.plot,
                    movies.long_plot,
                    movies.plot_toggle,
                    movies.awards,
                    movies.imdb_rating,
                    movies.rotten_tomatoes_rating,
                    movies.metacritic_rating,
                    movies.u_rate,
                    movies.watched,
                    movies.path,
                    movies.has_parts
                FROM movies
                LEFT JOIN ratings ON movies.rated = ratings.id
                LEFT JOIN movie_directors ON movies.id = movie_directors.movie_id
                LEFT JOIN directors ON movie_directors.director_id = directors.id
                LEFT JOIN movie_writers ON movies.id = movie_writers.movie_id
                LEFT JOIN writers ON movie_writers.writer_id = writers.id
                LEFT JOIN movie_actors ON movies.id = movie_actors.movie_id
                LEFT JOIN actors ON movie_actors.actor_id = actors.id
                LEFT JOIN movie_languages ON movies.id = movie_languages.movie_id
                LEFT JOIN languages ON movie_languages.language_id = languages.id
                LEFT JOIN movie_countries ON movies.id = movie_countries.movie_id
                LEFT JOIN countries ON movie_countries.country_id = countries.id
                LEFT JOIN movie_genres ON movies.id = movie_genres.movie_id
                LEFT JOIN genres ON movie_genres.genre_id = genres.id
                WHERE movies.id = ?
                GROUP BY movies.id
            """
            return fetch_one(cursor, query, (movie_id, ))
    except sqlite3.Error as e:
        log_error_with_context("get_full_movie_data", f"Failed to get movie data. Error: {e}")

def get_movies_titles_and_paths(movie_ids):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' for _ in movie_ids)
            query = f"SELECT id, title, path FROM movies WHERE id IN ({placeholders})"
            return fetch_all(cursor, query, movie_ids)
    except sqlite3.Error as e:
        log_error_with_context("get_movies_titles_and_paths", f"Failed to get movie data. Error: {e}")

def get_movie_parts(movie_id=None):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if movie_id:
                query = "SELECT file_path FROM movie_parts WHERE movie_id = ?"
                parts = fetch_all(cursor, query, (movie_id,))
            else:
                query = "SELECT file_path FROM movie_parts"
                parts = fetch_all(cursor, query)
            return [part[0] for part in parts]
    except sqlite3.Error as e:
        log_error_with_context("get_movie_parts", f"Failed to get movie parts. Error: {e}")

def get_all_languages_and_countries():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT 'language' AS type, language AS value FROM languages
                UNION ALL
                SELECT 'country' AS type, country AS value FROM countries
                ORDER BY type, value ASC
            """
            results = fetch_all(cursor, query)
            languages = []
            countries = []
            for row in results:
                if row[0] == 'language':
                    languages.append(row[1])
                elif row[0] == 'country':
                    countries.append(row[1])
            return {'languages': languages, 'countries': countries}
    except sqlite3.Error as e:
        log_error_with_context("get_all_languages_and_countries", f"Failed to get region data. Error: {e}")
        return {'languages': [], 'countries': []}

def update_movies(movie_ids, details):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            set_clause = ", ".join([f"{key} = ?" for key in details.keys()])
            query = f"UPDATE movies SET {set_clause} WHERE id = ?"
            values = list(details.values())
            for movie_id in movie_ids:
                execute_query(cursor, query, (*values, movie_id))
            conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        log_error_with_context("update_movies", f"Failed to update movie(s). Error: {e}")

def path_check(path=None):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if path:
                result = fetch_one(cursor, '''SELECT title, year FROM movies WHERE path = ?''', (path,))
                return result if result else False
            else:
                result = fetch_all(cursor, '''SELECT id, path FROM movies ORDER BY last_verified''')
                ids = [row[0] for row in result]
                paths = [row[1] for row in result]
                return ids, paths  # Return two lists: IDs and paths
    except sqlite3.Error as e:
        log_error_with_context("path_check", f"Failed to get movie path data. Error: {e}")

def movie_dupe_check(details):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            result = fetch_one(cursor, '''SELECT * FROM movies WHERE title = ? AND year = ?''',
                               (details.get('title', ''), details.get('year', '')))
            return True if result else False
    except sqlite3.Error as e:
        log_error_with_context("movie_dupe_check", f"Failed title/year check. Error: {e}")

def keyword_scan(keyword_query):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            result = fetch_all(cursor, '''
                SELECT keyword FROM keywords WHERE keyword LIKE ?
            ''', (f'%{keyword_query}%',))
            return [keyword[0] for keyword in result]
    except sqlite3.Error as e:
        log_error_with_context("keyword_scan", f"Failed to search for keywords. Error: {e}")

def get_keywords(movie_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            result = fetch_all(cursor, '''
                SELECT k.keyword 
                FROM keywords k
                JOIN movie_keywords mk ON k.id = mk.keyword_id
                WHERE mk.movie_id = ?
            ''', (movie_id,))
            return [row[0] for row in result]
    except sqlite3.Error as e:
        log_error_with_context("get_keywords", f"Failed to get keywords. Error: {e}")

def keywords_update(movie_id, keywords, action):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            conn.execute('BEGIN')

            current_date = datetime.now().strftime('%Y-%m-%d')
            execute_query(cursor, "UPDATE movies SET keyword_scrape_date = ? WHERE id = ?",
                          (current_date, movie_id))

            if action == 'add':
                keyword_ids = []
                existing_keywords = {}
                new_keywords = []

                existing_keywords_query = f'''SELECT id, keyword FROM keywords WHERE keyword IN ({','.join(['?']*len(keywords))})'''
                existing_keywords_result = fetch_all(cursor, existing_keywords_query, keywords)
                for result in existing_keywords_result:
                    existing_keywords[result[1]] = result[0]

                for keyword in keywords:
                    if keyword in existing_keywords:
                        keyword_ids.append(existing_keywords[keyword])
                    else:
                        new_keywords.append(keyword)

                if new_keywords:
                    cursor.executemany('''INSERT INTO keywords (keyword) VALUES (?)''', [(kw,) for kw in new_keywords])
                    keyword_ids.extend([cursor.lastrowid for _ in new_keywords])

                for keyword_id in keyword_ids:
                    execute_query(cursor, '''
                        INSERT INTO movie_keywords (movie_id, keyword_id)
                        VALUES (?, ?)
                        ON CONFLICT(movie_id, keyword_id) DO NOTHING
                    ''', (movie_id, keyword_id))

            elif action == 'remove':
                existing_keywords_query = f'''SELECT id FROM keywords WHERE keyword IN ({','.join(['?']*len(keywords))})'''
                keyword_ids = [row[0] for row in fetch_all(cursor, existing_keywords_query, keywords)]

                cursor.executemany('''DELETE FROM movie_keywords WHERE movie_id=? AND keyword_id=?''',
                                   [(movie_id, keyword_id) for keyword_id in keyword_ids])

                cursor.executemany('''DELETE FROM keywords WHERE id=? AND NOT EXISTS 
                                     (SELECT 1 FROM movie_keywords WHERE keyword_id=?)''',
                                   [(keyword_id, keyword_id) for keyword_id in keyword_ids])
            conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        log_error_with_context("keywords_update", f"Failed to update keywords. Error: {e}")

def update_poster_paths():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            rows = fetch_all(cursor, '''SELECT poster_path FROM movies''')
            correct_path = os.path.expanduser("~/.local/share/amdb/assets/posters")
            for row in rows:
                current_path = row[0]
                if not current_path.startswith(correct_path):
                    file_name = os.path.basename(current_path)
                    updated_path = os.path.join(correct_path, file_name)
                    execute_query(cursor, '''UPDATE movies SET poster_path = ? WHERE poster_path = ?''',
                                  (updated_path, current_path))
            conn.commit()
            return True
    except sqlite3.Error as e:
        log_error_with_context("update_poster_paths", f"Failed to update poster paths: {e}")

def u_watch(movie_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            execute_query(cursor, '''
                    UPDATE movies
                    SET watched = CASE watched WHEN 0 THEN 1 ELSE 0 END
                    WHERE id = ?
                ''', (movie_id,))
            conn.commit()
    except sqlite3.Error as e:
        log_error_with_context("u_watch", f"Failed to update watched status: {e}")

def u_rate(movie_id, u_rating):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            execute_query(cursor, '''
                    UPDATE movies
                    SET u_rate = ?
                    WHERE id = ?
                ''', (u_rating, movie_id))
            conn.commit()
    except sqlite3.Error as e:
        log_error_with_context("u_rate", f"Failed to update AMDb rating: {e}")

def b_watch(movie_ids, watched):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            watched_status = 1 if watched else 0
            cursor.executemany('''
                    UPDATE movies
                    SET watched = ?
                    WHERE id = ?
                ''', [(watched_status, movie_id) for movie_id in movie_ids])
            conn.commit()
    except sqlite3.Error as e:
        log_error_with_context("b_watch", f"Failed to update watched status: {e}")

def path_verify(movie_id):
    current_date = datetime.now().strftime('%Y-%m-%d')

    def search_for_file(filename):
        trash_folder = "trash"
        for root, dirs, files in os.walk("/"):  # Modify the root directory as needed
            if trash_folder in root.lower():
                continue  # Skip the "trash" folder
            if filename in files:
                return os.path.join(root, filename)
        return None

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            result = fetch_one(cursor, '''SELECT path, has_parts FROM movies WHERE id=?''', (movie_id,))
            if not result:
                return False, None
            path, has_parts = result
            if not os.path.exists(path):
                file_path = search_for_file(os.path.basename(path))
                if file_path:
                    execute_query(cursor, "UPDATE movies SET path = ?, last_verified = ? WHERE id = ?",
                                  (file_path, current_date, movie_id))
                    if has_parts:
                        parts = fetch_all(cursor, '''SELECT id, file_path FROM movie_parts WHERE movie_id=?''', (movie_id,))
                        new_parts_paths = []
                        for part_id, part_path in parts:
                            new_part_path = os.path.join(os.path.dirname(file_path), os.path.basename(part_path))
                            if os.path.exists(new_part_path):
                                new_parts_paths.append((new_part_path, part_id))
                        for new_part_path, part_id in new_parts_paths:
                            execute_query(cursor, "UPDATE movie_parts SET file_path = ? WHERE id = ?",
                                          (new_part_path, part_id))
                    conn.commit()
                    return True, file_path
                else:
                    execute_query(cursor, "UPDATE movies SET last_verified = NULL WHERE id = ?", (movie_id,))
                    conn.commit()
                    return False, None
            else:
                execute_query(cursor, "UPDATE movies SET last_verified = ? WHERE id = ?", (current_date, movie_id))
                conn.commit()
                return True, path
    except sqlite3.Error as e:
        log_error_with_context("path_verify", f"Failed to verify filepath: {e}")
        return False, None

def u_delete(movie_id, title=None):
    if title is None:
        movie_data = get_movies_titles_and_paths(movie_id)
        title = movie_data[1]

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            conn.execute('BEGIN')

            poster_path = fetch_one(cursor, '''SELECT poster_path FROM movies WHERE id=?''', (movie_id,))[0]
            count = fetch_one(cursor, "SELECT COUNT(*) FROM movies WHERE poster_path = ? AND id != ?",
                              (poster_path, movie_id))[0]

            if count == 0 and poster_path:
                if os.path.exists(poster_path):
                    os.remove(poster_path)
                    log_info(f"Poster file for {title} deleted.")
                else:
                    log_warning(f"Poster file for {title} not found: {poster_path}")

            related_tables = [
                ("movie_keywords", "keyword_id", "keywords"),
                ("movie_directors", "director_id", "directors"),
                ("movie_writers", "writer_id", "writers"),
                ("movie_actors", "actor_id", "actors"),
                ("movie_languages", "language_id", "languages"),
                ("movie_countries", "country_id", "countries"),
                ("movie_genres", "genre_id", "genres")
            ]

            for movie_table, column, main_table in related_tables:
                related_ids = fetch_all(cursor, f'''SELECT {column} FROM {movie_table} WHERE movie_id=?''', (movie_id,))
                orphaned_ids = set()

                for related_id, in related_ids:
                    count = fetch_one(cursor, f'''SELECT COUNT(*) FROM {movie_table} WHERE {column}=?''', (related_id,))[0]
                    if count == 1:
                        orphaned_ids.add(related_id)

                execute_query(cursor, f'''DELETE FROM {movie_table} WHERE movie_id=?''', (movie_id,))

                for orphaned_id in orphaned_ids:
                    execute_query(cursor, f'''DELETE FROM {main_table} WHERE id=?''', (orphaned_id,))

            execute_query(cursor, '''DELETE FROM movie_parts WHERE movie_id=?''', (movie_id,))
            execute_query(cursor, '''DELETE FROM movies WHERE id=?''', (movie_id,))

            conn.commit()
            log_info(f"Movie: {title} removed from the database")
    except sqlite3.Error as e:
        log_error_with_context("u_delete", f"Failed to delete movie: {e}")
        conn.rollback()

def u_plot(movie_id, plot_tog):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            execute_query(cursor, '''
                    UPDATE movies
                    SET plot_toggle = ?
                    WHERE id = ?
                ''', (plot_tog, movie_id))
            conn.commit()
    except sqlite3.Error as e:
        log_error_with_context("u_plot", f"Failed to update long_plot: {e}")
