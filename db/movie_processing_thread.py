# db/movie_processing_thread.py
import os
import shutil
import tempfile

import requests
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal

from config.config_handler import ConfigHandler
from db.API_request import get_movie_data, search_movie_data
from db.database_operations import add_new_movie, movie_dupe_check, add_series_parts, update_movies

# Path to the configuration file
CONFIG_FILE = os.path.expanduser("~/.config/amdb/config.ini")
# Initialize config handler
config = ConfigHandler(CONFIG_FILE)


def download_poster(poster_url, poster_path):
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(poster_path), exist_ok=True)
    # Download the poster image
    poster_response = requests.get(poster_url) if poster_url and poster_url != 'N/A' else None
    if poster_response and poster_response.status_code == 200:
        with open(poster_path, 'wb') as poster_file:
            poster_file.write(poster_response.content)
        image = Image.open(poster_path)
        # Resize image if width is not 300 pixels
        if image.width != 300:
            width_percent = 300 / float(image.size[0])
            height_size = int(float(image.size[1]) * float(width_percent))
            image = image.resize((300, height_size), Image.ANTIALIAS)
            image.save(poster_path)
    else:
        # Use a default poster if download fails
        default_poster_path = os.path.expanduser("~/.local/share/amdb/assets/tt_0000000.png")
        shutil.copy(default_poster_path, poster_path)


def download_temp_poster(url):
    # Validate URL
    if not url or url.lower() == 'n/a':
        return None

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException:
        return None

    try:
        # Extract the file name from the URL
        filename = os.path.basename(url)
        # Save the poster image to a temporary file
        temp_path = os.path.join(tempfile.gettempdir(), filename)

        # Write the content of the response to the temporary file
        with open(temp_path, 'wb') as f:
            f.write(response.content)

        # Open the downloaded image
        with Image.open(temp_path) as img:
            # Get the aspect ratio of the image
            aspect_ratio = img.width / img.height

            # Set the target width and height for the PNG
            target_width, target_height = 300, 455

            # Calculate the new width and height for the PNG while preserving the aspect ratio
            if aspect_ratio > 1:  # Image is wider than tall
                new_width = target_width
                new_height = int(new_width / aspect_ratio)
            else:  # Image is taller than wide
                new_height = target_height
                new_width = int(new_height * aspect_ratio)

            # Create a new image with transparent background
            new_img = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))

            # Calculate the position to paste the original image
            if new_width <= target_width and new_height <= target_height:
                # Image fits within the target dimensions, paste it centered
                x_offset = (target_width - new_width) // 2
                y_offset = (target_height - new_height) // 2
                new_img.paste(img, (x_offset, y_offset))
            else:
                # Image is larger than the target dimensions, resize it
                img.thumbnail((target_width, target_height))
                x_offset = (target_width - img.width) // 2
                y_offset = (target_height - img.height) // 2
                new_img.paste(img, (x_offset, y_offset))

            # Save the new image as PNG
            png_path = os.path.splitext(temp_path)[0] + ".png"
            new_img.save(png_path, "PNG")
        return png_path
    except (OSError, IOError, Image.DecompressionBombError, Image.UnidentifiedImageError):
        return None


def process_meta_data(movie, movie_data):
    # API request success
    title = movie_data.get('Title', '')
    imdb_id = movie_data.get('imdbID', '')
    # Path to save the poster
    poster_path = os.path.expanduser(f"~/.local/share/amdb/assets/posters/{title}_{imdb_id}.png")
    # Download poster image
    download_poster(movie_data.get('Poster', ''), poster_path)

    # Check `movie['path']` to see if it's a series, update the new table and 'parts' column
    has_parts = '|#| ' in movie['path']  # Check if there are multiple paths
    if has_parts:
        paths = sorted(movie['path'].split('|#|'))
        movie_id = ''
        parts = []
        is_first_part = True
        for part_path in paths:
            if is_first_part:
                movie_id = add_new_movie(movie_data, poster_path, part_path.strip())
                is_first_part = False
            else:
                parts.append(part_path)
        add_series_parts(movie_id, parts)
        movie_ids = [movie_id]
        details = {"has_parts": 1}
        update_movies(movie_ids, details)
    else:
        movie_id = add_new_movie(movie_data, poster_path, movie['path'])
    return movie_id


class MovieProcessingThread(QThread):
    # Define signals
    emit_progress_signal = pyqtSignal(int)
    emit_search_results_signal = pyqtSignal(dict)
    emit_complete_signal = pyqtSignal()

    def __init__(self, movies, r_type, parent=None):
        super(MovieProcessingThread, self).__init__(parent)
        self.movies = movies  # List of movies to process
        self.r_type = r_type  # Type of processing
        self.progress = 0  # Progress of processing

    def run(self):
        total_movies = len(self.movies)  # Total number of movies to process
        to_search = []
        if self.r_type == 'search':
            to_search = self.movies
            self.movies = []

        # First loop: Process each movie in self.movies
        for index, movie in enumerate(self.movies):
            # Get movie metadata from the OMDb API
            movie_data = get_movie_data(movie)
            if movie_data.get('Response', '') == 'True':
                # Movie metadata retrieved successfully
                details = {'title': movie_data['Title'], 'year': movie_data['Year']}
                duplicate = movie_dupe_check(details)
                if not duplicate:
                    # Process and add movie metadata to the database
                    movie_id = process_meta_data(movie, movie_data)
                    # Calculate progress percentage
                    self.progress = int(100 * (index + 1) / total_movies)
                    self.emit_progress_signal.emit(self.progress)  # Emit progress signal
                if duplicate:
                    # A movie with this title and year already exist, possible duplicate
                    to_search.append(movie)
            elif movie_data.get('Response', '') == 'False':
                # Couldn't get movie metadata, adding to search list
                to_search.append(movie)

        # Second loop: Process each movie in to_search
        for index, movie in enumerate(to_search):
            movie_options = []  # List to store movie options for the current movie
            movie_data = search_movie_data(movie)
            for movie_result in movie_data:
                if movie_result.get('Type') in ['movie', 'series', 'episode']:
                    title = movie_result.get('Title')
                    year = movie_result.get('Year')
                    imdb_id = movie_result.get('imdbID')
                    tmp_path = download_temp_poster(movie_result.get('Poster'))
                    movie_option = {
                        'index': index,
                        'imdb_id': imdb_id,
                        'title': title,
                        'year': year,
                        'poster': tmp_path,
                        'path': movie['path']
                    }
                    movie_options.append(movie_option)  # Add movie option to list

            # Emit options signal for the current movie
            self.emit_search_results_signal.emit(
                {'index': index, 'options': movie_options, 'path': movie['path']})

            # Calculate progress percentage for the second loop
            self.progress = int(100 * (index + 1 + total_movies) / (total_movies + len(to_search)))
            self.emit_progress_signal.emit(self.progress)  # Emit progress signal

        # Processing is complete
        self.emit_complete_signal.emit()  # Emit complete signal

