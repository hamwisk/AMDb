# ui/search_criteria.py
import os
from datetime import datetime

from config.config_handler import ConfigHandler
from db.database_operations import get_all_languages_and_countries

CONFIG_FILE = os.path.expanduser("~/.config/amdb/config.ini")


class SearchToolboxHandler:
    def __init__(self, ui, params):
        self.ui = ui
        self.config_handler = ConfigHandler(CONFIG_FILE)
        self.params = params

        if params == 'init':
            self.initialize_search_toolbox()

    def initialize_search_toolbox(self):
        current_year = datetime.now().year
        current_decade = (current_year // 10) * 10
        self.ui.minrange_edit.setValue(1878)
        self.ui.minrange_edit.setMinimum(1878)
        self.ui.maxrange_edit.setMaximum(current_year)
        self.ui.maxrange_edit.setValue(current_year)
        self.ui.maxrange_edit.setMinimum(self.ui.minrange_edit.value())
        self.ui.minrange_edit.setMaximum(self.ui.maxrange_edit.value())
        self.ui.year_edit.setMaximum(current_year)
        self.ui.year_edit.setValue(current_year)
        self.ui.decade_edit.setMaximum(current_decade)
        self.ui.decade_edit.setValue(current_decade)
        self.region_set()

    def handle_checkbox_state_change(self, checkbox):
        if self.ui.watched_checkBox.isChecked() or self.ui.unwatched_checkBox.isChecked():
            pass
        else:
            if checkbox == 0:
                self.ui.watched_checkBox.setChecked(True)
            else:
                self.ui.unwatched_checkBox.setChecked(True)

    def region_set(self):
        # Clear existing items
        self.ui.language_edit.clear()
        self.ui.country_edit.clear()

        # Set up combo-boxes
        self.ui.language_edit.addItem('All')
        self.ui.country_edit.addItem('All')

        # Fetch languages and countries from the database
        data = get_all_languages_and_countries()

        # Populate languages
        for lang in data['languages']:
            if lang != 'All':
                self.ui.language_edit.addItem(lang)

        # Populate countries
        for country in data['countries']:
            if country != 'All':
                self.ui.country_edit.addItem(country)

    def get_search_criteria(self):
        criteria = {}

        # Watched status
        if self.ui.watched_checkBox.isChecked():
            if self.ui.unwatched_checkBox.isChecked():
                # Both watched and unwatched checkboxes are checked (no filtering)
                pass
            else:
                # Only the watched checkbox is checked
                criteria['watched'] = 1
        elif self.ui.unwatched_checkBox.isChecked():
            # Only the unwatched checkbox is checked
            criteria['watched'] = 0

        # Check the rating slider and add to search parameters
        min_rating = self.ui.rating_select.value()
        if min_rating > 0:
            criteria['rating'] = min_rating

        # Title
        title_edit = self.ui.title_edit.text().strip()
        if title_edit:
            criteria['title'] = title_edit

        # Director
        director_edit = self.ui.director_edit.text().strip()
        if director_edit:
            criteria['director'] = director_edit

        # Actor
        actor_edit = self.ui.actor_edit.text().strip()
        if actor_edit:
            criteria['actors'] = actor_edit

        # Language
        language_edit = self.ui.language_edit.currentText()
        if language_edit != 'All' and language_edit != '':
            criteria['language'] = language_edit

        # Country
        country_edit = self.ui.country_edit.currentText()
        if country_edit != 'All' and country_edit != '':
            criteria['country'] = country_edit

        # Check selected MPA rating list and add to search parameters
        selected_rated = [item.text() for item in self.ui.mparating_list.selectedItems()]
        if selected_rated:
            # Add all selected MPA ratings to search parameters
            criteria['selected_rated'] = selected_rated

        # Check the release date criteria and add to search parameters
        if self.ui.year_radio.isChecked() or self.ui.decade_radio.isChecked():
            if self.ui.minrange_edit.value() == self.ui.maxrange_edit.value():
                criteria['year'] = self.ui.minrange_edit.value()
            else:
                criteria['range_min'] = self.ui.minrange_edit.value()
                criteria['range_max'] = self.ui.maxrange_edit.value()
        elif not self.ui.year_radio.isChecked() and not self.ui.decade_radio.isChecked():
            if self.ui.minrange_edit.value() == 1880 and self.ui.maxrange_edit.value() == datetime.now().year:
                pass
            else:
                if self.ui.minrange_edit.value() == self.ui.maxrange_edit.value():
                    criteria['year'] = self.ui.minrange_edit.value()
                else:
                    criteria['range_min'] = self.ui.minrange_edit.value()
                    criteria['range_max'] = self.ui.maxrange_edit.value()

        # Genre inclusion
        genre_include = self.ui.genre_include.selectedItems()
        genres_included = [item.text() for item in genre_include]
        if genres_included:
            criteria['genres_included'] = genres_included

        # Genre exclusion
        genre_exclude = self.ui.genre_exclude.selectedItems()
        genres_excluded = [item.text() for item in genre_exclude]
        if genres_excluded:
            criteria['genres_excluded'] = genres_excluded

        # Keyword inclusion
        keyword_include = self.ui.keywords.selectedItems()
        keywords_included = [item.text() for item in keyword_include]
        if keywords_included:
            criteria['keywords_included'] = keywords_included

        return criteria

    def clear_basic_filter_section(self):
        self.ui.actor_edit.clear()
        self.ui.director_edit.clear()
        self.ui.title_edit.clear()
        self.ui.language_edit.setCurrentIndex(0)
        self.ui.country_edit.setCurrentIndex(0)
        self.ui.mparating_list.clearSelection()
        self.ui.rating_select.setValue(0)
        self.ui.watched_checkBox.setChecked(True)
        self.ui.unwatched_checkBox.setChecked(True)

    def clear_date_section(self):
        # Uncheck radio buttons
        self.ui.year_radio.setAutoExclusive(False)
        self.ui.year_radio.setChecked(False)
        self.ui.decade_radio.setChecked(False)
        # Disable spin boxes
        self.ui.year_edit.setEnabled(False)
        self.ui.decade_edit.setEnabled(False)
        if self.ui.year_radio.setAutoExclusive(True):
            pass

        # Set datetime and year search parameters
        current_year = datetime.now().year
        current_decade = (current_year // 10) * 10
        self.ui.year_edit.setMaximum(current_year)
        self.ui.year_edit.setValue(current_year)
        self.ui.decade_edit.setMaximum(current_decade)
        self.ui.decade_edit.setValue(current_decade)
        self.ui.maxrange_edit.setMinimum(self.ui.minrange_edit.value())
        self.ui.minrange_edit.setMaximum(self.ui.maxrange_edit.value())
        self.ui.minrange_edit.setValue(1880)
        self.ui.maxrange_edit.setValue(current_year)

    def clear_genre_section(self):
        self.ui.genre_exclude.clearSelection()
        self.ui.genre_include.clearSelection()

    def clear_keyword_section(self):
        self.ui.keywords_edit.clear()
        self.ui.keywords.clearSelection()
        self.ui.keywords.clear()

    def clear_all_sections(self):
        self.clear_basic_filter_section()
        self.clear_date_section()
        self.clear_genre_section()
        self.clear_keyword_section()

    def clear_section(self, section):
        if section == 0:
            self.clear_all_sections()
        elif section == 1:
            self.clear_basic_filter_section()
        if section == 2:
            self.clear_date_section()
        if section == 3:
            self.clear_genre_section()
        if section == 4:
            self.clear_keyword_section()
