import requests
import csv

import pandas as pd
import numpy as np

def get_vix():
    vix_url = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"
    with requests.Session() as s:
        download = s.get(vix_url)

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        data = list(cr)
        headers = data.pop(0)
        vix_df = pd.DataFrame(data, columns=headers)

    vix_df.index = pd.to_datetime(vix_df['DATE'])
    vix_df = vix_df.drop(columns=['DATE'])
    vix_df = vix_df.apply(pd.to_numeric)
    return vix_df

def get_rvol():
    rvol_url = "https://cdn.cboe.com/api/global/us_indices/daily_prices/RVOL_History.csv"
    with requests.Session() as s:
        download = s.get(rvol_url)

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        data = list(cr)
        headers = data.pop(0)
        rvol_df = pd.DataFrame(data, columns=headers)

    rvol_df.index = pd.to_datetime(rvol_df['DATE'])
    rvol_df = rvol_df.drop(columns=['DATE'])
    rvol_df = rvol_df.apply(pd.to_numeric)
    return rvol_df
