import pandas as pd
import numpy as np
import BankInput
import constant
import History
import csv


## Checking if an update of Portfolio View is necessary (due to being to old or having new indices)

def UpdatePortfolioView():
    portfolio_view = pd.read_csv(constant.portfolio_view_path, 
        header=[0,1,2], 
        index_col = 0,
        parse_dates = [0]
    )

## Checking if new Portfolios / Symbols (WIP)
    portfolio_list_current = portfolio_view.columns.get_level_values(0).unique()
    symbol_list_current = portfolio_view.columns.get_level_values(1).unique()
    property_list_current = portfolio_view.columns.get_level_values(2).unique()

    transactions = BankInput.ReadTransactions(constant.transactions_path)
    portfolio_list_actual = transactions["Portfolio"].unique()
    symbol_list_actual = transactions["Symbol"].unique()

## Checking if outdated
    Update_Portfolio_View_Time(transactions,portfolio_view)

## 

def Update_Portfolio_View_Time(transactions,portfolio_view):
    lastday = portfolio_view.index[-1]
    yesterday = (pd.Timestamp.today() - pd.DateOffset(1)).replace(hour=0, minute=0, second=0,microsecond =0)
    hist = History.Read_History()
    if (lastday == yesterday):
        print("Portfolio View is up to date.")
    else:
        portfolio_view_update = pd.DataFrame(
        columns=portfolio_view.columns,
        index=pd.date_range(start=lastday, end=yesterday, closed="right")
        )
        print("Updating the following days in Portfolio View: "+ portfolio_view_update.index.strftime("%d.%m").values)
        for date in portfolio_view_update.index:
            transactions_to_date =  transactions.loc[constant.start:yesterday]
            portfolio_list_current = portfolio_view.columns.get_level_values(0).unique()
            for pf in portfolio_list_current:
                symbol_list_current = portfolio_view[pf].columns.get_level_values(0).unique()
                for symbol in symbol_list_current:
                    print(symbol + " " + pf + " " + str(date))
                    transactions_symbol_at_date = transactions_to_date.loc[(transactions_to_date["Portfolio"] == pf) & (transactions_to_date["Symbol"] == symbol)]
                    amount_at_date = transactions_symbol_at_date["Amount"].sum()
                    fees_at_date = transactions_symbol_at_date["Fee"].sum()
                    trans_at_date = transactions_symbol_at_date["Trans"].sum()

                    irr_list = ((-1)*transactions_symbol_at_date["Trans"]).tolist()
                    irr_list.append(amount_at_date * hist.loc[date,symbol])
                

                    portfolio_view_update.loc[date,(pf,symbol,"Holdings")] = amount_at_date
                    portfolio_view_update.loc[date,(pf,symbol,"Value")] = amount_at_date * hist.loc[date,symbol]
                    portfolio_view_update.loc[date,(pf,symbol,"Fees")] = fees_at_date
                    portfolio_view_update.loc[date,(pf,symbol,"RAD")] =  (amount_at_date * hist.loc[date,symbol]) / trans_at_date ## Fees are included in Amount / Transaction cost
                    portfolio_view_update.loc[date,(pf,symbol,"RADTX")] =  (0.75 * amount_at_date * hist.loc[date,symbol]) / trans_at_date ## Return with 25% stock rerturns tax
                    portfolio_view_update.loc[date,(pf,symbol,"XIRR")] = np.irr(irr_list)
    
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
        
        






# # Creating a multiindex-column for portfolio view
# portfolio_list = transactions["Portfolio"].unique()

# property_list = constant.pf_property_list

# multi_index_data = []
# for pf in portfolio_list:
#     for symbol in transactions["Symbol"].loc[transactions["Portfolio"] == pf].unique():
#         for prop in property_list:
#             multi_index_data += [[pf,symbol,prop]]

# cols = pd.MultiIndex.from_tuples(multi_index_data, names=["Portfolio", "Symbol", "Properties"])
# cols
# # Creating empty portfolio view data frame -- obsolete
# portfolio_view = pd.DataFrame(
#     columns=cols,
#     index=pd.date_range(start=constant.start, end=yesterday)
# )

# with open(constant.portfolio_view_path, mode = "w+", newline="\n", encoding="UTF-8") as file:
#         portfolio_view.to_csv(file,
#                sep = ",",
#                quoting = csv.QUOTE_NONNUMERIC,
#                quotechar = "\"",
#                line_terminator = "\n", 
#                index = True,
#                header = True
#             )
# ## Rearranging transactions to Portfolio/Stocks vs. time view


