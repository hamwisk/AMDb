# ui/keywords_dialog.py
import os

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog

from db.database_operations import get_keywords, keywords_update
from ui.ui_keywords_dialog import Ui_Form


class KeywordsDialog(QDialog):
    keywords_updated = pyqtSignal()  # Define a custom signal

    def __init__(self, movie_id, title, parent=None):
        super().__init__(parent)
        self.movie_keywords = None
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle(f"{title} - Keywords")
        self.movie_id = movie_id

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.expanduser("~/.local/share/amdb/assets/amdb.ico")))
        self.setWindowIcon(icon)

        # Connect the add_keyword button to the add_keyword method
        self.ui.add_keyword.clicked.connect(self.add_keyword)

        # Connect the list widget's itemClicked signal to the remove_keyword method
        self.ui.keyword_list.itemClicked.connect(self.remove_keyword)

        # Connect the 'save' and 'cancel' buttons
        self.ui.save_button.clicked.connect(self.save_changes)
        self.ui.cancel_button.clicked.connect(self.close_dialog)

        self.load_keywords()

    def load_keywords(self):
        self.movie_keywords = get_keywords(self.movie_id)
        self.ui.keyword_list.clear()
        if self.movie_keywords:
            self.ui.keyword_list.addItems(self.movie_keywords)

    def add_keyword(self):
        keyword = self.ui.new_keyword.text().strip()
        exists = any(self.ui.keyword_list.item(i).text() == keyword for i in range(self.ui.keyword_list.count()))
        if keyword and not exists:
            self.ui.keyword_list.addItem(keyword)
            self.ui.new_keyword.clear()  # Clear the input field after adding the keyword

    def remove_keyword(self, item):
        self.ui.keyword_list.takeItem(self.ui.keyword_list.row(item))

    def save_changes(self):
        # First make the updated variable and two lists
        updated, keywords_add, keywords_remove = False, [], []

        # Get the current keywords from the list widget
        current_keywords = [self.ui.keyword_list.item(i).text() for i in range(self.ui.keyword_list.count())]

        # Populate the 'add' list
        for keyword in current_keywords:
            if keyword not in self.movie_keywords:
                keywords_add.append(keyword)
                updated = True  # Set updated to True if we have new keywords to add

        # Populate the 'remove' list
        for keyword in self.movie_keywords:
            if keyword not in current_keywords:
                keywords_remove.append(keyword)
                updated = True  # Set updated to True if we have keywords to remove

        # Send keyword changes to database manager to update database
        if keywords_add:
            keywords_update(self.movie_id, keywords_add, action='add')

        if keywords_remove:
            keywords_update(self.movie_id, keywords_remove, action='remove')

        # Emit signal to notify that keywords have been updated
        if updated:
            self.keywords_updated.emit()

        # Close keyword dialog
        self.accept()  # Use accept() to close the dialog and indicate success

    def close_dialog(self):
        self.close()
