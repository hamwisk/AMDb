# db/delete_query.py
import os

from PyQt5 import QtGui
from PyQt5.QtWidgets import QMessageBox, QCheckBox, QVBoxLayout, QDialog, QLabel, QPushButton, QDialogButtonBox
from send2trash import send2trash

from db.database_operations import get_full_movie_data, u_delete, path_verify, get_movies_titles_and_paths


def is_safe_to_delete_folder(folder_path, movie_title):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if movie_title.lower() not in file.lower():
                return False  # If any file doesn't match the movie title, don't delete the folder
    return True


def delete_folder_and_close(dialog, parent_folder):
    send2trash(parent_folder)
    dialog.accept()


def confirm_delete_folder(folder_path):
    dialog = QDialog()
    dialog.setWindowTitle("Confirm Delete Folder")
    layout = QVBoxLayout()

    # Set the icon
    icon_path = os.path.expanduser("~/.local/share/amdb/assets/amdb.ico")
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(icon_path))
    dialog.setWindowIcon(icon)

    # Add folder name
    folder_label = QLabel(f"Folder: {folder_path}")
    layout.addWidget(folder_label)

    # Add list of files within the folder
    files_list = QLabel("Files in folder:")
    layout.addWidget(files_list)
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_label = QLabel(file)
            layout.addWidget(file_label)

    # Add confirmation button
    confirm_button = QPushButton("Confirm Delete")
    confirm_button.clicked.connect(lambda: delete_folder_and_close(dialog, folder_path))
    layout.addWidget(confirm_button)

    # Add cancel button
    cancel_button = QPushButton("Cancel")
    cancel_button.clicked.connect(dialog.reject)
    layout.addWidget(cancel_button)

    dialog.setLayout(layout)
    dialog.exec_()


def dialog_delete(movie_id, title):
    movie_data = get_full_movie_data(movie_id)
    msgBox = QMessageBox()

    # Set the icon
    icon_path = os.path.expanduser("~/.local/share/amdb/assets/amdb.ico")
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(icon_path))
    msgBox.setWindowIcon(icon)
    msgBox.setWindowTitle(f"Delete movie: {title}")

    msgBox.setText("Are you sure you want to delete this movie?")
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

    # Create checkboxes for deleting file and folder
    checkBoxFile = QCheckBox("Delete from hard drive")
    checkBoxFolder = QCheckBox("Delete containing folder")

    # Function to update the state of checkBoxFile based on checkBoxFolder
    def update_file_checkbox(state):
        if state == 2:  # Folder checkbox checked
            checkBoxFile.setChecked(True)
            checkBoxFile.setEnabled(False)
        else:  # Folder checkbox unchecked
            checkBoxFile.setEnabled(True)

    # Connect the state change of checkBoxFolder to update checkBoxFile
    checkBoxFolder.stateChanged.connect(update_file_checkbox)

    # Add checkboxes to the message box if the file exists
    exists, path = path_verify(movie_id)
    if exists:
        msgBox.layout().addWidget(checkBoxFile)
        msgBox.layout().addWidget(checkBoxFolder)

    # Show the message box and get the user's response
    reply = msgBox.exec_()

    if reply == QMessageBox.Yes:
        # Remove database entry
        u_delete(movie_id, title)

        # If checkbox exists and is checked, delete the parent folder
        if checkBoxFolder.isChecked():
            parent_folder = os.path.dirname(path)
            if is_safe_to_delete_folder(parent_folder, title):
                send2trash(parent_folder)
            else:
                # Display the folder name and list all the files within the folder and prompt user to confirm delete
                confirm_delete_folder(parent_folder)
        # If checkbox exists and is checked, delete the file from hard drive
        elif checkBoxFile.isChecked():
            send2trash(path)
        return True


class DeletionOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Deletion Level")

        layout = QVBoxLayout()

        self.label = QLabel("Select the deletion level:")
        layout.addWidget(self.label)

        self.db_only_checkbox = QCheckBox("Remove database entries and poster images from AMDb only")
        self.db_only_checkbox.setChecked(True)
        self.db_only_checkbox.setEnabled(False)
        self.db_only_checkbox.stateChanged.connect(self.update_checkboxes)
        layout.addWidget(self.db_only_checkbox)

        self.delete_file_checkbox = QCheckBox("Also delete the linked movie file from the filesystem (if possible)")
        self.delete_file_checkbox.stateChanged.connect(self.update_checkboxes)
        layout.addWidget(self.delete_file_checkbox)

        self.delete_folder_checkbox = QCheckBox("Also delete linked movie file parent directory (if possible)")
        self.delete_folder_checkbox.stateChanged.connect(self.update_checkboxes)
        layout.addWidget(self.delete_folder_checkbox)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)
        icon_path = os.path.expanduser("~/.local/share/amdb/assets/amdb.ico")
        self.setWindowIcon(QtGui.QIcon(icon_path))

    def update_checkboxes(self):
        if self.delete_folder_checkbox.isChecked():
            self.delete_file_checkbox.setChecked(True)
            self.delete_file_checkbox.setEnabled(False)
        elif self.delete_file_checkbox.isChecked():
            self.delete_file_checkbox.setEnabled(True)

    def get_selection(self):
        if self.delete_folder_checkbox.isChecked():
            return 3
        elif self.delete_file_checkbox.isChecked():
            return 2
        elif self.db_only_checkbox.isChecked():
            return 1
        return 1


def batch_delete(movie_ids):
    dialog = DeletionOptionsDialog()
    if dialog.exec_() == QDialog.Accepted:
        deletion_level = dialog.get_selection()

        # Fetch movie titles and paths in a single query
        movies_data = get_movies_titles_and_paths(movie_ids)

        for movie_data in movies_data:
            movie_id, title, path = movie_data

            # Remove database entry
            u_delete(movie_id, title)

            # If level 3, delete the parent folder
            if deletion_level == 3:
                parent_folder = os.path.dirname(path)
                if os.path.exists(parent_folder):
                    if is_safe_to_delete_folder(parent_folder, title):
                        send2trash(parent_folder)
                    else:
                        confirm_delete_folder(parent_folder)
            # If level 2, delete the file from hard drive
            elif deletion_level == 2:
                if os.path.isfile(path):
                    send2trash(path)
        return deletion_level
    return None
