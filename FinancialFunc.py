import constant
import BankInput
import History

def SymbolProperties(date,pf,sym):
    hist = History.Read_History()
    transactions = BankInput.ReadTransactions(constant.transactions_path)


    Holdings = transactions["Amount"].loc[(transactions["Portfolio"] == pf) & ( transactions["Symbol"] == sym)].loc[constant.start:date].sum()
    Value = Holdings * hist.loc[date,sym]
    return [Holdings,Value]