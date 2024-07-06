# batch_operations_toolbar.py

from PyQt5 import QtCore, QtWidgets

from config.logger import log_info
from db.database_operations import b_watch, path_verify, keywords_update
from db.delete_query import batch_delete
from ui.ui_batch_operations_toolbar import Ui_batch_operations_toolbar


class BatchOperationsToolbar(QtWidgets.QWidget):
    removeMovie = QtCore.pyqtSignal(int)
    clearSelection = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running_batch = 0
        self.ui = Ui_batch_operations_toolbar()
        self.ui.setupUi(self)
        self.setup_connections()

    def setup_connections(self):
        # Set group boxes to be unchecked
        self.ui.watched_groupbox.setChecked(False)
        self.ui.keywords_groupbox.setChecked(False)

        # Connect the delete checkbox to its handler
        self.ui.delete_checkbox.toggled.connect(self.handle_delete_checkbox)

        # Connect the cancel button to its handler
        self.ui.pushButton_2.clicked.connect(self.cancel_selection)

        # Connect the selected items list
        self.ui.selected_movies.disconnect()
        self.ui.selected_movies.clicked.connect(self.handle_deselect_movie)

        # Connect confirm button to execute batch operations
        self.ui.pushButton.released.connect(self.handle_confirm_batch_operation)

    def update_selected_movies_list(self, selected_movies):
        # Create a new list model with the selected movies
        self.ui.selected_movies.clear()

        for movie in selected_movies:
            title = movie[1]
            movie_id = movie[0]
            item = f"{movie_id}: {title}"
            self.ui.selected_movies.addItem(item)

    def handle_delete_checkbox(self, checked):
        # Disable/Enable other checkboxes and controls based on the delete checkbox state
        self.ui.watched_groupbox.setEnabled(not checked)
        self.ui.verify_checkbox.setEnabled(not checked)
        self.ui.keywords_groupbox.setEnabled(not checked)

        # Set group boxes to be unchecked
        self.ui.watched_groupbox.setChecked(False)
        self.ui.keywords_groupbox.setChecked(False)
        self.ui.verify_checkbox.setChecked(False)

    def handle_deselect_movie(self):
        selected_movies = self.ui.selected_movies.selectedItems()
        for movie_item in selected_movies:
            string = movie_item.text()  # Assuming the title is the text of the QListWidgetItem
            movie_id = int(string.split(':')[0])
            self.removeMovie.emit(movie_id)

    def cancel_selection(self):
        self.reset_toolbar()
        self.clearSelection.emit()

    def reset_toolbar(self):
        self.ui.delete_checkbox.setChecked(False)
        self.ui.add_keywords.clear()
        self.ui.remove_keywords.clear()
        self.ui.keywords_groupbox.setChecked(False)
        self.ui.watched_groupbox.setChecked(False)
        self.ui.verify_checkbox.setChecked(False)

    def handle_confirm_batch_operation(self):
        selected_movies = []

        # Compile list of selected movies to process
        for index in range(self.ui.selected_movies.count()):
            item = self.ui.selected_movies.item(index)
            movie_id = int(item.text().split(':')[0])  # Extract the movie ID from the item text
            selected_movies.append(movie_id)

            # Process path verification option for each selected movie
            if self.ui.verify_checkbox.isChecked():
                path_verify(movie_id)

        if self.ui.delete_checkbox.isChecked():
            # Need to be careful with automated  recursive directory removal, especially when running in a loop...
            deletion_level = batch_delete(selected_movies)
            if deletion_level is not None:
                # Perform deletion logic based on the selected deletion level
                log_info(f"Deletion level: {deletion_level}, Movies: {selected_movies}")
        else:
            # Process watched option for all selected movies
            if self.ui.watched_groupbox.isChecked():
                if self.ui.radio_watched.isChecked():
                    b_watch(selected_movies, True)
                elif self.ui.radio_unwatched.isChecked():
                    b_watch(selected_movies, False)

            # Process the option for keywords
            if self.ui.keywords_groupbox.isChecked():
                keywords_add = [kw.strip() for kw in self.ui.add_keywords.toPlainText().split('\n') if kw.strip()]
                keywords_remove = [kw.strip() for kw in self.ui.remove_keywords.toPlainText().split('\n') if kw.strip()]

                # Add and remove keywords for all selected movies
                for movie_id in selected_movies:
                    if keywords_add:
                        keywords_update(movie_id, keywords_add, action='add')
                    if keywords_remove:
                        print(keywords_remove)
                        keywords_update(movie_id, keywords_remove, action='remove')

        self.cancel_selection()
