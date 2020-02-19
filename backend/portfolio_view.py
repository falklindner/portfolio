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
        pfview = pd.DataFrame(
        columns=pd.MultiIndex.from_tuples(raw.columns[1:], names = raw.columns[0]),
        )

    else: 
        pfview = pd.read_csv(constant.portfolio_view_path, 
        header=[0,1,2], 
        index_col = 0,
        parse_dates = [0]
        )
    return pfview

def BuildNewColumns():
    transactions = BankInput.ReadTransactions()
    pf_list = transactions["Portfolio"].unique()
    properties = constant.pf_property_list
    
    pf_sym_list = []
    
    for pf in pf_list:
        pf_symbols = transactions["Symbol"].loc[transactions["Portfolio"] == pf].unique()
        pf_symbols = np.append(pf_symbols,"SUM_"+pf)
        for symbol in pf_symbols:
            for prop in properties:
                pf_sym_list.append((pf,symbol,prop))
    
    multiindex = pd.MultiIndex.from_tuples(pf_sym_list,names=["Portfolio","Symbol","Properties"])
    return multiindex
    
def Rebuild_PortfolioView():
    
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
    UpdatePortfolioView()



def UpdatePortfolioView():
    pfview = ReadPortfolioView()
    transactions = BankInput.ReadTransactions()
    Update_Portfolio_View_Time(transactions,pfview)

## 

def Update_Portfolio_View_Time(transactions,pfview):
    if (pfview.index.size == 0):
        logging.warning("Found empty Portfolio View")
        old_pf_lastday = constant.start
    else:
        old_pf_lastday = pfview.index[-1]
    
    history = backend.history.Read_History()
    hist_last_day = history.index[-1]
    yesterday= backend.constant.yesterday

    if (hist_last_day < yesterday): 
        logging.warning("History is not up to date, cannot update portfolio until yesterday. Will updated until last day of History.")
        update_end_day = hist_last_day
    else:
        update_end_day = yesterday
    ## Main Update loop    
    if (old_pf_lastday == yesterday):
        logging.info("Portfolio View is up to date.")
    else:
        pfview_update = pd.DataFrame(
        columns=pfview.columns,
        index=pd.date_range(start=old_pf_lastday, end=update_end_day, closed="right")
        )
        logging.info("Updating the days from " + old_pf_lastday.strftime("%d.%m.%y") + " until " + update_end_day.strftime("%d.%m.%y"))
    ## Updating all values in pfview_update
        for date in pfview_update.index:
            for portfolio in pfview.columns.get_level_values(0).unique():
                for symbol in pfview[portfolio].columns.get_level_values(0).unique():
                    if symbol.startswith("SUM_"):
                        pfview_update.update(Portfolio_Property_Array(date,portfolio,history,transactions))
                    else:
                        pfview_update.update(Symbol_Property_Array(history,transactions,date,portfolio,symbol))
    ## Patching together old pfview and pfview update + CSV export
        portfolio_view_new = pd.concat([pfview,pfview_update])
        with open(constant.portfolio_view_path, mode = "w+", newline="\n", encoding="UTF-8") as file:
            portfolio_view_new.to_csv(file,
               sep = ",",
               quoting = csv.QUOTE_NONNUMERIC,
               quotechar = "\"",
               line_terminator = "\n", 
               index = True,
               header = True
            )


def Symbol_Property_Array(history,transactions,date,portfolio,symbol):

    slicer = (transactions["Portfolio"] == portfolio) & (transactions["Symbol"] == symbol)

    holdings = transactions[slicer].loc[constant.start:date,"Amount"].sum()
    price = history.loc[date,(symbol,"Close")]
    value = price * holdings
    turnover = transactions[slicer].loc[constant.start:date,"Trans"].sum()
    fees = transactions[slicer].loc[constant.start:date,"Fee"].sum()
    ret_tot = value - turnover
    ret_per = 0 if np.isnan(ret_tot/turnover)  else ret_tot/turnover
    
    xirr_list=transactions[slicer].loc[constant.start:date,"Trans"].mul(-1).reset_index().values.tolist()
    if len(xirr_list) > 0: 
        xirr_list.append([date,value])
        try: 
            xirr_return = FinancialFunc.xirr(xirr_list)
            if (xirr_return > 1.5):
                logging.warning("XIRR computed value > 1.5 at  " + date.strftime("%d.%m.%y") + " for " + portfolio + "/" + symbol)
                xirr = 0
            else: 
                xirr = xirr_return
        except RuntimeError:
            logging.warning("XIRR encountered Runtime Error at " + date.strftime("%d.%m.%y") + " for " + portfolio + "/" + symbol)
            xirr = 0
    else: 
        xirr = 0
    iterables = [[portfolio], [symbol], constant.pf_property_list]
    return_frame = pd.DataFrame(
        index = [date],
        columns = pd.MultiIndex.from_product(iterables,names=["Portfolio","Symbol","Properties"]),
        data = np.array([[holdings],[price],[value],[turnover],[fees],[ret_tot],[ret_per],[xirr]]).T
    )
    return return_frame


def Portfolio_Property_Array(date,portfolio,history,transactions):
    slicer = (transactions["Portfolio"] == portfolio)
    symbols = transactions[slicer]["Symbol"].unique()

    value = sum([history.loc[date,(symbol,"Close")] *  transactions[slicer & (transactions["Symbol"] == symbol)].loc[constant.start:date,"Amount"].sum() for symbol in symbols])
    turnover = transactions[slicer].loc[constant.start:date,"Trans"].sum()
    fees = transactions[slicer].loc[constant.start:date,"Fee"].sum()
    ret_tot = value - turnover
    ret_per = 0 if np.isnan(ret_tot/turnover)  else ret_tot/turnover
    
    xirr_list=transactions[slicer].loc[constant.start:date,"Trans"].mul(-1).reset_index().values.tolist()
    if len(xirr_list) > 0: 
        xirr_list.append([date,value])
        try: 
            xirr_return = FinancialFunc.xirr(xirr_list)
            if (xirr_return > 1.5):
                logging.warning("XIRR computed value > 1.5 at  " + date.strftime("%d.%m.%y") + " for " + portfolio )
                xirr = 0
            else: 
                xirr = xirr_return
        except RuntimeError:
            logging.warning("XIRR encountered Runtime Error at " + date.strftime("%d.%m.%y") + " for " + portfolio )
            xirr = 0
    else: 
        xirr = 0
    iterables = [[portfolio],["SUM_"+portfolio], ["Value", "Turnover", "Fees", "Return(tot)", "Return(rel)", "XIRR"]]
    return_frame = pd.DataFrame(
        index = [date],
        columns = pd.MultiIndex.from_product(iterables,names=["Portfolio","Symbol","Properties"]),
        data = np.array([[value],[turnover],[fees],[ret_tot],[ret_per],[xirr]]).T
    )
    return return_frame




# date = pd.Timestamp("2020-02-02")
# pfview = ReadPortfolioView()
# portfolio = "Altersvorsorge"
# history = backend.history.Read_History()
# transactions = backend.bank_input.ReadTransactions()

# pfview
# pd.concat([pfview,return_frame], axis=1)["Altersvorsorge"].columns
# pfview["Altersvorsorge"].columns.get_level_values(0).unique()
# pfview.loc[date]["Altersvorsorge"]
# pfview_update.update(return_frame)
# pfview.loc[:,("Altersvorsorge",slice(None),slice(None))].update(return_frame)

# index = pd.DataFrame(columns=index)
# for portfolio in index.columns.get_level_values(0).unique():
#     for symbol in index[portfolio].columns.get_level_values(0).unique():
#         if symbol.startswith("SUM_"):
#             print(symbol + " is a sum")
#         #pfview.loc[:,("Altersvorsorge",slice(None),slice(None))].update(return_frame)
#         else:
#         #pfview_update.update(Symbol_Property_Array(history,transactions, date,portfolio,symbol))
#             print(symbol + " is a symbol")