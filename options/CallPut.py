import time
import pandas as pd
import numpy as np

class CallPut():
    '''
    the main thing is initial storage of bid and ask, everything else can be calculated later off that
    '''
    def __init__(self, *args):
        self.data = dict(*args)
        if self.data['putCall'] == 'CALL':
            self.data['option_type'] = 'c'
        else:
            self.data['option_type'] = 'p'

        # can use symbol for id (fully unique)
        self.contract_id = self.data['symbol']
        
        # just forcing to 0 for now, interpolation will be downstream
        for k, v, in self.data.items():
            if v == 'NaN':
                self.data[k] = 0

        self.data['mark'] = round(self.data['bid'] + ((self.data['ask'] - self.data['bid'])/2), 2)

        #convert dates to readable
        date_keys = ['tradeTimeInLong', 'quoteTimeInLong', 'expirationDate', 'lastTradingDay']
        for key in date_keys:
            self.data[key] = self._convert_readable_dates(self.data[key])
        
        #only need y/m/d for expiration date
        self.data['expirationDate'] = self.data['expirationDate'][:10]
        self.data['expirationDate'] = pd.to_datetime(self.data['expirationDate'], format="%Y-%m-%d")
    
    # using TDA's greeks FOR NOW (TODO: calculate implied volatilty for american options)
    def to_dict(self):
        return {
            'bid': pd.to_numeric(self.data['bid']),
            'ask': pd.to_numeric(self.data['ask']),
            'mark': pd.to_numeric(self.data['mark']),
            'strike': pd.to_numeric(self.data['strikePrice']),
            'option_type': self.data['option_type'],
            'delta': pd.to_numeric(self.data['delta']),
            'gamma': pd.to_numeric(self.data['gamma']),
            'theta': pd.to_numeric(self.data['theta']),
            'vega': pd.to_numeric(self.data['vega']),
            'implied_volatility': pd.to_numeric(self.data['volatility']),
            'volume': pd.to_numeric(self.data['totalVolume']),
            'open_interest': pd.to_numeric(self.data['openInterest']),
            'days_to_expiration': pd.to_numeric(self.data['daysToExpiration']),
            'expiry_date': self.data['expirationDate']
        }

    def _convert_readable_dates(self, epoch):
        '''
            @param: date in epoch milliseconds
            @return: human-readable date
        '''
        return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(epoch/1000.0))
