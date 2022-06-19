from scipy import stats, signal
import numpy as np
import pandas as pd
import numba

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

import time

ES_TICK_SIZE = 0.25
ohlc_dict = {
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
}
"""
ALL TIMES IN EST
"""
RTH = ['09:30:00', '17:00:00']
RTH_PERIOD = pd.Timedelta(minutes=450)

ETH = ['18:00:00', '9:29:00']
ETH_PERIOD = pd.Timedelta(minutes=929)

OPENING_RANGE_START = ['09:30:00']

def high_volume_nodes(df, kde_factor=0.01, num_samples=500, min_prom=5e-5, graph=False) -> list:
    '''
    plot and return all high volume nodes in given chart
    kde: uses gaussian distribution for kernel

    @param dataframe df: dataframe containing ohlcv data, just need ['volume', 'close'] in columns
    @param float kde_factor: bandwidth sensitivity --> smoothness of kde; adjust higher for fewer peaks
    @param int num_samples: number of bins to divide points into
    @param float min_prom: distance from peak to shoulder (lowest contour line respective to peak)
    @param boolean graph: set to true to display the charts (leave as is to just get the HVN's)

    @return peaks: list of high volume nodes
    '''
    volume = df['tickVolume']
    close = df['tickPrice']

    # px.histogram(df, x='volume', y='close', nbins=1000, orientation='h').show()

    kde = stats.gaussian_kde(close,weights=volume,bw_method=kde_factor)
    xr = np.linspace(close.min(),close.max(),num_samples)
    kdy = kde(xr)
    ticks_per_sample = (xr.max() - xr.min()) / num_samples

    def get_dist_plot(c, v, kx, ky):
        fig = go.Figure()
        fig.add_trace(go.Histogram(name='Vol Profile', x=c, y=v, nbinsx=num_samples, 
                                histfunc='sum', histnorm='probability density',
                                marker_color='#B0C4DE'))
        fig.add_trace(go.Scatter(name='KDE', x=kx, y=ky, mode='lines', marker_color='#D2691E'))
        return fig

    min_prom = min_prom
    peaks, peak_props = signal.find_peaks(kdy, prominence=min_prom)
    pkx = xr[peaks]
    pky = kdy[peaks]

    if graph:
        pk_marker_args = dict(size=10)
        fig = get_dist_plot(close, volume, xr, kdy)
        fig.add_trace(go.Scatter(name='Peaks', x=pkx, y=pky, mode='markers', marker=pk_marker_args))

        # Draw prominence lines
        left_base = peak_props['left_bases']
        right_base = peak_props['right_bases']
        line_x = pkx
        line_y0 = pky
        line_y1 = pky - peak_props['prominences']

        for x, y0, y1 in zip(line_x, line_y0, line_y1):
            fig.add_shape(type='line',
                xref='x', yref='y',
                x0=x, y0=y0, x1=x, y1=y1,
                line=dict(
                    color='red',
                    width=2,
                )
            )
        fig.show()
        plt.savefig("may_25_june_08.png")
    pkx = [round(p) for p in pkx]
    return pkx


def value_area(df, sigma=1, TICKS=False):
    '''
    determine VAH, VAL, POC, by volume

    @param dataframe df: contains ohlcv price data, in 1 minute increments
    @param float sigma: number of standard deviations from POC (ie, 1 --> 68% va, 2--> 95%)
    @param bool ticks: whether incoming data is tick format, if not then minute
    @param string interval: interval across which to aggregate value calculations
        interval options: ['1D'] # currently only calculating daily VAH's (ETH considered a separate "day")

    @return list of floats: [POC, VAH, VAL, day_high, day_low]



    '''
    if TICKS:
        volume_map = df.groupby(by=['tickPrice'])['tickVolume'].sum()

        day_high = volume_map.index.max()
        day_low = volume_map.index.min()

        poc = volume_map.idxmax()
        std_dev = np.std(np.array(list(volume_map.index)), ddof=0)
    else:
        day_high = df['high'].max()
        day_low = df['low'].min()

        volume_map = {}
        tick_range = np.arange(day_low, day_high+0.25, 0.25)
        for tick in tick_range:
            volume_map[tick] = 0

        for row in df.itertuples():
            bar_low = getattr(row, 'low')
            bar_high = getattr(row, 'high')
            bar_ticks = np.arange(bar_low, bar_high+0.25, 0.25)
            for t in bar_ticks:
                volume_map[t] += getattr(row, 'volume')

        poc = max(volume_map, key=volume_map.get)
        std_dev = np.std(np.array(list(volume_map.keys())), ddof=0)

    sigma *= std_dev
    vah = round((poc + sigma)*4) / 4
    val = round((poc - sigma)*4) / 4

    return poc, vah, val, day_high, day_low


def orb_stats(df, num_days, gap_size, sigma=1, TICKS=False, interval='1D'):
    '''
    EST
    sydney 16:00 to 01:00 (4pm to 1am)
    ny = 8:00 to 17:00 (8am to 5pm)
    london = 02:00 to 11:00 (2am to 11pm)
    tokyo = 19:00 to 04:00 (7pm to 4am)
    cash new york: 9:30 to 16:00

    @param float gap_size: % as decimal that price has jumped (gapped) from previous close to current open

    todo: compare to overnight high/low
    
    '''
    # prior stats to track
    prior_high = 0.0
    prior_low = 0.0
    ovn_high = 0.0
    ovn_low = 0.0
    prev_open = 0.0
    prev_close = 0.0

    prev_tpoc = 0
    prev_vpoc = 0
    prev_vah = 0
    prev_val = 0

    num_samples = 0

    # make into list, or data range or turn into objects/datatypes
    # orb stats
    orb5_ph = 0
    orb5_pl = 0
    orb5_ovnh = 0
    orb5_ovnl = 0

    orb10_ph = 0
    orb10_pl = 0
    orb10_ovnh = 0
    orb10_ovnl = 0

    orb15_ph = 0
    orb15_pl = 0
    orb15_ovnh = 0
    orb15_ovnl = 0

    orb30_ph = 0
    orb30_pl = 0
    orb30_ovnh = 0
    orb30_ovnl = 0

    # gap fill stats
    gap_fill = 0

    # assuming first period is an ETH period
    idx = df.index[0]
    while idx.date() < df.index[-1].date() - pd.Timedelta(days=1):
        # current day ETH
        eth_start_idx = idx
        eth_end_idx = idx + ETH_PERIOD
        eth_range_df = df[eth_start_idx:eth_end_idx]

        ovn_vpoc, ovn_vah, ovn_val, ovn_high, ovn_low = value_area(eth_range_df, sigma, TICKS)

        # current day RTH
        rth_start_idx = eth_end_idx + pd.Timedelta(minutes=1)
        rth_end_idx = rth_start_idx + RTH_PERIOD
        rth_range_df = df[rth_start_idx:rth_end_idx]
        today_vpoc, today_vah, today_val, today_high, today_low = value_area(rth_range_df, sigma, TICKS)
        todays_ticks_touched = np.arange(today_low, today_high + ES_TICK_SIZE, ES_TICK_SIZE)

        # skip first day for prior stats and check for skipped days in data
        if idx > df.index[0] and rth_start_idx in df.index:
            num_samples += 1 
            rth_open = rth_range_df['open'].iloc[0]
            gap = np.abs(round(np.log(rth_open) - np.log(prev_close), 5))
            if gap >= gap_size:
                if prev_close in todays_ticks_touched:
                    gap_fill += 1

            # 5 minute ORB
            orb_5 = rth_range_df.resample('5min').apply(ohlc_dict)

            # get top and bottom of 5 min ORB
            orb_5_top = orb_5['high'].iloc[0]
            orb_5_bot = orb_5['low'].iloc[0]

            # greater than orb --> prior high, ovnh
            if orb_5['close'].iloc[1] >= orb_5_top:
                if prior_high <= orb_5['high'].iloc[1:].max():
                    orb5_ph += 1
                if ovn_high <= orb_5['high'].iloc[1:].max():
                    orb5_ovnh += 1
            # less than orb --> prior low, ovnl
            if orb_5['close'].iloc[1] <= orb_5_bot:
                if prior_low >= orb_5['low'].iloc[1:].min():
                    orb5_pl += 1
                if ovn_low >= orb_5['low'].iloc[1:].min():
                    orb5_ovnl += 1

            # 10 minute ORB
            orb_10 = rth_range_df.resample('10min').apply(ohlc_dict)

            # get top and bottom of 10 min ORB
            orb_10_top = orb_10['high'].iloc[0]
            orb_10_bot = orb_10['low'].iloc[0]

            # greater than orb --> prior high, ovnh
            if orb_10['close'].iloc[1] >= orb_10_top:
                if prior_high <= orb_10['high'].iloc[1:].max():
                    orb10_ph += 1
                if ovn_high <= orb_10['high'].iloc[1:].max():
                    orb10_ovnh += 1
            # less than orb --> prior low, ovnl
            if orb_10['close'].iloc[1] <= orb_10_bot:
                if prior_low >= orb_10['low'].iloc[1:].min():
                    orb10_pl += 1
                if ovn_low >= orb_10['low'].iloc[1:].min():
                    orb10_ovnl += 1

            # 15 minute ORB
            orb_15 = rth_range_df.resample('15min').apply(ohlc_dict)

            # get top and bottom of 15 min ORB
            orb_15_top = orb_15['high'].iloc[0]
            orb_15_bot = orb_15['low'].iloc[0]

            # greater than orb --> prior high, ovnh
            if orb_15['close'].iloc[1] >= orb_15_top:
                if prior_high <= orb_15['high'].iloc[1:].max():
                    orb15_ph += 1
                if ovn_high <= orb_15['high'].iloc[1:].max():
                    orb15_ovnh += 1
            # less than orb --> prior low, ovnl
            if orb_15['close'].iloc[1] <= orb_15_bot:
                if prior_low >= orb_15['low'].iloc[1:].min():
                    orb15_pl += 1
                if ovn_low >= orb_15['low'].iloc[1:].min():
                    orb15_ovnl += 1

            # 30 minute ORB
            orb_30 = rth_range_df.resample('30min').apply(ohlc_dict)

            # get top and bottom of 30 min ORB
            orb_30_top = orb_30['high'].iloc[0]
            orb_30_bot = orb_30['low'].iloc[0]

            # greater than orb --> prior high, ovnh
            if orb_30['close'].iloc[1] >= orb_30_top:
                if prior_high <= orb_30['high'].iloc[1:].max():
                    orb30_ph += 1
                if ovn_high <= orb_30['high'].iloc[1:].max():
                    orb30_ovnh += 1
            # less than orb --> prior low, ovnl
            if orb_30['close'].iloc[1] <= orb_30_bot:
                if prior_low >= orb_30['low'].iloc[1:].min():
                    orb30_pl += 1
                if ovn_low >= orb_30['low'].iloc[1:].min():
                    orb30_ovnl += 1

        # account for data gaps
        if rth_start_idx in df.index:
            rth_vpoc, rth_vah, rth_val, rth_high, rth_low = value_area(rth_range_df)

            # storing for next day
            prior_high = rth_high
            prior_low = rth_low
            prev_open = rth_range_df['open'].iloc[0]
            prev_close = rth_range_df['close'].iloc[-1]

            prev_poc = rth_vpoc
            prev_vah = rth_vah
            prev_val = rth_val


        idx += pd.Timedelta(days=1)
        # account for saturdays/holidays
        while idx not in df.index:
            idx += pd.Timedelta(days=1)
    
    orb5_ph = (orb5_ph / num_samples) * 100
    orb5_pl = (orb5_pl / num_samples) * 100

    orb10_ph = (orb10_ph / num_samples) * 100
    orb10_pl = (orb10_pl / num_samples) * 100

    orb15_ph = (orb15_ph / num_samples) * 100
    orb15_pl = (orb15_pl / num_samples) * 100

    orb30_ph = (orb30_ph / num_samples) * 100
    orb30_pl = (orb30_pl / num_samples) * 100

    gap_fill = (gap_fill / num_samples) * 100

    orb5_ovnh = (orb5_ovnh / num_samples) * 100
    orb5_ovnl = (orb5_ovnl / num_samples) * 100

    orb10_ovnh = (orb10_ovnh / num_samples) * 100
    orb10_ovnl = (orb10_ovnl / num_samples) * 100

    orb15_ovnh = (orb15_ovnh / num_samples) * 100
    orb15_ovnl = (orb15_ovnl / num_samples) * 100

    orb30_ovnh = (orb30_ovnh / num_samples) * 100
    orb30_ovnl = (orb30_ovnl / num_samples) * 100

    print(f"this is considering {num_samples} days")

    print("Previous Day")
    print(f"exceeded orb 5min high --> prior high: {orb5_ph}%")
    print(f"exceeded orb 5min low --> prior low: {orb5_pl}%")

    print(f"exceeded orb 10min high --> prior high: {orb10_ph}%")
    print(f"exceeded orb 10min low --> prior low: {orb10_pl}%")

    print(f"exceeded orb 15min high --> prior high: {orb15_ph}%")
    print(f"exceeded orb 15min low --> prior low: {orb15_pl}%")

    print(f"exceeded orb 30min high --> prior high: {orb30_ph}%")
    print(f"exceeded orb 30min low --> prior low: {orb30_pl}%")


    print("Gap Fills")
    print(f"gap fill >= {gap_size*100}% from rth_open to prev_close {gap_fill}%")
    
    print("Overnight")
    print(f"orb 5 min --> ovnh: {orb5_ovnh}%")
    print(f"orb 5 min --> ovnl: {orb5_ovnl}%")

    print(f"orb 10 min --> ovnh: {orb10_ovnh}%")
    print(f"orb 10 min --> ovnl: {orb10_ovnl}%")

    print(f"orb 15 min --> ovnh: {orb15_ovnh}%")
    print(f"orb 15 min --> ovnl: {orb15_ovnl}%")

    print(f"orb 30 min --> ovnh: {orb30_ovnh}%")
    print(f"orb 30 min --> ovnl: {orb30_ovnl}%")


    # use f string to format, log file for standardizing output so no need to change each time



        



def time_value_area(df):
    '''
    determine VAH, VAL, POC, by time
    '''
    rth = ['09:30:00', '16:30:00']
    eth = ['18:00:00', '9:29:00']