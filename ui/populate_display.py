# ui/populate_display.py
import subprocess
import tempfile
from datetime import datetime

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from db.database_operations import u_watch, path_verify, get_movie_parts
from db.delete_query import dialog_delete
from ui.keywords_dialog import KeywordsDialog
from ui.ui_list_item import Ui_list_item
from ui.ui_movie_grid import Ui_movie_grid


class ClickableWidget(QWidget):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(ClickableWidget, self).__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super(ClickableWidget, self).mousePressEvent(event)


def movie_item_clicked(args):
    movie_id, result_window = args
    from ui.movie_details import MovieDetailsDialog
    open_movie_dialogs = result_window.movie_details_dialogs

    for dialog in open_movie_dialogs:
        if dialog.movie_id == movie_id:
            dialog.show()
            dialog.raise_()
            return

    main_window = result_window.parent().parent().parent().parent().parent()

    movie_details_dialog = MovieDetailsDialog(movie_id, parent=main_window)
    movie_details_dialog.watched_state_changed.connect(main_window.update_watched_status)
    movie_details_dialog.show()

    # Add the dialog to the list of open dialogs
    open_movie_dialogs.append(movie_details_dialog)


def create_list_items(movie_details, result_window, unselected_style):
    for movie in movie_details:
        (movie_id, title, year, genre, poster_path, path, watched, keyword_update, path_verified, series) = \
            (movie[0], movie[1], str(movie[2]), movie[3], movie[4], movie[5], movie[6], movie[7], movie[8], movie[9])

        list_item = Ui_list_item()
        list_item_widget = QtWidgets.QWidget(parent=result_window)
        list_item.setupUi(list_item_widget)
        list_item_widget.setStyleSheet(unselected_style)  # Apply unselected style initially

        args = (movie[0], result_window)
        list_item.reel.clicked.connect(lambda state, mid=args: movie_item_clicked(mid))

        tooltip_str = (f'<html><head/><body><p><img src="{poster_path}" width="300"></p>'
                       f'<p><span style="font-size:24pt; font-weight:600;">{title}</span></p>'
                       f'</body></html>')

        # Set up the 'Watched' checkbox
        list_item.watched_status.setChecked(watched == 1)
        list_item.watched_status.stateChanged.connect(lambda state, mid=movie_id: u_watch(mid))

        # Set up the 'Play' button
        args = (movie_id, path, series)
        list_item.play_movie.clicked.connect(lambda state, mid=args: launch_movie(mid))

        # Set up the 'Delete' button
        args = (movie_id, title, list_item_widget, result_window)
        list_item.delete_movie.clicked.connect(lambda state, mid=args: delete_movie(mid))

        # Set the 'title' and 'year' data and poster image tooltip
        list_item.title.setText(title)
        list_item.year.setText(f"({year})")
        list_item.genre.setText(genre.replace(",", ", "))

        # Set up the 'Keywords' checkbox and button
        list_item.keywords_updated.setText(keyword_update)
        list_item.keyword_status.setChecked(True) if (keyword_update is not None) else False
        args = (title, movie_id, list_item)
        list_item.keywords_updated.clicked.connect(lambda state, mid=args: keyword_dialog(mid))

        # Set up the 'Filepath' checkbox and button
        list_item.filepath_verified.setText(path_verified)
        list_item.filepath_status.setChecked(True) if (path_verified is not None) else False
        args = (movie_id, list_item, series)
        list_item.filepath_verified.clicked.connect(lambda state, mid=args: pop_path(mid))

        item = QtWidgets.QListWidgetItem(result_window)
        row_width = int(result_window.width() - 22)  # Adjust for scrollbar width
        item.setSizeHint(QtCore.QSize(row_width, 55))  # Fixed width and height
        list_item_widget.ui_movie_list_instance = list_item

        # Set tool-tip text for items
        list_item.play_movie.setToolTip(path)
        list_item.delete_movie.setToolTip("Delete Movie")
        list_item.reel.setToolTip("Show Movie Details")
        list_item_widget.setToolTip(tooltip_str)  # Set tooltip for the entire widget

        # Store the movie_id on the widget and add widget to result_window
        list_item_widget.movie_id = movie_id
        result_window.setItemWidget(item, list_item_widget)


def create_grid_items(movie_details, result_window, max_title_length=16):
    for movie in movie_details:
        movie_id, title, year, genre, poster_path = movie[0], movie[1], movie[2], movie[3], movie[4]

        movie_item = Ui_movie_grid()
        movie_item_widget = ClickableWidget(parent=result_window)  # Use ClickableWidget
        movie_item.setupUi(movie_item_widget)

        truncated_title = title if len(title) <= max_title_length else title[:max_title_length] + "..."
        title_date_str = (f"<html><head/><body><p>{truncated_title}<span style=\" vertical-align:super;\"> "
                          f"({str(year)})</span></p></body></html>")
        tooltip_str = (f"<html><head/><body><p><span style=\" font-size:24pt; font-weight:600;\">"
                       f"{title}</p></body></html>")
        movie_item.movie_title.setText(title_date_str)
        movie_item.movie_title.setToolTip(tooltip_str)
        movie_item.movie_poster.setPixmap(QPixmap(poster_path))
        movie_item.movie_genre.setText(genre)
        movie_item.movie_genre.setToolTip(genre)
        movie_item.__setattr__('movie_id', movie_id)

        item = QtWidgets.QListWidgetItem(result_window)
        item.setSizeHint(movie_item_widget.sizeHint())
        movie_item_widget.ui_movie_grid_instance = movie_item
        args = (movie[0], result_window)
        movie_item_widget.clicked.connect(lambda mid=args: movie_item_clicked(mid))  # Connect custom signal
        result_window.setItemWidget(item, movie_item_widget)


def launch_movie(args):
    movie_id, path, series = args
    if series:
        part_paths = get_movie_parts(movie_id)

        # Create a temporary playlist file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m3u") as playlist_file:
            playlist_file.write(f"{path}\n".encode("utf-8"))
            for part_path in part_paths:
                playlist_file.write(f"{part_path}\n".encode("utf-8"))
            playlist_path = playlist_file.name

        # Launch the media player with the playlist
        subprocess.Popen(['xdg-open', playlist_path])
    else:
        subprocess.Popen(['xdg-open', path])


def pop_path(args):
    movie_id, list_item, series = args
    auto_updated, path = path_verify(movie_id)

    if auto_updated:
        if path:
            list_item.play_movie.setToolTip(path)
            list_item.play_movie.clicked.disconnect()
            args = (movie_id, path, series)
            list_item.play_movie.clicked.connect(lambda: launch_movie(args))
        current_date = datetime.now().strftime('%Y-%m-%d')
        list_item.filepath_verified.setText(current_date)
        list_item.filepath_status.setChecked(True)
    else:
        list_item.filepath_verified.setText('')
        list_item.filepath_status.setChecked(False)


def update_keywords_list_item(list_item):
    current_date = datetime.now().strftime('%Y-%m-%d')
    list_item.keywords_updated.setText(current_date)
    list_item.keyword_status.setChecked(True)


def keyword_dialog(args):
    title, movie_id, list_item = args
    dialog = KeywordsDialog(movie_id, title)
    # Connect the custom signal to the update function
    dialog.keywords_updated.connect(lambda: update_keywords_list_item(list_item))

    if dialog.exec_():
        pass


def delete_movie(args):
    movie_id, title, list_item_widget, result_window = args
    deleted = dialog_delete(movie_id, title)
    if deleted:
        for index in range(result_window.count()):
            item = result_window.item(index)
            if result_window.itemWidget(item) == list_item_widget:
                result_window.takeItem(index)
                break
