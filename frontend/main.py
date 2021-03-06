import BankInput
import PortfolioView
import constant
import History
import matplotlib as plt
import PortfolioPerformance
import FinancialFunc

## Paths and default settings 



## CSV Import of account transactions

input_dkb = BankInput.DfFromDKB(constant.dkb_path)
input_cd = BankInput.DfFromComdirect(constant.cd_path)


## Updating the main transaction repository (transactions_path)

BankInput.UpdateTransactions(input_dkb,constant.transactions_path)
BankInput.UpdateTransactions(input_cd,constant.transactions_path)
#BankInput.LoadTransactions()

History.Update_History()
PortfolioView.UpdatePortfolioView()



transactions = BankInput.ReadTransactions()
portfolio_view = PortfolioView.ReadPortfolioView()

transactions.loc[transactions["Symbol"] == "AIR.PA"]
portfolio_view.loc[:,("Airbus","AIR.PA","XIRR")]


PortfolioPerformance.PortfolioToPP("data/export.csv")





transactions.loc["Amount"].sum()
# pf_symbol_at_date[["Trans"]].to_records(index_dtypes = "datetime.date" )

# xirr_list = ((-1)*pf_symbol_at_date["Trans"]).tolist()
# xirr_list.append(amount_at_date * hist.loc[date,symbol])
# xirr_list

# financial.xirr()




# portfolio_view.to_csv(portfolio_view_path)


# portfolio_view.loc['2019-01-01':yesterday].index

# first = portfolio_view["Airbus","AIR.PA","Holdings"].ne(0).idxmax()

#plt.plot(portfolio_view.loc[constant.start:yesterday].index,portfolio_view.loc[first:yesterday]["Airbus","AIR.PA","Value"])
# plt.show()