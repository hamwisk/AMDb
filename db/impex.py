# db/impex.py
import configparser
import os
import shutil
import zipfile
from datetime import datetime

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from config.logger import log_info, log_warning, log_error
from db.database_operations import update_poster_paths


def export_db(self):
    log_info('Database Backup Initialized')
    current_db = os.path.expanduser("~/.local/share/amdb/assets/movies.db")
    current_post = os.path.expanduser("~/.local/share/amdb/assets/posters")
    current_config = os.path.expanduser("~/.config/amdb/config.ini")

    # Create a temporary directory for backup
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)

    try:
        # Copy the database file to the temporary directory
        shutil.copy(current_db, backup_dir)

        # Copy the posters folder to the temporary directory
        shutil.copytree(current_post, os.path.join(backup_dir, 'posters'))

        # Suggested filename
        suggested_filename = f"AMDb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.backup"
        suggested_filename = os.path.join(os.path.expanduser("~"), suggested_filename)

        # Prompt the user to choose the backup file location with a suggested filename
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        zip_filename, _ = QFileDialog.getSaveFileName(self, "Save Backup File", suggested_filename,
                                                      "Backup Files;;All Files (*)", options=options)

        if zip_filename:
            # Create a zip file containing the backup items
            with zipfile.ZipFile(zip_filename, 'w') as backup_zip:
                # Add the database file
                backup_zip.write(os.path.join(backup_dir, os.path.basename(current_db)), 'movies.db')

                # Add the posters folder
                for root, dirs, files in os.walk(os.path.join(backup_dir, 'posters')):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.join(backup_dir, 'posters'))
                        backup_zip.write(file_path, os.path.join('posters', arcname))

                # Add the config file to the zip
                backup_zip.write(current_config, 'config.ini')

            log_info(f'Database Backup Completed: {zip_filename}')

            # Inform the user about the completion
            QMessageBox.information(self, "Backup Completed",
                                    f"Database backup completed successfully. "
                                    f"Backup file saved to:\n{zip_filename}")
    except Exception as e:
        log_warning(f"Database backup failed: {e}")
        # Inform the user about the failure
        QMessageBox.warning(self, "Backup Failed", f"Database backup failed. Error: {e}")
    finally:
        # Cleanup: Remove the temporary directory
        shutil.rmtree(backup_dir, ignore_errors=True)


def import_db(self):
    extraction_dir = ''
    temp_backup = os.path.expanduser("~/.local/share/amdb/assets/movies_backup_temp.db")
    log_info("Initializing database import")
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    import_filename, _ = QFileDialog.getOpenFileName(self, "Select Backup File", os.path.expanduser("~"),
                                                     "Backup Files (*.backup);;All Files (*)", options=options)

    if import_filename:
        try:
            # Create a temporary directory for extraction
            extraction_dir = f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(extraction_dir, exist_ok=True)

            # Extract the contents of the backup file to the temporary directory
            with zipfile.ZipFile(import_filename, 'r') as backup_zip:
                backup_zip.extractall(extraction_dir)

            # Check if the user wants to continue without backing up
            response = QMessageBox.warning(self, "Warning",
                                           "Importing will overwrite your current database and posters.\n"
                                           "Do you want to back up your existing data before proceeding?",
                                           QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                           QMessageBox.Yes)

            if response == QMessageBox.Cancel:
                log_info("Database import canceled by user")
                return

            if response == QMessageBox.Yes:
                export_db(self)

            # Import config file
            config = configparser.ConfigParser()
            config.read(os.path.join(extraction_dir, 'config.ini'))
            cv = self.config_handler.get_config_option('Database', 'version')
            iv = config['Database']['version']

            # Check the version is the same as in current config
            if cv == iv:
                # Import config file
                current_config = os.path.expanduser("~/.config/amdb/config.ini")
                imported_config = os.path.join(extraction_dir, 'config.ini')
                shutil.copy(imported_config, current_config)

                # Import database file
                current_db = os.path.expanduser("~/.local/share/amdb/assets/movies.db")
                imported_db = os.path.join(extraction_dir, 'movies.db')
                shutil.copy(imported_db, current_db)

                # Import posters folder
                imported_posters = os.path.join(extraction_dir, 'posters')
                current_post = os.path.expanduser("~/.local/share/amdb/assets/posters")
                shutil.rmtree(current_post, ignore_errors=True)
                shutil.copytree(imported_posters, current_post)

                # Update database entries for possible new posters folder
                update_poster_paths()

                log_info(f'Database Import Completed: {import_filename}')

                # Display success message
                QMessageBox.information(self, "Import Successful", "Database import completed successfully.",
                                        QMessageBox.Ok)
            else:
                log_warning(f"Database import failed: Incompatible version ({iv})")
                QMessageBox.critical(self, "Import Failed",
                                     f"Error during database import: Incompatible version ({iv})",
                                     QMessageBox.Ok)
        except Exception as e:
            log_warning(f"Import Failed\n"
                        "Error during database import: {str(e)}")
            # Display error message
            QMessageBox.critical(self, "Import Failed", f"Error during database import: {str(e)}",
                                 QMessageBox.Ok)

        finally:
            # Cleanup: Remove the temporary extraction directory
            shutil.rmtree(extraction_dir, ignore_errors=True)
            # Cleanup: Remove the temporary backup file if it exists
            if os.path.exists(temp_backup):
                os.remove(temp_backup)
