import yfinance as yf
import pandas as pd
import constant


def Read_History():
    hist = pd.read_csv(constant.hist_path,
    index_col=0,
    parse_dates = [0],
    header = 0,
    skiprows = 0
    )
    return hist

## Construct data frame with historical values of all symbols in portfolio

def Update_History():
    hist = Read_History()
    lastday = hist.index[-1]
    yesterday = (pd.Timestamp.today() - pd.DateOffset(1)).replace(hour=0, minute=0, second=0,microsecond =0)
    if (lastday == yesterday):
        print("History is up to date.")
    else:
        hist_update = pd.DataFrame(
        columns=hist.columns,
        index=pd.date_range(start=lastday, end=yesterday, closed="right")
        )
        print("Updating the following days in History: "+ str(hist_update.index.strftime("%d.%m").values))
        for symbol in hist_update.columns:
            hist_update[symbol] = yf.Ticker(symbol).history(start = lastday, end = yesterday).Close

        hist_new = hist.append(hist_update).fillna(method="ffill")
        hist_new.to_csv(constant.hist_path)

## Saving historical values to hist_path 