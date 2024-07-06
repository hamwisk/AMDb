import os

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QListWidgetItem

from db.API_request import get_tt_data
from db.movie_processing_thread import download_temp_poster
from ui.ui_search_dialog import Ui_Dialog


class MovieSelectionDialog(QDialog, Ui_Dialog):
    def __init__(self, movie_options, parent=None):
        super().__init__(parent)
        self.index = movie_options['index']
        self.movie_options = movie_options['options']
        self.path = movie_options['path']

        self.setupUi(self)
        self.setWindowTitle("Select Movie")
        self.set_icon()

        self.pushButton.clicked.connect(self.add_movie_option)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.label.setText(f"Select the correct movie:\n{self.path}")
        # Populate the list widget and set the initial poster
        self.populate_list()
        self.movie_list_widget.itemSelectionChanged.connect(self.update_poster_preview)
        if self.movie_options:
            self.set_poster(self.movie_options[0]['poster'])

    def set_icon(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.expanduser("~/.local/share/amdb/assets/amdb.ico")))
        self.setWindowIcon(icon)

    def populate_list(self):
        # Populate the list widget with movie titles
        self.movie_list_widget.clear()
        for movie in self.movie_options:
            title = movie.get('title')
            year = movie.get('year')
            item = QListWidgetItem(f"{title} ({year})")
            item.setData(QtCore.Qt.UserRole, movie)
            self.movie_list_widget.addItem(item)

    def update_poster_preview(self):
        current_item = self.movie_list_widget.currentItem()
        if current_item:
            movie = current_item.data(QtCore.Qt.UserRole)
            poster_path = movie.get('poster')
            self.set_poster(poster_path)

    def set_poster(self, poster_path):
        pixmap = QtGui.QPixmap(poster_path)
        self.poster_preview.setPixmap(pixmap.scaled(self.poster_preview.size(), QtCore.Qt.KeepAspectRatio))

    def selected_movie(self):
        current_item = self.movie_list_widget.currentItem()
        if current_item:
            return current_item.data(QtCore.Qt.UserRole)
        return None

    def add_movie_option(self):
        # Updates the list with a new movie title
        movie_data = get_tt_data(self.tt_edit.text(), long_plot=0)
        if movie_data and movie_data.get('Response') == 'True':
            index = len(self.movie_options) + 1
            # Maybe don't need to add one as the index starts at 0, but it's 'counted from 1
            title = movie_data.get('Title')
            year = movie_data.get('Year')
            imdb_id = movie_data.get('imdbID')
            tmp_path = download_temp_poster(movie_data.get('Poster'))
            movie = {
                'index': index,
                'imdb_id': imdb_id,
                'title': title,
                'year': year,
                'poster': tmp_path,
                'path': self.path
            }
            self.movie_options.append(movie)  # Add movie option to list
            self.populate_list()
