import pandas as pd 
import datetime

start = pd.Timestamp(year = 2016, month = 1, day = 18)
yesterday = (pd.Timestamp.today() - pd.DateOffset(1)).replace(hour=23, minute=0, second=0,microsecond =0)
today_market_close = pd.Timestamp.today().replace(hour=22, minute=0, second=0,microsecond =0)

xetra = "data/t7-xetr-allTradableInstruments.csv"

dict_path = "data/dict.csv"

dkb_path = "data/inputs/"
dkb_pattern = "dkb*.csv"
cd_path  = "data/inputs/"
cd_pattern = "ums*.csv"

transactions_path = "data/transactions.csv"


hist_path = "data/newhist.csv"
portfolio_view_path = "data/pfview.csv"


datefrmt = lambda x: datetime.datetime.strptime(x, "%d.%m.%Y")
pf_property_list = ["Holdings", "Price", "Value", "Turnover", "Fees", "Return(tot)", "Return(rel)", "XIRR"]