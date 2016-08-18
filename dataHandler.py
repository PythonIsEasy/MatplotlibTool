#
# This file contains the DfDialog class for getting Data
# from the imported file path and databases.
#


from PyQt4 import QtCore,QtGui,uic
import os
import pandas as pd
from mysql import connector
import mysql
from pymongo import MongoClient


class DfDialog(QtGui.QDialog):
    def __init__(self,iput):
        super(DfDialog,self).__init__()
        uic.loadUi("ui/dataset.ui",self)
        self.input = iput
        self.check = False
        self.getInput()
        self.df_input = QtGui.QTextEdit()
        self.df_area.setWidget(self.df_input)
        self.setWindowTitle("Import Dataframe from File")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.importButton.setEnabled(False)
        self.exec_btn.clicked.connect(self.dataframe)
        self.buttons()
        self.show()

    def getInput(self):
        if self.input == "mysql":
            uic.loadUi("ui/sqlwidget.ui",self.wdg)
        elif self.input == "mongodb":
            uic.loadUi("ui/mdbwidget.ui",self.wdg)
        else:
            uic.loadUi("ui/filewidget.ui",self.wdg)
            self.combobox()
            self.file_name()
            self.file_label.setText(self.input)

    def dataframe(self):
        self.df_input.clear()

        if self.input == "mysql":
            query = "SELECT * from "+self.wdg.name_field.text()
            self.df = pd.read_sql(query,con=self._get_mysql())
        elif self.input == "mongodb":
            client = self._get_mongo()
            db = client[self.wdg.dbMongo.text()]
            collection = db[self.wdg.name_field.text()]

            cursor = list(collection.find())
            data = pd.DataFrame(cursor)
            cols = "date","closep","highp","lowp","openp","volume"
            del data["_id"]
            data = data.reindex(columns=cols)
            data[["date","volume"]] = data[["date","volume"]].astype(int)
            self.df = data

        else:
            temp = str(self.wdg.combo_sep.currentText())
            if temp == "Comma":
                self.sep = ","
            elif temp == "Whitespace":
                self.sep = " "
            elif temp == "Semicolon":
                self.sep = ";"
            elif temp == "Tab":
                self.sep = "    "

            if self.wdg.radio_yes.isChecked():
                self.df = pd.read_table(self.input, sep=self.sep)

            if self.wdg.radio_no.isChecked():
                self.header = ["date", "closep", "highp", "lowp", "openp", "volume"]
                self.df = pd.read_table(self.input, sep=self.sep, names=self.header)

        self.df_input.append(str(self.df))
        self.importButton.setEnabled(True)

    def file_name(self):
        base = os.path.basename(self.input)
        base = os.path.splitext(base)[0]
        self.wdg.name_field.setText(base)

    def import_data(self):
        self.close()
        self.name = self.wdg.name_field.text()
        return self.name, self.df

    def import_btn(self):
        self.check = True
        self.close()

    def import_check(self):
        return self.check

    def combobox(self):
        item_list = "Comma","Whitespace","Semicolon","Tab"
        self.wdg.combo_sep.addItems(item_list)
        item_list = "Use numbers","Use Columns"
        self.wdg.combo_rows.addItems(item_list)

    def buttons(self):
        self.cancelButton.clicked.connect(self.close)
        self.importButton.clicked.connect(self.import_btn)

    def _get_mysql(self):
        try:
            conn = mysql.connector.connect(
                user=self.wdg.userSQL.text(),
                password=self.wdg.pswSQL.text(),
                host=self.wdg.hostSQL.text(),
                database=self.wdg.dbSQL.text()
            )
        except Exception as e:
            print("mysql", str(e))

        return conn

    def _get_mongo(self):
        client = MongoClient(self.wdg.hostMongo.text(), int(self.wdg.portMongo.text()))
        return client

