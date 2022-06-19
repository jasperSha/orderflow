import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from volume_profile import value_area, high_volume_nodes

import pytz

pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.set_option('display.float_format', lambda x: '%.2f' % x)

"""
first step, figure out how to quantify when
ticks are hitting a large passive buyer or seller,
ie a lot of ticks at the exact same price but does not
pass price.
    - subset, figure out how to determine direction into
    a passive iceberg, ie often we hit a passive buyer/seller
    a bunch of ticks get burnt into there,
    we retract a bit, but only for a few ticks, and keep coming back
    to hit that buyer/seller.
    then if/when does that break, (how much volume, HVN or LVN, GEX, VIX, etc.)

for both delta, considering magnitude PAST bid/ask, ie
positive bidDelta --> selling below bid, ie aggressive sellers
positive askDelta --> buying above ask, ie aggressive buyers

bid/ask volume imbalance (little difference for HFT)
signed transaction volume (signed quantity, number of shares bot minus number of shares sold in last
n seconds (they used 15 seconds))
bid/ask spread (positive value indicating diff between bid and ask prices)

one successful example is when the spread is tight, and signed transaction volume is largely negative
this implies strong selling pressure

price: feature measuring recent directional movement of executed prices
smart price: variation on mid-price, where average of bid/ask prices weighted according to their inverse volume
trade sign: feature measuring whether buyers or sellers crossed spread more frequently in recent executions


subtract mean, divide by std, time-averaged over a recent interval
(they discretized features into bins for state features)

smart price was their best solo feature
spread not as useful apparently?


more easily quantifiable ideas:
average tick range per hour of day (can use minute data for this)
average volume per hour of day
identify V reversal days --> find average bid/ask delta near the lows


"""
ohlc_dict = {
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'none': 'sum'
}

def agg_delta_volume(row):
    


# df = pd.read_parquet("data/futures/ES/all_ticks.parquet")

# df = df['2021-10-19 04:29:00': '2021-10-19 17:01:00']
# print(df['tickPrice'].max(), df['tickPrice'].min())

df = pd.read_parquet("data/futures/ES/apr28_jun10_ticks.parquet")

# check delta imbalance --> assign to bid volume or ask volume (just set boolean)
delta_conditions = [
    df['tickPrice'] <= df['bestBid'],
    df['tickPrice'] >= df['bestAsk']
]
choices = ['bidSide', 'askSide']
df['delta'] = np.select(delta_conditions, choices, default=None)

print(df.head())
# df['']
# df = df.resample('5min').apply(ohlc_dict)


# df = df.loc[(df.index >='2022-04 18:00') & (df.index <= '2022-05-12 16:59:00')]








# peaks = high_volume_nodes(df, kde_factor=0.01,num_samples=500, graph=True)
# print(peaks)

# df = df.resample('30min').apply(ohlc_dict)


# # initiative participants (aggressively above ask or below bid txns, and breaching)
# print(df.loc[(df['bidDelta'] <= -5) | (df['askDelta'] >= 5)][:5])
# txns = df.groupby(by=[df.index]).agg({
#     'tickVolume': 'sum',
#     'tickPrice': 'first',
#     'bestBid': 'first',
#     'bestAsk': 'first',
#     'bidDelta': 
# })
# print(df.shape)
# print(txns.head())
# df = df[:50]
# print(df)
# s = df.groupby(df.index)['tickPrice']
# print(s.nunique())
# print(s.apply(lambda x: x > 1).count())

# df = df.resample('1D').apply(ohlc_dict)
