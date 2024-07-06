import os

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox

from ui.ui_add_movies import Ui_add_movies_dialog


def populate_list_widget(list_widget, movie_list, selectable=True):
    list_widget.clear()  # Clear the existing items in the list widget
    movie_list = sorted(movie_list, key=lambda x: x['title'])

    for movie in movie_list:
        item = QtWidgets.QListWidgetItem(f"{movie['title']} ({movie['year']})")
        # Set the complete movie dictionary as data for the item
        item.setData(1, movie)

        # Add a tooltip with the movie path
        tooltip_text = f"Path: {movie['path']}"
        item.setToolTip(tooltip_text)

        if not selectable:
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)

        list_widget.addItem(item)


class AddMoviesUI(QDialog):
    def __init__(self, p_inc, y_ish, t_ish, d_ish, s_inc, parent=None):
        super().__init__(parent)
        self.ui = Ui_add_movies_dialog()
        self.ui.setupUi(self)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.expanduser("~/.local/share/amdb/assets/amdb.ico")))
        self.setWindowIcon(icon)

        # Populate and connect itemSelectionChanged for each list widget
        populate_list_widget(self.ui.p_inc_list_widget, p_inc)
        self.ui.p_inc_list_widget.itemSelectionChanged.connect(self.handle_selection_changed)

        populate_list_widget(self.ui.y_ish_list_widget, y_ish)
        self.ui.y_ish_list_widget.itemSelectionChanged.connect(self.handle_selection_changed)

        populate_list_widget(self.ui.t_ish_list_widget, t_ish)
        self.ui.t_ish_list_widget.itemSelectionChanged.connect(self.handle_selection_changed)

        populate_list_widget(self.ui.d_ish_list_widget, d_ish, selectable=False)  # Make duplicates not selectable
        self.ui.d_ish_list_widget.itemSelectionChanged.connect(self.handle_selection_changed)

        populate_list_widget(self.ui.s_inc_list_widget, s_inc)
        self.ui.s_inc_list_widget.itemSelectionChanged.connect(self.handle_selection_changed)

        self.selected_movies = []  # Initialize the selected_movies attribute

        # Connect signals
        self.ui.buttonBox.accepted.connect(self.accept_button_clicked)
        self.ui.buttonBox.rejected.connect(self.reject)

        # Set tab titles
        self.ui.category_tabs.setTabText(
            self.ui.category_tabs.indexOf(self.ui.p_inc_tab),
            f"Possible Inclusions ({len(p_inc)})")
        self.ui.category_tabs.setTabText(
            self.ui.category_tabs.indexOf(self.ui.y_ish_tab),
            f"Year Issues ({len(y_ish)})")
        self.ui.category_tabs.setTabText(
            self.ui.category_tabs.indexOf(self.ui.t_ish_tab),
            f"Title Issues ({len(t_ish)})")
        self.ui.category_tabs.setTabText(
            self.ui.category_tabs.indexOf(self.ui.s_inc_tab),
            f"Series Files ({len(s_inc)})")
        self.ui.category_tabs.setTabText(
            self.ui.category_tabs.indexOf(self.ui.d_ish_tab),
            f"Duplicates ({len(d_ish)})")

    def get_selection(self):
        # Get the selected items from all 5 list widgets
        p_inc_selected_items = self.ui.p_inc_list_widget.selectedItems()
        y_ish_selected_items = self.ui.y_ish_list_widget.selectedItems()
        t_ish_selected_items = self.ui.t_ish_list_widget.selectedItems()
        s_inc_selected_items = self.ui.s_inc_list_widget.selectedItems()

        # Combine the selected items from all list widgets
        selected_items = (
                p_inc_selected_items +
                y_ish_selected_items +
                t_ish_selected_items +
                s_inc_selected_items
        )
        return selected_items

    def handle_selection_changed(self):
        selected_items = self.get_selection()
        # Limit the number of selected items to 100
        if len(selected_items) > 100:
            QMessageBox.warning(self, "Warning", "You can select a maximum of 100 movies.")

            # Deselect the last selected item
            last_item = selected_items[-1]
            last_item.setSelected(False)

    def accept_button_clicked(self):
        # Get selected movies from each tab
        selected_items = self.get_selection()
        for movie in selected_items:
            self.selected_movies.append(movie.data(1))

        self.accept()
