# ui/preferences_dialog.py
import os

from PyQt5 import QtGui
from PyQt5.QtWidgets import QDialog, QMessageBox

from ui.ui_preferences import Ui_Dialog


class PreferencesDialog(QDialog, Ui_Dialog):
    def __init__(self, config):
        super().__init__()
        self.setupUi(self)

        # Store the ConfigHandler instance
        self.config_handler = config

        # Initialize UI and load preferences
        self.init_ui()

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.expanduser("~/.local/share/amdb/assets/amdb.ico")))
        self.setWindowIcon(icon)

        self.load_preferences()

        # Connect signals and slots
        self.connect_signals()

    def init_ui(self):
        """Initialize UI components and additional setup."""
        # Populate API server dropdown
        api_ops = sorted(self.config_handler.get_config_option('API server', 'options').split(', '))
        for api in api_ops:
            self.API_server.addItem(api)

    def load_preferences(self):
        """Load existing preferences into the UI."""
        # Load API settings
        api_selected = self.config_handler.get_config_option('API server', 'set')
        self.API_server.setCurrentText(api_selected)
        self.lineEdit_host.setText(self.config_handler.get_config_option('API url', api_selected))
        self.lineEdit_key.setText(self.config_handler.get_config_option('API keys', api_selected))

        # Load request type preferences
        request_type = self.config_handler.get_config_option('API server', 'r_type', default='get')
        if request_type == 'get':
            self.r_type_s.setChecked(True)
        else:
            self.r_type_a.setChecked(True)

    def connect_signals(self):
        """Connect UI components to their corresponding slots."""
        self.toolBox.currentChanged.connect(self.update_stacked_widget)
        self.buttonBox.accepted.connect(self.apply_preferences)
        self.API_server.currentIndexChanged.connect(self.on_api_server_changed)

    def apply_preferences(self):
        """Apply and save the preferences."""
        # Save API settings
        api_selected = self.API_server.currentText()
        self.config_handler.set_config_option('API server', 'set', api_selected)
        self.config_handler.set_config_option('API url', api_selected, self.lineEdit_host.text())
        self.config_handler.set_config_option('API keys', api_selected, self.lineEdit_key.text())

        # Save request type preferences
        request_type = 'get' if self.r_type_s.isChecked() else 'search'
        self.config_handler.set_config_option('API server', 'r_type', request_type)

        # Show a message box indicating that preferences have been applied
        QMessageBox.information(self, 'Preferences Applied', 'Preferences have been applied successfully.')

    def update_stacked_widget(self, index):
        """Update the current page in the stacked widget when the toolbox tab is changed."""
        self.stackedWidget.setCurrentIndex(index)

    def on_api_server_changed(self, index):
        """Handle API server selection change."""
        api_selected = self.API_server.itemText(index)
        self.lineEdit_host.setText(self.config_handler.get_config_option('API url', api_selected))
        self.lineEdit_key.setText(self.config_handler.get_config_option('API keys', api_selected))
