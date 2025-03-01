# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'list_item.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_list_item(object):
    def setupUi(self, list_item):
        list_item.setObjectName("list_item")
        list_item.resize(889, 50)
        list_item.setMaximumSize(QtCore.QSize(16777215, 50))
        self.gridLayout = QtWidgets.QGridLayout(list_item)
        self.gridLayout.setContentsMargins(-1, 0, -1, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.line_4 = QtWidgets.QFrame(list_item)
        self.line_4.setMinimumSize(QtCore.QSize(0, 41))
        self.line_4.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.gridLayout.addWidget(self.line_4, 0, 12, 1, 1)
        self.keyword_status = QtWidgets.QCheckBox(list_item)
        self.keyword_status.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.keyword_status.sizePolicy().hasHeightForWidth())
        self.keyword_status.setSizePolicy(sizePolicy)
        self.keyword_status.setObjectName("keyword_status")
        self.gridLayout.addWidget(self.keyword_status, 0, 13, 1, 1)
        self.reel = QtWidgets.QCommandLinkButton(list_item)
        self.reel.setMaximumSize(QtCore.QSize(39, 16777215))
        self.reel.setText("")
        icon = QtGui.QIcon.fromTheme("system-search")
        self.reel.setIcon(icon)
        self.reel.setObjectName("reel")
        self.gridLayout.addWidget(self.reel, 0, 23, 1, 1)
        self.title = QtWidgets.QLabel(list_item)
        self.title.setMinimumSize(QtCore.QSize(0, 39))
        self.title.setObjectName("title")
        self.gridLayout.addWidget(self.title, 0, 6, 1, 1)
        self.play_movie = QtWidgets.QCommandLinkButton(list_item)
        self.play_movie.setMinimumSize(QtCore.QSize(0, 41))
        self.play_movie.setMaximumSize(QtCore.QSize(69, 41))
        icon = QtGui.QIcon.fromTheme("media-playback-start")
        self.play_movie.setIcon(icon)
        self.play_movie.setIconSize(QtCore.QSize(22, 22))
        self.play_movie.setObjectName("play_movie")
        self.gridLayout.addWidget(self.play_movie, 0, 24, 1, 1)
        self.filepath_status = QtWidgets.QCheckBox(list_item)
        self.filepath_status.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filepath_status.sizePolicy().hasHeightForWidth())
        self.filepath_status.setSizePolicy(sizePolicy)
        self.filepath_status.setObjectName("filepath_status")
        self.gridLayout.addWidget(self.filepath_status, 0, 16, 1, 1)
        self.watched_status = QtWidgets.QCheckBox(list_item)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.watched_status.sizePolicy().hasHeightForWidth())
        self.watched_status.setSizePolicy(sizePolicy)
        self.watched_status.setMinimumSize(QtCore.QSize(0, 39))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.watched_status.setFont(font)
        self.watched_status.setObjectName("watched_status")
        self.gridLayout.addWidget(self.watched_status, 0, 25, 1, 1)
        self.keywords_updated = QtWidgets.QPushButton(list_item)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.keywords_updated.sizePolicy().hasHeightForWidth())
        self.keywords_updated.setSizePolicy(sizePolicy)
        self.keywords_updated.setMinimumSize(QtCore.QSize(117, 0))
        self.keywords_updated.setMaximumSize(QtCore.QSize(117, 16777215))
        self.keywords_updated.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.keywords_updated.setFlat(True)
        self.keywords_updated.setObjectName("keywords_updated")
        self.gridLayout.addWidget(self.keywords_updated, 0, 14, 1, 1)
        self.line = QtWidgets.QFrame(list_item)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy)
        self.line.setMinimumSize(QtCore.QSize(0, 41))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 0, 5, 1, 1)
        self.filepath_verified = QtWidgets.QPushButton(list_item)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filepath_verified.sizePolicy().hasHeightForWidth())
        self.filepath_verified.setSizePolicy(sizePolicy)
        self.filepath_verified.setMinimumSize(QtCore.QSize(117, 0))
        self.filepath_verified.setMaximumSize(QtCore.QSize(117, 16777215))
        self.filepath_verified.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.filepath_verified.setFlat(True)
        self.filepath_verified.setObjectName("filepath_verified")
        self.gridLayout.addWidget(self.filepath_verified, 0, 17, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 8, 1, 1)
        self.genre = QtWidgets.QLabel(list_item)
        self.genre.setMinimumSize(QtCore.QSize(0, 39))
        self.genre.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.genre.setObjectName("genre")
        self.gridLayout.addWidget(self.genre, 0, 11, 1, 1)
        self.line_5 = QtWidgets.QFrame(list_item)
        self.line_5.setMinimumSize(QtCore.QSize(0, 41))
        self.line_5.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.gridLayout.addWidget(self.line_5, 0, 15, 1, 1)
        self.line_2 = QtWidgets.QFrame(list_item)
        self.line_2.setMinimumSize(QtCore.QSize(0, 41))
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 0, 21, 1, 1)
        self.year = QtWidgets.QLabel(list_item)
        self.year.setMinimumSize(QtCore.QSize(0, 39))
        self.year.setIndent(5)
        self.year.setObjectName("year")
        self.gridLayout.addWidget(self.year, 0, 7, 1, 1)
        self.delete_movie = QtWidgets.QCommandLinkButton(list_item)
        self.delete_movie.setMinimumSize(QtCore.QSize(0, 39))
        self.delete_movie.setMaximumSize(QtCore.QSize(39, 16777215))
        self.delete_movie.setText("")
        icon = QtGui.QIcon.fromTheme("user-trash")
        self.delete_movie.setIcon(icon)
        self.delete_movie.setObjectName("delete_movie")
        self.gridLayout.addWidget(self.delete_movie, 0, 22, 1, 1)

        self.retranslateUi(list_item)
        QtCore.QMetaObject.connectSlotsByName(list_item)

    def retranslateUi(self, list_item):
        _translate = QtCore.QCoreApplication.translate
        list_item.setToolTip(_translate("list_item", "<html><head/><body><p>poster image</p></body></html>"))
        self.keyword_status.setText(_translate("list_item", "Keywords updated:"))
        self.play_movie.setText(_translate("list_item", "Play"))
        self.filepath_status.setText(_translate("list_item", "File path verified:"))
        self.watched_status.setText(_translate("list_item", "Watched"))
        self.keywords_updated.setToolTip(_translate("list_item", "View/Modify Keywords"))
        self.filepath_verified.setToolTip(_translate("list_item", "Veryfy/Auto-update path now"))
