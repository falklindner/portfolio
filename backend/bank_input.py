import logging
import pandas as pd
import csv
import yfinance as yf
import backend.constant as constant
import glob


def ReadTransactions():
    portfolio = pd.read_csv(constant.transactions_path, 
        parse_dates=[0,1],
        index_col=0
    )
    return portfolio


def ToYahoo(wkn):
    xetra = pd.read_csv(constant.xetra,
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
            logging.warning("WKN could not be found in Yahoo Finance")
            return
        else:
            wkn_mod = xetra[xetra["WKN"].str.contains(wkn)].Mnemonic.values[0] + ".DE"
            test_mod = yf.Ticker(wkn_mod)
            count_mod = test_mod.history(period="1m").Close.count()
            return wkn_mod


def ReadDict():
    with open (constant.dict_path) as file:
        reader = csv.reader(file)
        wkn_dict = dict(reader)
    return wkn_dict

def DfFromDKB(path):
    files = [f for f in glob.glob(path + constant.dkb_pattern)]
    wkn_symbol = ReadDict()
    dataframe = pd.DataFrame()
    for f in files:
        logging.debug("Importing " + f)
        fileframe = pd.read_csv(f,
            skiprows = 1,
            usecols = [0,1,2,3,4,5,6,7,9],
            parse_dates = [0,1],
            date_parser = constant.datefrmt,
            decimal=",",
            thousands=".",
            names = ["Execute","Booking","Amount","Name","WKN","Currency","Price","Trans","Portfolio"]
        )
        dataframe = dataframe.append(fileframe)
    dataframe.drop_duplicates(inplace=True)
    dataframe["Fee"] = (dataframe["Trans"]-dataframe["Amount"]*dataframe["Price"]).round(2)
    dataframe["Symbol"] = dataframe["WKN"].replace(wkn_symbol)
    dataframe = dataframe.set_index("Booking")
    dataframe = dataframe.sort_index()
    return dataframe

def DfFromComdirect(path):
    files = [f for f in glob.glob(path + constant.cd_pattern)]
    wkn_symbol = ReadDict()
    dataframe = pd.DataFrame()
    for f in files:
        logging.debug("Importing " +f)
        amount = pd.read_csv(f,
            skiprows = 4,
            delimiter = ";",
            encoding = "cp1252",
            decimal = ".",
            usecols = [2],
            names = ["Amount"], 
            header = None
        )
        parsed = pd.read_csv(f,
            skiprows = 4,
            delimiter = ";",
            encoding = "cp1252",
            parse_dates = [0,1],
            date_parser = constant.datefrmt, 
            decimal = ",",
            usecols = [0,1,3,4,5,6,7],
            names = ["Execute","Booking","Name","WKN","Currency","Price","Trans"], 
            header = None
        )
        fileframe = pd.concat([parsed,amount], axis = 1)
        dataframe = dataframe.append(fileframe)
        
    dataframe.drop_duplicates(inplace=True)
    dataframe = dataframe.assign(Portfolio="Altersvorsorge")
    dataframe["Fee"] = (dataframe["Trans"]-dataframe["Amount"]*dataframe["Price"]).round(2)
    dataframe["Symbol"] = dataframe["WKN"].replace(wkn_symbol)
    dataframe = dataframe.set_index("Booking")
    dataframe = dataframe.sort_index()
    return dataframe

def Rebuild_Transactions():
    input_dkb = DfFromDKB(constant.dkb_path)
    input_cd = DfFromComdirect(constant.dkb_path)
    input_all = pd.concat([input_dkb,input_cd]).sort_index()
    with open(constant.transactions_path, mode = "w+", newline="\n", encoding="UTF-8") as file:
            input_all.to_csv(file,
                sep = ",",
                quoting = csv.QUOTE_NONNUMERIC,
                quotechar = "\"",
                line_terminator = "\n", 
                index = True,
                header = True
            )

def UpdateTransactions():
    input_dkb = DfFromDKB(constant.dkb_path)
    input_cd = DfFromComdirect(constant.cd_path)
    input_all = pd.concat([input_dkb,input_cd]).sort_index()

    Portfolio = ReadTransactions()
    LatestTrans = Portfolio.index[-1]
    New_Trans = input_all[input_all.index > LatestTrans ]
    if New_Trans.shape[0] > 0:
        Portfolio = pd.concat([Portfolio,New_Trans])
        with open(constant.transactions_path, mode = "w+", newline="\n", encoding="UTF-8") as file:
            Portfolio.to_csv(file,
                sep = ",",
                quoting = csv.QUOTE_NONNUMERIC,
                quotechar = "\"",
                line_terminator = "\n", 
                index = True,
                header = True
            )
            logging.info("Updated " + str(New_Trans.shape[0]) + " transactions.")
    else:
        logging.info("Transactions are up to date.")