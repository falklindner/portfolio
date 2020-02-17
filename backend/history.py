import backend.portfolio_view 
import backend.bank_input
import pandas as pd
import backend.constant as constant
import backend.secrets as secrets
import logging
import time
# from alpha_vantage.timeseries import TimeSeries

import yfinance as yf


def Rebuild_History():
    if (pd.Timestamp.today() < pd.Timestamp.today().replace(hour = 20, minute = 0, second = 0)):
        logging.warning("Need to wait until 20:00") ## After 20:00 Yahoo Finance will store the EoD / Close price (that is sometimes not present the next day)
    else:    
        # Setting up history dataframe with columns from all transactions
        symbol_list = backend.bank_input.ReadTransactions()["Symbol"].unique()

        properties = ["Close", "Volume", "Dividends"]
        hist_columns = pd.MultiIndex.from_product([symbol_list,properties], names=["Symbol", "Property"])
        hist = pd.DataFrame(
            columns=hist_columns,
            index=pd.date_range(start=constant.start, end=pd.Timestamp.today(), closed="right", name = "date"),
            dtype="float64"
        )
        # derecated. No advantage over yahoo finance
        # if (method == "alpha"):
        #     # Getting historical data from Alpha Vantage
        #     ts = TimeSeries(key = secrets.alpha_vantage_api_key, output_format='pandas', indexing_type='date')
        #     for symbol in symbol_list:
        #         data, meta_data = ts.get_daily_adjusted(symbol=symbol, outputsize="full")
        #         data.to_csv("data/hist_" + symbol + ".csv")
        #         time.sleep(15) ## Only 5 API calls per minute in free tier 
        #     # Harmonizing Alpha Vantage data in one dataframe
        #     collection = {}
        #     for symbol in symbol_list:
        #         path = "data/hist_" + symbol + ".csv"
        #         collection[symbol] = pd.read_csv(path, index_col=0, parse_dates=[0])[["5. adjusted close","6. volume", "7. dividend amount"]].rename(columns={"5. adjusted close":"Close","6. volume": "Volume", "7. dividend amount":"Dividends"})
        #     join = pd.concat(collection, axis=1,names=["Symbol", "Property"])

        symbol_list_string = ""
        for symbol in symbol_list:
            symbol_list_string = str(symbol_list_string + symbol + " ")

        ten_days_before= (constant.yesterday - pd.DateOffset(9)).replace(hour=0, minute=0, second=0,microsecond =0)

        data_legacy = yf.download(  # or pdr.get_data_yahoo(...
            # tickers list or string as well
            tickers = symbol_list_string,

            # use "period" instead of start/end
            # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            # (optional, default is '1mo')
            #period = "ytd",
            start = constant.start,
            end = constant.yesterday,
            # fetch data by interval (including intraday if period < 60 days)
            # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            # (optional, default is '1d')
            interval = "1d",

            # group by ticker (to access via data['SPY'])
            # (optional, default is 'column')
            group_by = 'ticker',
            actions= True,

            # adjust all OHLC automatically
            # (optional, default is False)
            auto_adjust = True,

            # download pre/post regular market hours data
            # (optional, default is False)
            prepost = True,

            # use threads for mass downloading? (True/False/Integer)
            # (optional, default is True)
            threads = True,

            # proxy URL scheme use use when downloading?
            # (optional, default is None)
            proxy = None
        )
        data_recent = yf.download(  
            tickers = symbol_list_string,
            start = ten_days_before,
            end = pd.Timestamp.today(),
            interval = "1d",
            group_by = 'ticker',
            actions= True,
            auto_adjust = True,
            prepost = True,
            threads = True,
            proxy = None
        )
        
        hist_legacy = data_legacy.loc[constant.start:,(slice(None),("Close","Volume","Dividends"))]
        hist_recent = data_recent.loc[:,(slice(None),("Close","Volume","Dividends"))]
        hist.update(hist_legacy)
        hist.update(hist_recent)
          

        # Updating empty History dataframe with harmonized data
        hist.sort_index(axis=1, inplace=True)
        hist.update(hist.loc[:,(slice(None),slice("Close"))].interpolate(method="linear")) # Linear interpolation for missing data in all "Close" columns 
        hist.update(hist.loc[:,(slice(None),("Volume","Dividends"))].fillna(0))
        hist.to_csv(constant.hist_path)




def Read_History():
    try:
        hist = pd.read_csv(constant.hist_path,
        index_col=0,
        parse_dates = [0],
        header = [0,1],
        skiprows = 0
        )
    except:
        logging.warning("Importing history from " + constant.hist_path + " failed.")
        hist = pd.DataFrame()
    return hist


## Construct data frame with historical values of all symbols in portfolio

def Update_History(): 
    if (pd.Timestamp.today() < pd.Timestamp.today().replace(hour = 20, minute = 0, second = 0)):
        logging.warning("Need to wait until 20:00") ## After 20:00 Yahoo Finance will store the EoD / Close price (that is sometimes not present the next day)
    else: 
        hist = Read_History()

        ## Determining the time period for history file update
        if (hist.size == 0):
            logging.warning("Found empty History. Renewing history from " + str(constant.start))
            Rebuild_History()
            return
        else:
            lastday = hist.index[-1]
        today = pd.Timestamp.today().replace(hour = 0, minute = 0, second = 0, microsecond = 0)
        
        ## Creating the list of columns (stocks) for the history file (either by old hist.csv or by checking portfolio)
        if (hist.columns.size == 0):
            logging.warning("Using Symbols from transactions instead of hist.csv")
            symbols = backend.bank_input.ReadTransactions()["Symbol"].unique()
            properties = ["Close", "Volume", "Dividends"]
            hist_columns = pd.MultiIndex.from_product([symbols,properties], names=["Symbol", "Property"])
        else:
            hist_columns = hist.columns

        ## Main update loop. Creating Dataframe to append to old history
        if (lastday == today):
            logging.debug("History is up to date.")
        else:
            hist_update = pd.DataFrame(
            columns=hist_columns,
            index=pd.date_range(start=lastday, end=today, closed="right"),
            dtype="float64"
            )

            ## Update loop
            logging.debug("Updating the following days in History: "+ str(hist_update.index.strftime("%d.%m").values))
            
            symbol_list_string = ""
            for symbol in backend.bank_input.ReadTransactions()["Symbol"].unique():
                symbol_list_string = str(symbol_list_string + symbol + " ")
            
            data_recent = yf.download(  
            tickers = symbol_list_string,
            start = lastday + pd.DateOffset(1),
            end = pd.Timestamp.today(),
            interval = "1d",
            group_by = 'ticker',
            actions= True,
            auto_adjust = True,
            prepost = True,
            threads = True,
            proxy = None
            )
            hist_update = data_recent.loc[:,(slice(None),("Close","Volume","Dividends"))]
            hist = hist.append(hist_update)
            hist.sort_index(axis=1, inplace=True)
            if hist.index.size == hist.drop_duplicates().index.size:
                hist.update(hist.loc[:,(slice(None),slice("Close"))].interpolate(method="linear")) # Linear interpolation for missing data in all "Close" columns 
                hist.update(hist.loc[:,(slice(None),("Volume","Dividends"))].fillna(0))
                hist.to_csv(constant.hist_path)
            else:
                logging.warning("No new data was given from Yahoo Finance.")
