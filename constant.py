import pandas as pd 

start = pd.Timestamp(year = 2016, month = 1, day = 15)

xetra = "data/t7-xetr-allTradableInstruments.csv"

dkb_path = "data/dkb_sg.csv"
cd_path  = "data/umsaetze_9774844981_20191118-2138.csv"

transactions_path = "data/transactions.csv"
hist_path = "data/Hist.csv"
portfolio_view_path = "data/pfview.csv"
dict_path = "data/dict.csv"


datefrmt = lambda x: pd.datetime.strptime(x, "%d.%m.%Y")
pf_property_list = ["Holdings", "Value", "Fees", "RAD", "RADTX", "XIRR"]