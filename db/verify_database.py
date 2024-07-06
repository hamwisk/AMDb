# db/verifyDatabase.py
import os
from datetime import datetime

from PyQt5.QtCore import QObject, pyqtSignal

from config.logger import log_info
from db.database_operations import path_verify, path_check, update_movies


def search_for_file(filename):
    trash_folder = "trash"
    for root, dirs, files in os.walk("/"):  # Modify the root directory as needed
        if trash_folder in root.lower():
            continue  # Skip the "trash" folder
        if filename in files:
            return os.path.join(root, filename)
    return None


def update_verification_date(movie_id):
    current_date = datetime.now().strftime('%Y-%m-%d')
    movie_ids = [movie_id]
    details = {"last_verified": current_date}
    update_movies(movie_ids, details)


def auto_find_path(movie_id, path):
    # Get the expected filename from the path stored in the database
    filename = os.path.basename(path)
    # Search the system for a path to the filename
    file_path = search_for_file(filename)
    if file_path:
        # Store the new path to the database
        movie_ids = [movie_id]
        details = {"path": file_path}
        update_movies(movie_ids, details)
        return True
    # Return "False" when automatic path repair fails
    return False


class VerifyDatabaseWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    unfixed = pyqtSignal(tuple)  # Signal to emit movie data for unfixed paths

    def __init__(self):
        super().__init__()
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        broken_paths = []
        ids, paths = path_check()  # Get all movie IDs and paths sorted by last_verified

        # Check for broken paths
        for movie_id, path in zip(ids, paths):
            if not self._is_running:
                break
            if not os.path.exists(path):
                # Append the broken path to the broken paths list
                broken_paths.append((movie_id, path))
            else:
                # Or update the date for a valid path
                update_verification_date(movie_id)

        if len(broken_paths) == 0:
            log_info("No broken paths found in the database")
        else:
            # Fix broken paths
            for index, (movie_id, path) in enumerate(broken_paths):
                # Calculate progress percentage
                self.progress.emit(int(100 * (index + 1) / len(broken_paths)))

                if not self._is_running:
                    break

                # Attempt to automatically fix the broken path
                updated, path = path_verify(movie_id)

                if updated:
                    # Updated paths and current date stored to the database
                    update_verification_date(movie_id)
                    title, year = path_check(path)
                    log_info(f"Path updated for {title} ({year})to {path}")
                else:
                    # Emit the movie data for the unfixed path
                    self.unfixed.emit((movie_id, path))

        log_info("Database paths verification complete")
        self.finished.emit()
        self.stop()
