import logging

import backend.bank_input
import backend.portfolio_view
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta


def df_comdirect():
    
    # Take only "Altersvorsorge" data, which is Comdirect
    transactions = backend.bank_input.ReadTransactions()
    pfview = backend.portfolio_view.ReadPortfolioView()
    
    cd_view = pd.DataFrame(
        index = transactions["Symbol"].loc[transactions["Portfolio"] == "Altersvorsorge"].unique()
    )

    lastday = pfview.index[-1]
    six_mon_ago = lastday-relativedelta(months=6)
    symbol_slicer = np.invert(pfview.columns.get_level_values(1).str.contains("SUM"))

    cd_view["Stück"] = pfview.loc[lastday:,("Altersvorsorge",symbol_slicer,"Holdings")].values.flatten().transpose()
    cd_view["Wert"] = pfview.loc[lastday:,("Altersvorsorge",symbol_slicer,"Value")].values.flatten().transpose()
    cd_view["Kaufwert"] = pfview.loc[lastday:,("Altersvorsorge",symbol_slicer,"Turnover")].values.flatten().transpose() - pfview.loc[lastday:,("Altersvorsorge",symbol_slicer,"Fees")].values.flatten().transpose()
    cd_view["Diff"]  = cd_view["Wert"] - cd_view["Kaufwert"]
    cd_view["Diff(%)"] = 100*(cd_view["Wert"] - cd_view["Kaufwert"])/cd_view["Kaufwert"]
    cd_view["6Mon(%)"] = 100*((pfview.loc[lastday,("Altersvorsorge",symbol_slicer,"Price")]/pfview.loc[six_mon_ago,("Altersvorsorge",symbol_slicer,"Price")]).values.flatten().transpose()-1)
    cd_view["XIRR"] = 100*pfview.loc[lastday:,("Altersvorsorge",symbol_slicer,"XIRR")].values.flatten().transpose()
    cd_view.sort_values(by=["Stück"],inplace=True, ascending=False)

    return cd_view

def df_portfolio():
    transactions = backend.bank_input.ReadTransactions()
    pfview = backend.portfolio_view.ReadPortfolioView()
    lastday = pfview.index[-1]
    six_mon_ago = lastday-relativedelta(months=6)
    sum_slicer = pfview.columns.get_level_values(1).str.contains("SUM")

    df = pd.DataFrame(index = transactions["Portfolio"].unique())
    
    df["Wert"] = pfview.loc[lastday:,(slice(None),sum_slicer,"Value")].values.flatten().transpose()
    df["Kaufwert"] = pfview.loc[lastday:,(slice(None),sum_slicer,"Turnover")].values.flatten().transpose() - pfview.loc[lastday:,(slice(None),sum_slicer,"Fees")].values.flatten().transpose()
    df["Diff"] = pfview.loc[lastday:,(slice(None),sum_slicer,"Return(tot)")].values.flatten().transpose()
    df["Diff(%)"] = 100*pfview.loc[lastday:,(slice(None),sum_slicer,"Return(rel)")].values.flatten().transpose()
    df["6Mon(%)"] = 100*((pfview.loc[lastday,(slice(None),sum_slicer,"Value")]/pfview.loc[six_mon_ago,(slice(None),sum_slicer,"Value")]).values.flatten().transpose()-1)
    df["XIRR"] = 100*pfview.loc[lastday:,(slice(None),sum_slicer,"XIRR")].values.flatten().transpose()

    return df

def xirr_timeseries():
    transactions = backend.bank_input.ReadTransactions()
    pfview = backend.portfolio_view.ReadPortfolioView()
    sum_slicer = pfview.columns.get_level_values(1).str.contains("SUM")
    df = pfview.loc[:,(slice(None),sum_slicer,"XIRR")]
    newcols = pfview.loc[:,(slice(None),sum_slicer,"XIRR")].columns.droplevel(level=1).droplevel(level=1)
    df.columns = newcols
    
    return df

def returns_timeseries():
    transactions = backend.bank_input.ReadTransactions()
    pfview = backend.portfolio_view.ReadPortfolioView()
    sum_slicer = pfview.columns.get_level_values(1).str.contains("SUM")
    df = pfview.loc[:,(slice(None),sum_slicer,"Return(rel)")]
    newcols = pfview.loc[:,(slice(None),sum_slicer,"Return(rel)")].columns.droplevel(level=1).droplevel(level=1)
    df.columns = newcols
    
    return df