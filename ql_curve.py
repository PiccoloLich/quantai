# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 22:48:34 2019

@author: piccolo
"""
import QuantLib as ql
from pandas import DataFrame
import random as rnd

import matplotlib.pyplot as plt
import csv

def get_rates(yield_curve, day_count, calendar=ql.UnitedStates()):
    """
    get the discount factors and zero rates from a yield curve
    
    yield_curve: the yield curve
    day_count:   the day count convention
    calendar:    the calendar
    months:      number of months
    
    """
    tenors = []
    zero_rates = []
    discount_factors = []
    ref_date = yield_curve.referenceDate()
    for yrs in yield_curve.times():
        d = calendar.advance(ref_date, ql.Period(int(yrs*365.25), ql.Days))
        compounding = ql.Compounded
        freq = ql.Semiannual
        zero_rate = yield_curve.zeroRate(yrs, compounding, freq).rate()
        discount_factor = yield_curve.discount(d, True)
        tenors.append(yrs)
        zero_rates.append(zero_rate)
        discount_factors.append(discount_factor)
    return DataFrame(list(zip(tenors, zero_rates, discount_factors)),
                     columns=["Maturities","ZeroRate", "DiscountFactor"])

def gen_curve_instruments(swap_periods=None, 
                          lower_bound=0.0, 
                          upper_bound=1.0, 
                          is_sorted=True):
    """
    generate curve building instruments randomly
    
    swap_periods:  the swap periods, if None a default schedule will be used
    lower_bound:   the lower bound
    upper_bound:   the upper bound
    is_sorted:     whether the results should be sorted
    """
    if swap_periods is None:
        swap_periods = [ql.Period(1,ql.Days),
                        ql.Period(1,ql.Weeks),
                        ql.Period(2,ql.Weeks),
                        ql.Period(3,ql.Weeks),
                        ql.Period(1,ql.Months),
                        ql.Period(2,ql.Months),
                        ql.Period(3,ql.Months),
                        ql.Period(4,ql.Months),
                        ql.Period(5,ql.Months),
                        ql.Period(6,ql.Months),
                        ql.Period(9,ql.Months),
                        ql.Period(1,ql.Years),
                        ql.Period(18,ql.Months),
                        ql.Period(2,ql.Years),
                        ql.Period(3,ql.Years),
                        ql.Period(4,ql.Years),
                        ql.Period(5,ql.Years),
                        ql.Period(6,ql.Years),
                        ql.Period(7,ql.Years),
                        ql.Period(8,ql.Years),
                        ql.Period(9,ql.Years),
                        ql.Period(10,ql.Years),
                        ql.Period(12,ql.Years),
                        ql.Period(15,ql.Years),
                        ql.Period(20,ql.Years),
                        ql.Period(25,ql.Years),
                        ql.Period(30,ql.Years),
                        ql.Period(40,ql.Years)
                        ]
    n_periods = len(swap_periods)
    rates = [rnd.uniform(lower_bound, upper_bound) for i in range(0, n_periods)]
    if is_sorted:
        rates.sort()
    
    