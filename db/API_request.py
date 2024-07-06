# db/API_request.py
import os

import requests
from config.logger import log_warning
from config.config_handler import ConfigHandler

CONFIG_FILE = os.path.expanduser("~/.config/amdb/config.ini")
config = ConfigHandler(CONFIG_FILE)


def api_key():
    server = config.get_config_option('API server', 'Set')
    return config.get_config_option('API keys', server)


def api_url():
    server = config.get_config_option('API server', 'Set')
    return config.get_config_option('API url', server)


def get_movie_data(movie):
    params = {'apikey': api_key(), 't': movie['title'], 'y': movie['year']}
    response = requests.get(api_url(), params=params)
    if response.status_code == 200:
        # API request was successful
        movie_data = response.json()
        return movie_data
    else:
        # API request failed
        log_warning(f"Failed to download {movie['path']} - Error: {response.status_code}")
        return None


def search_movie_data(movie):
    params = {'apikey': api_key(), 's': movie['title'], 'y': movie['year'], 'page': 1}
    response = requests.get(api_url(), params=params)
    if response.status_code == 200:
        # API request was successful
        movie_data = response.json()
        return movie_data.get('Search', [])  # Return the list of movies
    else:
        # API request failed
        log_warning(f"Failed to download {movie['path']} - Error: {response.status_code}")
        return []


def get_tt_data(tt_code, long_plot):
    params = {'apikey': api_key(), 'i': tt_code}

    if long_plot:
        params['plot'] = 'full'

    response = requests.get(api_url(), params=params)
    if response.status_code == 200:
        # Parse JSON response
        movie_data = response.json()
        return movie_data
    else:
        # Log a warning if API request fails
        log_warning(f"Failed to download {tt_code} data - Error: {response.status_code}")
        return None
