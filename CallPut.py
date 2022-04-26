import time

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

        self.data['mark'] = round(self.data['bid'] + ((self.data['ask'] - self.data['bid'])/2), 2)

        #convert dates to readable
        date_keys = ['tradeTimeInLong', 'quoteTimeInLong', 'expirationDate', 'lastTradingDay']
        for key in date_keys:
            self.data[key] = self._convert_readable_dates(self.data[key])
        
        #only need y/m/d for expiration date
        self.data['expirationDate'] = self.data['expirationDate'][:10]
    
    # using TDA's greeks FOR NOW (TODO: calculate implied volatilty for american options)
    def to_dict(self):
        return {
            'bid': self.data['bid'],
            'ask': self.data['ask'],
            'mark': self.data['mark'],
            'strike': self.data['strikePrice'],
            'option_type': self.data['option_type'],
            'delta': self.data['delta'],
            'gamma': self.data['gamma'],
            'theta': self.data['theta'],
            'vega': self.data['vega'],
            'implied_volatility': self.data['volatility'],
            'volume': self.data['totalVolume'],
            'open_interest': self.data['openInterest'],
            'days_to_expiration': self.data['daysToExpiration'],
            'expiry_date': self.data['expirationDate']
        }

    def _convert_readable_dates(self, epoch):
        '''
            @param: date in epoch milliseconds
            @return: human-readable date
        '''
        return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(epoch/1000.0))
