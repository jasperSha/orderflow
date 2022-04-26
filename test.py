#!/usr/bin/env python3

import py_vollib 
from py_vollib.black_scholes  import black_scholes as bs
from py_vollib.black_scholes.implied_volatility import implied_volatility as iv
from py_vollib.black_scholes.greeks.analytical import delta 
from py_vollib.black_scholes.greeks.analytical import gamma
from py_vollib.black_scholes.greeks.analytical import rho
from py_vollib.black_scholes.greeks.analytical import theta
from py_vollib.black_scholes.greeks.analytical import vega

# note this monkeypatches the underlying pyvollib (all the calls remain same)
import py_vollib_vectorized
import numpy as np


"""
price (float) – the Black-Scholes option price
S (float) – underlying asset price
sigma (float) – annualized standard deviation, or volatility
K (float) – strike price
t (float) – time to expiration in years
r (float) – risk-free interest rate
flag (str) – ‘c’ or ‘p’ for call or put.
"""
def greek_val(flag, S, K, t, r, sigma):
    price = bs(flag, S, K, t, r, sigma)
    
    imp_v = iv(price, S, K, t, r, flag)

    print('imp iv from black scholes:', imp_v)
    delta_calc = delta(flag, S, K, t, r, sigma)
    gamma_calc = gamma(flag, S, K, t, r, sigma)
    rho_calc = rho(flag, S, K, t, r, sigma)
    theta_calc = theta(flag, S, K, t, r, sigma)
    vega_calc = vega(flag, S, K, t, r, sigma)
    return np.array([ price, imp_v ,theta_calc, delta_calc ,rho_calc ,vega_calc ,gamma_calc])

flag = 'c'
S = 439.67
K = 450
sigma = .2217
r = 0.0101
t = 9.0/365

market_price = 1.09 # buy side

market_iv = iv(market_price, S, K, t, r, flag)
print('imp iv calculated from market price:', market_iv)

call=greek_val('c', S, K, t, r, market_iv)

#put=greek_val('p', S, K, t, r, market_iv)

print('price:', call[0])
print('implied vol:', call[1])
print('theta:', call[2])
print('delta:', call[3])
print('rho:', call[4])
print('vega:', call[5])
print('gamma:', call[6])

print('price:', put[0])
print('implied vol:', put[1])
print('theta:', put[2])
print('delta:', put[3])
print('rho:', put[4])
print('vega:', put[5])
print('gamma:', put[6])

