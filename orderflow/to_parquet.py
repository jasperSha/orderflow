import pandas as pd

import glob
import pytz
import time

pd.options.display.max_columns = None
pd.options.display.max_rows = None

eastern = pytz.timezone('US/Eastern')

def dates(epoch):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(epoch/1000.0))

"""
WARNING GLOB.GLOB RETURNS FILES IN ORDER OF OS.LISTDIR MUST SORT BEFOREHAND
IF LOADING TRUNCATED LISTS (or just dont sort)
"""
files = glob.glob("/home/jaspersha/Downloads/tickdata/*.csv")

df = []
for f in files:
    # # only looking back to specific date
    # first_and_last = f.split(".")[-2].split("/")[-1].split("_")
    # first = first_and_last[0]
    # last = first_and_last[1]

    # first = pd.to_datetime(dates(int(first)))
    # last = pd.to_datetime(dates(int(last)))
    # if first <= pd.to_datetime("2022-04-28"):
    #     continue


    csv = pd.read_csv(f)
    df.append(csv)

df = pd.concat(df)
df = df.drop_duplicates(subset=['tickId', 'datetime'])

df['datetime'] = pd.to_datetime(df['datetime'], unit='ms').dt.tz_localize(pytz.utc).dt.tz_convert(eastern)

df = df.sort_values(by=['datetime'])
df.index = df['datetime']
df = df.drop(columns=['datetime'])

# df['gap'] = df.index.to_series().diff() > pd.Timedelta(hours=1.1)
# print(df.loc[df['gap']==True])
# print(df.head(), df.tail())


# df.to_parquet("data/futures/ES/apr28_jun10_ticks.parquet")
df.to_parquet("data/futures/ES/all_ticks.parquet")
