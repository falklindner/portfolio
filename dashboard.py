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
import frontend.financial_func as FinancialFunc

pfview = PortfolioView.ReadPortfolioView()
transactions = BankInput.ReadTransactions(constant.transactions_path)



pflist = pfview.columns.get_level_values(0).unique()
pf = pflist[0]

lastdate = pfview.index[-1]

pfview.loc[:,(pf,slice(None),"Holdings")]
hist = History.Read_History()
hist.loc[lastdate,"LYYA.DE"]
lastdate

value_last = pfview.loc[lastdate,(pf,slice(None),"Value")].sum()
invest_last = transactions["Trans"].loc[transactions["Portfolio"] == pf].sum()
return_last = value_last - invest_last
return_last_percent = return_last/invest_last

dtd = pfview.index[-2]
mtd = pfview.index[-31]
ytd = pfview.index[-366]

value_dtd = pfview.loc[dtd,(pf,slice(None),"Value")].sum()
value_mtd = pfview.loc[mtd,(pf,slice(None),"Value")].sum() 
value_ytd = pfview.loc[ytd,(pf,slice(None),"Value")].sum() 

pf_transactions  = transactions["Trans"].loc[transactions["Portfolio"] == pf]

ytd_transactions = ((-1)*pf_transactions[ytd:]).reset_index().values.tolist()
mtd_transactions = ((-1)*pf_transactions[mtd:]).reset_index().values.tolist()
dtd_transactions = ((-1)*pf_transactions[dtd:]).reset_index().values.tolist()

ytd_transactions.append([lastdate,value_last])
ytd_transactions.insert(0,[ytd,(-1)*value_ytd])

mtd_transactions.append([lastdate,value_last])
mtd_transactions.insert(0,[mtd,(-1)*value_mtd])

dtd_transactions.append([lastdate,value_last])
dtd_transactions.insert(0,[dtd,(-1)*value_dtd])


XIRR_YTD = FinancialFunc.xirr(ytd_transactions).round(2)
XIRR_MTD = FinancialFunc.xirr(mtd_transactions).round(2)
XIRR_DTD = FinancialFunc.xirr(dtd_transactions).round(2)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

value_view = pfview.loc[:,(pf,slice(None),"Value")].sum(axis=1)
xdata = value_view.index
ydata = value_view.values


component1 = go.Scatter(
     x=xdata,
     y=ydata
)




layout = dict(
    title='Total Value',
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


fig_data =[component1]
fig = dict(data=fig_data, layout=layout)

# # Now here's the Dash part:


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

data = {"Value(Tot)": [str(int(value_last.round(0))) + "€"], "Gain(Tot)": [str(int(return_last.round(0))) + "€"], "Gain(%)":[str(return_last_percent.round(2))] ,"XIRR(YTD)":[XIRR_YTD],"XIRR(MTD)":[XIRR_MTD],"XIRR(DTD)":[XIRR_DTD]}

df = pd.DataFrame.from_dict(data)



app.layout = html.Div(children=[
    html.H1(children="Altersvorsorge"),
    dash_table.DataTable(
        id='table',
        columns=[{"name":i , "id":i} for  i in df.columns],
        data=df.to_dict('records'),
    ),
    dcc.Graph(id="mygraph", figure=fig)
])

if __name__ == '__main__':
    app.run_server(debug=True)
