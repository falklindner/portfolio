import logging 

import backend.bank_input as BankInput
import backend.portfolio_view as portfolio_view
import backend.history as history
import pandas as pd

import dash_html_components as html
import plotly.graph_objects as go
import dash_core_components as dcc

import matplotlib.pyplot as plt



def generate_macd_analysis(no_one,no_two,no_three):
        hist = history.Read_History()
        symbol_list = hist.columns.get_level_values(0).unique()
        analysis_cols = ["MACD", "MACD Signal","MACD Hist"]
        update_df = pd.DataFrame(index = hist.index, columns=pd.MultiIndex.from_product([hist.columns.levels[0],analysis_cols]))
        def ewm(dataframe, days):
            return dataframe.ewm(span=days,adjust = False).mean()
        
        update_df.loc[:,("AIR.PA","MACD")].update(ewm(hist.loc[:,("AIR.PA","Close")],no_one)-ewm(hist.loc[:,("AIR.PA","Close")],no_two))
        update_df.loc[:,("AIR.PA","MACD Signal")].update(ewm(update_df.loc[:,("AIR.PA","MACD")],no_three))
        

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



def get_table_layout():
        return dict(
        height = 800,
        yaxis=dict(
        range = [0,0.6]
        ),
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                        label='1m',
                        step='month',
                        stepmode='backward'),
                    dict(count=6,
                        label='6m',
                        step='month',
                        stepmode='backward'),
                    dict(count=1,
                        label='YTD',
                        step='year',
                        stepmode='todate'),
                    dict(count=1,
                        label='1y',
                        step='year',
                        stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible = True
            ),
            type='date'
        )
    )
