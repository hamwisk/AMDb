# ui/view_log.py
import os
import sys

from PyQt5 import QtGui
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem
from ui.ui_view_log import Ui_LogViewer


class ViewLog(QDialog):
    def __init__(self, log_path, parent=None):
        super().__init__(parent)
        self.ui = Ui_LogViewer()
        self.ui.setupUi(self)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.expanduser("~/.local/share/amdb/assets/amdb.ico")))
        self.setWindowIcon(icon)

        self.load_logs(log_path)
        self.adjust_dialog_size()  # Adjust the size based on the content
        self.center()  # Center the dialog on the screen

    def center(self):
        # Center the window on the screen
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def load_logs(self, log_path):
        with open(log_path, 'r') as file:
            lines = file.readlines()
            self.ui.logs_table.setRowCount(len(lines))
            for row_num, line in enumerate(lines):
                date = line[:23].strip()
                rest = line[24:].split(']: ', 1)
                log_type = rest[0].strip('[').strip()
                log_message = rest[1].strip()

                # Set the text color based on the log type
                if log_type == 'INFO':
                    color = QColor('green')
                elif log_type == 'WARNING':
                    color = QColor('orange')
                elif log_type == 'ERROR':
                    color = QColor('red')
                else:
                    color = QColor('black')

                date_item = QTableWidgetItem(date)
                log_type_item = QTableWidgetItem(log_type)
                log_message_item = QTableWidgetItem(log_message)

                # Set the text color for each item
                log_type_item.setForeground(color)
                log_message_item.setForeground(color)

                self.ui.logs_table.setItem(row_num, 0, date_item)
                self.ui.logs_table.setItem(row_num, 1, log_type_item)
                self.ui.logs_table.setItem(row_num, 2, log_message_item)

    def adjust_dialog_size(self):
        # Resize the dialog to fit the table's content
        self.ui.logs_table.resizeColumnsToContents()
        table_width = sum([self.ui.logs_table.columnWidth(i) for i in range(self.ui.logs_table.columnCount())]) + 26
        table_height = self.ui.logs_table.rowHeight(0) * self.ui.logs_table.rowCount() + self.ui.logs_table.horizontalHeader().height()

        self.resize(table_width + 40, min(table_height + 80, 800))  # Add some padding and set a max height
