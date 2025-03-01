# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'splash.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SplashScreen(object):
    def setupUi(self, SplashScreen):
        SplashScreen.setObjectName("SplashScreen")
        SplashScreen.resize(520, 545)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SplashScreen.sizePolicy().hasHeightForWidth())
        SplashScreen.setSizePolicy(sizePolicy)
        SplashScreen.setMaximumSize(QtCore.QSize(560, 545))
        self.image_frame = QtWidgets.QWidget(SplashScreen)
        self.image_frame.setObjectName("image_frame")
        self.frame = QtWidgets.QFrame(self.image_frame)
        self.frame.setGeometry(QtCore.QRect(8, 2, 504, 504))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(2)
        self.frame.setObjectName("frame")
        self.splash_image = QtWidgets.QLabel(self.frame)
        self.splash_image.setGeometry(QtCore.QRect(2, 2, 500, 500))
        self.splash_image.setObjectName("splash_image")
        self.text_frame = QtWidgets.QFrame(self.image_frame)
        self.text_frame.setGeometry(QtCore.QRect(8, 510, 504, 30))
        font = QtGui.QFont()
        font.setBold(True)
        self.text_frame.setFont(font)
        self.text_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.text_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.text_frame.setLineWidth(2)
        self.text_frame.setObjectName("text_frame")
        self.label_version_number = QtWidgets.QLabel(self.text_frame)
        self.label_version_number.setGeometry(QtCore.QRect(130, 5, 210, 20))
        self.label_version_number.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_version_number.setObjectName("label_version_number")
        self.version_number = QtWidgets.QLabel(self.text_frame)
        self.version_number.setGeometry(QtCore.QRect(342, 5, 32, 20))
        self.version_number.setObjectName("version_number")
        SplashScreen.setCentralWidget(self.image_frame)

        self.retranslateUi(SplashScreen)
        QtCore.QMetaObject.connectSlotsByName(SplashScreen)

    def retranslateUi(self, SplashScreen):
        _translate = QtCore.QCoreApplication.translate
        self.label_version_number.setText(_translate("SplashScreen", "Andy\'s Movie Database - Version:"))
