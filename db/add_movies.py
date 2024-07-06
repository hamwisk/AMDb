# db/add_movies.py
import datetime
import difflib
import os
import re

from PyQt5.QtWidgets import QFileDialog

from db.database_operations import path_check, get_movie_parts


def clean_folder_name(folder_name):
    # Compile the regex pattern to find years in parentheses
    year_pattern = re.compile(r'\((\d{4})\)')
    current_year = datetime.datetime.now().year

    match = year_pattern.search(folder_name)  # Search for the pattern in the folder name
    if match:
        year = int(match.group(1))  # Extract the year from the match
        if 1880 <= year <= current_year:
            cleaned_name = re.sub(year_pattern, '', folder_name).strip()  # Remove the pattern and strip spaces
            return cleaned_name
    return folder_name  # Return original name if no match or invalid year


def extract_year_from_name(file_name):
    year_match = re.search(r'[({]([0-9]{4})[})]', file_name)  # Search for year in the file name
    if year_match:
        return int(year_match.group(1))  # Return the year if found
    return None  # Return None if no year found


def extract_movie_details(self, extensions):
    current_year = datetime.datetime.now().year
    movie_extensions = [ext.strip() for ext in extensions.split(',')]  # Get list of movie extensions
    folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder', os.path.expanduser("~"))  # Open folder dialog

    if not folder_path:
        return [], [], [], [], []  # Return empty lists if no folder selected
    p_inc, y_ish, t_ish, d_ish = [], [], [], []  # Initialize lists for different categories

    # Store all database paths as a temporary variable rather than performing multiple SQL lookups
    ids, current_paths = path_check()
    all_path_parts = get_movie_parts()

    for root, dirs, files in os.walk(folder_path):  # Walk through the directory
        for file_name in files:
            _, file_extension = os.path.splitext(file_name)
            if file_extension and file_extension[1:].lower() in movie_extensions:  # Check if file is a movie
                path = os.path.join(root, file_name)
                year = extract_year_from_name(file_name)  # Extract year from file name
                if path not in current_paths and path not in all_path_parts:
                    if year and 1880 <= year <= current_year:
                        title = re.sub(r'\s*[({]\d{4}[})]\s*', '', os.path.splitext(file_name)[0]).strip()
                        p_inc.append({'title': title, 'year': year, 'path': path})  # Add movie to p_inc list
                    else:
                        title, year, category = handle_no_year_case(file_name, path, current_year)
                        if category == 'p_inc':
                            p_inc.append({'title': title, 'year': year, 'path': path})
                        elif category == 'y_ish':
                            y_ish.append({'title': title, 'year': year, 'path': path})
                        elif category == 't_ish':
                            t_ish.append({'title': title, 'year': year, 'path': path})
                else:
                    if year and 1880 <= year <= current_year:
                        title = re.sub(r'\s*[({]\d{4}[})]\s*', '', os.path.splitext(file_name)[0]).strip()
                    else:
                        title, year, category = handle_no_year_case(file_name, path, current_year)
                    d_ish.append({'title': title, 'year': year, 'path': path})  # Add duplicates to d_ish

    s_inc = process_series([p_inc, y_ish, t_ish])  # Process series from movie lists
    return p_inc, y_ish, t_ish, d_ish, s_inc  # Return all lists


def handle_no_year_case(file_name, path, current_year):
    match = re.search(r'\b(\d{4})\b', file_name)
    if match:
        year = int(match.group(1))
        if 1880 < year < current_year:
            title = re.sub(rf'\b{year}\b.*', '', file_name).strip()
            title = re.sub(r'(?<!\.)\.(?!\.)', ' ', title).strip()  # Remove full stops and strip spaces
            return title, year, 'p_inc'

    file_name = os.path.splitext(os.path.basename(path))[0]
    parent_folder_name = os.path.basename(os.path.dirname(path))
    if file_name in parent_folder_name:
        year = extract_year_from_name(parent_folder_name)
        if year:
            return file_name, year, 'p_inc'
        return file_name, 'None', 'y_ish'
    return file_name, 'None', 't_ish'


def process_series(lists_to_process):
    s_inc = []
    for movie_list in lists_to_process:
        current_series, series_dict = series_check(movie_list)
        for title, years_dict in series_dict.items():
            for year, paths in years_dict.items():
                joined_paths = '|#| '.join(paths)  # Join paths into a single string
                s_inc.append({'title': title, 'year': year, 'path': joined_paths})
    return s_inc  # Return series list


def series_check(movies):
    folder_dict = {}
    for movie in movies:
        movie_title, movie_year, movie_path = movie['title'], movie['year'], movie['path']
        folder_name = os.path.basename(os.path.dirname(movie_path)).strip()

        if folder_name not in folder_dict:
            folder_dict[folder_name] = [{'title': movie_title, 'episodes': [
                {'title': movie_title, 'year': movie_year, 'path': movie_path}]}]
        else:
            found_series = False
            for series in folder_dict[folder_name]:
                similarity = difflib.SequenceMatcher(None, movie_title, series['title']).ratio()
                if similarity > 0.8:  # Check if movie is part of an existing series
                    series['episodes'].append({'title': movie_title, 'year': movie_year, 'path': movie_path})
                    found_series = True
                    break
            if not found_series:
                folder_dict[folder_name].append({'title': movie_title, 'episodes': [
                    {'title': movie_title, 'year': movie_year, 'path': movie_path}]})

    series_dict = {}
    for folder_name, series_list in folder_dict.items():
        for series in series_list:
            if len(series['episodes']) > 1:
                cleaned_name = clean_folder_name(folder_name)
                if cleaned_name not in series_dict:
                    series_dict[cleaned_name] = {}
                for episode in series['episodes']:
                    year = episode['year']
                    if year not in series_dict[cleaned_name]:
                        series_dict[cleaned_name][year] = []
                    series_dict[cleaned_name][year].append(episode['path'])
                    movies.remove({'title': episode['title'], 'year': year, 'path': episode['path']})

    return movies, series_dict  # Return updated movies and series dictionary
