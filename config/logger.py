# config/logger.py

import logging
import os


def truncate_log_file(log_file_path, max_size_bytes):
    # Check if the log file size exceeds the maximum size
    if os.path.getsize(log_file_path) > max_size_bytes:
        log_warning(f"Log file exceeded maximum file size of: {max_size_bytes}")

        # Rename the existing log file to 'old_log.log'
        old_log_file_path = os.path.join(os.path.dirname(log_file_path), "old_log.log")
        os.rename(log_file_path, old_log_file_path)

        # Create a new 'main_log.log' file
        open(log_file_path, 'w').close()  # This will create an empty 'main_log.log' file

        log_info(f"Log file archived as '{old_log_file_path}'. New 'main_log.log' created.")


def log_info(message):
    logging.info(message)


def log_warning(message):
    logging.warning(message)


def log_error(message):
    logging.error(message)


def setup_logging(log_file_path):
    if not os.path.exists(log_file_path):
        try:
            # Configure logging to write to the log file
            logging.basicConfig(filename=log_file_path, level=logging.INFO,
                                format="%(asctime)s [%(levelname)s]: %(message)s")

        except OSError as e:
            print(f"Failed to create system log at {log_file_path}. Error: {e}")
    else:
        logging.basicConfig(filename=log_file_path, level=logging.INFO,
                            format="%(asctime)s [%(levelname)s]: %(message)s")
        # Truncate the log file if it exceeds the maximum size
        max_size_bytes = 512 * 512  # 1 MB, adjust as needed
        truncate_log_file(log_file_path, max_size_bytes)
        log_info(f"AMDb log located at: {log_file_path}")
