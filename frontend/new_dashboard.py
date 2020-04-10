import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.style.use('seaborn')

import ta
import backend.history

hist = backend.history.Read_History()
df = hist.loc[:,("AIR.PA",slice(None))].droplevel(level=0,axis=1).reset_index()

df = ta.add_all_ta_features(df, "Open", "High", "Low", "Close", "Volume", fillna=True)

plt.plot(df[1200:].Close)
plt.plot(df[1200:].volatility_bbh, label='High BB')
plt.plot(df[1200:].volatility_bbl, label='Low BB')
plt.plot(df[1200:].volatility_bbm, label='EMA BB')
plt.title('Bollinger Bands')
plt.legend()
plt.show()