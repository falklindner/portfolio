import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import dash_auth


import pandas as pd

import frontend.dash_portfolio as dash_portfolio

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']




app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

tab2_content = html.Div(children=html.H4("Work in progress"))


app.layout = html.Div([
    html.H1('Dash Tabs'),
    dcc.Tabs(id="tabs-example", value='tab-1', children=[
        dcc.Tab(label='Portfolio Information', value='tab-1'),
        dcc.Tab(label='Tab Two', value='tab-2'),
    ]),
    html.Div(id='tabs-content-example')
])

@app.callback(
    Output('tabs-content-example', 'children'),
    [Input('tabs-example', 'value')])


def render_content(tab):
    if tab == 'tab-1':
        return dash_portfolio.generate_pf_content()
    elif tab =='tab-2':
        return tab2_content


if __name__ == '__main__':
    app.run_server(debug=True)
