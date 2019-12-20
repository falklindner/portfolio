import pandas as pd 

start = pd.Timestamp(year = 2016, month = 1, day = 15)

xetra = "data/t7-xetr-allTradableInstruments.csv"

dkb_path = "data/"
dkb_pattern = "dkb*.csv"

cd_path  = "data/"
cd_pattern = "ums*.csv"


transactions_path = "data/transactions.csv"
hist_path = "data/hist.csv"
portfolio_view_path = "data/pfview.csv"
dict_path = "data/dict.csv"


datefrmt = lambda x: pd.datetime.strptime(x, "%d.%m.%Y")
pf_property_list = ["Holdings", "Value", "Fees", "RAD", "RADTX", "XIRR"]