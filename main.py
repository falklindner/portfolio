import pandas as pd
import numpy as np 
from lib import financial

import matplotlib.pyplot as plt
# import re
import csv
import yfinance as yf
# from pandas_datareader import data as pdr
from PortfolioPerformance import PortfolioToPP
import Bank_Input

## Paths and default settings 

dkb_path = "data/dkb_sg.csv"
cd_path  = "data/umsaetze_9774844981_20191118-2138.csv"

portfolio_path = "data/Portfolio.csv"
hist_path = "data/Hist.csv"
portfolio_view_path = "data/Portfolio_View.csv"

## CSV Import of account transactions

input_dkb = Bank_Input.DfFromDKB(dkb_path,portfolio_path)
input_cd = Bank_Input.DfFromComdirect(cd_path,portfolio_path)

## Updating the main transaction repository (portfolio_path)

Bank_Input.UpdatePortfolio(input_dkb,portfolio_path)
Bank_Input.UpdatePortfolio(input_cd,portfolio_path)

## Rearranging transactions to Portfolio/Stocks vs. time view

portfolio = Bank_Input.ReadPortfolio(portfolio_path)

portfolio_list = portfolio["Portfolio"].unique()
symbol_list =  portfolio["Symbol"].unique()
property_list = ["Holdings", "Value", "Fees", "RAD", "RADTX", "XIRR"]


## Time constants

start = pd.Timestamp(year = 2016, month = 1, day = 15)
now = pd.Timestamp.today()
yesterday = (now - pd.DateOffset(1)).replace(hour=0, minute=0, second=0,microsecond =0)
time_index = pd.date_range(start=start, end=now)

## Construct data frame with historical values of all symbols in portfolio

hist = pd.DataFrame(
    columns = symbol_list,
    index = pd.date_range(start=start, end=yesterday)
)

for symbol in symbol_list:
    hist[symbol] = yf.Ticker(symbol).history(start = start, end = yesterday).Close

## Saving historical values to hist_path 
## TBD hist update instead of complete download

hist.to_csv(hist_path)
hist = pd.read_csv(hist_path,
    index_col=0,
    parse_dates = [0],
    header = 0,
    skiprows = 0
)
hist.fillna(method="ffill", inplace= True)

## Creating a multiindex-column for portfolio view

multi_index_data = []
for pf in portfolio_list:
    for symbol in portfolio["Symbol"].loc[portfolio["Portfolio"] == pf].unique():
        for prop in property_list:
            multi_index_data += [[pf,symbol,prop]]

cols = pd.MultiIndex.from_tuples(multi_index_data, names=["Portfolio", "Symbol", "Properties"])

## Creating empty portfolio view data frame

portfolio_view = pd.DataFrame(
    columns=cols,
    index=pd.date_range(start=start, end=yesterday)
   
)

## Filling portfolio view data frame with values from transactions per day

for date in  portfolio_view.index:
    pf_at_date = portfolio.set_index("Execute").loc[start:date]
    for pf in portfolio_list:
        for symbol in portfolio["Symbol"].loc[portfolio["Portfolio"] == pf].unique():
            pf_symbol_at_date = pf_at_date.loc[(pf_at_date["Portfolio"] == pf) & (pf_at_date["Symbol"] == symbol)]
            amount_at_date = pf_symbol_at_date["Amount"].sum()
            fees_at_date = pf_symbol_at_date["Fee"].sum()
            trans_at_date = pf_symbol_at_date["Trans"].sum()

            irr_list = ((-1)*pf_symbol_at_date["Trans"]).tolist()
            irr_list.append(amount_at_date * hist.loc[date,symbol])
           

            portfolio_view.loc[date,(pf,symbol,"Holdings")] = amount_at_date
            portfolio_view.loc[date,(pf,symbol,"Value")] = amount_at_date * hist.loc[date,symbol]
            portfolio_view.loc[date,(pf,symbol,"Fees")] = fees_at_date
            portfolio_view.loc[date,(pf,symbol,"RAD")] =  (amount_at_date * hist.loc[date,symbol]) / trans_at_date ## Fees are included in Amount / Transaction cost
            portfolio_view.loc[date,(pf,symbol,"RADTX")] =  (0.75 * amount_at_date * hist.loc[date,symbol]) / trans_at_date ## Return with 25% stock rerturns tax
            portfolio_view.loc[date,(pf,symbol,"XIRR")] = np.irr(irr_list)



date = portfolio_view.index[1000]
pf = portfolio_list[0]
symbol =  portfolio["Symbol"].loc[portfolio["Portfolio"] == pf].unique()[0]
pf_at_date = portfolio.set_index("Execute").loc[start:date]
pf_symbol_at_date = pf_at_date.loc[(pf_at_date["Portfolio"] == pf) & (pf_at_date["Symbol"] == symbol)]
amount_at_date = pf_symbol_at_date["Amount"].sum()
fees_at_date = pf_symbol_at_date["Fee"].sum()
trans_at_date = pf_symbol_at_date["Trans"].sum()



pf_symbol_at_date[["Trans"]].to_records(index_dtypes = "datetime.date" )

xirr_list = ((-1)*pf_symbol_at_date["Trans"]).tolist()
xirr_list.append(amount_at_date * hist.loc[date,symbol])
xirr_list

financial.xirr()






portfolio_view


portfolio_view.to_csv(portfolio_view_path)


portfolio_view.loc['2019-01-01':yesterday].index

first = portfolio_view["Airbus","AIR.PA","Holdings"].ne(0).idxmax()

plt.plot(portfolio_view.loc[first:yesterday].index,portfolio_view.loc[first:yesterday]["Airbus","AIR.PA","Value"])
plt.show()