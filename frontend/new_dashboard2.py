import backend.bank_input as BankInput
import backend.portfolio_view as portfolio_view

pfview = portfolio_view.ReadPortfolioView()
lastday = pfview.index[-1]

transactions = BankInput.ReadTransactions()

xirr_list = ((-1)*transactions["Trans"].loc[(transactions["Symbol"] == "LYPG.DE") & (transactions["Portfolio"] == "Altersvorsorge")])
xirr_list[lastday] = pfview[("Altersvorsorge","LYPG.DE","Value")].loc[lastday]
xirr_list.to_csv("data/x010_xirr.csv", sep=";", decimal=",")


pfview.loc[:,("Rücklage","Total", "Value")] = pfview.loc[:,("Rücklage", slice(None),"Value")].sum(axis=1)

pfview.loc[:,("Rücklage", slice(None),"Value")]