import pandas as pd
import numpy as np 
import datetime
import matplotlib.pyplot as plt

datefrmt = lambda x: pd.datetime.strptime(x, "%d.%m.%Y")
encoding = "cp1252"

amount = pd.read_csv("ums.csv",
    skiprows = 4,
    delimiter = ";",
    encoding = encoding,
    decimal = ".",
    usecols = [2],
    names = ["Amount"], 
    header = None
)

parsed = pd.read_csv("ums.csv",
    skiprows = 4,
    delimiter = ";",
    encoding = encoding,
    parse_dates = [0,1],
    date_parser = datefrmt, 
    decimal = ",",
    usecols = [0,1,3,4,5,6,7],
    names = ["Execute","Booking","Name","WKN","Currency","Price","Trans"], 
    header = None
)



input_form = pd.concat([parsed,amount], axis = 1)
input_form = input_form.assign(Portfolio="Altersvorsorge")

input_form["Fees"] = round(input_form["Trans"]-(input_form["Amount"]*input_form["Price"]),2)
input_form

input_form.loc[(input_form["Execute"] < datetime.datetime(2019,2,1)) & (input_form["WKN"] == "ETF110")]