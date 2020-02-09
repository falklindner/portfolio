import pandas as pd
import csv
import yfinance as yf
import backend.constant as constant
import glob

def ReadTransactions(path):
    portfolio = pd.read_csv(path, 
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
            print("WKN could not be found in Yahoo Finance")
            return
        else:
            wkn_mod = xetra[xetra["WKN"].str.contains(wkn)].Mnemonic.values[0] + ".DE"
            test_mod = yf.Ticker(wkn_mod)
            count_mod = test_mod.history(period="1m").Close.count()
            return wkn_mod


def ReadDict():
    with open ("data/dict.csv") as file:
        reader = csv.reader(file)
        wkn_dict = dict(reader)
    return wkn_dict

def DfFromDKB(path):
    files = [f for f in glob.glob(path + constant.dkb_pattern)]
    wkn_symbol = ReadDict()
    dataframe = pd.DataFrame()
    for f in files:
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
    dataframe = dataframe.set_index("Execute")
    dataframe = dataframe.sort_index()
    return dataframe

def DfFromComdirect(path):
    files = [f for f in glob.glob(path + constant.cd_pattern)]
    wkn_symbol = ReadDict()
    dataframe = pd.DataFrame()
    for f in files:
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
    dataframe = dataframe.set_index("Execute")
    dataframe = dataframe.sort_index()
    return dataframe

def LoadTransactions():
    input_dkb = DfFromDKB(constant.dkb_path)
    input_cd = DfFromComdirect(constant.dkb_path)
    input_all = pd.concat([input_dkb,input_cd], sort=False).sort_index()
    with open(constant.transactions_path, mode = "w+", newline="\n", encoding="UTF-8") as file:
            input_all.to_csv(file,
                sep = ",",
                quoting = csv.QUOTE_NONNUMERIC,
                quotechar = "\"",
                line_terminator = "\n", 
                index = True,
                header = True
            )



def UpdateTransactions(Input_Trans,Ref_Trans):
    Portfolio = ReadTransactions(Ref_Trans)
    LatestTrans = Portfolio.index[-1]
    New_Trans = Input_Trans[Input_Trans.index > LatestTrans ]
    if New_Trans.shape[0] > 0:
        Portfolio = pd.concat([Portfolio,New_Trans],ignore_index = True, sort = False)
        with open(Ref_Trans, mode = "a+", newline="\n", encoding="UTF-8") as file:
            New_Trans.to_csv(file,
                sep = ",",
                quoting = csv.QUOTE_NONNUMERIC,
                quotechar = "\"",
                line_terminator = "\n", 
                index = True,
                header = True
            )
            print("Updated ",New_Trans.shape[0]," transactions.")
    else:
        print("Transactions are up to date.")