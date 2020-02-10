from backend.portfolio_view import ReadPortfolioView
import pandas as pd
import backend.constant as constant
import backend.secrets as secrets
import logging
import time
from alpha_vantage.timeseries import TimeSeries


# import yfinance as yf

logging.basicConfig(filename="backend.log", format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)



def Rebuild_History():
    # Setting up history dataframe with columns from Portfolio
    symbol_list = ReadPortfolioView().columns.get_level_values(1).unique()
    properties = ["Close", "Volume", "Dividend"]
    hist_columns = pd.MultiIndex.from_product([symbol_list,properties], names=["Symbol", "Property"])
    hist = pd.DataFrame(
        columns=hist_columns,
        index=pd.date_range(start=constant.start, end=yesterday, closed="right", name = "date"),
        dtype="float64"
        )
    
    # Getting historical data from Alpha Vantage
    ts = TimeSeries(key = secrets.alpha_vantage_api_key, output_format='pandas', indexing_type='date')
    for symbol in symbol_list:
        data, meta_data = ts.get_daily_adjusted(symbol=symbol, outputsize="full")
        data.to_csv("data/hist_" + symbol + ".csv")
        time.sleep(15) ## Only 5 API calls per minute in free tier 

    # Harmonizing Alpha Vantage data in one dataframe
    collection = {}
    for symbol in symbol_list:
        path = "data/hist_" + symbol + ".csv"
        collection[symbol] = pd.read_csv(path, index_col=0, parse_dates=[0])[["5. adjusted close","6. volume", "7. dividend amount"]].rename(columns={"5. adjusted close":"Close","6. volume": "Volume", "7. dividend amount":"Dividend"})
    join = pd.concat(collection, axis=1,names=["Symbol", "Property"])
    
    # Updating empty History dataframe with harmonized data
    hist.update(join)
    hist.sort_index(axis=1, inplace=True)
    hist.update(hist.loc[:,(slice(None),slice("Close"))].interpolate(method="linear")) # Linear interpolation for missing data in all "Close" columns 
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
    
    hist = Read_History()

    ## Determining the time period for history file update
    if (hist.size == 0):
        logging.warning("Found empty History. Renewing history from " + str(constant.start))
        Rebuild_History()
        return
    else:
        lastday = hist.index[-1]
    yesterday = (pd.Timestamp.today() - pd.DateOffset(1)).replace(hour=0, minute=0, second=0,microsecond =0)
    
    ## Creating the list of columns (stocks) for the history file (either by old hist.csv or by checking portfolio)
    if (hist.columns.size == 0):
        logging.warning("Using Symbols from portfolio instead of hist.csv")
        symbols = ReadPortfolioView().columns.get_level_values(1).unique()
        properties = ["Close", "Volume", "Dividend"]
        hist_columns = pd.MultiIndex.from_product([symbols,properties], names=["Symbol", "Property"])
    else:
        hist_columns = hist.columns

    ## Main update loop. Creating Dataframe to append to old history
    if (lastday == yesterday):
        logging.debug("History is up to date.")
    else:
        hist_update = pd.DataFrame(
        columns=hist_columns,
        index=pd.date_range(start=lastday, end=yesterday, closed="right"),
        dtype="float64"
        )

        ## Update loop
        logging.debug("Updating the following days in History: "+ str(hist_update.index.strftime("%d.%m").values))
        ts = TimeSeries(key = secrets.alpha_vantage_api_key, output_format='pandas', indexing_type='date')
        for symbol in hist_columns.get_level_values(0).unique():
            logging.debug("Fetching data from Alpha Vantage")
            data, meta_data = ts.get_daily_adjusted(symbol=symbol, outputsize="compact")
            data.sort_index(inplace = True) ## API returns index wrong way around
            newdata = data.loc[lastday:yesterday,["5. adjusted close","6. volume", "7. dividend amount"]].rename(columns={"5. adjusted close":"Close","6. volume": "Volume", "7. dividend amount":"Dividend"})
            hist_update[symbol] = newdata
            time.sleep(15) ## Only 5 API calls per minute in free tier 

        hist_new = hist.append(hist_update).fillna(method="ffill")
        hist_new.to_csv(constant.hist_path)
