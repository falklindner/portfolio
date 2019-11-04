import pandas as pd
import numpy as np 
import datetime
import matplotlib.pyplot as plt

headers = ["Execute", "Booking", "No", "Name", "WKN", "Currency", "Price", "Trans"]
datefrmt = lambda x: pd.datetime.strptime(x, "%d.%m.%Y")
amount = pd.read_csv("ums.csv",
    skiprows = 4,
    delimiter = ";",
    encoding = "cp1252",
    decimal = ".",
    usecols = [2],
    names = ["Amount"], 
    header = None
)

input = pd.read_csv("ums.csv",
    skiprows = 4,
    delimiter = ";",
    encoding = "cp1252",
    parse_dates = [0,1],
    date_parser = datefrmt, 
    decimal = ",",
    usecols = [0,1,3,4,5,6,7],
    names = ["Execute","Booking","Name","WKN","Currency","Price","Trans"], 
    header = None
)

input = pd.concat([input,amount], axis = 1)
input["Fees"] = round(input["Trans"]-(input["Amount"]*input["Price"]),2)
input

input.loc[(input["Execute"] < datetime.datetime(2019,2,1)) & (input["WKN"] == "ETF110")]