import os
import os
import re
import subprocess
import tempfile
import textwrap

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QImage, QPainter, QDesktopServices
from PyQt5.QtWidgets import QMainWindow, QDialog, QWidget

from db.API_request import get_tt_data
from db.database_operations import u_rate, u_plot, update_movies, get_full_movie_data, get_movie_parts, get_keywords
from ui.ui_movie_details import Ui_movie_details_dialog


def wrap_title(title, year=None, max_width=36):
    if len(title) > max_width:
        title = '<br />'.join(textwrap.wrap(title, width=max_width))
    if year:
        title_with_year = (f"<html><head/><body><p>{title} "
                           f"<span style=\"vertical-align:super;\">({year})</span></p></body></html>")
    else:
        title_with_year = f"<html><head/><body><p>{title}</p></body></html>"
    return title_with_year


class CustomProgressBar(QWidget):
    def __init__(self, rating, crit, movie_id=None, movie_slug=None, movie_year=None):
        super().__init__()
        self.rating = rating
        self.crit = crit
        self.movie_id = movie_id
        self.movie_slug = movie_slug
        self.movie_year = movie_year
        self.setGeometry(0, 0, 50, 50)
        self.setWindowTitle('Custom Progress Bar')

        icons_path = os.path.expanduser("~/.local/share/amdb/assets/icons/")
        icon_path_c = f"{icons_path}{crit}_logo.png"
        icon_path_g = f"{icons_path}{crit}_logo_grey.png"
        self.colour = QImage(icon_path_c)
        self.greyed = QImage(icon_path_g)
        self.setCursor(Qt.PointingHandCursor)  # Change cursor to hand to indicate clickable
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawImage(0, 0, self.greyed)
        height = self.colour.height()
        visible_height = int(height * (self.rating / 100.0))
        transparent_image = QImage(self.colour.size(), QImage.Format_ARGB32)
        transparent_image.fill(Qt.transparent)
        painter_colored = QPainter(transparent_image)
        painter_colored.drawImage(0, height - visible_height, self.colour, 0, height - visible_height,
                                  self.colour.width(), visible_height)
        painter_colored.end()
        painter.drawImage(0, 0, transparent_image)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.open_critic_page()

    def open_critic_page(self):
        if self.crit == 'imdb' and self.movie_id:
            url = f'https://www.imdb.com/title/{self.movie_id}/'
        elif self.crit == 'rt' and self.movie_slug:
            url = f'https://www.rottentomatoes.com/m/{self.movie_slug}'
        elif self.crit == 'mc' and self.movie_slug:
            url = f'https://www.metacritic.com/movie/{self.movie_slug}'
        else:
            url = None

        if url:
            QDesktopServices.openUrl(QUrl(url))

    def set_rating(self, rating):
        self.rating = rating
        self.update()


class MovieDetailsDialog(QMainWindow, Ui_movie_details_dialog):
    watched_state_changed = pyqtSignal(int, bool)

    def __init__(self, movie_id, parent=None):
        super(MovieDetailsDialog, self).__init__(parent)
        self.movie_id = movie_id
        movie = get_full_movie_data(movie_id)
        if movie:
            (self.imdb_id, self.title, self.year, self.rated, self.released, self.poster_path, self.genre, self.runtime,
             self.directors, self.writers, self.actors, self.languages, self.countries, self.plot, self.long_plot,
             self.plot_toggle, self.awards, self.imdb_rating, self.rotten_tomatoes_rating,
             self.metacritic_rating, self.amdb_rating, self.watched, self.path, self.has_parts) = movie
        self.keywords = get_keywords(self.movie_id)

        self.setupUi(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.expanduser("~/.local/share/amdb/assets/amdb.ico")))
        self.setWindowIcon(icon)
        self.setWindowTitle(self.title)
        self.populate_movie_details()

    def populate_movie_details(self):
        title = self.title
        year = self.year
        wrapped_title = wrap_title(title, year)
        self.movie_title_year.setText(f"<html><head/><body><p>{wrapped_title}</p></body></html>")
        self.movie_rated.setText(self.rated)
        self.movie_released.setText(self.released)
        self.movie_runtime.setText(self.runtime)
        self.movie_genre.setText(self.genre.replace(",", ", "))
        self.movie_director.setText(self.directors.replace(",", ", "))
        self.movie_writers.setText(self.writers.replace(",", ", "))
        self.movie_actors.setText(self.actors.replace(",", ", "))

        if self.plot_toggle:
            plot_html = f"<b>Long Plot:</b></p><p>{self.long_plot}"
            self.toggle_plot.setText("Show less")
        else:
            plot_html = f"<b>Plot:</b></p><p>{self.plot}"
        self.movie_plot.setText(plot_html)

        if self.keywords:
            keywords_html = "<b>Keywords:</b><br><ul>" + "".join(
                f"<li>{keyword}</li>" for keyword in self.keywords) + "</ul>"
            self.movie_keywords.setText(keywords_html)

        self.movie_awards.setText(self.awards)

        movie_slug_rt = re.sub(r'\W+', '',
                               self.title.replace(' ', '_').lower())  # Generate slug with underscores
        movie_slug_mc = re.sub(r'[^\w-]', '', self.title.replace(' ', '-').lower())

        if self.imdb_rating:
            rating = self.imdb_rating/10
            self.label_imdb.setText(f"'{rating}/10'")
            progress_bar = CustomProgressBar(self.imdb_rating, 'imdb', movie_id=self.imdb_id)
            self.gridLayout_3.addWidget(progress_bar, 0, 0, 1, 1)
        if self.rotten_tomatoes_rating:
            self.label_rt.setText(f"'{self.rotten_tomatoes_rating}%'")
            progress_bar = CustomProgressBar(self.rotten_tomatoes_rating, 'rt', movie_slug=movie_slug_rt)
            self.gridLayout_3.addWidget(progress_bar, 0, 1, 1, 1)
        if self.metacritic_rating:
            self.label_mc.setText(f"'{self.metacritic_rating}/100'")
            progress_bar = CustomProgressBar(self.metacritic_rating, 'mc', movie_slug=movie_slug_mc)
            self.gridLayout_3.addWidget(progress_bar, 0, 2, 1, 1)

        self.movie_language.setText(self.languages.replace(",", ", "))
        self.movie_country.setText(self.countries.replace(",", ", "))
        self.movie_poster.setPixmap(QtGui.QPixmap(self.poster_path))

        self.play_movie.clicked.connect(lambda: self.play())
        self.watched_movie.setChecked(bool(self.watched))
        self.watched_movie.stateChanged.connect(lambda: self.set_watched())
        self.toggle_plot.clicked.connect(lambda: self.set_plot())
        self.rate_movie.setEnabled(bool(self.watched))
        self.rate_movie.clicked.connect(lambda: self.set_rating())

        if self.watched:
            self.label_amdb.setText(f"'{self.amdb_rating}%'")
            progress_bar = CustomProgressBar(self.amdb_rating, 'amdb')
            progress_bar.setObjectName("amdb_rating")
            self.gridLayout_3.addWidget(progress_bar, 0, 3, 1, 1)

    def play(self):
        if self.has_parts:
            part_paths = get_movie_parts(self.movie_id)

            # Create a temporary playlist file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".m3u") as playlist_file:
                playlist_file.write(f"{self.path}\n".encode("utf-8"))
                for part_path in part_paths:
                    playlist_file.write(f"{part_path}\n".encode("utf-8"))
                playlist_path = playlist_file.name

            # Launch the media player with the playlist
            print(playlist_path)
            subprocess.Popen(['xdg-open', playlist_path])
        else:
            subprocess.Popen(['xdg-open', self.path])

    def set_watched(self):
        self.watched = self.watched_movie.isChecked()
        self.watched_state_changed.emit(self.movie_id, self.watched)
        self.rate_movie.setEnabled(self.watched)

    def set_rating(self, movie):
        dialog = RatingDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            user_rating = dialog.get_rating()
            u_rate(movie[0], user_rating)
            self.label_amdb.setText(f"'{user_rating}%'")

            # Find and remove the existing CustomProgressBar widget by its object name
            existing_widget = self.findChild(CustomProgressBar, "amdb_rating")
            if existing_widget is not None:
                self.gridLayout_3.removeWidget(existing_widget)
                existing_widget.deleteLater()

            # Add the new CustomProgressBar widget
            progress_bar = CustomProgressBar(user_rating, 'amdb')
            progress_bar.setObjectName("amdb_rating")
            self.gridLayout_3.addWidget(progress_bar, 0, 3, 1, 1)

    def set_plot(self):
        if self.plot_toggle == 1:
            # Condition: User asks to hide long plot
            self.movie_plot.setText(f"<b>Plot:</b></p><p>{self.plot}")
            self.toggle_plot.setText("Show full plot...")
            u_plot(self.movie_id, plot_tog=0)
            self.plot_toggle = 0
        else:
            if self.long_plot:
                # Condition: User asks to show long plot, long plot exists in movies.db
                self.movie_plot.setText(f"<b>Long Plot:</b></p><p>{self.long_plot}")
            else:
                # Condition: User asks to show long plot, long plot needs to be downloaded
                new_movie_data = get_tt_data(tt_code=self.imdb_id, long_plot=1)
                if new_movie_data:
                    self.movie_plot.setText(f"<b>Long Plot:</b></p><p>{new_movie_data['Plot']}")
                    movie_ids = [self.movie_id]
                    details = {"long_plot": new_movie_data['Plot']}
                    update_movies(movie_ids, details)

            self.toggle_plot.setText("Show less")
            u_plot(self.movie_id, plot_tog=1)
            self.plot_toggle = 1


class RatingDialog(QDialog):
    def __init__(self, parent=None):
        super(RatingDialog, self).__init__(parent)
        self.setupUi()
        self.rating = 50  # Default rating

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(189, 227)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalSlider = QtWidgets.QSlider(self)
        self.verticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider.setObjectName("verticalSlider")
        self.verticalSlider.setMaximum(100)
        self.gridLayout.addWidget(self.verticalSlider, 0, 1, 1, 1)
        self.spinBox = QtWidgets.QSpinBox(self)
        self.spinBox.setObjectName("spinBox")
        self.spinBox.setMaximum(100)
        self.gridLayout.addWidget(self.spinBox, 1, 0, 1, 2)
        self.logo_frame = QtWidgets.QFrame(self)
        self.logo_frame.setMinimumSize(QtCore.QSize(150, 150))
        self.logo_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.logo_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.logo_frame.setObjectName("logo_frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.logo_frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout.addWidget(self.logo_frame, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)

        self.retranslateUi()
        self.verticalSlider.valueChanged['int'].connect(self.update_widgets)
        self.spinBox.valueChanged['int'].connect(self.update_widgets)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.customProgressBar = CustomProgressBar(self.spinBox.value(), 'AMDb')
        self.customProgressBar.setObjectName("amdb_rating")
        self.gridLayout_2.addWidget(self.customProgressBar)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Rate Movie"))

    def update_widgets(self, value):
        self.spinBox.blockSignals(True)
        self.verticalSlider.blockSignals(True)
        self.spinBox.setValue(value)
        self.verticalSlider.setValue(value)
        self.customProgressBar.set_rating(value)
        self.spinBox.blockSignals(False)
        self.verticalSlider.blockSignals(False)

    def get_rating(self):
        return self.spinBox.value()
