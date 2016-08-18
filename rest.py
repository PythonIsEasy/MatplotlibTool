#
# This file contains important functions for calculations and converting dates.
#

import matplotlib.dates as mdates
import numpy as np

# converts bytes
def bytedate2num(fmt):
    def converter(byte):
        return mdates.strpdate2num(fmt)(byte.decode("utf-8"))
    return converter

# convert the date to a numeric number
def date2num(df,fmt):
    date_converter = bytedate2num(fmt)
    date = np.loadtxt(df, converters={0: date_converter})
    return date


# calculates the lim
def lims(df,lim,percent):
    lim = lim
    if lim == "max":
        lim = np.max(df)
        lim = lim*percent

    elif lim == "min":
        lim = np.min(df)
        lim = lim*percent

    else:
        lim = float(lim)

    return lim  # return the lim

# calculates the moving average
def movingaverage(values,window):

    weights = (np.repeat(1.0,window))/window

    smas = np.convolve(values,weights,"valid")
    return smas  # return the average


# calculates the RSI
def rsiFunc(prices,n=14):
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    down = -seed[seed<0].sum()/n
    up = seed[seed>=0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n,len(prices)):
        delta= deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval=0.
            downval = -delta

        up = (up*(n-1)+upval)/n
        down = (down*(n-1)+downval)/n

        rs = up/down
        rsi[i]= 100.-100./(1.+rs)

    return rsi  # return the RSI