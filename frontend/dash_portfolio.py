import logging

import backend.bank_input
import backend.portfolio_view
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

import dash_html_components as html
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_table
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol

def generate_pf_content():
    day,pf_sym_view = df_pf_symbol()
    pf_sym_view.reset_index(inplace=True)
    xirr_timeseries = get_xirr_timeseries()
    return_timeseries = get_returns_timeseries()

    xirr_traces = []
    for column in xirr_timeseries.columns:
        xirr_traces.append(
                go.Scatter(
                x = xirr_timeseries.index, 
                y = xirr_timeseries[column],
                name = column
                )
        )
    xirr_data = xirr_traces

    return_traces = []
    for column in return_timeseries.columns:
        return_traces.append(
                go.Scatter(
                x = return_timeseries.index, 
                y = return_timeseries[column],
                name = column
                )
        )
    return_data = return_traces

    xirr_fig = go.Figure(data=xirr_data, layout=get_table_layout())
    return_fig = go.Figure(data=return_data, layout=get_table_layout())

    tab1_content = html.Div(children=[
            html.H1(children=["Portfolio Data from "+day.strftime("%d.%m.%y")],style={'textAlign': 'center'}),
            html.Div(style={'width': '75%', 'margin' : 'auto'}, children=[
                dash_table.DataTable(
                id='table',
                columns = [{
                    'id'   : "Portfolio",
                    'name' : "Portfolio",
                    'type' : "text"
                },{
                    'id'   : "Symbol",
                    'name' : "Symbol",
                    'type' : "text"
                },{
                    'id'   : "Holdings",
                    'name' : "Holdings",
                    'type' : "numeric"    
                },{
                    'id'   : "Price",
                    'name' : "Price",
                    'type' : "numeric",              
                    'format': euro(2)
                },{
                    'id'   : "Value",
                    'name' : "Value",
                    'type' : "numeric",              
                    'format': euro(2)
                },{
                    'id'   : "Turnover",
                    'name' : "Turnover",
                    'type' : "numeric",              
                    'format': euro(2)
                },{
                    'id'   : "Fees",
                    'name' : "Fees",
                    'type' : "numeric",              
                    'format': euro(2)
                },{
                    'id'   : "Return(tot)",
                    'name' : "Return(tot)",
                    'type' : "numeric",
                    'format' : euro(2)
                },{
                    'id'   : "Return(rel)",
                    'name' : "Return(rel)",
                    'type' : "numeric",
                    'format' :  FormatTemplate.percentage(1)
                },{
                    'id'   : "XIRR",
                    'name' : "XIRR",
                    'type' : "numeric",              
                    'format': FormatTemplate.percentage(1)
                },

                ],
                data = pf_sym_view.round(2).to_dict("records"),
                style_as_list_view=True,
                style_cell={"textAlign":'right', "padding":'5px', 'fontSize':14, 'font-family':'sans-serif' },
                style_header={
                    'backgroundColor': 'darkgrey', 'fontWeight': 'bold', 'color' : 'white'
                }, 
                style_cell_conditional=[{
                        'if': {'column_id': header },
                        'textAlign': 'left',  'width' : '50px'
                    } for header in ["Portfolio", "Symbol"]
                    ] + [
                    {
                        'if': {'column_id': data_header },
                        'textAlign': 'right', 'width' : '20px'
                    } for data_header  in pf_sym_view.columns.drop(["Portfolio","Symbol"])
                    ],
                style_data_conditional=[{
                        'if': { 'filter_query' : '{Symbol} = ""'},
                        'backgroundColor': 'lightgrey', 'fontWeight' : 'bold'
                    }
                    ],
                )]
            ),
            html.H4(children="Time Series"),
            html.H5(children="XIRR Chart"),
            dcc.Graph(figure=xirr_fig),
            html.H5(children="Total Returns Chart"),
            dcc.Graph(figure=return_fig)
    ])
    return tab1_content

def euro(prec):
    return Format(precision=prec,scheme=Scheme.fixed, symbol=Symbol.yes, symbol_suffix=" €")

def df_pf_symbol():
    pfview = backend.portfolio_view.ReadPortfolioView()
    lastday = pfview.index[-1]
    df = pfview.loc[lastday].unstack(level=2).reset_index()
    df["Symbol"] = df.loc[:,"Symbol"].str.replace("^SUM_.*","",regex=True)
    df = df.sort_values(by=["Portfolio","Symbol"]).set_index(["Portfolio","Symbol"])
    return lastday, df


def df_comdirect():
    
    # Take only "Altersvorsorge" data, which is Comdirect
    transactions = backend.bank_input.ReadTransactions()
    pfview = backend.portfolio_view.ReadPortfolioView()
    
    cd_view = pd.DataFrame(
        index = transactions["Symbol"].loc[transactions["Portfolio"] == "Altersvorsorge"].unique()
    )

    lastday = pfview.index[-1]
    six_mon_ago = lastday-relativedelta(months=6)
    symbol_slicer = np.invert(pfview.columns.get_level_values(1).str.contains("SUM"))

    cd_view["Stück"] = pfview.loc[lastday:,("Altersvorsorge",symbol_slicer,"Holdings")].values.flatten().transpose()
    cd_view["Akt.Kurs"] = pfview.loc[lastday:,("Altersvorsorge",symbol_slicer,"Price")].values.flatten().transpose()
    cd_view["Wert"] = pfview.loc[lastday:,("Altersvorsorge",symbol_slicer,"Value")].values.flatten().transpose()
    cd_view["Kaufwert"] = pfview.loc[lastday:,("Altersvorsorge",symbol_slicer,"Turnover")].values.flatten().transpose() - pfview.loc[lastday:,("Altersvorsorge",symbol_slicer,"Fees")].values.flatten().transpose()
    cd_view["Diff"]  = cd_view["Wert"] - cd_view["Kaufwert"]
    cd_view["Diff(%)"] = 100*(cd_view["Wert"] - cd_view["Kaufwert"])/cd_view["Kaufwert"]
    cd_view["6Mon(%)"] = 100*((pfview.loc[lastday,("Altersvorsorge",symbol_slicer,"Price")]/pfview.loc[six_mon_ago,("Altersvorsorge",symbol_slicer,"Price")]).values.flatten().transpose()-1)
    cd_view["XIRR"] = 100*pfview.loc[lastday:,("Altersvorsorge",symbol_slicer,"XIRR")].values.flatten().transpose()
    cd_view.sort_values(by=["Stück"],inplace=True, ascending=False)

    return cd_view

def df_portfolio():
    transactions = backend.bank_input.ReadTransactions()
    pfview = backend.portfolio_view.ReadPortfolioView()
    lastday = pfview.index[-1]
    six_mon_ago = lastday-relativedelta(months=6)
    sum_slicer = pfview.columns.get_level_values(1).str.contains("SUM")

    df = pd.DataFrame(index = transactions["Portfolio"].unique())
    
    df["Wert"] = pfview.loc[lastday:,(slice(None),sum_slicer,"Value")].values.flatten().transpose()
    df["Kaufwert"] = pfview.loc[lastday:,(slice(None),sum_slicer,"Turnover")].values.flatten().transpose() - pfview.loc[lastday:,(slice(None),sum_slicer,"Fees")].values.flatten().transpose()
    df["Diff"] = pfview.loc[lastday:,(slice(None),sum_slicer,"Return(tot)")].values.flatten().transpose()
    df["Diff(%)"] = 100*pfview.loc[lastday:,(slice(None),sum_slicer,"Return(rel)")].values.flatten().transpose()
    df["6Mon(%)"] = 100*((pfview.loc[lastday,(slice(None),sum_slicer,"Value")]/pfview.loc[six_mon_ago,(slice(None),sum_slicer,"Value")]).values.flatten().transpose()-1)
    df["XIRR"] = 100*pfview.loc[lastday:,(slice(None),sum_slicer,"XIRR")].values.flatten().transpose()

    return df

def get_xirr_timeseries():
    transactions = backend.bank_input.ReadTransactions()
    pfview = backend.portfolio_view.ReadPortfolioView()
    sum_slicer = pfview.columns.get_level_values(1).str.contains("SUM")
    df = pfview.loc[:,(slice(None),sum_slicer,"XIRR")]
    newcols = pfview.loc[:,(slice(None),sum_slicer,"XIRR")].columns.droplevel(level=1).droplevel(level=1)
    df.columns = newcols
    
    return df

def get_returns_timeseries():
    transactions = backend.bank_input.ReadTransactions()
    pfview = backend.portfolio_view.ReadPortfolioView()
    sum_slicer = pfview.columns.get_level_values(1).str.contains("SUM")
    df = pfview.loc[:,(slice(None),sum_slicer,"Return(rel)")]
    newcols = pfview.loc[:,(slice(None),sum_slicer,"Return(rel)")].columns.droplevel(level=1).droplevel(level=1)
    df.columns = newcols
    
    return df

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

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    ) 



