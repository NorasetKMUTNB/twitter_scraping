# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog_newkey.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_until_date_window(object):
    def setupUi(self, until_date_window):
        until_date_window.setObjectName("until_date_window")
        until_date_window.resize(442, 435)
        self.gridLayout = QtWidgets.QGridLayout(until_date_window)
        self.gridLayout.setObjectName("gridLayout")
        self.date_label = QtWidgets.QLabel(until_date_window)
        self.date_label.setObjectName("date_label")
        self.gridLayout.addWidget(self.date_label, 0, 2, 1, 1, QtCore.Qt.AlignRight)
        self.buttonBox = QtWidgets.QDialogButtonBox(until_date_window)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 3)
        self.keyword_label = QtWidgets.QLabel(until_date_window)
        self.keyword_label.setStyleSheet("font: 11pt \"Helvetica\";")
        self.keyword_label.setObjectName("keyword_label")
        self.gridLayout.addWidget(self.keyword_label, 0, 0, 1, 2)
        self.line = QtWidgets.QFrame(until_date_window)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 2, 0, 1, 3)
        self.aday_calendarWidget = QtWidgets.QCalendarWidget(until_date_window)
        self.aday_calendarWidget.setObjectName("aday_calendarWidget")
        self.gridLayout.addWidget(self.aday_calendarWidget, 4, 0, 1, 3)
        self.label = QtWidgets.QLabel(until_date_window)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(until_date_window)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 5, 0, 1, 3)

        self.retranslateUi(until_date_window)
        self.buttonBox.accepted.connect(until_date_window.accept) # type: ignore
        self.buttonBox.rejected.connect(until_date_window.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(until_date_window)

    def retranslateUi(self, until_date_window):
        _translate = QtCore.QCoreApplication.translate
        until_date_window.setWindowTitle(_translate("until_date_window", "Dialog"))
        self.date_label.setText(_translate("until_date_window", "TODAY : "))
        self.keyword_label.setText(_translate("until_date_window", "new keyword"))
        self.label.setText(_translate("until_date_window", "What\'s a day you want to crawler?"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    until_date_window = QtWidgets.QDialog()
    ui = Ui_until_date_window()
    ui.setupUi(until_date_window)
    until_date_window.show()
    sys.exit(app.exec_())
