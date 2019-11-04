import pandas as pd
import numpy as np 
import datetime
import matplotlib.pyplot as plt

headers = ["Execute", "Booking", "No", "Name", "WKN", "Currency", "Price", "Trans"]

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
    decimal = ",",
    usecols = [0,1,3,4,5,6,7],
    names = ["Execute","Booking","Name","WKN","Currency","Price","Trans"], 
    header = None
)

input = pd.concat([input,amount], axis = 1)
