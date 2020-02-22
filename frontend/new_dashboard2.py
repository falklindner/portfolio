import logging 

import backend.bank_input as BankInput
import backend.portfolio_view as portfolio_view
import backend.history as history
import pandas as pd

import dash_html_components as html
import plotly.graph_objects as go
import dash_core_components as dcc

import matplotlib.pyplot as plt

def generate_symbol_analysis():
        hist = history.Read_History()
        symbol_list = hist.columns.get_level_values(0).unique()
        analysis_cols = ["Signal","MACD"]
        update_df = pd.DataFrame(index = hist.index, columns=pd.MultiIndex.from_product([hist.columns.levels[0],analysis_cols]))
        def ewm(dataframe, days):
            return dataframe.ewm(span=days,adjust = False).mean()
        
        update_df.loc[:,("AIR.PA","MACD")].update(ewm(hist.loc[:,("AIR.PA","Close")],12)-ewm(hist.loc[:,("AIR.PA","Close")],26))
        update_df.loc[:,("AIR.PA","Signal")].update(ewm(update_df.loc[:,("AIR.PA","MACD")],9))
        

        plt.plot(update_df.index, update_df.loc[:,("AIR.PA","MACD")], label="MACD", color = "black" )
        plt.plot(update_df.index, update_df.loc[:,("AIR.PA","Signal")], label="Signal", color = "red")
        plt.bar(update_df.index,update_df.loc[:,("AIR.PA","MACD")]-update_df.loc[:,("AIR.PA","Signal")], label="Histogram", color ="blue")
        
        plt.plot(hist.index, hist.loc[:,("AIR.PA","Close")])
        plt.axhline(linewidth=1, color='r')
        plt.axvline(x=pd.Timestamp("2019-11-17"),ymin=0,ymax=120)
        plt.legend(loc='upper left')
        plt.show()
        df = pd.DataFrame(index =hist.index)
        table = html.Table(
        # Header
        [html.Tr(
            [html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
        ) 
    
    
        tab2_content = html.Div(children=[
            html.H4(children='Stock Analysis'),
            generate_table(cd_view.round(2))
            ],
            style={'width': '100%', 'display': 'inline-block','margin-left': 10})








pfview = portfolio_view.ReadPortfolioView()
lastday = pfview.index[-1]

transactions = BankInput.ReadTransactions()

xirr_list = ((-1)*transactions["Trans"].loc[(transactions["Symbol"] == "LYPG.DE") & (transactions["Portfolio"] == "Altersvorsorge")])
xirr_list[lastday] = pfview[("Altersvorsorge","LYPG.DE","Value")].loc[lastday]
xirr_list.to_csv("data/x010_xirr.csv", sep=";", decimal=",")


pfview.loc[:,("Rücklage","Total", "Value")] = pfview.loc[:,("Rücklage", slice(None),"Value")].sum(axis=1)

pfview.loc[:,("Rücklage", slice(None),"Value")]