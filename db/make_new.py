import os
import sqlite3

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QPushButton, QLabel, QVBoxLayout, QDialog

from config.logger import log_info


def db_connect():
    # Connect to the SQLite database
    db_path = os.path.expanduser("~/.local/share/amdb/assets/movies.db")
    conn = sqlite3.connect(db_path)
    return conn

def drop_all_tables():
    # Connect to the SQLite database
    conn = db_connect()
    cursor = conn.cursor()

    # Query to get the names of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
    tables = cursor.fetchall()

    # Drop each table
    for table in tables:
        table_name = table[0]
        drop_table_sql = f"DROP TABLE IF EXISTS {table_name};"
        cursor.execute(drop_table_sql)

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def create_tables():
    # SQL commands to create tables with constraints and optimizations
    sql_commands = [
        """CREATE TABLE movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imdb_id TEXT NOT NULL CHECK(length(imdb_id) <= 10),
            title TEXT NOT NULL,
            year INTEGER CHECK(year >= 1878),
            rated INTEGER,
            released DATE,
            runtime TEXT CHECK(length(runtime) <= 10),
            plot TEXT,
            long_plot TEXT,
            plot_toggle BOOLEAN,
            awards TEXT,
            imdb_rating INTEGER CHECK(imdb_rating >= 0 AND imdb_rating <= 100),
            rotten_tomatoes_rating INTEGER CHECK(rotten_tomatoes_rating >= 0 AND rotten_tomatoes_rating <= 100),
            metacritic_rating INTEGER CHECK(metacritic_rating >= 0 AND metacritic_rating <= 100),
            average_rating INTEGER CHECK(average_rating >= 0 AND average_rating <= 100),
            type TEXT CHECK(length(type) <= 10),
            production TEXT,
            poster_path TEXT,
            path TEXT,
            watched BOOLEAN,
            u_rate INTEGER CHECK(u_rate >= 0 AND u_rate <= 100),
            keyword_scrape_date DATE,
            last_verified DATE,
            has_parts BOOLEAN DEFAULT 0,
            FOREIGN KEY (rated) REFERENCES ratings(id)
        );""",
        """CREATE TABLE ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rating TEXT NOT NULL
        );""",
        """INSERT INTO ratings (rating) VALUES ('G'), ('PG'), ('PG-13'), ('R'), ('NC-17'), ('NR/UR');""",
        """CREATE TABLE alias_titles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            alias_title TEXT NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
        );""",
        """CREATE INDEX idx_alias_titles_movie_id ON alias_titles (movie_id);""",
        """CREATE TABLE directors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );""",
        """CREATE TABLE writers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );""",
        """CREATE TABLE actors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );""",
        """CREATE TABLE movie_directors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            director_id INTEGER NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
            FOREIGN KEY (director_id) REFERENCES directors(id) ON DELETE CASCADE
        );""",
        """CREATE INDEX idx_movie_directors_movie_id ON movie_directors (movie_id);""",
        """CREATE INDEX idx_movie_directors_director_id ON movie_directors (director_id);""",
        """CREATE TABLE movie_writers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            writer_id INTEGER NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
            FOREIGN KEY (writer_id) REFERENCES writers(id) ON DELETE CASCADE
        );""",
        """CREATE INDEX idx_movie_writers_movie_id ON movie_writers (movie_id);""",
        """CREATE INDEX idx_movie_writers_writer_id ON movie_writers (writer_id);""",
        """CREATE TABLE movie_actors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            actor_id INTEGER NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
            FOREIGN KEY (actor_id) REFERENCES actors(id) ON DELETE CASCADE
        );""",
        """CREATE INDEX idx_movie_actors_movie_id ON movie_actors (movie_id);""",
        """CREATE INDEX idx_movie_actors_actor_id ON movie_actors (actor_id);""",
        """CREATE TABLE keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL
        );""",
        """CREATE TABLE movie_parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            file_path VARCHAR(255) NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
        );""",
        """CREATE INDEX idx_movie_parts_movie_id ON movie_parts (movie_id);""",
        """CREATE TABLE movie_keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            keyword_id INTEGER NOT NULL,
            UNIQUE (movie_id, keyword_id),
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
            FOREIGN KEY (keyword_id) REFERENCES keywords(id) ON DELETE CASCADE
        );""",
        """CREATE INDEX idx_movie_keywords_movie_id ON movie_keywords (movie_id);""",
        """CREATE INDEX idx_movie_keywords_keyword_id ON movie_keywords (keyword_id);""",
        """CREATE TABLE languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language TEXT NOT NULL
        );""",
        """CREATE TABLE movie_languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            language_id INTEGER NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
            FOREIGN KEY (language_id) REFERENCES languages(id) ON DELETE CASCADE
        );""",
        """CREATE INDEX idx_movie_languages_movie_id ON movie_languages (movie_id);""",
        """CREATE INDEX idx_movie_languages_language_id ON movie_languages (language_id);""",
        """CREATE TABLE countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT NOT NULL
        );""",
        """CREATE TABLE movie_countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            country_id INTEGER NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
            FOREIGN KEY (country_id) REFERENCES countries(id) ON DELETE CASCADE
        );""",
        """CREATE INDEX idx_movie_countries_movie_id ON movie_countries (movie_id);""",
        """CREATE INDEX idx_movie_countries_country_id ON movie_countries (country_id);""",
        """CREATE TABLE genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            genre TEXT NOT NULL
        );""",
        """CREATE TABLE movie_genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            genre_id INTEGER NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
            FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
        );""",
        """CREATE INDEX idx_movie_genres_movie_id ON movie_genres (movie_id);""",
        """CREATE INDEX idx_movie_genres_genre_id ON movie_genres (genre_id);"""
    ]

    conn = db_connect()
    cursor = conn.cursor()

    # Execute each SQL command
    for command in sql_commands:
        cursor.execute(command)

    # Commit changes and close the connection
    conn.commit()
    conn.close()


@pyqtSlot()
def reset_amdb():
    # Perform a full reset of all data
    confirm_dialog = QDialog()
    confirm_dialog.setWindowTitle("Reset Database")
    icon_path = os.path.expanduser("~/.local/share/amdb/assets/amdb.ico")
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(icon_path))
    confirm_dialog.setWindowIcon(icon)

    layout = QVBoxLayout()

    label = QLabel("This will reset all AMDb data.")
    continue_button = QPushButton("Continue")  # Sends signal to worker to stop
    cancel_button = QPushButton("Cancel")
    layout.addWidget(label)
    layout.addWidget(continue_button)
    layout.addWidget(cancel_button)

    confirm_dialog.setLayout(layout)

    # Connect buttons to their respective functions
    continue_button.clicked.connect(lambda: show_final_warning(confirm_dialog))
    cancel_button.clicked.connect(confirm_dialog.reject)

    # Execute the dialog
    confirm_dialog.exec_()


@pyqtSlot()
def show_final_warning(parent_dialog):
    # Close the initial dialog
    parent_dialog.accept()

    # Create the final warning dialog
    final_warning_dialog = QDialog()
    final_warning_dialog.setWindowTitle("Final Warning")
    icon_path = os.path.expanduser("~/.local/share/amdb/assets/amdb.ico")
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(icon_path))
    final_warning_dialog.setWindowIcon(icon)

    layout = QVBoxLayout()

    label = QLabel("This action will drop all SQL tables and re-make them. Are you sure you want to proceed?")
    proceed_button = QPushButton("Proceed")
    cancel_button = QPushButton("Cancel")
    layout.addWidget(label)
    layout.addWidget(QLabel("Please confirm your action:"))  # Offset the button positions
    layout.addWidget(proceed_button)
    layout.addWidget(cancel_button)

    final_warning_dialog.setLayout(layout)

    # Connect buttons to their respective functions
    proceed_button.clicked.connect(lambda: perform_reset(final_warning_dialog))
    cancel_button.clicked.connect(final_warning_dialog.reject)

    # Position the final warning dialog offset from the first one
    screen_geometry = QApplication.desktop().screenGeometry()
    final_warning_dialog.move(screen_geometry.width() // 2 - 100, screen_geometry.height() // 2 - 100)

    # Execute the dialog
    final_warning_dialog.exec_()


@pyqtSlot()
def perform_reset(dialog):
    # Here, add the actual reset logic
    # For example, clear the database or reset application settings
    log_info("Resetting data...")  # Replace this with actual reset code
    drop_all_tables()
    create_tables()
    log_info("SQL tables reset")
    # Close the dialog after performing the reset
    dialog.accept()
