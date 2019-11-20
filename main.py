import pandas as pd
# import numpy as np 
# import datetime
# import matplotlib.pyplot as plt
# import re
import csv
import yfinance as yf
# from pandas_datareader import data as pdr
from PortfolioPerformance import PortfolioToPP
import Bank_Input


dkb_path = "data/dkb_sg.csv"
cd_path  = "data/umsaetze_9774844981_20191118-2138.csv"
portfolio_path = "data/Portfolio.csv"

input_dkb = Bank_Input.DfFromDKB(dkb_path,portfolio_path)
input_cd = Bank_Input.DfFromComdirect(cd_path,portfolio_path)

Bank_Input.UpdatePortfolio(input_dkb,portfolio_path)
Bank_Input.UpdatePortfolio(input_cd,portfolio_path)

portfolio = Bank_Input.ReadPortfolio(portfolio_path)

portfolio

start = pd.Timestamp(year = 2016, month = 1, day = 15)
today = pd.Timestamp.date(pd.Timestamp.today())

symbol_list = portfolio["Symbol"].unique()

hist = pd.DataFrame(
    columns = symbol_list,
    index = pd.date_range(start=start, end=today)
)

for symbol in symbol_list:
    hist[symbol] = yf.Ticker(symbol).history(start = start, end = today).Close

hist
hist.to_csv("hist.csv")
hist = pd.read_csv("hist.csv",
    index_col=0,
    parse_dates = [0],
    header = 0,
    skiprows = 0
)

analysis = pd.DataFrame(
    index=pd.date_range(start=start, end=today)
)