import sys
import os

import shutil

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QDateTimeEdit, QApplication, QWidget
from PyQt5.QtCore import QThread, Qt, QEvent, QDate
from PyQt5.QtGui import QPalette, QTextCharFormat

from new_key_interface import *
from date_interface import *
from popup_progress import *

from datetime import datetime, timedelta

from Widgets.Counting import *
from Widgets.TwitterManager import *


########################################################################
## NewKey
########################################################################
class DialogNewKey(QDialog):
    def __init__(self, key, parent=None):
        super().__init__(parent)
        self.key = key

        self.setWindowTitle("NEW KEY")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("% s is a new keyword, Do you want to search?"%self.key)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

########################################################################
## Delete
########################################################################
class DialogDelete(QDialog):
    def __init__(self, key, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Delete?")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Do you sure to detele {}?".format(key))
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

########################################################################
## Update
########################################################################
class UpdateDialog(QDialog):
    def __init__(self, key, parent=None):
        super().__init__(parent)
        self.key = key
        self.ui = Ui_until_date_window()
        self.ui.setupUi(self)
        self.begin_date = None
        self.end_date = None

        self.highlight_format = QTextCharFormat()
        self.highlight_format.setBackground(self.palette().brush(QPalette.Highlight))
        self.highlight_format.setForeground(self.palette().color(QPalette.HighlightedText))

        # date now
        self.date_now = QDate.currentDate()

        date_now_str = self.date_now.toString(Qt.ISODate)
        date_now_obj = datetime.strptime(date_now_str, '%Y-%m-%d')

        self.ui.date_label.setText("TODAY : "+ date_now_str + " UTC+00:00")
        self.ui.keyword_label.setText(self.key)

        until_date_str = (date_now_obj - timedelta(days=7)).date().isoformat()
        until_date_obj = QDate.fromString(until_date_str, Qt.ISODate)

        #######################################################################
        # ADD FUNCTION ELEMENT
        #######################################################################
        self.ui.aday_calendarWidget.setDateRange(until_date_obj, self.date_now);
        self.ui.aday_calendarWidget.clicked.connect(self.date_is_clicked)

    ########################################################################
    ## FUNCTION
    ########################################################################
    def format_range(self, format):
        if self.begin_date and self.end_date:
            d0 = min(self.begin_date, self.end_date)
            d1 = max(self.begin_date, self.end_date)

            while d0 <= d1:
                self.ui.aday_calendarWidget.setDateTextFormat(d0, format)
                d0 = d0.addDays(1)

    def date_is_clicked(self, date):
        # reset highlighting of previously selected date range
        self.format_range(QTextCharFormat())
        if QApplication.instance().keyboardModifiers() & Qt.ShiftModifier and self.begin_date:
            self.end_date = date
            # set highilighting of currently selected date range
            self.format_range(self.highlight_format)
        else:
            self.begin_date = date
            self.end_date = date
        self.show()

########################################################################
## Date
########################################################################
class DateDialog(QDialog):
    def __init__(self, key, parent):
        super().__init__(parent)
        self.key = key
        self.parent = parent
        self.ui = Ui_date_window()
        self.ui.setupUi(self)

        self.count = Counting()

        # date now
        self.date_now = QDate.currentDate()

        self.ui.keyword_label.setText(self.key)
        self.ui.date_label.setText("TODAY : "+ self.date_now.toString(Qt.ISODate) + ' UTC+00:00')

        #######################################################################
        # ADD FUNCTION ELEMENT
        #######################################################################
        self.createFilter()

        self.ui.DateList.itemChanged.connect(self.testCheck)

        self.ui.clear_btn.clicked.connect(self.clearFilter)
        self.ui.select_btn.clicked.connect(self.selectFilter)

        self.ui.del_btn.clicked.connect(self.delDate)

        self.ui.cancelButton.clicked.connect(self.close)
        self.ui.doneButton.clicked.connect(self.changeFilter)

    ########################################################################
    ## FUNCTION
    ########################################################################
    def changeFilter(self, event):
        # print(self.dict_date)
        self.parent.dict_date = self.dict_date

        self.parent.ui.base_date_comboBox.clear()
        self.parent.list_date = ['All']
        for i in self.parent.dict_date:
            if self.parent.dict_date[i] : 
                self.parent.list_date.append(i)
        self.parent.ui.base_date_comboBox.addItems(self.parent.list_date)

        self.close()

    def testCheck(self, item):
        fil = item.text()
        self.dict_date[fil] = not self.dict_date[fil]     # change item 
    
    def selectFilter(self): # select all item
        for i in self.parent.dict_date:
            self.parent.dict_date[i] = True
        self.createFilter()

    def clearFilter(self):  # deselect all item
        for i in self.parent.dict_date:
            self.parent.dict_date[i] = False
        self.createFilter()
    
    def createFilter(self):
        for i in range(self.ui.DateList.count()):    # clear all item
            self.ui.DateList.takeItem(0)

        self.dict_date = self.parent.dict_date
        for i in self.dict_date:
            item = QtWidgets.QListWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled) # can check/uncheck

            if self.dict_date[i]:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

            item.setData(QtCore.Qt.DisplayRole, i)
            self.ui.DateList.addItem(item)

    def delDate(self):
        date = self.ui.DateList.currentItem().text()
        dlg = DialogDelete(date)
        
        if dlg.exec():
            dir_path = './backup/{}/file_date/{}'.format(self.key, date)
            try:
                shutil.rmtree(dir_path)
                
            except OSError as e:
                print("Error: %s : %s" % (dir_path, e.strerror))

            # get list date in Key directory
            folder = './backup/{}/file_date'.format(self.key)
            datelist = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]

            # process union
            self.parent.pbar.show()
            self.parent.pbar.set_key_progress(self.key)
            self.parent.pbar.reset_progressBar()

            self.parent.pbar.set_progress_label('Union {}'.format(date))
            self.parent.twm.union_file_tw(self.key, datelist)
            self.parent.pbar.on_count_changed(33)

            self.parent.twm.union_file_word(self.key, datelist)
            self.parent.pbar.on_count_changed(66)

            self.parent.twm.union_file_hashtag(self.key, datelist)
            self.parent.pbar.on_count_changed(99)
            self.parent.pbar.close()
            
            # loaddate
            self.parent.loaddate(self.key)
            # setting current item
            self.parent.ui.base_date_comboBox.setCurrentText('All')
            # loaddata
            self.parent.date_changed('All')

        self.createFilter()


########################################################################
## PopUp Progress
########################################################################
class PopupProgress(QWidget):
    def __init__(self, key, parent=None):
        super().__init__(parent)
        self.ui = Ui_popup_progress()
        self.ui.setupUi(self)

        # set key_label
        self.set_key_progress(key)

    ########################################################################
    ## FUNCTION
    ########################################################################
    def set_key_progress(self, key):
        self.ui.key_label.setText(key)

    def set_progress_label(self, text):
        self.ui.progress_label.setText(text)

    def on_count_changed(self, value):
        self.ui.progressBar.setValue(value)

    def reset_progressBar(self):
        self.ui.progressBar.setValue(0)
