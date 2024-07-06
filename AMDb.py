# AMDb.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer
from config.config_handler import ConfigHandler
from config.logger import log_warning, setup_logging, log_info
from ui.mainwindow import MainApp
from ui.splash import Splash

# Define version number
VERSION_NUMBER = 5.1

# Define paths
DATA_PATH = os.path.expanduser("~/.local/share/amdb/assets/")
LOGS_PATH = os.path.expanduser("~/.local/share/amdb/logs/")
CONFIG_FILE = os.path.expanduser("~/.config/amdb/config.ini")

# Ensure directories exist
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(LOGS_PATH, exist_ok=True)


def main():
    # Initialize the QApplication instance
    app = QApplication(sys.argv)

    # Show splash screen
    splash = Splash(version_number=VERSION_NUMBER)
    splash.show()

    # Initialize config handler
    config = ConfigHandler(CONFIG_FILE)

    # Set up logging
    log_filepath = os.path.join(LOGS_PATH, "main_log.log")
    setup_logging(log_filepath)
    log_info("Starting AMDb")

    # Get the database version number from the config and verify with program version
    version_number = config.get_config_option("Database", "version")
    if float(version_number) != VERSION_NUMBER:
        log_warning("Database version does not match current version of AMDb")

    splash_time = int(config.get_config_option('Display', 'splash_time', default=5000))
    QTimer.singleShot(splash_time, splash.close)

    # Initialize and show main window
    main_window = MainApp(config, splash)
    main_window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
