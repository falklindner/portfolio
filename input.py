import pandas as pd
import numpy as np 
import datetime
import matplotlib.pyplot as plt
import re

# from pandas_datareader import data as pdr
import yfinance as yf



datefrmt = lambda x: pd.datetime.strptime(x, "%d.%m.%Y")
encoding = "cp1252"

dkb = pd.read_csv("dkb_sg.csv",
    skiprows = 1,
    usecols = [0,1,2,3,4,5,6,7,9],
    parse_dates = [0,1],
    date_parser = datefrmt,
    decimal=",",
    thousands=".",
    names = ["Execute","Booking","Amount","Name","WKN","Currency","Price","Trans","Portfolio"]
)
amount = pd.read_csv("ums.csv",
    skiprows = 4,
    delimiter = ";",
    encoding = encoding,
    decimal = ".",
    usecols = [2],
    names = ["Amount"], 
    header = None
)
parsed = pd.read_csv("ums.csv",
    skiprows = 4,
    delimiter = ";",
    encoding = encoding,
    parse_dates = [0,1],
    date_parser = datefrmt, 
    decimal = ",",
    usecols = [0,1,3,4,5,6,7],
    names = ["Execute","Booking","Name","WKN","Currency","Price","Trans"], 
    header = None
)



input_form = pd.concat([parsed,amount], axis = 1)
input_form = input_form.assign(Portfolio="Altersvorsorge")
cumulation = pd.concat([input_form,dkb],ignore_index = True)

xetra = pd.read_csv("t7-xetr-allTradableInstruments.csv",
    skiprows = 2,
    delimiter = ";",
    encoding = encoding,
    decimal= "."
)



def toyahoo(wkn):
    test = yf.Ticker(wkn)
    count = test.history(period="1m").Close.count()
    if ( count > 0):
        return test
    else:
        wkn_mod = xetra[xetra["WKN"].str.contains(wkn)].Mnemonic.values[0] + ".DE"
        test_mod = yf.Ticker(wkn_mod)
        count_mod = test_mod.history(period="1m") 
        if ( count_mod > 0): 
            return test_mod
        else:
            print("WKN could not be found in Yahoo Finance")
            exit()


toyahoo("LYX0AG")

test = yf.Ticker("LYX0AG")
a = test.history(period="1m").Close.count()


test = yf.Ticker("AMEW.DE")

lookup("LYX0AG")
xetra.loc[xetra["WKN"] == "LYX0AG"]

list_wkns = pd.DataFrame(cumulation.WKN.unique(), columns=["WKN"])
list_wkns



input_form

input_form.loc[(input_form["Execute"] < datetime.datetime(2019,2,1)) & (input_form["WKN"] == "ETF110")]


class Stock:
    def __init__(self, WKN, GoogleSymbol, YahooSymbol):
        self.wkn = WKN
        self.gsymbol = GoogleSymbol
        self.ysymbol = YahooSymbol
        self.own = 0
    def mod(self, amount):
        self.own = self.own + amount





msci_world_it_lyxor = Stock("LYX0GP", "FRA:LYPG", "LYPG.DE")
msci_world_lyxor = Stock("LYX0AG", "FRA:LYYA","LYYA.DE")
msci_world_comstage = Stock("ETF110", "FRA:X010", "X010.DE")
msci_world_amundi = Stock("A2H59Q", "FRA:AMEW", "AMEW.DE")
msci_world_it_xtrackers = Stock("A113FM", "FRA:XDWT", "XDWT.DE")
airbus = Stock("AIR.PA", "ETR:AIR", "AIR.PA")
known_stocks = [airbus,msci_world_amundi,msci_world_comstage,msci_world_it_lyxor,msci_world_it_xtrackers,msci_world_lyxor]


av = cumulation.loc[cumulation["Portfolio"] == "Altersvorsorge"]

av["WKN"].unique().size


for wkn in av["WKN"].unique():
   if (wkn not in known_stocks.wkn):
       print(wkn "is not known")
   print(wkn)


