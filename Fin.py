import time

import pandas as pd
import numpy as np

import py_vollib
from py_vollib.black_scholes  import black_scholes as bs
from py_vollib.black_scholes.implied_volatility import implied_volatility
from py_vollib.black_scholes.greeks.analytical import delta 
from py_vollib.black_scholes.greeks.analytical import gamma
from py_vollib.black_scholes.greeks.analytical import rho
from py_vollib.black_scholes.greeks.analytical import theta
from py_vollib.black_scholes.greeks.analytical import vega

import py_vollib_vectorized
from py_vollib_vectorized.api import price_dataframe

from CallPut import CallPut

RISK_FREE_RATE = 0.0101

class Fin:
    def __init__(self, session=None, opt_params: dict = {}):
        '''
            Primary object for handling stock queries for historical and options data
        '''
        assert session is not None, 'requires session for init'
        assert opt_params is not None, 'requires options parameters for pull'

        self.session = session
        self.opt_params = opt_params
        self.symbol = opt_params['symbol']

        self.data = {}
        self._set_data()
        
        self.deltas = np.arange(-0.001, 0.999, 0.001)

    def get_options_by_delta(self, date: int, delta_range: float):
        '''
            Get options at date with strikes ranging from ATM(d = 0.5) outward to the delta provided
            @params 
            delta: float range from 0.001 to 0.999 inclusive
            date: int index from nearest to furthest date
            @return:
                list of strikes
        '''
        if delta_range not in self.deltas:
            raise InvalidDeltaException("Invalid Delta")

        expiry_date = self.data['dates'][date]

        min_delta = 0.5 - delta_range
        max_delta = 0.5 + delta_range
        
        callputs = []
        for callput in self.data['options'][expiry_date]:
            d = abs(callput.delta)
            if d >= min_delta and d <= max_delta:
                print("in range: ", callput)
                callputs.append(callput)
        return callputs
            
    def _get_quote(self):
        instruments = [self.symbol]
        quote = self.session.get_quotes(instruments=instruments)
        return quote[self.symbol]

    def _set_data(self):
        '''
            Separates pulled option chain into calls, puts, and dates
        '''
        start = time.time()
        chain = self.session.get_options_chain(option_chain=self.opt_params)
        end = time.time()
        print('%s seconds for pulling chain from api'%(end - start))

        self.underlying = chain['underlyingPrice']
        self.total_num_contracts = chain['numberOfContracts']

        calls_map = chain['callExpDateMap']
        puts_map = chain['putExpDateMap']

        #using the first strike of each expiry date chain to get the date of the chain
        options = {}
        dates = []
        calls = []
        puts = []

        for days, strikes in calls_map.items():
            for strike, value in strikes.items():
                call = CallPut(dict(value[0].items()))
                calls.append(call)

            # just picking one call to grab expiry date (all in this loop are same date)
            d = call.data['expirationDate']
            options[d] = []

            # maintain list of dates
            dates.append(d)
        
        for days, strikes in puts_map.items():
            for strike, value in strikes.items():
                put = CallPut(dict(value[0].items())) # api returns a list here (of one element)
                puts.append(put)

        for c in calls:
            call_date = c.data['expirationDate']
            if call_date in options.keys():
                options[call_date].append(c)

        for p in puts:
            put_date = p.data['expirationDate']
            if put_date in options.keys():
                options[put_date].append(p)


        # storing in flat structure for vectorized greeks
        all_contracts = calls + puts
        all_contracts = pd.DataFrame.from_records([c.to_dict() for c in all_contracts])            

        # stored in options as top level to send to gcloud
        # options = {
        #   'date': [calls/puts]
        # }
        self.data['options'] = options
        self.data['all_contracts'] = all_contracts
        self.data['expiry_dates'] = pd.to_datetime(dates, format='%Y-%m-%d')

    def get_contracts(self):
        return self.data['all_contracts']

    def get_data(self):
        return self.data
    
    def refresh_data(self):
        '''
        TODO: 
            only altering bid/ask here
            will also recalculate greeks
        '''
        chain = self.session.get_options_chain(option_chain=self.opt_params)

        # just update the bid/ask of each callput
        # get around pulling entire chain?

    
    def calculate_greeks(self):
        '''
        delta, gamma, theta, vega, rho, implied volatility
        '''
        contracts = self.data['all_contracts']
        contracts = contracts.loc[(contracts['strike'] > 420) & (contracts['strike'] < 460)]
        print(contracts.shape[0])
        contracts['S'] = self.underlying
        contracts['annualized_dte'] = contracts['days_to_expiration'] / 365
        contracts['risk_free_rate'] = RISK_FREE_RATE

        df = price_dataframe(
            contracts,
            flag_col='option_type',
            underlying_price_col='S',
            strike_col='strike',
            annualized_tte_col='annualized_dte',
            riskfree_rate_col='risk_free_rate',
            price_col='mark',
            model='black_scholes',
            inplace=False
            )

        # S = self.underlying
        # option_type = contracts['option_type']
        # K = contracts['strike']
        # T = contracts['days_to_expiration'] / 365
        # mark = contracts['mark']

        # iVol = implied_volatility(mark, S, K, T, RISK_FREE_RATE, option_type)
        # theoretical_price = bs(option_type, S, K, T, RISK_FREE_RATE, iVol)

        # contracts['delta'] = delta(flag, S, K, T, RISK_FREE_RATE, iVol)
        # contracts['gamma'] = gamma(flag, S, K, T, RISK_FREE_RATE, iVol)
        # contracts['theta'] = theta(flag, S, K, T, RISK_FREE_RATE, iVol)
        # contracts['vega'] = vega(flag, S, K, T, RISK_FREE_RATE, iVol)
        # contracts['rho'] = rho(flag, S, K, T, RISK_FREE_RATE, iVol)

        # contracts['implied_volatility'] = iVol
        # contracts['theoretical_price'] = theoretical_price

        return df