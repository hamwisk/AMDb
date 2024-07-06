# ui/mainwindow.py
import os

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt, pyqtSlot, QThread, QTimer
from PyQt5.QtWidgets import QMainWindow, QListWidget, QDialog, QLabel, QVBoxLayout, QProgressBar, QPushButton, QMessageBox

from config.logger import log_info
from db.API_request import get_tt_data
from db.database_operations import keyword_scan, get_movies, u_watch
from db.make_new import reset_amdb
from db.movie_processing_thread import MovieProcessingThread, process_meta_data
from db.verify_database import VerifyDatabaseWorker
from ui.fix_dialog import FixPathDialog
from ui.populate_display import create_grid_items, create_list_items
from ui.preferences_dialog import PreferencesDialog
from ui.search_criteria import SearchToolboxHandler
from ui.ui_main_window import Ui_MovieCat
from ui.view_log import ViewLog


class MainApp(QMainWindow):
    def __init__(self, config, splash):
        super().__init__()
        self.paths_to_fix = []  # List to queue paths that need fixing
        self.movies_to_search = []
        self.current_search_dialog = None
        self.current_fix_dialog = None
        self.worker_thread_complete = False
        self.search_processing_complete = False
        self.toolbar_widget = None
        self.batch_operations_toolbar = None
        self.len_movies = None
        self.loaded_movies = None
        self.selected_keywords = []
        self.movie_processing_thread = None
        self.progress_bar = None
        self.previously_selected_tab = None
        self.selected_movies = None
        self.selected_style = None
        self.unselected_style = None
        self.thread = None
        self.worker = None

        self.ui = Ui_MovieCat()
        self.ui.setupUi(self)
        self.config_handler = config
        self.splash = splash
        self.toolbox_handler = SearchToolboxHandler(self.ui, params='init')

        self.search_keyword_debounce = QTimer()
        self.search_crit_debounce = QTimer()
        self.display_flow_debounce_timer = QTimer()

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.expanduser("~/.local/share/amdb/assets/amdb.ico")))
        self.setWindowIcon(icon)

        # Initialize display mode and search column as class-level variables
        self.display_mode = self.config_handler.get_config_option('Display', 'display_mode')
        self.search_col = int(self.config_handler.get_config_option('Sort', 'method'))
        self.reverse_mode = self.config_handler.get_config_option('Sort', 'descending')

        # Set the main window size
        window_width = int(self.config_handler.get_config_option('Display', 'window_width', default=1144))
        window_height = int(self.config_handler.get_config_option('Display', 'window_height', default=567))
        self.resize(window_width, window_height)

        # Create the result_window
        self.result_window = QListWidget()
        self.result_window.setViewMode(QtWidgets.QListView.IconMode)
        self.result_window.setFlow(QtWidgets.QListView.LeftToRight)

        # Define lazy-loading params
        self.load_size = 50  # Number of movies to load at a time
        self.current_offset = 0
        self.movie_details = []  # Store all fetched movie details

        # Override the wheelEvent method for result_window
        def wheel_event(event):
            delta_boost = 1
            delta = (-event.angleDelta().y()) * delta_boost
            if event.modifiers() & Qt.ControlModifier:
                x = self.result_window.horizontalScrollBar().value()
                self.result_window.horizontalScrollBar().setValue(x - delta)
            if event.modifiers() & Qt.ShiftModifier:
                y = self.result_window.verticalScrollBar().value()
                # Multiply the delta by 0.1 when Shift is pressed and convert to integer
                self.result_window.verticalScrollBar().setValue(int(y + (0.1 * delta)))
            else:
                y = self.result_window.verticalScrollBar().value()
                self.result_window.verticalScrollBar().setValue(int(y + delta))

        self.result_window.wheelEvent = wheel_event

        self.setup_timers()
        self.setup_connections()

        self.on_tab_changed()
        self.display_flow()
        self.display_update('init')

    def setup_timers(self):
        # Set up a timer for debouncing search criteria
        self.search_crit_debounce.setInterval(250)
        self.search_crit_debounce.setSingleShot(True)
        self.search_crit_debounce.timeout.connect(lambda: self.display_update('scan'))
        # Set up a timer for debouncing search keyword
        self.search_keyword_debounce.setInterval(250)
        self.search_keyword_debounce.setSingleShot(True)
        self.search_keyword_debounce.timeout.connect(lambda: self.display_update('keyword'))
        # Set up a timer for debouncing display_flow
        self.display_flow_debounce_timer.setInterval(240)
        self.display_flow_debounce_timer.setSingleShot(True)
        self.display_flow_debounce_timer.timeout.connect(self.display_flow)

    def setup_connections(self):
        # Connect the scroll event
        self.result_window.verticalScrollBar().valueChanged.connect(self.lazy_load_more)

        # Connect the currentChanged and itemSelectionChanged signals
        self.ui.display_tabs.currentChanged.connect(self.on_tab_changed)
        self.result_window.itemSelectionChanged.connect(self.result_select)

        # Connect signals and slots for the menu bar: File
        self.ui.actionAdd_Movies.triggered.connect(self.add_movies)
        self.ui.actionImport_Database.triggered.connect(self.db_import)
        self.ui.actionExport_Database.triggered.connect(self.db_backup)
        self.ui.actionClose.triggered.connect(self.close)

        # Connect signals and slots for the menu bar: Edit
        self.ui.actionVerify_Paths.triggered.connect(self.verify_paths)
        self.ui.actionReset_Data.triggered.connect(reset_amdb)
        self.ui.actionPreferences.triggered.connect(self.preferences)

        # Connect signals and slots for the menu bar: View
        if self.config_handler.get_config_option('Display', 'display_mode') == 'grid':
            self.ui.actionGrid_View.setChecked(True)
        else:
            self.ui.actionGrid_View.setChecked(False)
        self.ui.actionGrid_View.triggered.connect(
            lambda checked=self.ui.actionGrid_View.isChecked(): self.set_view(checked))
        self.ui.actionAdded.triggered.connect(lambda: self.set_sort_method('0'))
        self.ui.actionTitle.triggered.connect(lambda: self.set_sort_method('1'))
        self.ui.actionYear.triggered.connect(lambda: self.set_sort_method('2'))
        self.ui.actionDescending.triggered.connect(lambda: self.set_sort_method('3'))
        if self.config_handler.get_config_option('Sort', 'descending') == 'True':
            self.ui.actionDescending.setChecked(True)
        self.ui.actionView_Log.triggered.connect(self.view_log)
        self.ui.actionInfo.triggered.connect(self.view_splash)

        # Connect signals and slots for the menu bar: Window
        self.ui.actionMinimise.triggered.connect(self.showMinimized)
        self.ui.actionMaximise.triggered.connect(self.showMaximized)
        self.ui.actionFull_Screen.triggered.connect(self.showFullScreen)

        # Connect the signals for basic search criteria
        self.ui.watched_checkBox.stateChanged.connect(lambda: self.display_update('w:0'))
        self.ui.watched_checkBox.stateChanged.connect(self.display_update_debounce)
        self.ui.unwatched_checkBox.stateChanged.connect(lambda: self.display_update('w:1'))
        self.ui.unwatched_checkBox.stateChanged.connect(self.display_update_debounce)
        self.ui.rating_select.valueChanged.connect(self.display_update_debounce)
        self.ui.title_edit.textChanged.connect(self.display_update_debounce)
        self.ui.director_edit.textChanged.connect(self.display_update_debounce)
        self.ui.actor_edit.textChanged.connect(self.display_update_debounce)
        self.ui.language_edit.currentIndexChanged.connect(self.display_update_debounce)
        self.ui.country_edit.currentIndexChanged.connect(self.display_update_debounce)
        self.ui.mparating_list.itemSelectionChanged.connect(self.display_update_debounce)

        # Connect the signals for date search criteria
        self.ui.year_radio.toggled['bool'].connect(lambda: self.display_update('year'))
        self.ui.year_radio.toggled['bool'].connect(self.ui.year_edit.setEnabled)
        self.ui.year_edit.valueChanged.connect(lambda: self.display_update('year'))
        self.ui.decade_radio.toggled['bool'].connect(lambda: self.display_update('decade'))
        self.ui.decade_radio.toggled['bool'].connect(self.ui.decade_edit.setEnabled)
        self.ui.decade_edit.valueChanged.connect(lambda: self.display_update('decade'))
        self.ui.date_tabs.currentChanged.connect(lambda: self.display_update('range'))
        self.ui.minrange_edit.valueChanged.connect(self.display_update_debounce)
        self.ui.minrange_edit.valueChanged.connect(lambda: self.display_update('max_range'))
        self.ui.maxrange_edit.valueChanged.connect(self.display_update_debounce)
        self.ui.maxrange_edit.valueChanged.connect(lambda: self.display_update('min_range'))

        # Connect the signals for genre search criteria
        self.ui.genre_include.itemSelectionChanged.connect(self.display_update_debounce)
        self.ui.genre_exclude.itemSelectionChanged.connect(self.display_update_debounce)

        # Connect the signals for keyword search criteria
        self.ui.keywords_edit.textChanged.connect(self.keyword_update_debounce)
        self.ui.keywords.itemClicked.connect(self.toggle_selected_keyword)

        # Connect the signals for clear functions
        self.ui.filter_clear.released.connect(lambda: self.display_update('c:0'))
        self.ui.basicfilter_clear.released.connect(lambda: self.display_update('c:1'))
        self.ui.date_clear.released.connect(lambda: self.display_update('c:2'))
        self.ui.genre_clear.released.connect(lambda: self.display_update('c:3'))
        self.ui.keyword_clear.released.connect(lambda: self.display_update('c:4'))

    @pyqtSlot()
    def add_movies(self):
        from db.add_movies import extract_movie_details
        extensions = self.config_handler.get_config_option("Movie", "movie_extensions")
        p_inc, y_ish, t_ish, d_ish, s_inc = extract_movie_details(self, extensions)
        from ui.add_movies import AddMoviesUI
        # Show the Add Movies UI and pass the movie lists
        add_movies_ui = AddMoviesUI(p_inc, y_ish, t_ish, d_ish, s_inc)
        result = add_movies_ui.exec_()
        if result == QDialog.Accepted:
            # User clicked "OK", and selected_movies contains the selected movies list
            selected_movies = add_movies_ui.selected_movies
            request_type = self.config_handler.get_config_option("API server", "r_type")
            # Create an instance of MovieProcessingThread
            self.movie_processing_thread = MovieProcessingThread(selected_movies, request_type)
            # Connect signals from the thread to update UI
            self.movie_processing_thread.emit_progress_signal.connect(self.update_progress)
            self.movie_processing_thread.emit_search_results_signal.connect(self.queue_search)
            self.movie_processing_thread.emit_complete_signal.connect(self.worker_thread_finished)
            # Start the thread
            self.update_progress(0)
            self.movie_processing_thread.start()
            self.worker_thread_complete = False  # Reset flag
            self.search_processing_complete = True  # Reset flag

    @pyqtSlot(dict)
    def queue_search(self, result):
        self.search_processing_complete = False
        self.movies_to_search.append(result)
        if not self.current_search_dialog:
            self.show_next_search_dialog()

    def show_next_search_dialog(self):
        if self.movies_to_search:
            movie_id = None
            result = self.movies_to_search.pop(0)

            from ui.search_dialog import MovieSelectionDialog
            self.current_search_dialog = MovieSelectionDialog(result, self)

            if self.current_search_dialog.exec_():
                # Retrieve the selected movie
                selected_movie = self.current_search_dialog.selected_movie()
                if selected_movie:
                    imdb_id = selected_movie.get('imdb_id')
                    path = selected_movie.get('path')
                    if imdb_id:
                        # Proceed with updating the database using imdb_id
                        movie_details = get_tt_data(imdb_id, 0)
                        selected_movie['path'] = path  # Ensure path is included in the movie dictionary
                        movie_id = process_meta_data(selected_movie, movie_details)  # Pass the movie dictionary

            if movie_id:
                self.on_search_dialog_closed()

    def on_search_dialog_closed(self):
        self.current_search_dialog = None
        if self.movies_to_search:
            self.show_next_search_dialog()
        else:
            self.search_processing_complete = True
            self.processing_complete()

    @pyqtSlot()
    def worker_thread_finished(self):
        self.worker_thread_complete = True
        self.processing_complete()

    def processing_complete(self):
        if self.worker_thread_complete and self.search_processing_complete:
            # Processing is complete
            self.statusBar().clearMessage()
            self.statusBar().removeWidget(self.progress_bar)
            # Show the processing finished message
            QMessageBox.information(self, "New movies added to the database",
                                    "Updated database, please click to refresh the display", QMessageBox.Ok)
            if QMessageBox.Ok:
                self.toolbox_handler.region_set()

    def update_progress(self, progress):
        self.ui.statusbar.clearMessage()  # Clear previous messages

        # Check if the progress bar exists
        if not self.progress_bar:
            # Create a progress bar
            self.progress_bar = QProgressBar(self)
            self.progress_bar.setGeometry(10, 10, 200, 25)
            self.statusBar().addWidget(self.progress_bar)

        # Update the progress bar value
        self.progress_bar.setValue(progress)

    @pyqtSlot()
    def db_backup(self):
        from db.impex import export_db
        export_db(self)

    @pyqtSlot()
    def db_import(self):
        from db.impex import import_db
        import_db(self)
        self.display_update_debounce()

    @pyqtSlot()
    def closeEvent(self, event):
        log_info("Closing application")

        window_width = int(self.config_handler.get_config_option('Display', 'window_width',
                                                                 default=1001))
        window_height = int(self.config_handler.get_config_option('Display', 'window_height',
                                                                  default=561))
        window_size = self.size()
        width, height = window_size.width(), window_size.height()
        if window_width != width:
            self.config_handler.set_config_option('Display', 'window_width', width)
        if window_height != height:
            self.config_handler.set_config_option('Display', 'window_height', height)

        # Log the end of the program and close
        log_info("AMDb program finished")
        self.close()

    def resizeEvent(self, event):
        # Call the debounced display_flow when the window is resized
        self.display_flow_debounce_timer.start()

        # Continue with any other actions you want to take on resize
        super().resizeEvent(event)

    @pyqtSlot()
    def verify_paths(self):
        verify_dialog = QDialog(self)
        verify_dialog.setWindowTitle("Verifying Database")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.expanduser("~/.local/share/amdb/assets/amdb.ico")))
        verify_dialog.setWindowIcon(icon)

        layout = QVBoxLayout()

        label = QLabel("Repairing broken movie paths... Please wait.")
        layout.addWidget(label)

        # Create a progress bar
        progress_bar = QProgressBar(self)
        progress_bar.setGeometry(10, 10, 200, 25)
        layout.addWidget(progress_bar)
        progress_bar.setValue(0)

        cancel_button = QPushButton("Cancel")  # Sends signal to worker to stop
        layout.addWidget(cancel_button)
        verify_dialog.setLayout(layout)

        # Set up the worker and thread
        self.thread = QThread()
        self.worker = VerifyDatabaseWorker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(verify_dialog.close)

        self.worker.progress.connect(progress_bar.setValue)
        self.worker.unfixed.connect(self.queue_fix_dialog)  # Connect the unfixed signal to queue_fix_dialog
        cancel_button.clicked.connect(self.worker.stop)
        cancel_button.clicked.connect(self.thread.quit)

        self.thread.start()
        verify_dialog.exec()

        # Show the verification finished message
        QMessageBox.information(self, "Database Verification Finished",
                                "Verification has finished. Please check the log for details.", QMessageBox.Ok)

    @pyqtSlot(tuple)
    def queue_fix_dialog(self, movie_data):
        self.paths_to_fix.append(movie_data)
        if not self.current_fix_dialog:
            self.show_next_fix_dialog()

    def show_next_fix_dialog(self):
        if self.paths_to_fix:
            movie_data = self.paths_to_fix.pop(0)
            self.current_fix_dialog = FixPathDialog(movie_data[0], self)
            self.current_fix_dialog.finished.connect(self.on_fix_dialog_closed)
            self.current_fix_dialog.exec()

    def on_fix_dialog_closed(self):
        self.current_fix_dialog = None
        self.show_next_fix_dialog()

    @pyqtSlot()
    def preferences(self):
        preferences_dialog = PreferencesDialog(config=self.config_handler)
        preferences_dialog.exec()

    @pyqtSlot()
    def view_log(self):
        log_path = os.path.join(os.path.expanduser("~/.local/share/amdb/logs/"), "main_log.log")
        view_log_dialog = ViewLog(log_path, self)
        view_log_dialog.exec_()  # Use exec_() to display the dialog modal

    @pyqtSlot()
    def set_view(self, checked):
        setting = 'grid' if checked else 'list'
        self.config_handler.set_config_option('Display', 'display_mode', setting)
        self.display_mode = setting  # Update the class-level variable
        self.display_flow_debounce_timer.start()
        self.on_tab_changed()

    @pyqtSlot()
    def set_sort_method(self, method):
        # Set 'sort' option specified in the config file
        option = 'method'
        if method == '3':
            option = 'descending'
            method = self.ui.actionDescending.isChecked()
            self.reverse_mode = str(method)
        else:
            self.search_col = int(method)
        self.config_handler.set_config_option('Sort', option, method)
        self.display_update_debounce()

    @pyqtSlot()
    def view_splash(self):
        self.splash.show()

    @pyqtSlot()
    def on_tab_changed(self):
        # Get the current and previous tabs
        current_tab_widget = self.ui.display_tabs.currentWidget()

        # Clear the result_window
        self.result_window.clear()
        self.result_window.movie_details_dialogs = []

        # Remove result_window from the previous tab's layout
        if self.previously_selected_tab is not None:
            previous_tab_layout = self.previously_selected_tab.layout()
            if previous_tab_layout is not None:
                previous_tab_layout.removeWidget(self.result_window)
                previous_tab_layout.removeWidget(self.toolbar_widget)

        # Add result_window to the current tab's layout
        current_tab_layout = current_tab_widget.layout()
        if current_tab_layout is not None:
            current_tab_layout.addWidget(self.result_window)

            if self.display_mode == 'list':
                # Add the batch operations toolbar
                from ui.batch_operations_toolbar import BatchOperationsToolbar
                self.batch_operations_toolbar = BatchOperationsToolbar()
                self.toolbar_widget = QtWidgets.QWidget()
                self.batch_operations_toolbar.ui.setupUi(self.toolbar_widget)
                self.toolbar_widget.setVisible(False)  # Initially hidden
                current_tab_layout.addWidget(self.toolbar_widget)
                # Connect toolbar signals to main window slots
                self.batch_operations_toolbar.removeMovie.connect(self.remove_movie)
                self.batch_operations_toolbar.clearSelection.connect(self.clear_selected_movies)

                # Set the drag-and-drop settings for the result_window (QListWidget)
                self.result_window.setDragEnabled(False)
                self.result_window.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)

        # Update the previously_selected_tab
        self.previously_selected_tab = current_tab_widget
        self.display_update_debounce()

    def display_update_debounce(self):
        # Restart the timer when a search parameter changes
        self.search_crit_debounce.start()  # Adjust the timeout (milliseconds) based on your needs
        self.ui.statusbar.showMessage(f"Searching the database...")

    def keyword_update_debounce(self):
        # Restart the timer when a search parameter changes
        self.search_keyword_debounce.start()  # Adjust the timeout (milliseconds) based on your needs

    def toggle_selected_keyword(self, item):
        keyword = item.text()
        if keyword in self.selected_keywords:
            self.selected_keywords.remove(keyword)
            self.keyword_update_debounce()  # Debounce keyword scan after removing a selected keyword
        else:
            self.ui.keywords_edit.clear()
            self.selected_keywords.append(keyword)
            self.ui.keywords.clear()
            self.ui.keywords.addItems(self.selected_keywords)  # Add selected keywords
            self.ui.keywords.selectAll()  # Select all rows
        self.display_update_debounce()

    def display_flow(self):
        adjusted_width = self.result_window.width() + 292
        if self.display_mode == 'grid':
            optimal_grid_item_width = int((adjusted_width - 310) / max(1, int((adjusted_width - 310) / 310)))
            row_width = optimal_grid_item_width
            row_height = 530
            self.result_window.setGridSize(QtCore.QSize(row_width, row_height))
            self.result_window.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
            self.result_window.setUniformItemSizes(True)
        elif self.display_mode == 'list':
            row_width = int(self.result_window.width() - 22)
            row_height = 51
            self.result_window.setGridSize(QtCore.QSize(row_width, row_height))
            self.result_window.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
            self.unselected_style = """
                QWidget {
                    background-color: white;
                    color: black;
                }
            """
            self.selected_style = """
                QWidget {
                    background-color: lightblue;
                    color: black;
                }
            """
        else:
            # Set a default view mode to 'grid' if the setting is unknown
            self.set_view(1)

    def display_update(self, param):
        if param == 'scan':
            search_criteria = self.toolbox_handler.get_search_criteria()
            keywords = self.selected_keywords
            self.current_offset = 0  # Reset the offset for a new search
            selected_tab = self.ui.display_tabs.tabText(self.ui.display_tabs.currentIndex())
            self.movie_details = (get_movies
                                  (details=search_criteria, keywords=keywords, tab=selected_tab,
                                   limit=self.load_size, offset=self.current_offset,
                                   sort_method=self.search_col, descending=self.reverse_mode, fields=self.display_mode))
            self.current_offset = self.load_size
            self.populate_result_window(self.movie_details, append=False)  # Clear existing items initially
            self.batch_operations_toolbar.setup_connections() if self.display_mode != 'grid' else None
            self.ui.statusbar.clearMessage()
        elif param == 'range':
            if self.ui.date_tabs.currentIndex() == 1:
                # Uncheck radio buttons
                self.ui.year_radio.setAutoExclusive(False)
                self.ui.year_radio.setChecked(False)
                self.ui.decade_radio.setChecked(False)
                # Disable spin boxes
                self.ui.year_edit.setEnabled(False)
                self.ui.decade_edit.setEnabled(False)
                if self.ui.year_radio.setAutoExclusive(True):
                    pass
        elif param == 'min_range':
            if self.ui.minrange_edit.value() > self.ui.maxrange_edit.value():
                self.ui.minrange_edit.setValue(self.ui.maxrange_edit.value())
        elif param == 'max_range':
            if self.ui.maxrange_edit.value() < self.ui.minrange_edit.value():
                self.ui.maxrange_edit.setValue(self.ui.minrange_edit.value())
        elif param == 'year':
            self.ui.minrange_edit.setValue(self.ui.year_edit.value())
            self.ui.maxrange_edit.setValue(self.ui.year_edit.value())
        elif param == 'decade':
            self.ui.minrange_edit.setValue(self.ui.decade_edit.value())
            self.ui.maxrange_edit.setValue(self.ui.decade_edit.value() + 9)
        elif param == 'w:0' or param == 'w:1':
            index = int(param.split(':')[1])
            self.toolbox_handler.handle_checkbox_state_change(index)
        elif param == 'keyword':
            self.ui.keywords.clear()
            self.ui.keywords.addItems(self.selected_keywords)  # Add selected keywords
            self.ui.keywords.selectAll()  # Select all rows
            keyword_value = self.ui.keywords_edit.text().strip()
            if keyword_value:
                keywords = sorted(keyword_scan(f'%{keyword_value}%'))
                selected_keywords_set = set(self.selected_keywords)
                unselected_keywords = [keyword for keyword in keywords if keyword not in selected_keywords_set]
                self.ui.keywords.addItems(unselected_keywords)  # Add unselected keywords
            pass
        elif param == 'c:0' or param == 'c:1' or param == 'c:2' or param == 'c:3' or param == 'c:4':
            index = int(param.split(':')[1])
            self.toolbox_handler.clear_section(index)
            if index == 0 or index == 4:
                self.selected_keywords.clear()
            self.display_update_debounce()
        else:
            pass

    def lazy_load_more(self):
        scroll_threshold = 600
        scroll_position = self.result_window.verticalScrollBar().value()
        scroll_load_point = int(self.result_window.verticalScrollBar().maximum())
        if (scroll_position + scroll_threshold) >= scroll_load_point:
            new_movies = get_movies(details=self.toolbox_handler.get_search_criteria(), keywords=self.selected_keywords,
                                    tab=self.ui.display_tabs.tabText(self.ui.display_tabs.currentIndex()),
                                    limit=self.load_size, offset=self.current_offset,
                                    sort_method=self.search_col, descending=self.reverse_mode, fields=self.display_mode)
            self.current_offset += self.load_size
            self.populate_result_window(new_movies, append=True)

    def populate_result_window(self, movie_details, append=False):
        if not append:
            self.result_window.clear()

        # Conditional check for grid/List view-mode
        if self.display_mode == 'grid':
            create_grid_items(movie_details, self.result_window)
        elif self.display_mode == 'list':
            create_list_items(movie_details, self.result_window, self.unselected_style)
        else:
            self.set_view(1)

    def result_select(self):
        self.selected_movies = []
        for i in range(self.result_window.count()):
            item = self.result_window.item(i)
            widget = self.result_window.itemWidget(item)
            if item.isSelected():
                widget.setStyleSheet(self.selected_style)
                # movie should have the movie's id and title
                movie = (widget.movie_id, widget.ui_movie_list_instance.title.text())
                self.selected_movies.append(movie)
            else:
                widget.setStyleSheet(self.unselected_style)

        if len(self.selected_movies) >= 2:
            self.batch_operations_toolbar.update_selected_movies_list(self.selected_movies)
            self.toolbar_widget.setVisible(True)  # Initially hidden
            # Show toolbar if hidden and update the selected movies list
            pass
        else:
            self.toolbar_widget.setVisible(False)
            # Hide toolbar if showing
            pass

    @pyqtSlot(int)
    def remove_movie(self, movie_id):
        for i in range(self.result_window.count()):
            item = self.result_window.item(i)
            widget = self.result_window.itemWidget(item)
            if item.isSelected() and widget.movie_id == movie_id:
                item.setSelected(False)

    @pyqtSlot()
    def clear_selected_movies(self):
        self.display_update_debounce()

    def movie_item_clicked(self, args):
        movie, result_window = args
        from ui.movie_details import MovieDetailsDialog
        open_movie_dialogs = result_window.movie_details_dialogs

        for dialog in open_movie_dialogs:
            if dialog.movie_id == movie[0]:
                dialog.show()
                dialog.raise_()
                return

        movie_details_dialog = MovieDetailsDialog(movie, parent=self)
        movie_details_dialog.watched_state_changed.connect(self.update_watched_status)
        movie_details_dialog.show()

        # Add the dialog to the list of open dialogs
        open_movie_dialogs.append(movie_details_dialog)

    def update_watched_status(self, movie_id, is_watched):
        if self.display_mode == 'list':
            # Find the corresponding list item and update its checkbox state
            for i in range(self.result_window.count()):
                item = self.result_window.item(i)
                widget = self.result_window.itemWidget(item)
                if widget and widget.movie_id == movie_id:
                    widget.ui_movie_list_instance.watched_status.setChecked(is_watched)
                    break
        else:
            u_watch(movie_id)
