########################################################################
## CONVERT .UI & .QRC
# pyrcc5 resources.qrc -o resources_rc.py
# pyuic5 -x ui_interface.ui -o tweety_interface.py 
# pyuic5 -x dialog_date.ui -o date_interface.py 
# pyuic5 -x popup_progress.ui -o popup_progress.py 
########################################################################

########################################################################
## IMPORTS
########################################################################
import os
import sys
import re

import shutil

from Widgets.TwitterManager import *
from Widgets.ThreadWorker import *
from DialogGui import *

########################################################################
# IMPORT GUI FILE
from tweety_interface import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QEvent, QDate
########################################################################

########################################################################
## MAIN WINDOW CLASS
########################################################################
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.ui = Ui_App()
        self.ui.setupUi(self)
        self.list_keyword = []
        self.key = ''
        self.twm = twitter_manager()

        self.pbar = PopupProgress('')

        self.getListKeyword()
        self.date_now = QDate.currentDate()

        #######################################################################
        # ADD FUNCTION ELEMENT
        #######################################################################
        self.ui.date_label.setText("TODAY : "+ self.date_now.toString(Qt.ISODate) + ' UTC+00:00')
        self.ui.Search_LineEdit.returnPressed.connect(self.search)
        self.ui.SearchList.itemDoubleClicked.connect(self.doubleClick)     # double-click
        self.ui.SearchList.installEventFilter(self)     # right-click

        self.ui.all_ex_btn.clicked.connect(self.export_all)
        self.ui.seldate_btn.clicked.connect(self.selection_date)
        self.ui.seldate_btn.setEnabled(False)
        self.ui.base_date_comboBox.currentTextChanged.connect(self.date_changed)
        #######################################################################
        # SHOW WINDOW
        #######################################################################
        self.show()
        #######################################################################

    ########################################################################
    ## FUNCTION
    ########################################################################
    def getListKeyword(self):
        """ 
        This method will collect keywords have been searched 
        """
        self.ui.SearchList.clear()
        folder = './/backup'
        self.list_keyword = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]
        self.ui.SearchList.addItems(self.list_keyword)


    def loaddate(self, key):
        """ 
        This method will collect date in keyword
        """
        self.ui.seldate_btn.setEnabled(True)
        self.ui.base_date_comboBox.currentTextChanged.disconnect(self.date_changed)
        self.ui.Search_LineEdit.clear()
        self.ui.base_date_comboBox.clear()
        self.list_date = ['All']
        self.dict_date = {}
        self.key = key

        self.ui.Search_LineEdit.setText("{}".format(self.key))

        folder = './backup/{}/file_date'.format(key)
        datelist = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]

        for date in datelist:
            self.list_date.append(date)
            self.dict_date[date] = True

        self.ui.base_date_comboBox.addItems(self.list_date)
        self.ui.base_date_comboBox.currentTextChanged.connect(self.date_changed)


    def loaddata(self):
        """ 
        This method will make all table 
        """
        self.pbar.set_key_progress(self.key)
        self.pbar.show()

        # thread worker open csv
        self.workerCSV = WorkerCSV(self)
        self.workerCSV.start()
        self.workerCSV.finished.connect(self.finish_worker_csv)
        self.workerCSV.update_progress.connect(self.update_worker)


    def doubleClick(self, item): # double-click
        """ 
        This method will use when double-click, it selection item in Listwidget show dataframe 
        """
        # set self.key from the item is selected
        self.key = item.text()
        self.loaddata()
        self.loaddate(self.key)


    def eventFilter(self, source, event):
        """ 
        This method will use when right-click item in listwidget 
        """
        if event.type() == QEvent.ContextMenu and source is self.ui.SearchList:
            menu = QMenu()

            upact = menu.addAction(QIcon("images\icons8-downloading-updates-96.png"),'&Update')
            delact = menu.addAction(QIcon("images\icons8-delete-96.png"),'&Delete')

            action = menu.exec_(event.globalPos())
            item = source.itemAt(event.pos())

            # set self.key from the item is selected
            self.key = item.text()

            # update keyword
            if action == upact:
                self.updia = UpdateDialog(self.key)   
                if self.updia.exec():    
                    self.begin_date = self.updia.begin_date.toString(Qt.ISODate)
                    self.end_date = self.updia.end_date.toString(Qt.ISODate)
                    print(self.begin_date, self.end_date)

                    self.pbar = PopupProgress(self.key)
                    self.pbar.show()

                    # thread worker tweet
                    self.workerTW = WorkerTweet(self)
                    self.workerTW.start()
                    self.workerTW.finished.connect(self.finish_worker_tweet)
                    self.workerTW.update_progress.connect(self.update_worker)

            # delete keyword
            elif action == delact: 
                self.deldla = DialogDelete(self.key)
                if self.deldla.exec():
                    dir_path = './backup/{}'.format(self.key)
                    try:
                        shutil.rmtree(dir_path)
                        # if open keyword that will delete
                        if self.key == self.ui.base_label.text().lower():
                            self.clear_all()
                        else :
                            self.getListKeyword()
                    except OSError as e:
                        print("Error: %s : %s" % (dir_path, e.strerror))

            return True
        return super().eventFilter(source, event)


    def search(self):
        """ 
        This method will reset all main widget 
        """
        # set self.key from the line edit
        self.key = self.ui.Search_LineEdit.text().lower()

        # check keyword is in listwidget
        if self.key in self.list_keyword: 
            self.loaddata()
            self.loaddate(self.key)
        else : 
            dlg = DialogNewKey(self.key)
            if dlg.exec():
                self.updia = UpdateDialog(self.key)
                if self.updia.exec():
                    self.twm.create_key_directory(self.key)

                    self.begin_date = self.updia.begin_date.toString(Qt.ISODate)
                    self.end_date = self.updia.end_date.toString(Qt.ISODate)

                    self.pbar.set_key_progress(self.key)
                    self.pbar.show()

                    self.workerTW = WorkerTweet(self)
                    self.workerTW.start()
                    self.workerTW.finished.connect(self.finish_worker_tweet)
                    self.workerTW.update_progress.connect(self.update_worker)


    def selection_date(self):
        """ 
        This method will call new widget for selection range date 
        """
        self.key = self.ui.base_label.text().lower()
        datedia = DateDialog(self.key, self)
        datedia.show()


    def date_changed(self, value):
        """ 
        This method will load data with selection date 
        """
        self.pbar.set_key_progress(self.key)
        self.pbar.show()
        self.DateSelection = value

        self.workerCD = WorkerChangeDate(self)
        self.workerCD.start()
        self.workerCD.finished.connect(self.finish_worker_change_date)
        self.workerCD.update_progress.connect(self.update_worker)


    def clear_all(self):
        """ 
        This method will reset all main widget
        """
        self.getListKeyword()   # reset list keyword

        self.ui.seldate_btn.setEnabled(False)   # Disabled button selection date
        self.ui.Search_LineEdit.setText('')     # Clear LineEdit

        # Clear date combobox
        self.list_date = ['All']
        self.ui.base_date_comboBox.currentTextChanged.disconnect(self.date_changed)
        self.ui.base_date_comboBox.clear()
        self.ui.base_date_comboBox.addItems(self.list_date)
        self.ui.base_date_comboBox.currentTextChanged.connect(self.date_changed)

        self.ui.base_table.setRowCount(0)       # Clear table base
        self.ui.word_table.setRowCount(0)       # Clear table word
        self.ui.hashtag_table.setRowCount(0)    # Clear table hashtag
        
        self.ui.base_label.setText('Keyword')   # Change Keyword Label
        
        # Change Per Lable
        self.ui.positive_label.setText('Positive : 0%')
        self.ui.negative_label.setText('Negative : 0%')
        self.ui.neutal_label.setText('Neutal : 0%')

        # Change Status Lable
        self.ui.status_base_label.setText('0 Tweets')
        self.ui.status_word_label.setText('0 Words')
        self.ui.status_hashtag_label.setText('0 Hashtags')

    def export_all(self):
        """ 
        This method will export all file
        """
        self.pbar.show()

        self.workerEX = WorkerExport(self)
        self.workerEX.start()
        self.workerEX.finished.connect(self.finish_worker_export)
        self.workerEX.update_progress.connect(self.update_worker)


    ########################################################################
    # FINISH THREAD WORKER
    ########################################################################

    def finish_worker_tweet(self):
        """ This method is end worker tweet, it will load data with selection date """
        self.workerTW.stop()
        self.pbar.close()
        self.getListKeyword()
        self.loaddata()

    def finish_worker_csv(self):
        self.workerCSV.stop()
        self.pbar.close()
        self.loaddate(self.key)

    def finish_worker_change_date(self):
        self.workerCD.stop()
        self.pbar.close()

    def finish_worker_export(self):
        self.workerEX.stop()
        self.pbar.close()

    def update_worker(self, val):
        self.pbar.ui.progressBar.setValue(val)

    ########################################################################

########################################################################
## EXECUTE APP
########################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
########################################################################
## END===>
########################################################################
    