# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 22:48:34 2019

@author: piccolo
"""
import QuantLib as ql
import pandas as pd
import random as rnd

def get_rate_df(curve_index, swap_rates, yield_curve, calendar=ql.UnitedStates()):
    """
    get the discount factors and zero rates from a yield curve
    
    yield_curve: the yield curve
    calendar:    the calendar
    """
    curve_indexes = []
    tenors = []
    zero_rates = []
    discount_factors = []
    ref_date = yield_curve.referenceDate()
    for yrs in yield_curve.times():
        curve_indexes.append(curve_index)
        d = calendar.advance(ref_date, ql.Period(int(yrs*365.25), ql.Days))
        compounding = ql.Compounded
        freq = ql.Semiannual
        zero_rate = yield_curve.zeroRate(yrs, compounding, freq).rate()
        discount_factor = yield_curve.discount(d, True)
        tenors.append(yrs)
        zero_rates.append(zero_rate)
        discount_factors.append(discount_factor)
    #return a data frame
    return pd.DataFrame(list(zip(curve_indexes,
                              tenors,
                              swap_rates,
                              zero_rates,
                              discount_factors)),
                     columns=["CurveIndex",
                              "Maturities",
                              "SwapRate",
                              "ZeroRate",
                              "DiscountFactor"])

def gen_single_curve(valuation_date=None,
                     swap_periods=None,
                     lower_bound=0.0,
                     upper_bound=0.2,
                     is_sorted=True,
                     interpolation = "CubicZero",
                     calendar=ql.UnitedStates(),
                     bussiness_convention = ql.ModifiedFollowing,
                     day_count = ql.Actual360(),
                     coupon_frequency = ql.Annual
                    ):
    """
    generate curve building instruments randomly
    
    valuation_date:  the valuation date
    swap_periods:    the swap periods, if None a default schedule will be used
    lower_bound:     the lower bound
    upper_bound:     the upper bound
    is_sorted:       whether the results should be sorted
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
    swap_rates = [rnd.uniform(lower_bound, upper_bound) for i in range(0, n_periods)]
    if is_sorted:
        swap_rates.sort()
    
    ql.Settings.instance().evaluationDate = valuation_date
    
    #SwapRateHelper
    swap_helpers = []
    for rate,tenor in list(zip(swap_rates,swap_periods)):
        swap_helpers.append(ql.SwapRateHelper(ql.QuoteHandle(ql.SimpleQuote(rate/100.0)),
            tenor, calendar,
            coupon_frequency, bussiness_convention,
            day_count,
            ql.Euribor3M()))

    rate_helpers = swap_helpers

    #Bulid the curve and return
    if interpolation == "CubicZero":
        curve = ql.PiecewiseCubicZero(valuation_date,rate_helpers,day_count)
    if interpolation == "LinearZero":
        curve = ql.PiecewiseLinearZero(valuation_date,rate_helpers,day_count)
    return swap_periods, swap_rates, curve

def gen_curve_sample(n_samples, output, val_date=ql.Date(4,4,2019)):
    """
    save the generated rates into a dataframe
    """
    df=pd.DataFrame()
    for i in range(n_samples):
        swap_periods, swap_rates, curve = gen_single_curve(valuation_date=val_date)
        idf = get_rate_df(i, swap_rates, curve)
        df = df.append(idf)

    df.to_csv(output)

def test1():
    gen_curve_sample(100, "test1.csv")
    
if __name__ == "__main__":
    test1()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    