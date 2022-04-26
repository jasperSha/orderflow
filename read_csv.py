import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.options.display.max_columns = None


df = pd.read_csv('data/SPY_2022-04-25 18:00:18.csv')
greeks = ['delta', 'gamma', 'theta', 'vega']

df['net_delta'] = df['delta'] * df['open_interest']
df['net_call_gamma'] = df['gamma'].loc[df['option_type'] == 'c'] * df['open_interest']
df['net_put_gamma'] = df['gamma'].loc[df['option_type'] == 'p'] * -df['open_interest']
df = df.groupby('strike', as_index=False, sort=True).agg(
    {
        'net_delta': 'sum',
        'net_call_gamma': 'sum',
        'net_put_gamma': 'sum',
        'open_interest': 'sum',
        'days_to_expiration': 'first'
    }
)
df['net_gamma'] = df['net_call_gamma'] - df['net_put_gamma']

df = df.loc[df['days_to_expiration'] <= 2]
df = df.loc[(df['strike'] >= 410) & (df['strike'] <= 450)]
print(df.head())
# flip_index = np.where(np.diff(np.sign(df['net_gamma'])))[0][0]
# print(df.iloc[flip_index])
# df.plot(x='strike', y='net_call_gamma', kind='bar')
# df.plot(x='strike', y='net_put_gamma', kind='bar')
fig = plt.figure()
ax = plt.subplot(111)

ax.bar(df['strike'], df['net_call_gamma'], width=0.2)
ax.bar(df['strike'], df['net_put_gamma'], width=0.2)
plt.show()