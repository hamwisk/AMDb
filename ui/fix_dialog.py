# fix_dialog.py
import os
import sqlite3
from datetime import datetime

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog

from config.logger import log_info, log_warning


class FixPathDialog(QDialog):
    finished = pyqtSignal()

    def __init__(self, movie_id, parent=None):
        super().__init__(parent)
        self.submit_button = None
        self.title = None
        self.broken_path = None
        self.line_edit = None
        self.movie_id = movie_id
        self.database_path = os.path.expanduser("~/.local/share/amdb/assets/movies.db")
        self.init_ui()

    def init_ui(self):
        movie_data = self.get_movie_data(self.movie_id)

        self.setWindowTitle(f"Correct Movie Path for {movie_data[0]}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.expanduser("~/.local/share/amdb/assets/amdb.ico")))
        self.setWindowIcon(icon)

        layout = QVBoxLayout()

        # Create UI elements
        self.title = movie_data[0]
        title_label = QLabel(movie_data[0])
        year_label = QLabel(str(movie_data[1]))
        poster_label = QLabel()
        poster_label.setPixmap(QPixmap(movie_data[3]))
        self.broken_path = movie_data[2]
        self.line_edit = QLineEdit(self.broken_path)
        browse_button = QPushButton("Browse")
        self.submit_button = QPushButton("Skip")
        delete_button = QPushButton("Delete")

        # Add UI elements to the layout
        layout.addWidget(title_label)
        layout.addWidget(year_label)
        layout.addWidget(poster_label)
        layout.addWidget(self.line_edit)
        layout.addWidget(browse_button)
        layout.addWidget(self.submit_button)
        layout.addWidget(delete_button)

        # Connect signals to slots
        browse_button.clicked.connect(self.select_path)
        self.submit_button.clicked.connect(self.submit_paths)
        delete_button.clicked.connect(self.delete_broken_path)
        self.line_edit.textChanged.connect(self.skip_continue)

        self.setLayout(layout)

    @pyqtSlot()
    def skip_continue(self):
        if self.line_edit.text() == self.broken_path:
            self.submit_button.setText("Skip")
        else:
            self.submit_button.setText("Submit")

    def get_movie_data(self, movie_id):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT title, year, path, poster_path FROM movies WHERE id=?", (movie_id,))
        movie_data = cursor.fetchone()
        conn.close()
        return movie_data

    @pyqtSlot()
    def select_path(self):
        open_folder = os.path.expanduser("~")
        new_path, _ = QFileDialog.getOpenFileName(
            self, 'Select Movie File', open_folder, 'Video Files (*.mp4 *.mkv *.avi);;All Files (*)'
        )
        if new_path:
            self.line_edit.setText(new_path)

    @pyqtSlot()
    def submit_paths(self):
        new_path = self.line_edit.text()
        if new_path != self.broken_path:
            current_date = datetime.now().strftime('%Y-%m-%d')
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE movies SET path = ?, last_verified = ? WHERE id = ?",
                           (new_path, current_date, self.movie_id))
            conn.commit()
            conn.close()
            log_info(f"Path updated for {self.title} to {new_path}")
        else:
            log_warning(f"Movie with broken path update skipped: {self.title}")
        self.finished.emit()  # Emit finished signal
        super(FixPathDialog, self).accept()

    @pyqtSlot()
    def delete_broken_path(self):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movies WHERE id = ?", (self.movie_id,))
        conn.commit()
        conn.close()
        self.finished.emit()  # Emit finished signal
        super(FixPathDialog, self).reject()
