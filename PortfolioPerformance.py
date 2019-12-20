import pandas as pd
import datetime
import csv
import BankInput
import constant


def PortfolioToPP (input_path,output_path):
    input_portfolio = BankInput.ReadTransactions(input_path)
    
    pp_headers = [
        'Symbol', 
        'Name', 
        'DisplaySymbol', 
        'Exchange', 
        'Portfolio', 
        'Currency', 
        'Quantity', 
        'Cost Per Share', 
        'Cost Basis Method', 
        'Commission', 
        'Date', 
        'PurchaseFX', 
        'Source', 
        'Type', 
        'Notes']


    csv_raw = pd.DataFrame(columns=pp_headers).to_csv(
        sep = ",",
        line_terminator = "\n", 
        index = False,
        header = True)

    for portfolio in input_portfolio["Portfolio"].unique():
        portfolio_symbols = input_portfolio["Symbol"].loc[input_portfolio["Portfolio"] == portfolio].unique()
        for symbol in  portfolio_symbols:
            data_basis = input_portfolio.loc[(input_portfolio["Portfolio"] == portfolio) & (input_portfolio["Symbol"] == symbol)]
            symbol_name = input_portfolio["Name"].loc[input_portfolio["Symbol"] == symbol].values[0]
            top_row_data = {
                "Symbol":symbol, 
                "Name":symbol_name,
                "Portfolio":portfolio,
                "Currency":data_basis["Currency"].unique(),
                "Source":"1"
            }
            
            symbol_frame = pd.DataFrame(top_row_data, columns=pp_headers)
            transaction_data = {
                "Symbol":symbol,
                "Name":symbol_name,
                "Portfolio":portfolio,
                "Currency":data_basis["Currency"],
                "Quantity":data_basis["Amount"],
                "Cost Per Share":data_basis["Price"],
                "Cost Basis Method":0,
                "Commission":data_basis["Fee"],
                "Date":data_basis.index.map(datetime.date.isoformat) + " GMT+01:00",
                "Source":1,
                "Type":"Buy"
            }
            
            transaction_frame = pd.DataFrame(transaction_data, columns=pp_headers)

            symbol_frame = symbol_frame.append(transaction_frame, ignore_index=True)
            csv_raw += symbol_frame.to_csv(
                sep = ",",
                quoting = csv.QUOTE_NONNUMERIC,
                quotechar = "\"",
                line_terminator = "\n", 
                index = False,
                header = False
            )
            
            csv_raw += "\n"

    with open(output_path, mode = "w+", newline="\n", encoding="UTF-8") as file:
        file.write(csv_raw)
