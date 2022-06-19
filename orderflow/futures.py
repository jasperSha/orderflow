import pandas as pd
import numpy as np

from volume_profile import high_volume_nodes, value_area, orb_stats

'''
opening range: 9:30 - 10:30 EST

define value area of ETH and RTH
val, vah, poc
same for tpo's, tpoc
ovnh, ovnl

TODO: 1min --> db for volatility stats
tick data --> orderflow

'''

pd.options.display.max_columns = None
pd.options.display.max_rows = None
ohlc_dict = {
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
}


# df = pd.read_csv("data/futures/ES/20050906_20220527_es_1min.csv")
df = pd.read_csv("data/futures/ES/ES_continuous_adjusted_1min.csv")
df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
df.index = pd.to_datetime(df['timestamp'])
df = df.drop(columns=['timestamp'])

# # define starting date (starting with ETH)
df = df.loc[(df.index >='2017-12-20 00:00:00') & (df.index <= '2022-05-25 23:59:00')]
num_days = df.resample('1D').apply(ohlc_dict).shape[0]
gap_size = 0.0025

df = df.resample('30min').apply(ohlc_dict)
df['avg_range'] = ((df['high'] - df['low']).groupby(df.index).transform('median').round(2))
print(df)

# orb_stats(df, num_days, gap_size)


