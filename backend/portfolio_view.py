import logging
import pandas as pd
import numpy as np
import backend.bank_input as BankInput
import backend.constant as constant
import backend.history 
import csv
import backend.financial_func as FinancialFunc
import os

## Checking if an update of Portfolio View is necessary (due to being to old or having new indices)
def ReadPortfolioView():
    if (pd.read_csv(constant.portfolio_view_path,header=[0,1,2]).size == 0):
        raw = pd.read_csv(constant.portfolio_view_path, 
        header=[0,1,2],
        )
        portfolio_view = pd.DataFrame(
        columns=pd.MultiIndex.from_tuples(raw.columns[1:], names = raw.columns[0]),
#        index=pd.date_range(start=constant.start, end=constant.start)
        )

    else: 
        portfolio_view = pd.read_csv(constant.portfolio_view_path, 
        header=[0,1,2], 
        index_col = 0,
        parse_dates = [0]
        )
    return portfolio_view

def BuildNewColumns():
    transactions = BankInput.ReadTransactions(constant.transactions_path)
    pf_list = transactions["Portfolio"].unique()
    properties = constant.pf_property_list
    
    pf_sym_list = []
    
    for pf in pf_list:
        pf_symbols = transactions["Symbol"].loc[transactions["Portfolio"] == pf].unique()
        for symbol in pf_symbols:
            for prop in properties:
                pf_sym_list.append((pf,symbol,prop))
    
    multiindex = pd.MultiIndex.from_tuples(pf_sym_list,names=["Portfolio","Symbol","Properties"])
    return multiindex
    
def LoadPortfolioView():
    
    firstday = constant.start
    yesterday = backend.constant.yesterday
    pfview_cols = BuildNewColumns()

    ## Moving existing csv to backup
    try:
        os.rename(constant.portfolio_view_path,constant.portfolio_view_path + "-old.csv")
    except FileNotFoundError:
        logging.Warning("Portfolio View File not found. Creating a new one")
    except FileExistsError:
        logging.warning("Overwriting existing backup.")
        os.replace(constant.portfolio_view_path,constant.portfolio_view_path + "-old.csv")
    
    pfview = pd.DataFrame(columns=pfview_cols)
    pfview.to_csv(constant.portfolio_view_path,
               sep = ",",
               quoting = csv.QUOTE_NONNUMERIC,
               quotechar = "\"",
               line_terminator = "\n", 
               index = True,
               header = True
    )
    logging.warning("Erased pfview.csv values and loaded a new header.")



def UpdatePortfolioView():
    portfolio_view = ReadPortfolioView()
    transactions = BankInput.ReadTransactions(constant.transactions_path)
    Update_Portfolio_View_Time(transactions,portfolio_view)

## 

def Update_Portfolio_View_Time(transactions,portfolio_view):
    if (portfolio_view.index.size == 0):
        logging.warning("Found empty Portfolio View")
        lastday = constant.start
    else:
        lastday = portfolio_view.index[-1]
    yesterday = backend.constant.yesterday

    hist = backend.history.Read_History()
    if (hist.index[-1] < yesterday): 
        logging.warning("History is not up to date, cannot update portfolio")
        return 

    
    if (lastday == yesterday):
        logging.info("Portfolio View is up to date.")
    else:
        portfolio_view_update = pd.DataFrame(
        columns=portfolio_view.columns,
        index=pd.date_range(start=lastday, end=yesterday, closed="right")
        )
        logging.info("Updating the days from " + lastday.strftime("%d.%m.%y") + " until " + yesterday.strftime("%d.%m.%y"))
        for date in portfolio_view_update.index:
            
            transactions_to_date =  transactions.loc[constant.start:date]
            portfolio_list_current = portfolio_view.columns.get_level_values(0).unique()
            for pf in portfolio_list_current:
                symbol_list_current = portfolio_view[pf].columns.get_level_values(0).unique()
                for symbol in symbol_list_current:
                    # print(symbol + " " + pf + " " + str(date))
                    transactions_symbol_at_date = transactions_to_date.loc[(transactions_to_date["Portfolio"] == pf) & (transactions_to_date["Symbol"] == symbol)]
                    amount_at_date = transactions_symbol_at_date["Amount"].sum()
                    fees_at_date = transactions_symbol_at_date["Fee"].sum()
                    trans_at_date = transactions_symbol_at_date["Trans"].sum()

                    portfolio_view_update.loc[date,(pf,symbol,"Price")] = hist.loc[date,(symbol,"Close")]
                    portfolio_view_update.loc[date,(pf,symbol,"Transactions")] = trans_at_date
                    portfolio_view_update.loc[date,(pf,symbol,"Holdings")] = amount_at_date
                    portfolio_view_update.loc[date,(pf,symbol,"Value")] = amount_at_date * hist.loc[date,(symbol,"Close")]
                    portfolio_view_update.loc[date,(pf,symbol,"Fees")] = fees_at_date
                    portfolio_view_update.loc[date,(pf,symbol,"Return(tot)")] =  amount_at_date * hist.loc[date,(symbol,"Close")] - trans_at_date  ## Fees are included in Amount / Transaction cost
                    if (trans_at_date == 0):
                        portfolio_view_update.loc[date,(pf,symbol,"Return(rel)")] = 0
                    else:
                        portfolio_view_update.loc[date,(pf,symbol,"Return(rel)")] =  (amount_at_date * hist.loc[date,(symbol,"Close")] - trans_at_date ) / trans_at_date ## Fees are included in Amount / Transaction cost
                    
                    if (amount_at_date == 0):
                        portfolio_view_update.loc[date,(pf,symbol,"XIRR")] = 0
                    else:
                        xirr_list = ((-1)*transactions_symbol_at_date["Trans"]).reset_index().values.tolist()
                        xirr_list.append([date,amount_at_date * hist.loc[date,(symbol,"Close")]])
                        try: 
                            xirr = FinancialFunc.xirr(xirr_list)
                            if (xirr > 1.5):
                                portfolio_view_update.loc[date,(pf,symbol,"XIRR")] = 0
                            else: 
                                portfolio_view_update.loc[date,(pf,symbol,"XIRR")] = xirr
                        except RuntimeError:
                            portfolio_view_update.loc[date,(pf,symbol,"XIRR")] = 0
    
        portfolio_view_new = pd.concat([portfolio_view,portfolio_view_update])
        with open(constant.portfolio_view_path, mode = "w+", newline="\n", encoding="UTF-8") as file:
            portfolio_view_new.to_csv(file,
               sep = ",",
               quoting = csv.QUOTE_NONNUMERIC,
               quotechar = "\"",
               line_terminator = "\n", 
               index = True,
               header = True
            )
