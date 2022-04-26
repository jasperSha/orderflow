import pandas as pd
import numpy as np

def live_gamma(contracts):
    '''
    @param df contracts: all contracts, flat structure, unsorted by any strike/expiry
    plot gamma by volume
    vertical axis
    calls on left, puts on right
    30DTE

    '''
    