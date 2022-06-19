from cboe import get_rvol, get_vix

import matplotlib.pyplot as plt


rvol_df = get_rvol()
vix_df = get_vix()
vix_df = vix_df.drop(columns=['OPEN', 'HIGH', 'LOW'])

rvol_df = rvol_df.loc['2021-08-01':'2022-06-14']
vix_df = vix_df.loc['2021-08-01':'2022-06-14']

ax = vix_df.plot()
rvol_df.plot(ax=ax)
plt.show()