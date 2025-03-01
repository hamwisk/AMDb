# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'batch_operations_toolbar.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_batch_operations_toolbar(object):
    def setupUi(self, batch_operations_toolbar):
        batch_operations_toolbar.setObjectName("batch_operations_toolbar")
        batch_operations_toolbar.resize(567, 168)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(batch_operations_toolbar.sizePolicy().hasHeightForWidth())
        batch_operations_toolbar.setSizePolicy(sizePolicy)
        batch_operations_toolbar.setMaximumSize(QtCore.QSize(16777215, 169))
        self.gridLayout_2 = QtWidgets.QGridLayout(batch_operations_toolbar)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(batch_operations_toolbar)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.line = QtWidgets.QFrame(batch_operations_toolbar)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_2.addWidget(self.line, 1, 0, 1, 4)
        self.watched_groupbox = QtWidgets.QGroupBox(batch_operations_toolbar)
        self.watched_groupbox.setMaximumSize(QtCore.QSize(16777215, 55))
        self.watched_groupbox.setCheckable(True)
        self.watched_groupbox.setObjectName("watched_groupbox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.watched_groupbox)
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.radio_watched = QtWidgets.QRadioButton(self.watched_groupbox)
        self.radio_watched.setObjectName("radio_watched")
        self.horizontalLayout.addWidget(self.radio_watched)
        self.radio_unwatched = QtWidgets.QRadioButton(self.watched_groupbox)
        self.radio_unwatched.setObjectName("radio_unwatched")
        self.horizontalLayout.addWidget(self.radio_unwatched)
        self.gridLayout_2.addWidget(self.watched_groupbox, 2, 2, 2, 1)
        self.verify_checkbox = QtWidgets.QCheckBox(batch_operations_toolbar)
        font = QtGui.QFont()
        font.setBold(True)
        self.verify_checkbox.setFont(font)
        self.verify_checkbox.setObjectName("verify_checkbox")
        self.gridLayout_2.addWidget(self.verify_checkbox, 4, 2, 1, 1)
        self.delete_checkbox = QtWidgets.QCheckBox(batch_operations_toolbar)
        font = QtGui.QFont()
        font.setBold(True)
        self.delete_checkbox.setFont(font)
        self.delete_checkbox.setObjectName("delete_checkbox")
        self.gridLayout_2.addWidget(self.delete_checkbox, 5, 2, 1, 1)
        self.pushButton = QtWidgets.QPushButton(batch_operations_toolbar)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_2.addWidget(self.pushButton, 4, 3, 2, 1)
        self.pushButton_2 = QtWidgets.QPushButton(batch_operations_toolbar)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_2.addWidget(self.pushButton_2, 3, 3, 1, 1)
        self.keywords_groupbox = QtWidgets.QGroupBox(batch_operations_toolbar)
        font = QtGui.QFont()
        font.setBold(True)
        self.keywords_groupbox.setFont(font)
        self.keywords_groupbox.setCheckable(True)
        self.keywords_groupbox.setObjectName("keywords_groupbox")
        self.gridLayout = QtWidgets.QGridLayout(self.keywords_groupbox)
        self.gridLayout.setContentsMargins(3, 6, 3, 3)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(self.keywords_groupbox)
        font = QtGui.QFont()
        font.setBold(False)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.keywords_groupbox)
        font = QtGui.QFont()
        font.setBold(False)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 1, 1, 1)
        self.add_keywords = QtWidgets.QTextEdit(self.keywords_groupbox)
        font = QtGui.QFont()
        font.setBold(False)
        self.add_keywords.setFont(font)
        self.add_keywords.setObjectName("add_keyword")
        self.gridLayout.addWidget(self.add_keywords, 1, 0, 1, 1)
        self.remove_keywords = QtWidgets.QTextEdit(self.keywords_groupbox)
        font = QtGui.QFont()
        font.setBold(False)
        self.remove_keywords.setFont(font)
        self.remove_keywords.setObjectName("remove_keywords")
        self.gridLayout.addWidget(self.remove_keywords, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.keywords_groupbox, 2, 1, 4, 1)
        self.selected_groupbox = QtWidgets.QGroupBox(batch_operations_toolbar)
        font = QtGui.QFont()
        font.setBold(True)
        self.selected_groupbox.setFont(font)
        self.selected_groupbox.setCheckable(False)
        self.selected_groupbox.setObjectName("selected_groupbox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.selected_groupbox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.selected_movies = QtWidgets.QListWidget(self.selected_groupbox)
        self.selected_movies.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.selected_movies.setFrameShadow(QtWidgets.QFrame.Plain)
        self.selected_movies.setLineWidth(0)
        self.selected_movies.setObjectName("selected_movies")
        self.verticalLayout_2.addWidget(self.selected_movies)
        self.gridLayout_2.addWidget(self.selected_groupbox, 2, 0, 4, 1)

        self.retranslateUi(batch_operations_toolbar)
        QtCore.QMetaObject.connectSlotsByName(batch_operations_toolbar)

    def retranslateUi(self, batch_operations_toolbar):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("batch_operations_toolbar", "Batch operations"))
        self.watched_groupbox.setTitle(_translate("batch_operations_toolbar", "Watched"))
        self.radio_watched.setText(_translate("batch_operations_toolbar", "Yes"))
        self.radio_unwatched.setText(_translate("batch_operations_toolbar", "No"))
        self.verify_checkbox.setText(_translate("batch_operations_toolbar", "Verify Filepath"))
        self.delete_checkbox.setText(_translate("batch_operations_toolbar", "Delete"))
        self.pushButton.setText(_translate("batch_operations_toolbar", "Confirm\n"
"Batch\n"
"Operation"))
        self.pushButton_2.setText(_translate("batch_operations_toolbar", "Cancel"))
        self.keywords_groupbox.setTitle(_translate("batch_operations_toolbar", "Keywords"))
        self.label_2.setText(_translate("batch_operations_toolbar", "Add"))
        self.label_3.setText(_translate("batch_operations_toolbar", "Remove"))
        self.selected_groupbox.setTitle(_translate("batch_operations_toolbar", "Selected Movies"))
