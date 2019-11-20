import pandas as pd
import csv
import yfinance as yf

datefrmt = lambda x: pd.datetime.strptime(x, "%d.%m.%Y")
input_portfolio = pd.read_csv("data/Portfolio.csv", 
    parse_dates=[0,1]
)

def ReadPortfolio(path):
    portfolio = pd.read_csv(path, 
        parse_dates=[0,1]
    )
    return portfolio


def ToYahoo(wkn):
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

def CreateDict(path):
    ReadPortfolio(path)
    wkn_symbol = input_portfolio.drop_duplicates(subset=["WKN"])[["WKN","Symbol"]].set_index("WKN").T.to_dict(orient="list")
    return wkn_symbol

def DfFromDKB(input_path, ref_path):
    wkn_symbol = CreateDict(ref_path)
    dataframe = pd.read_csv(input_path,
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

def DfFromComdirect(input_path, ref_path):
    wkn_symbol = CreateDict(ref_path)
    amount = pd.read_csv(input_path,
        skiprows = 4,
        delimiter = ";",
        encoding = "cp1252",
        decimal = ".",
        usecols = [2],
        names = ["Amount"], 
        header = None
    )
    parsed = pd.read_csv(input_path,
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