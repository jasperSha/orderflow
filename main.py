import datetime
import time

from login import login
from Fin import Fin

session = login()
ticker = 'SPY'
opt_params = {
    'symbol': ticker,
    'opt_range': 'NTM'
}

stock = Fin(session, opt_params)

while True:
    try:
        contracts = stock.get_contracts()
        timestamp = str(datetime.datetime.now())[:19]
        contracts.to_csv('data/%s_%s.csv'%(ticker, timestamp), index=False)
        time.sleep(5)
    except:
        continue


'''
right now, callput has no access to spot price, its at Fin object level
probably should just do greeks at fin level, not callput ( to vectorize)

todo: 50-16 delta 0dte spx straddles
todo: sum gamma and send to tradingview api? or just manually
'''