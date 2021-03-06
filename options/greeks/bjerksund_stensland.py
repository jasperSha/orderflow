import math
import numpy as np
from scipy.stats import mvn, norm

import logging

logger = logging.getLogger(__name__)

RISK_FREE_RATE = 0.0284
DIVIDEND = 0.0146

"""
approx_implied vol for starting point for searching iVol for either
european or american
-->
gbs implied vol(newton rhapson) --> european style options
ameri implied using bisection --> american style options
now we have our implied volatility from market price

merton for european style (w dividends) --> calls _gbs (gbs_test_inputs) --> greeks
params: (option_type, fs(spot), x(strike), t(time to expiry in years),
         r(risk_free_rate), q(continuous yield of underlying), v(ivol))
        - use black scholes if no dividends (still euro style)

american for american style
params: (option_type, fs(spot), x(strike), t(time to expiry in years),
         r(risk_free), q(dividend), v(ivol))
         - for no dividend, just set q to 0




"""

# ---------------------------
# Black Scholes: stock Options (no dividend yield)
def black_scholes(option_type, fs, x, t, r, v):
    """ Generalized Black-Scholes formula for option pricing.

    In the traditional Black Scholes model, the option is based on common stock - an
    instrument that is traded at its present value. The stock price does not get present
    valued – it starts at its present value (a ‘spot price’) and drifts upwards over
    time at the risk free rate.

    Args:
        option_type (str): Type of the option. "p" for put and "c" for call options.
        fs (float): Price of underlying asset.
        x (float): Strike price.
        t (float): Time to expiration in years. 1 for one year, 0.5 for 6 months.
        r (float): Risk free rate.
        v (float): Implied volatility of underlying asset.

    Returns:
        value (float): Price of the option.
        delta (float): First derivative of value with respect to price of underlying.
        gamma (float): Second derivative of value w.r.t price of underlying.
        theta (float): First derivative of value w.r.t. time to expiration.
        vega (float): First derivative of value w.r.t. implied volatility.
        rho (float): First derivative of value w.r.t. risk free rates.
    """
    b = r
    return _gbs(option_type, fs, x, t, r, b, v)


# ---------------------------
# Merton Model: Stocks Index, stocks with a continuous dividend yields
def merton(option_type, fs, x, t, r, q, v):
    """Pricing stock options with continuous dividend yields.

    The Merton model is a variation of the Black Scholes model for assets that pay
    dividends to shareholders. Dividends reduce the value of the option because the
    option owner does not own the right to dividends until the option is exercised.

    Args:
        option_type (str): Type of the option. "p" for put and "c" for call options.
        fs (float): Price of underlying asset.
        x (float): Strike price.
        t (float): Time to expiration in years. 1 for one year, 0.5 for 6 months.
        r (float): Risk free rate.
        q (float): Continuous yield of the underlying security.
        v (float): Implied volatility of underlying asset.

    Returns:
        value (float): Price of the option.
        delta (float): First derivative of value with respect to price of underlying.
        gamma (float): Second derivative of value w.r.t price of underlying.
        theta (float): First derivative of value w.r.t. time to expiration.
        vega (float): First derivative of value w.r.t. implied volatility.
        rho (float): First derivative of value w.r.t. risk free rates.
    """
    b = r - q
    return _gbs(option_type, fs, x, t, r, b, v)

# Inputs: option_type = "p" or "c", fs = price of underlying, x = strike, t = time to expiration, r = risk free rate
#         b = cost of carry, v = implied volatility
# Outputs: value, delta, gamma, theta, vega, rho
def _gbs(option_type, fs, x, t, r, b, v):
    logger.debug("Debugging Information: _gbs()")
    # -----------
    # Test Inputs (throwing an exception on failure)
    _gbs_test_inputs(option_type, fs, x, t, r, b, v)

    # -----------
    # Create preliminary calculations
    t__sqrt = math.sqrt(t)
    d1 = (math.log(fs / x) + (b + (v * v) / 2) * t) / (v * t__sqrt)
    d2 = d1 - v * t__sqrt

    if option_type == "c":
        # it's a call
        logger.debug("     Call Option")
        value = fs * math.exp((b - r) * t) * norm.cdf(d1) - x * math.exp(-r * t) * norm.cdf(d2)
        delta = math.exp((b - r) * t) * norm.cdf(d1)
        gamma = math.exp((b - r) * t) * norm.pdf(d1) / (fs * v * t__sqrt)
        theta = -(fs * v * math.exp((b - r) * t) * norm.pdf(d1)) / (2 * t__sqrt) - (b - r) * fs * math.exp(
            (b - r) * t) * norm.cdf(d1) - r * x * math.exp(-r * t) * norm.cdf(d2)
        vega = math.exp((b - r) * t) * fs * t__sqrt * norm.pdf(d1)
        rho = x * t * math.exp(-r * t) * norm.cdf(d2)
    else:
        # it's a put
        logger.debug("     Put Option")
        value = x * math.exp(-r * t) * norm.cdf(-d2) - (fs * math.exp((b - r) * t) * norm.cdf(-d1))
        delta = -math.exp((b - r) * t) * norm.cdf(-d1)
        gamma = math.exp((b - r) * t) * norm.pdf(d1) / (fs * v * t__sqrt)
        theta = -(fs * v * math.exp((b - r) * t) * norm.pdf(d1)) / (2 * t__sqrt) + (b - r) * fs * math.exp(
            (b - r) * t) * norm.cdf(-d1) + r * x * math.exp(-r * t) * norm.cdf(-d2)
        vega = math.exp((b - r) * t) * fs * t__sqrt * norm.pdf(d1)
        rho = -x * t * math.exp(-r * t) * norm.cdf(-d2)

    logger.debug("     d1= {0}\n     d2 = {1}".format(d1, d2))
    logger.debug("     delta = {0}\n     gamma = {1}\n     theta = {2}\n     vega = {3}\n     rho={4}".format(delta, gamma,
                                                                                                        theta, vega,
                                                                                                        rho))

    return value, delta, gamma, theta, vega, rho



# American Options
def american(option_type, fs, x, t, r, q, v):
    """Pricing function for American-style options.

    Price American-style options using the Bjerksund-Stensland (2002) closed-form
    approximation.

    Args:
        option_type (str): Type of the option. "p" for put and "c" for call options.
        fs (float): Price of underlying asset.
        x (float): Strike price.
        t (float): Time to expiration in years. 1 for one year, 0.5 for 6 months.
        r (float): Risk free rate.
        q (float): Dividend payment. Set q=0 for non-dividend paying options.
        v (float): Implied volatility.

    Returns:
        value (float): Price of the option.
        delta (float): First derivative of value with respect to price of underlying.
        gamma (float): Second derivative of value w.r.t price of underlying.
        theta (float): First derivative of value w.r.t. time to expiration.
        vega (float): First derivative of value w.r.t. implied volatility.
        rho (float): First derivative of value w.r.t. risk free rates.
    """
    b = r - q
    return _american_option(option_type, fs, x, t, r, b, v)

# -----------
# Generalized American Option Pricer
# This is a wrapper to check inputs and route to the current "best" American option model
def _american_option(option_type, fs, x, t, r, b, v):
    # -----------
    # Test Inputs (throwing an exception on failure)
    logger.debug("Debugging Information: _american_option()")
    _gbs_test_inputs(option_type, fs, x, t, r, b, v)

    # -----------
    if option_type == "c":
        # Call Option
        logger.debug("     Call Option")
        return _bjerksund_stensland_2002(fs, x, t, r, b, v)
    else:
        # Put Option
        logger.debug("     Put Option")

        # Using the put-call transformation: P(X, FS, T, r, b, V) = C(FS, X, T, -b, r-b, V)
        # WARNING - When reconciling this code back to the B&S paper, the order of variables is different

        put__x = fs
        put_fs = x
        put_b = -b
        put_r = r - b

        # pass updated values into the Call Valuation formula
        return _bjerksund_stensland_2002(put_fs, put__x, t, put_r, put_b, v)


# -----------
# American Call Option (Bjerksund Stensland 2002 approximation)
def _bjerksund_stensland_2002(fs, x, t, r, b, v):
    # -----------
    # initialize output
    # using GBS greeks (TO DO: update greek calculations)
    my_output = _gbs("c", fs, x, t, r, b, v)

    e_value = my_output[0]
    delta = my_output[1]
    gamma = my_output[2]
    theta = my_output[3]
    vega = my_output[4]
    rho = my_output[5]

    # debugging for calculations
    logger.debug("-----")
    logger.debug("Debug Information: _Bjerksund_Stensland_2002())")

    # If b >= r, it is never optimal to exercise before maturity
    # so we can return the GBS value
    if b >= r:
        logger.debug("     Returning GBS value")
        return e_value, delta, gamma, theta, vega, rho

    # -----------
    # Create preliminary calculations
    v2 = v ** 2
    t1 = 0.5 * (math.sqrt(5) - 1) * t
    t2 = t

    beta_inside = ((b / v2 - 0.5) ** 2) + 2 * r / v2
    # forcing the inside of the sqrt to be a positive number
    beta_inside = abs(beta_inside)
    beta = (0.5 - b / v2) + math.sqrt(beta_inside)
    b_infinity = (beta / (beta - 1)) * x
    b_zero = max(x, (r / (r - b)) * x)

    h1 = -(b * t1 + 2 * v * math.sqrt(t1)) * ((x ** 2) / ((b_infinity - b_zero) * b_zero))
    h2 = -(b * t2 + 2 * v * math.sqrt(t2)) * ((x ** 2) / ((b_infinity - b_zero) * b_zero))

    i1 = b_zero + (b_infinity - b_zero) * (1 - math.exp(h1))
    i2 = b_zero + (b_infinity - b_zero) * (1 - math.exp(h2))

    alpha1 = (i1 - x) * (i1 ** (-beta))
    alpha2 = (i2 - x) * (i2 ** (-beta))

    # debugging for calculations
    logger.debug("     t1 = {0}".format(t1))
    logger.debug("     beta = {0}".format(beta))
    logger.debug("     b_infinity = {0}".format(b_infinity))
    logger.debug("     b_zero = {0}".format(b_zero))
    logger.debug("     h1 = {0}".format(h1))
    logger.debug("     h2 = {0}".format(h2))
    logger.debug("     i1 = {0}".format(i1))
    logger.debug("     i2 = {0}".format(i2))
    logger.debug("     alpha1 = {0}".format(alpha1))
    logger.debug("     alpha2 = {0}".format(alpha2))

    # check for immediate exercise
    if fs >= i2:
        value = fs - x
    else:
        # Perform the main calculation
        value = (alpha2 * (fs ** beta)
                 - alpha2 * _phi(fs, t1, beta, i2, i2, r, b, v)
                 + _phi(fs, t1, 1, i2, i2, r, b, v)
                 - _phi(fs, t1, 1, i1, i2, r, b, v)
                 - x * _phi(fs, t1, 0, i2, i2, r, b, v)
                 + x * _phi(fs, t1, 0, i1, i2, r, b, v)
                 + alpha1 * _phi(fs, t1, beta, i1, i2, r, b, v)
                 - alpha1 * _psi(fs, t2, beta, i1, i2, i1, t1, r, b, v)
                 + _psi(fs, t2, 1, i1, i2, i1, t1, r, b, v)
                 - _psi(fs, t2, 1, x, i2, i1, t1, r, b, v)
                 - x * _psi(fs, t2, 0, i1, i2, i1, t1, r, b, v)
                 + x * _psi(fs, t2, 0, x, i2, i1, t1, r, b, v))

    # in boundary conditions, this approximation can break down
    # Make sure option value is greater than or equal to European value
    value = max(value, e_value)

    # -----------
    # Return Data
    return value, delta, gamma, theta, vega, rho


    # ---------------------------
# American Option Intermediate Calculations

# -----------
# The Psi() function used by _Bjerksund_Stensland_2002 model
def _psi(fs, t2, gamma, h, i2, i1, t1, r, b, v):
    vsqrt_t1 = v * math.sqrt(t1)
    vsqrt_t2 = v * math.sqrt(t2)

    bgamma_t1 = (b + (gamma - 0.5) * (v ** 2)) * t1
    bgamma_t2 = (b + (gamma - 0.5) * (v ** 2)) * t2

    d1 = (math.log(fs / i1) + bgamma_t1) / vsqrt_t1
    d3 = (math.log(fs / i1) - bgamma_t1) / vsqrt_t1

    d2 = (math.log((i2 ** 2) / (fs * i1)) + bgamma_t1) / vsqrt_t1
    d4 = (math.log((i2 ** 2) / (fs * i1)) - bgamma_t1) / vsqrt_t1

    e1 = (math.log(fs / h) + bgamma_t2) / vsqrt_t2
    e2 = (math.log((i2 ** 2) / (fs * h)) + bgamma_t2) / vsqrt_t2
    e3 = (math.log((i1 ** 2) / (fs * h)) + bgamma_t2) / vsqrt_t2
    e4 = (math.log((fs * (i1 ** 2)) / (h * (i2 ** 2))) + bgamma_t2) / vsqrt_t2

    tau = math.sqrt(t1 / t2)
    lambda1 = (-r + gamma * b + 0.5 * gamma * (gamma - 1) * (v ** 2))
    kappa = (2 * b) / (v ** 2) + (2 * gamma - 1)

    psi = math.exp(lambda1 * t2) * (fs ** gamma) * (_cbnd(-d1, -e1, tau)
                                                    - ((i2 / fs) ** kappa) * _cbnd(-d2, -e2, tau)
                                                    - ((i1 / fs) ** kappa) * _cbnd(-d3, -e3, -tau)
                                                    + ((i1 / i2) ** kappa) * _cbnd(-d4, -e4, -tau))
    return psi

# -----------
# The Phi() function used by _Bjerksund_Stensland_2002 model and the _Bjerksund_Stensland_1993 model
def _phi(fs, t, gamma, h, i, r, b, v):
    d1 = -(math.log(fs / h) + (b + (gamma - 0.5) * (v ** 2)) * t) / (v * math.sqrt(t))
    d2 = d1 - 2 * math.log(i / fs) / (v * math.sqrt(t))

    lambda1 = (-r + gamma * b + 0.5 * gamma * (gamma - 1) * (v ** 2))
    kappa = (2 * b) / (v ** 2) + (2 * gamma - 1)

    phi = math.exp(lambda1 * t) * (fs ** gamma) * (norm.cdf(d1) - ((i / fs) ** kappa) * norm.cdf(d2))

    logger.debug("-----")
    logger.debug("Debug info for: _phi()")
    logger.debug("    d1={0}".format(d1))
    logger.debug("    d2={0}".format(d2))
    logger.debug("    lambda={0}".format(lambda1))
    logger.debug("    kappa={0}".format(kappa))
    logger.debug("    phi={0}".format(phi))
    return phi

# -----------
# Cumulative Bivariate Normal Distribution
# Primarily called by Psi() function, part of the _Bjerksund_Stensland_2002 model
def _cbnd(a, b, rho):
    # This distribution uses the Genz multi-variate normal distribution
    # code found as part of the standard SciPy distribution
    lower = np.array([0, 0])
    upper = np.array([a, b])
    infin = np.array([0, 0])
    correl = rho
    error, value, inform = mvn.mvndst(lower, upper, infin, correl)
    return value




# ----------
# Inputs (not all functions use all inputs)
#      fs = forward/spot price
#      x = Strike
#      t = Time (in years)
#      r = risk free rate
#      b = cost of carry
#      cp = Call or Put price
#      precision = (optional) precision at stopping point
#      max_steps = (optional) maximum number of steps

# ----------
# Approximate Implied Volatility
#
# This function is used to choose a starting point for the
# search functions (Newton and bisection searches).
# Brenner & Subrahmanyam (1988), Feinstein (1988)
def _approx_implied_vol(option_type, fs, x, t, r, b, cp):
    _test_option_type(option_type)

    ebrt = math.exp((b - r) * t)
    ert = math.exp(-r * t)

    a = math.sqrt(2 * math.pi) / (fs * ebrt + x * ert)

    if option_type == "c":
        payoff = fs * ebrt - x * ert
    else:
        payoff = x * ert - fs * ebrt

    b = cp - payoff / 2
    c = (payoff ** 2) / math.pi

    v = (a * (b + math.sqrt(b ** 2 + c))) / math.sqrt(t)

    return v

# ### Public Interface for implied Volatility Functions

def euro_implied_vol(option_type, fs, x, t, r, q, cp):
    """Implied volatility calculator for European options.

    Args:
        option_type (str): Type of the option. "p" for put and "c" for call options.
        fs (float): Price of underlying asset.
        x (float): Strike price.
        t (float): Time to expiration in years. 1 for one year, 0.5 for 6 months.
        r (float): Risk free rate.
        q (float): Dividend payment. Set q=0 for non-dividend paying options.
        cp (float): The price of the call or put observed in the market.

    Returns:
        value (float): Implied volatility.
    """
    b = r - q
    return _gbs_implied_vol(option_type, fs, x, t, r, b, cp)

# ----------
# Find the Implied Volatility of an European (GBS) Option given a price
# using Newton-Raphson method for greater speed since Vega is available
def _gbs_implied_vol(option_type, fs, x, t, r, b, cp, precision=.00001, max_steps=100):
    return _newton_implied_vol(_gbs, option_type, x, fs, t, b, r, cp, precision, max_steps)


# ----------
# Calculate Implied Volatility with a Newton Raphson search
def _newton_implied_vol(val_fn, option_type, x, fs, t, b, r, cp, precision=.00001, max_steps=100):
    # make sure a valid option type was entered
    _test_option_type(option_type)

    # Estimate starting Vol, making sure it is allowable range
    v = _approx_implied_vol(option_type, fs, x, t, r, b, cp)
    v = max(_GBS_Limits.MIN_V, v)
    v = min(_GBS_Limits.MAX_V, v)

    # Calculate the value at the estimated vol
    value, delta, gamma, theta, vega, rho = val_fn(option_type, fs, x, t, r, b, v)
    min_diff = abs(cp - value)

    logger.debug("-----")
    logger.debug("Debug info for: _Newton_ImpliedVol()")
    logger.debug("    Vinitial={0}".format(v))

    # Newton-Raphson Search
    countr = 0
    while precision <= abs(cp - value) <= min_diff and countr < max_steps:

        v = v - (value - cp) / vega
        if (v > _GBS_Limits.MAX_V) or (v < _GBS_Limits.MIN_V):
            logger.debug("    Volatility out of bounds")
            break

        value, delta, gamma, theta, vega, rho = val_fn(option_type, fs, x, t, r, b, v)
        min_diff = min(abs(cp - value), min_diff)

        # keep track of how many loops
        countr += 1
        logger.debug("     IVOL STEP {0}. v={1}".format(countr, v))


    # check if function converged and return a value
    if abs(cp - value) < precision:
        # the search function converged
        return v
    else:
        # if the search function didn't converge, try a bisection search
        return _bisection_implied_vol(val_fn, option_type, fs, x, t, r, b, cp, precision, max_steps)




def amer_implied_vol(option_type, fs, x, t, r, q, cp):
    """Implied volatility calculator for American options.

    Args:
        option_type (str): Type of the option. "p" for put and "c" for call options.
        fs (float): Price of underlying asset.
        x (float): Strike price.
        t (float): Time to expiration in years. 1 for one year, 0.5 for 6 months.
        r (float): Risk free rate.
        q (float): Dividend payment. Set q=0 for non-dividend paying options.
        cp (float): The price of the call or put observed in the market.

    Returns:
        value (float): Implied volatility.
    """
    b = r - q
    return _american_implied_vol(option_type, fs, x, t, r, b, cp)

# ----------
# Find the Implied Volatility of an American Option given a price
# Using bisection method since Vega is difficult to estimate for Americans
def _american_implied_vol(option_type, fs, x, t, r, b, cp, precision=.00001, max_steps=100):
    return _bisection_implied_vol(_american_option, option_type, fs, x, t, r, b, cp, precision, max_steps)


# ----------
# Find the Implied Volatility using a Bisection search
def _bisection_implied_vol(val_fn, option_type, fs, x, t, r, b, cp, precision=.00001, max_steps=100):
    logger.debug("-----")
    logger.debug("Debug info for: _bisection_implied_vol()")

    # Estimate Upper and Lower bounds on volatility
    # Assume American Implied vol is within +/- 50% of the GBS Implied Vol
    v_mid = _approx_implied_vol(option_type, fs, x, t, r, b, cp)

    if (v_mid <= _GBS_Limits.MIN_V) or (v_mid >= _GBS_Limits.MAX_V):
        # if the volatility estimate is out of bounds, search entire allowed vol space
        v_low = _GBS_Limits.MIN_V
        v_high = _GBS_Limits.MAX_V
        v_mid = (v_low + v_high) / 2
    else:
        # reduce the size of the vol space
        v_low = max(_GBS_Limits.MIN_V, v_mid * .5)
        v_high = min(_GBS_Limits.MAX_V, v_mid * 1.5)

    # Estimate the high/low bounds on price
    cp_mid = val_fn(option_type, fs, x, t, r, b, v_mid)[0]

    # initialize bisection loop
    current_step = 0
    diff = abs(cp - cp_mid)

    logger.debug("     American IVOL starting conditions: CP={0} cp_mid={1}".format(cp, cp_mid))
    logger.debug("     IVOL {0}. V[{1},{2},{3}]".format(current_step, v_low, v_mid, v_high))

    # Keep bisection volatility until correct price is found
    while (diff > precision) and (current_step < max_steps):
        current_step += 1

        # Cut the search area in half
        if cp_mid < cp:
            v_low = v_mid
        else:
            v_high = v_mid

        cp_low = val_fn(option_type, fs, x, t, r, b, v_low)[0]
        cp_high = val_fn(option_type, fs, x, t, r, b, v_high)[0]

        v_mid = v_low + (cp - cp_low) * (v_high - v_low) / (cp_high - cp_low)
        v_mid = max(_GBS_Limits.MIN_V, v_mid)  # enforce high/low bounds
        v_mid = min(_GBS_Limits.MAX_V, v_mid)  # enforce high/low bounds

        cp_mid = val_fn(option_type, fs, x, t, r, b, v_mid)[0]
        diff = abs(cp - cp_mid)

        logger.debug("     IVOL {0}. V[{1},{2},{3}]".format(current_step, v_low, v_mid, v_high))

    # return output
    if abs(cp - cp_mid) < precision:
        return v_mid
    else:
        raise GBS_CalculationError(
            "Implied Vol did not converge. Best Guess={0}, Price diff={1}, Required Precision={2}".format(v_mid, diff,
                                                                                                          precision))


def assert_close(a, b, prec=.000001):
    """This function tests that two floating point numbers are the same.

    Numbers less than 1 million are considered the same if they are within .000001 of each other
    Numbers larger than 1 million are considered the same if they are within .0001% of each other
    User can override the default precision if necessary
    """

    if (a < 1000000.0) and (b < 1000000.0):
        d = abs(a - b)
        d_type = "Difference"
    else:
        d = abs((a - b) / a)
        d_type = "Percent Difference"

    logging.debug("Comparing {0} and {1}. Difference is {2}, Difference Type is {3}".format(a, b, d, d_type))

    result = True if d < prec else False
    if (__name__ == "__main__") and (result is False):
        raise AssertionError("FAILED TEST. Comparing {0} and {1}. Difference is {2}, Difference Type is {3}".format(a, b, d, d_type))

    return result


# This class contains the limits on inputs for GBS models
# It is not intended to be part of this module's public interface
class _GBS_Limits:
    # An GBS model will return an error if an out-of-bound input is input
    MAX32 = 2147483248.0

    MIN_T = 1.0 / 1000.0  # requires some time left before expiration
    MIN_X = 0.01
    MIN_FS = 0.01

    # Volatility smaller than 0.5% causes American Options calculations
    # to fail (Number to large errors).
    # GBS() should be OK with any positive number. Since vols less
    # than 0.5% are expected to be extremely rare, and most likely bad inputs,
    # _gbs() is assigned this limit too
    MIN_V = 0.005

    MAX_T = 100
    MAX_X = MAX32
    MAX_FS = MAX32

    # Asian Option limits
    # maximum TA is time to expiration for the option
    MIN_TA = 0

    # This model will work with higher values for b, r, and V. However, such values are extremely uncommon.
    # To catch some common errors, interest rates and volatility is capped to 200%
    # This reason for 2 (200%) is mostly to cause the library to throw an exceptions
    # if a value like 15% is entered as 15 rather than 0.15)
    MIN_b = -1
    MIN_r = -1

    MAX_b = 1
    MAX_r = 2
    MAX_V = 2


# This class defines the Exception that gets thrown when invalid input is placed into the GBS function
class GBS_InputError(Exception):
    def __init__(self, mismatch):
        Exception.__init__(self, mismatch)


# This class defines the Exception that gets thrown when there is a calculation error
class GBS_CalculationError(Exception):
    def __init__(self, mismatch):
        Exception.__init__(self, mismatch)

# ------------------------------
# This function makes sure inputs are OK
# It throws an exception if there is a failure
def _gbs_test_inputs(option_type, fs, x, t, r, b, v):
    # -----------
    # Test inputs are reasonable
    _test_option_type(option_type)

    if (x < _GBS_Limits.MIN_X) or (x > _GBS_Limits.MAX_X):
        raise GBS_InputError(
            "Invalid Input Strike Price (X). Acceptable range for inputs is {1} to {2}".format(x, _GBS_Limits.MIN_X,
                                                                                               _GBS_Limits.MAX_X))

    if (fs < _GBS_Limits.MIN_FS) or (fs > _GBS_Limits.MAX_FS):
        raise GBS_InputError(
            "Invalid Input Forward/Spot Price (FS). Acceptable range for inputs is {1} to {2}".format(fs,
                                                                                                      _GBS_Limits.MIN_FS,
                                                                                                      _GBS_Limits.MAX_FS))

    if (t < _GBS_Limits.MIN_T) or (t > _GBS_Limits.MAX_T):
        raise GBS_InputError(
            "Invalid Input Time (T = {0}). Acceptable range for inputs is {1} to {2}".format(t, _GBS_Limits.MIN_T,
                                                                                             _GBS_Limits.MAX_T))

    if (b < _GBS_Limits.MIN_b) or (b > _GBS_Limits.MAX_b):
        raise GBS_InputError(
            "Invalid Input Cost of Carry (b = {0}). Acceptable range for inputs is {1} to {2}".format(b,
                                                                                                      _GBS_Limits.MIN_b,
                                                                                                      _GBS_Limits.MAX_b))

    if (r < _GBS_Limits.MIN_r) or (r > _GBS_Limits.MAX_r):
        raise GBS_InputError(
            "Invalid Input Risk Free Rate (r = {0}). Acceptable range for inputs is {1} to {2}".format(r,
                                                                                                       _GBS_Limits.MIN_r,
                                                                                                       _GBS_Limits.MAX_r))

    if (v < _GBS_Limits.MIN_V) or (v > _GBS_Limits.MAX_V):
        raise GBS_InputError(
            "Invalid Input Implied Volatility (V = {0}). Acceptable range for inputs is {1} to {2}".format(v,
                                                                                                           _GBS_Limits.MIN_V,
                                                                                                           _GBS_Limits.MAX_V))                                      
# ------------------------------
# This function verifies that the Call/Put indicator is correctly entered
def _test_option_type(option_type):
    if (option_type != "c") and (option_type != "p"):
        raise GBS_InputError("Invalid Input option_type ({0}). Acceptable value are: c, p".format(option_type))
