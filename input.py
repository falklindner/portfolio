import pandas as pd
import numpy as np 
import datetime
import matplotlib.pyplot as plt
import re
import csv
import yfinance as yf
# from pandas_datareader import data as pdr
from PortfolioPerformance import PortfolioToPP


datefrmt = lambda x: pd.datetime.strptime(x, "%d.%m.%Y")

def toyahoo(wkn):
    xetra = pd.read_csv("data/t7-xetr-allTradableInstruments.csv",
    skiprows = 2,
    delimiter = ";",
    encoding = "cp1252",
    decimal= "."
    )
    test = yf.Ticker(wkn)
    count = test.history(period="1m").Close.count()
    if ( count > 0):
        return wkn
    else:
        if ( xetra[xetra["WKN"].str.contains(wkn)].Mnemonic.values.size == 0 ):
            print("WKN could not be found in Yahoo Finance")
            return
        else:
            wkn_mod = xetra[xetra["WKN"].str.contains(wkn)].Mnemonic.values[0] + ".DE"
            test_mod = yf.Ticker(wkn_mod)
            count_mod = test_mod.history(period="1m").Close.count()
            return wkn_mod

input_portfolio = pd.read_csv("data/Portfolio.csv", 
    parse_dates=[0,1]
)
wkn_list = input_portfolio.WKN.unique().tolist()
yahoo_list = []
for wkn in wkn_list:
    yahoo_list.append(toyahoo(wkn))

wkn_symbol = dict(zip(wkn_list,yahoo_list))
wkn_symbol

def DfFromDKB(path):
    dataframe = pd.read_csv("data/dkb_sg.csv",
        skiprows = 1,
        usecols = [0,1,2,3,4,5,6,7,9],
        parse_dates = [0,1],
        date_parser = datefrmt,
        decimal=",",
        thousands=".",
        names = ["Execute","Booking","Amount","Name","WKN","Currency","Price","Trans","Portfolio"]
    )
    dataframe["Fee"] = (dataframe["Trans"]-dataframe["Amount"]*dataframe["Price"]).round(2)
    dataframe["Symbol"] = dataframe["WKN"].replace(wkn_symbol)
    return dataframe

def DfFromComdirect(path):
    amount = pd.read_csv(path,
        skiprows = 4,
        delimiter = ";",
        encoding = "cp1252",
        decimal = ".",
        usecols = [2],
        names = ["Amount"], 
        header = None
    )
    parsed = pd.read_csv(path,
        skiprows = 4,
        delimiter = ";",
        encoding = "cp1252",
        parse_dates = [0,1],
        date_parser = datefrmt, 
        decimal = ",",
        usecols = [0,1,3,4,5,6,7],
        names = ["Execute","Booking","Name","WKN","Currency","Price","Trans"], 
        header = None
    )
    dataframe = pd.concat([parsed,amount], axis = 1)
    dataframe = dataframe.assign(Portfolio="Altersvorsorge")
    dataframe["Fee"] = (dataframe["Trans"]-dataframe["Amount"]*dataframe["Price"]).round(2)
    dataframe["Symbol"] = dataframe["WKN"].replace(wkn_symbol)
    return dataframe




def UpdatePortfolio (Input_Trans,path):
    Portfolio = pd.read_csv(path, 
        parse_dates=[0,1]
    )
    LatestTrans = Portfolio["Execute"][Portfolio["Execute"].idxmax()]
    Input_Trans.sort_values(by = ["Execute"], inplace= True)
    New_Trans = Input_Trans.loc[Input_Trans["Execute"] > LatestTrans ]
    if New_Trans.shape[0] > 0:
        Portfolio = pd.concat([Portfolio,New_Trans],ignore_index = True, sort = False)
        with open(path, mode = "w+", newline="\n", encoding="UTF-8") as file:
            Portfolio.to_csv(file,
                sep = ",",
                quoting = csv.QUOTE_NONNUMERIC,
                quotechar = "\"",
                line_terminator = "\n", 
                index = False,
                header = True
            )
            print("Updated ",New_Trans.shape[0]," transactions in Portfolio.")
    else:
        print("Portfolio is up to date.")







start = pd.Timestamp(year = 2016, month = 1, day = 1)
today = pd.Timestamp.date(pd.Timestamp.today())



hist = pd.DataFrame(
    columns = yahoo_list,
  #  index = pd.date_range(start=start, end=end)
)

for symbol in yahoo_list:
    hist[symbol] = yf.Ticker(symbol).history(start = start, end = today).Close


hist.to_csv("hist.csv")
hist = pd.read_csv("hist.csv",
    index_col=0,
    parse_dates = [0],
    header = 0,
    skiprows = 0
)

