import backend.bank_input as BankInput
from backend.portfolio_view import UpdatePortfolioView, ReadPortfolioView
import backend.constant as constant
import backend.history as History
import pandas as pd



## Paths and default settings 



## CSV Import of account transactions

input_dkb = BankInput.DfFromDKB(constant.dkb_path)
input_cd = BankInput.DfFromComdirect(constant.cd_path)



## Updating the main transaction repository (transactions_path)

BankInput.UpdateTransactions(input_dkb,constant.transactions_path)
BankInput.UpdateTransactions(input_cd,constant.transactions_path)
#BankInput.LoadTransactions()


UpdatePortfolioView()



transactions = BankInput.ReadTransactions(constant.transactions_path)
portfolio_view = ReadPortfolioView()


lastday = portfolio_view.index[-1]
cd_index = portfolio_view["Altersvorsorge"].columns.get_level_values(0).unique()
cd_view = pd.DataFrame(
    index = cd_index,
    columns = ["Holdings", "Value", "Returns", "Return(%)", "XIRR"]
)

transactions["Amount"].loc[(transactions["Portfolio"] == "Altersvorsorge") & (transactions["Symbol"] == "LYYA.DE")].sum()
portfolio_view.loc[:,("Altersvorsorge","LYYA.DE","Holdings")].tail(50)

cd_view["Holdings"] = portfolio_view.loc[lastday:,("Altersvorsorge",slice(None),"Holdings")].values.flatten().transpose()
cd_view["Value"] = portfolio_view.loc[lastday:,("Altersvorsorge",slice(None),"Value")].values.flatten().transpose().round(0)
cd_view["Returns"] = portfolio_view.loc[lastday:,("Altersvorsorge",slice(None),"Return(tot)")].values.flatten().transpose().round(0)
cd_view["Return(%)"] = portfolio_view.loc[lastday:,("Altersvorsorge",slice(None),"Return(rel)")].values.flatten().transpose().round(2)
cd_view["XIRR"] = portfolio_view.loc[lastday:,("Altersvorsorge",slice(None),"XIRR")].values.flatten().transpose().round(2)
