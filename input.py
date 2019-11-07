import pandas as pd
import numpy as np 
import datetime
import matplotlib.pyplot as plt

from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override() 


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

cumulation.WKN.unique()

input_form["Fees"] = round(input_form["Trans"]-(input_form["Amount"]*input_form["Price"]),2)
input_form

input_form.loc[(input_form["Execute"] < datetime.datetime(2019,2,1)) & (input_form["WKN"] == "ETF110")]

pdr.get_data_yahoo("AIR.PA")
pdr.get_data_yahoo_actions("X010.DE")

class Stock:
    def __init__(self, WKN, GoogleSymbol, YahooSymbol):
        self.wkn = WKN
        self.gsymbol = GoogleSymbol
        self.ysymbol = YahooSymbol
        self.own = 0
    def mod(amount):
        own = own + amount



msci_world_it_lyxor = Stock("LYX0GP", "FRA:LYPG", "LYPG.DE")
msci_world_lyxor = Stock("LYX0AG", "FRA:LYYA","LYYA.DE")
msci_world_comstage = Stock("ETF110", "FRA:X010", "X010.DE")
msci_world_amundi = Stock("A2H59Q", "FRA:AMEW", "AMEW.DE")
msci_world_it_xtrackers = ("A113FM", "FRA:XDWT", "XDWT.DE")
airbus = ("AIR.PA", "ETR:AIR", "AIR.PA")
known_stocks = [airbus,msci_world_amundi,msci_world_comstage,msci_world_it_lyxor,msci_world_it_xtrackers,msci_world_lyxor]


av = cumulation.loc[cumulation["Portfolio"] == "Altersvorsorge"]

av["WKN"].unique().size


for wkn in av["WKN"].unique():
   if (wkn not in known_stocks.wkn):
       print(wkn "is not known")
   print(wkn)


