#
# This file contains the WebData class.
# Main method of this class gets yahoo finance data and saves it in a file.
# Also saving the data in da MongoDB and Mysql database is possible.
#


import urllib.request
import mysql
from mysql import connector
import pandas as pd
from pymongo import MongoClient
from PyQt4 import QtGui, uic


class WebData(QtGui.QDialog):
    def __init__(self):
        super(WebData,self).__init__()
        # init WebData Dialog
        uic.loadUi("ui/webData.ui",self)

        # init fileDialog to select the file path
        self.fileDialog = QtGui.QFileDialog()
        self.saveBtn.clicked.connect(self.run)
        self.saveFile = ""
        self.show()

    # Main method
    def run(self):

        # writing the file
        self.addData()

        if self.checkSQL.isChecked():
            # saves the data in a mysql database
            self.dataToSql()

        if self.checkMongo.isChecked():
            # saves the data in a mongodb database
            self.dataToMongo()

        title = "Save File"
        text = "File and database connection"
        info = "Creating the file and saving in databases was successful!"
        # init a message box
        self.msgBox(title,text,info)

    def addData(self):
        stock = self.stock.text()
        timerange = self.range.text()
        self.saveFile = self._path()

        # url for yahoo data
        url = "http://chartapi.finance.yahoo.com/instrument/1.0/"+stock+"/chartdata;" \
              "type=quote;range=" + timerange + "/csv"

        saveFile = open(self.saveFile, "w")  # open the file for writing the data
        sourceCode = urllib.request.urlopen(url).read().decode("utf-8")  # opens the url and reads the data
        splitSource = sourceCode.split("\n")  # split the data in lines

        for eachLine in splitSource:
            if "values" not in eachLine:
                splitLine = eachLine.split(",")  # split the line in values
                if len(splitLine) == 6:  # if length is 6, date, closep, highp, lowp, openp and volume are in one line.
                    lineToWrite = eachLine + "\n"
                    saveFile.write(lineToWrite)  # write the file

        saveFile.close()  # close the file

    def _path(self):
        path = QtGui.QFileDialog.getSaveFileName(self.fileDialog,"Save File")
        return path  # return the path

    def dataToMongo(self):
        client = self.getMongoConnection()
        db = client[self.dbMongo.text()]
        collection = db[self.colMongo.text()]

        #  pandas function to read the file and transform it into a dataframe
        data = pd.read_table(self.saveFile, sep=",", names=["date", "closep", "highp", "lowp", "openp", "volume"])

        # saves the dataframe in a mongodb database
        collection.insert_many(data.to_dict("records"))

        client.close()  # close the client to cut connection to the database

    def getMongoConnection(self):
        client = MongoClient(self.hostMongo.text(), int(self.portMongo.text()))
        return client  # return a mongodb connection

    def dataToSql(self):
        conn = self.getMysqlConnection()
        if conn is not None:  # if connection was successful

            #  pandas reads the file and writes the data in a dataframe
            data = pd.read_table(self.saveFile, sep=",", names=["date", "closep", "highp", "lowp", "openp", "volume"])

            # pandas writes the dataframe in a mysql database table
            data.to_sql(con=conn, name=self.stock.text(), if_exists="replace", flavor="mysql", index=False)

            conn.close()  # close the connection
            title = "File to database"
            text = "Creating the table was successful!"
            info = "Added the data frame to the database"
            self.msgBox(title,text,info)  # init the message box
        else:
            title = "Error"
            text = "Connection failed!"
            info = "Connection to database was not successful"
            self.msgBox(title,text,info)

    def getMysqlConnection(self):
        try:
            # create the mysql connection
            conn = mysql.connector.connect(
                user=self.userSQL.text(),
                password=self.pswSQL.text(),
                host=self.hostSQL.text(),
                database=self.dbSQL.text()
            )
        except Exception as e:
            print("mysql", str(e))

        return conn  # return the connection

    def msgBox(self,title,text,info):
        #  create a messagebox
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setInformativeText(info)
        msg.setStandardButtons(QtGui.QMessageBox.Ok)
        msg.exec_()