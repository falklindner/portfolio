import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
import backend.portfolio_view as PortfolioView
import backend.constant as constant
import backend.bank_input as BankInput
import backend.history as History
import backend.financial_func as FinancialFunc

import frontend.dash_comdirect as dash_comdirect

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    ) 




app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

cd_view = dash_comdirect.df_comdirect().reset_index()


app.layout = html.Div(children=[
    html.H4(children='Comdirect View'),
    generate_table(cd_view.round(2))
])


if __name__ == '__main__':
    app.run_server(debug=True)
