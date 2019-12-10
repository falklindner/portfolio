import BankInput
import PortfolioView
import constant
import History

## Paths and default settings 



## CSV Import of account transactions

input_dkb = BankInput.DfFromDKB(constant.dkb_path)
input_cd = BankInput.DfFromComdirect(constant.cd_path)

## Updating the main transaction repository (transactions_path)

BankInput.UpdateTransactions(input_dkb,constant.transactions_path)
BankInput.UpdateTransactions(input_cd,constant.transactions_path)

History.Update_History()

PortfolioView.UpdatePortfolioView()



# date = portfolio_view.index[1000]
# pf = portfolio_list[0]
# symbol =  portfolio["Symbol"].loc[portfolio["Portfolio"] == pf].unique()[0]
# pf_at_date = portfolio.set_index("Execute").loc[constant.start:date]
# pf_symbol_at_date = pf_at_date.loc[(pf_at_date["Portfolio"] == pf) & (pf_at_date["Symbol"] == symbol)]
# amount_at_date = pf_symbol_at_date["Amount"].sum()
# fees_at_date = pf_symbol_at_date["Fee"].sum()
# trans_at_date = pf_symbol_at_date["Trans"].sum()



# pf_symbol_at_date[["Trans"]].to_records(index_dtypes = "datetime.date" )

# xirr_list = ((-1)*pf_symbol_at_date["Trans"]).tolist()
# xirr_list.append(amount_at_date * hist.loc[date,symbol])
# xirr_list

# financial.xirr()






# portfolio_view


# portfolio_view.to_csv(portfolio_view_path)


# portfolio_view.loc['2019-01-01':yesterday].index

# first = portfolio_view["Airbus","AIR.PA","Holdings"].ne(0).idxmax()

# plt.plot(portfolio_view.loc[first:yesterday].index,portfolio_view.loc[first:yesterday]["Airbus","AIR.PA","Value"])
# plt.show()