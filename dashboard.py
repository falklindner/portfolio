import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import PortfolioView

portfolio = "Airbus"
symbol = "AIR.PA"

portfolio_view = PortfolioView.ReadPortfolioView()
xdata = portfolio_view.index
ydata = portfolio_view.loc[:,(portfolio,symbol,"XIRR")].values



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


component1 = go.Scatter(
    x=xdata,
    y=ydata
    )




layout = dict(
    title='Time Series with Rangeslider',
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
                dict(step='all')
            ])
        ),
        rangeslider=dict(),
        type='date'
    )
)


data =[component1]
fig = dict(data=data, layout=layout)

# Now here's the Dash part:


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    dcc.Graph(id='my-graph', figure=fig)
])


if __name__ == '__main__':
    app.run_server(debug=True)