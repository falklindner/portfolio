import logging

import backend.bank_input
import pandas as pd
from dateutil.relativedelta import relativedelta


def df_comdirect():
    
    # Take only "Altersvorsorge" data, which is Comdirect
    transactions = backend.bank_input.ReadTransactions()
    
    cd_view = pd.DataFrame(
        index = transactions.loc[transactions["Portfolio"] == "Altersvorsorge"].unique()
    )

    lastday = pfview.index[-1]
    six_mon_ago = lastday-relativedelta(months=6)

    cd_view["Stück"] = pfview.loc[lastday:,("Altersvorsorge",slice(None),"Holdings")].values.flatten().transpose()
    cd_view["Wert"] = pfview.loc[lastday:,("Altersvorsorge",slice(None),"Value")].values.flatten().transpose()
    cd_view["Kaufwert"] = pfview.loc[lastday:,("Altersvorsorge",slice(None),"Transactions")].values.flatten().transpose() - pfview.loc[lastday:,("Altersvorsorge",slice(None),"Fees")].values.flatten().transpose()
    cd_view["Diff"]  = cd_view["Wert"] - cd_view["Kaufwert"]
    cd_view["Diff(%)"] = (cd_view["Wert"] - cd_view["Kaufwert"])/cd_view["Kaufwert"]*100
    cd_view["6Mon(%)"] = 100*((pfview.loc[lastday,("Altersvorsorge",slice(None),"Price")]/pfview.loc[six_mon_ago,("Altersvorsorge",slice(None),"Price")]).values.flatten().transpose()-1)
    cd_view["XIRR"] = 100*pfview.loc[lastday:,("Altersvorsorge",slice(None),"XIRR")].values.flatten().transpose()
    cd_view.sort_values(by=["Stück"],inplace=True, ascending=False)

    return cd_view


