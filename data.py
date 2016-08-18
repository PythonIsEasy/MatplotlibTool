#
# This file contains 2 classes:
# The ImportDialog, which task is to get new Data from a file or a database.
# The ShowDialog, which shows the imported Data
#

from PyQt4 import QtCore,QtGui,uic
import dataHandler as ds


class ImportDialog(QtGui.QDialog):
    def __init__(self):
        # Init the dialog and sets up the gui
        super(ImportDialog,self).__init__()

        # Load ui for MainWindow
        uic.loadUi("ui/import_data.ui",self)

        self.fileDialog = QtGui.QFileDialog()
        self.buttons()
        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint)
        self.check = False
        self.df_list = {}
        self.name_list = []
        self.count = 0
        self.show()

    def buttons(self):
        # Connect the buttons with functions
        self.fileBtn.clicked.connect(self.fileReader)
        self.import_btn.clicked.connect(self.close)
        self.dbBtn.clicked.connect(self.dbReader)

    # Function for importing data from a File and
    # opens a QT file dialog to chose the file.
    # The path of file is the parameter for the data set dialog class

    def fileReader(self):
        self.fileDialog.setFileMode(QtGui.QFileDialog.AnyFile)
        self.fileDialog.setFilter("Text files (*.txt)")
        if self.fileDialog.exec_():
            filenames = self.fileDialog.selectedFiles()
            file = "".join(filenames)
            self.file_up = ds.df_import(file)
            self.file_up.exec_()
            if self.file_up.close():
                # If imported
                self.check = self.file_up.check
                # Get the data
                if self.check is True:
                    self.getData()

    def getData(self):
        # Gets the data from the df dialog
        self.name, self.df = self.file_up.import_data()
        self.name = self.name.lower()

        self.df_list[self.name] = self.df
        self.name_list.append(self.name)

        self.df_to_list()

    def dbReader(self):
        if self.radioSQL.isChecked():
            # Parameter is mysql, so the ui can load the mysql widget
            self.file_up = ds.df_import("mysql")
            self.file_up.exec_()
            if self.file_up.close():
                self.check = self.file_up.check
                if self.check is True:
                    self.getData()

        else:
            # Same goes for mongodb
            self.file_up = ds.df_import("mongodb")
            self.file_up.exec_()
            if self.file_up.close():
                self.check = self.file_up.check
                if self.check is True:
                    self.getData()

    def df_to_list(self):
        # Shows the list of names of imported dataframes
        item_df = QtGui.QListWidgetItem()
        item_df.setText(self.name)

        self.rows = self.df.shape[0]
        self.cols = self.df.shape[1]

        self.df_view.insertItem(self.count, item_df)

        # init list widget item
        item_data = QtGui.QListWidgetItem()
        item_data.setText(str(self.rows) + " obs. of " + str(self.cols) + " variables")

        self.data_display.insertItem(self.count, item_data)
        self.count += 1


class DataDialog(QtGui.QDialog):
    def __init__(self,name_list,df_list):
        # init DataDialog
        super(DataDialog,self).__init__()
        self.tab = QtGui.QTabWidget()
        self.table = QtGui.QTableWidget()

        self.hbox = QtGui.QHBoxLayout()
        self.hbox.addWidget(self.tab)

        self.setLayout(self.hbox)
        self.setFixedSize(700,500)
        self.setWindowTitle("Data")

        self.name_list = name_list
        self.df_list = df_list
        self.getData()
        self.show()

    def tables(self, df, rows, cols):
        headers = list(df.columns.values)

        # Flags are used in QT for disabling editability of items
        flags = QtCore.Qt.ItemFlags()
        flags != QtCore.Qt.ItemIsEditable

        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

        for m in range(rows):
            for n in range(cols):
                item = df.loc[df.index[m], headers[n]]
                newitem = QtGui.QTableWidgetItem(str(item))

                # add the flags
                newitem.setFlags(flags)
                self.table.setItem(m, n, newitem)

    def setTable(self, df):
        self.rows = df.shape[0]
        self.cols = df.shape[1]  #

        # init the table
        self.table = QtGui.QTableWidget()
        self.table.setRowCount(self.rows)
        self.table.setColumnCount(self.cols)
        self.tables(df, self.rows, self.cols)

    def getData(self):
        for name in self.name_list:

            # adds df to table
            self.setTable(self.df_list[name])
            # creates new tab
            self.tab.addTab(self.table, name)

