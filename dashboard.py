import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import dash_auth
import backend.secrets as secrets

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

cd_view = dash_comdirect.df_comdirect().reset_index().rename({"index":"Symbol"})
pf_view = dash_comdirect.df_portfolio().reset_index()

xirr_timeseries = dash_comdirect.xirr_timeseries()
return_timeseries = dash_comdirect.returns_timeseries()



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


layout = dict(
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

xirr_fig = go.Figure(data=xirr_data, layout=layout)
return_fig = go.Figure(data=return_data, layout=layout)




tab1_content = html.Div(children=[
    html.Div(children=[
        html.H4(children='Comdirect View'),
        generate_table(cd_view.round(2))
        ],
        style={'width': '49%', 'display': 'inline-block','margin-left': 10}),
    html.Div(children=[
        html.H4(children='Portfolio View'),
        generate_table(pf_view.round(2)),
        ],
        style={'width': '49%', 'display': 'inline-block','margin-right': 10}),
    html.H4(children="Time Series"),
    html.H5(children="XIRR Chart"),
    dcc.Graph(figure=xirr_fig),
    html.H5(children="Total Returns Chart"),
    dcc.Graph(figure=return_fig)
])

tab2_content = html.Div(children=html.H4("Work in progress"))

VALID_USERNAME_PASSWORD_PAIRS = {
    secrets.username : secrets.password
}

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

app.layout = html.Div([
    html.H1('Dash Tabs'),
    dcc.Tabs(id="tabs-example", value='tab-1', children=[
        dcc.Tab(label='Tab One', value='tab-1'),
        dcc.Tab(label='Tab Two', value='tab-2'),
    ]),
    html.Div(id='tabs-content-example')
])

@app.callback(Output('tabs-content-example', 'children'),
              [Input('tabs-example', 'value')])

def render_content(tab):
    if tab == 'tab-1':
        return tab1_content
    elif tab == 'tab-2':
        return tab2_content


if __name__ == '__main__':
    app.run_server(debug=True)
