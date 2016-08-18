#
# This program is a plot tool for Yahoo stock data using Qt4 and
# the python library Matplotlib. It is possible to get new Yahoo
# stock data and save it in a file or database.
# Data can also be imported to the tool via files or databases.
# The imported data can be used to plot financial graphs.
# Available graphs: line,scatter and ohlc.
# Written by Christopher Niedermaier
#


import sys
from PyQt4 import QtGui, uic
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.finance import _candlestick
from matplotlib import pylab
import rest as mpl
import data
import finance


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # init main window
        uic.loadUi("ui/analysis.ui", self)
        self.setWindowTitle("Data Science Time Series Project")
        self.icon = QtGui.QIcon("python.png")
        self.df_list = {}
        self.name_list = []
        self.setWindowIcon(self.icon)
        self.create_btn.clicked.connect(self.create_figure)
        self.plot_btn.clicked.connect(self.plot)
        self.plot_btn.setEnabled(False)
        self.create_btn.setEnabled(False)
        self.matplot_diagrams()
        self.subplot_area = QtGui.QTextEdit()
        self.scrollArea.setWidget(self.subplot_area)
        self.menu()
        self.show()

    def menu(self):

        # Menu bar for opening the import data set dialog.
        self.menu_bar = self.menuBar().addMenu("File")
        self.menu_bar.addAction("New Data", self.webData)
        self.menu_bar.addAction("Import Data", self.import_data)
        self.menu_bar.addAction("Show Data", self.show_data)

    def webData(self):
        dialog = finance.WebData()
        dialog.exec_()

    # Open the dialog class.
    def import_data(self):
        dialog = data.ImportDialog()
        dialog.exec_()

        # When closed, data binding from another window/dialog is possible.
        if dialog.close():
            self.name_list.extend(dialog.name_list)
            temp = dialog.name_list
            text = ", ".join(temp)
            self.df_list.update(dialog.df_list)
            self.variables.addItems(temp)
            self.subplot_area.append(text + " imported\n")
            self.create_btn.setEnabled(True)

    # Ppen the show data sets dialog.
    def show_data(self):
        dialog = data.DataDialog(self.name_list, self.df_list)
        dialog.exec_()

    def get_axes(self):
        self.data = self.df_list[self.variables.currentText()]

        # Xaxis is always a date array in time series.
        # Select column from data frame for Yaxis.

        x = self.data[self.candle_date.text()]
        y = self.data[self.y_plot.text()]
        vol = self.data["volume"]
        return x, y, vol

    # Add items for diagrams.

    def matplot_diagrams(self):
        dia_list = "plot", "scatter", "ohlc"
        self.diagrams.addItems(dia_list)

    # Defining y-lim for the graph.

    def ylim(self, subplot, df):
        if self.y_top.text() != "":
            top = mpl.lims(df, self.y_top.text(), float(self.y_percent_top.text()))
            subplot.set_ylim(top=top)

        if self.y_bot.text() != "":
            bot = mpl.lims(df, self.y_bot.text(), float(self.y_percent_bot.text()))
            subplot.set_ylim(bottom=bot)

    # Show grid on graph.
    def grid(self):
        if self.axes_grid.isChecked():
            plt.grid(True, color=self.tick_color.text())

    # Modifies all labels,spines and ticks and changes the color.
    def ax_color(self):
        self.ax1.spines['bottom'].set_color(self.tick_color.text())
        self.ax1.spines['top'].set_color(self.tick_color.text())
        self.ax1.spines['right'].set_color(self.tick_color.text())
        self.ax1.spines['left'].set_color(self.tick_color.text())

        [i.set_color(self.tick_color.text()) for i in plt.gca().get_xticklabels()]
        [i.set_color(self.tick_color.text()) for i in plt.gca().get_yticklabels()]

        self.ax1.tick_params(axis="x", color=self.tick_color.text())
        self.ax1.tick_params(axis="y", color=self.tick_color.text())

    # Function for creating the matplotlib-figure and its subplot.
    def create_figure(self):
        self.fig = plt.figure(facecolor=self.facecolor.text())
        plt.rcParams.update({"font.size": int(self.font_size.text())})
        self.subplot_area.append("Figure created. Facecolor: " + self.facecolor.text())

        self.ax1 = plt.subplot2grid((5,4),(1,0),rowspan=4, colspan=4,axisbg=self.axisbg.text())
        self.subplot_area.append("Ax1 created.\n")

        self.ax_color()
        self.plot_btn.setEnabled(True)

    # Function for setting up the labels of the axes.
    def labels(self):
        plt.xlabel(self.x_label.text())
        plt.ylabel(self.y_label.text())
        self.ax1.xaxis.label.set_color(self.tick_color.text())
        self.ax1.yaxis.label.set_color(self.tick_color.text())

    # Function for creating a legend.
    def legend(self):
        if self.check_legend.isChecked():
            handles, labels = self.ax1.get_legend_handles_labels()
            leg = plt.legend(handles, labels, loc=int(self.legend_loc.text()), ncol=int(self.legend_ncol.text()),
                             prop={"size": int(self.legend_size.text())}, fancybox=True,
                             borderaxespad=float(self.legend_border.text()))

            leg.get_frame().set_alpha(0.4)
            textEd = pylab.gca().get_legend().get_texts()
            pylab.setp(textEd[0:5], color="black")

    # function for plotting a candlestick chart
    def candlestick(self):
        data = self.df_list[self.variables.currentText()]

        # Get the variables for the candle array
        date, openp, closep, highp, lowp, volume = data["date"], data["openp"], data["closep"], data["highp"], data[
            "lowp"], data["volume"]
        x = 0
        y = len(date)

        candleArray = []
        date = mpl.date2num(date, str(self.fmt.text()))
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter(self.date_formatter.text()))

        # Filling the candle array.
        while x < y:
            appendLine = date[x], openp[x], closep[x], highp[x], lowp[x]
            candleArray.append(appendLine)
            x += 1

        # Plot the candle stick.
        _candlestick(self.ax1, candleArray, width=float(self.candle_width.text()), colorup=self.colorup.text(),
                     colordown=self.colordown.text())

        self.grid()
        self.labels()
        self.volume(date, volume)

        if self.radio_average.isChecked():
            self.moving_average(date, closep)

        self.legend()

        if self.radio_rsi.isChecked():
            self.rsi(date, closep)

        self.subplot_area.append("OHLC chart plotted\n")
        plt.subplots_adjust(left=.09,bottom=.14,right=.93,top=.95,wspace=.20,hspace=0)
        plt.suptitle(self.title.text(), color=self.tick_color.text(), fontsize=16)

    # Function for adding moving averages.
    def moving_average(self, date, closep):

        # Moving average function from another class calculates the averages
        av1 = mpl.movingaverage(closep, int(self.av1.text()))
        av2 = mpl.movingaverage(closep, int(self.av2.text()))
        av3 = mpl.movingaverage(closep, int(self.av3.text()))

        # Very important, since the higher the SMA the more errors are in data.
        # We have to reduce the index of x to plot the averages.
        # If not, we get the exception "index out of bound".
        sp = len(date[int(self.av3.text()) - 1:])

        label1 = self.av1.text() + " SMA"
        label2 = self.av2.text() + " SMA"
        label3 = self.av3.text() + " SMA"

        # Plot the averages.
        self.ax1.plot(date[-sp:], av1[-sp:], self.av1_col.text(), label=label1, linewidth=1.5)
        self.ax1.plot(date[-sp:], av2[-sp:], self.av2_col.text(), label=label2, linewidth=1.5)
        self.ax1.plot(date[-sp:], av3[-sp:], self.av3_col.text(), label=label3, linewidth=1.5)

        self.subplot_area.append("Added moving average with " + label1 + " to chart")
        self.subplot_area.append("Added moving average with " + label2 + " to chart")
        self.subplot_area.append("Added moving average with " + label3 + " to chart")

    # Function for adding the volume subplot.
    def volume(self, date, volume):
        if self.volume_radio.isChecked():
            volumeMin = 0

            self.ax1v = self.ax1.twinx()
            self.ax1v.fill_between(date, volumeMin, volume, facecolor=self.vol_color.text(), alpha=.5)
            self.ax1v.grid(False)
            self.ax1v.spines["bottom"].set_color("#5998ff")
            self.ax1v.spines["top"].set_color("#5998ff")
            self.ax1v.spines["left"].set_color("#5998ff")
            self.ax1v.spines["right"].set_color("#5998ff")
            self.ax1v.tick_params(axis="y", colors="w")
            self.ax1v.tick_params(axis="x", colors="w")
            self.ax1v.axes.yaxis.set_ticklabels([])
            self.ax1v.set_ylim(0, 10 * volume.max())
            self.subplot_area.append("Added Volume to chart")

    # Function for plotting line and scatter charts.
    def line_and_scatter(self):
        x, y, volume = self.get_axes()
        x = mpl.date2num(x, str(self.fmt.text()))
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter(self.date_formatter.text()))
        self.ylim(self.ax1, y)

        plt.suptitle(self.title.text(), fontsize=16)
        self.grid()
        self.volume(x, volume)
        self.labels()
        if self.radio_average.isChecked():
            self.moving_average(x, y)

        if self.diagrams.currentText() == "plot":
            self.ax1.plot(x, y, color=self.color.text())
            self.subplot_area.append("Line chart plotted\n")

        elif self.diagrams.currentText() == "scatter":
            self.ax1.scatter(x, y, color=self.color.text())
            self.subplot_area.append("Scatter chart plotted\n")

        self.legend()
        self.rsi(x,y)
        plt.subplots_adjust(left=.09,bottom=.14,right=.93,top=.95,wspace=.20,hspace=0)

    # Adding the RSI to graph.
    def rsi(self,date,closep):
        rsi = mpl.rsiFunc(closep)
        self.axRsi = plt.subplot2grid((5, 4), (0, 0), sharex=self.ax1, rowspan=1, colspan=4, axisbg="#07000d")

        rsiCol = self.rsi_color.text()
        self.axRsi.plot(date, rsi, rsiCol, linewidth=float(self.rsi_width.text()))

        self.axRsi.axhline(70, color=rsiCol)
        self.axRsi.axhline(30, color=rsiCol)

        # It is widely accepted to say, that over 70 a stock is overbought.
        # Under 30, the stock is underbought.
        self.axRsi.fill_between(date, rsi, 70, where=(rsi >= 70), facecolor=rsiCol, edgecolor=rsiCol)
        self.axRsi.fill_between(date, rsi, 30, where=(rsi <= 30), facecolor=rsiCol, edgecolor=rsiCol)

        self.axRsi.spines["bottom"].set_color("#5998ff")
        self.axRsi.spines["top"].set_color("#5998ff")
        self.axRsi.spines["left"].set_color("#5998ff")
        self.axRsi.spines["right"].set_color("#5998ff")

        self.axRsi.tick_params(axis="y", colors="w")
        self.axRsi.tick_params(axis="x", colors="w")

        self.axRsi.set_yticks([30, 70])
        self.axRsi.yaxis.label.set_color("w")

        self.subplot_area.append("Rsi added to chart.")

        plt.setp(self.axRsi.get_xticklabels(), visible=False)
        plt.ylabel("RSI")

    # Function for calling the candlestick or the line_and_scatter function.
    def plot(self):
        try:
            if self.diagrams.currentText() == "ohlc":
                self.candlestick()
            else:
                self.line_and_scatter()
            plt.show()
            self.plot_btn.setEnabled(False)
        except Exception as e:
            print(str(e))

            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Critical)
            msg.setWindowTitle("Plot Error")
            msg.setText("Error occurred. Plotting was unsuccessful.")
            msg.setInformativeText(str(e))
            msg.setStandardButtons(QtGui.QMessageBox.Ok)
            msg.exec_()


# Starting the application.
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    app.setStyle("plastique")
    app.exec_()
