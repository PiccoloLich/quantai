#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate american option PV and sensitivity as training sample

@author: piccolo
"""

import QuantLib as ql
from timeit import default_timer as timer
from datetime import date, timedelta
import random
import pandas as pd
from multiprocessing import Pool
import os

def datetime_to_ql(py_date):
    """
    convert a python date to quantlib date

    py_date: the python datetime
    """
    datetime_to_ql.month_table = {1: ql.January, 
                                  2: ql.February,
                                  3: ql.March,
                                  4: ql.April,
                                  5: ql.May,
                                  6: ql.June,
                                  7: ql.July,
                                  8: ql.August,
                                  9: ql.September,
                                  10: ql.October,
                                  11: ql.November,
                                  12: ql.December}
    day = py_date.day
    month = py_date.month
    ql_month = datetime_to_ql.month_table[month]
    year = py_date.year
    ql_date = ql.Date(day, ql_month, year)
    return ql_date

def _get_pricing_engine(method, process, time_steps, grid_points):
    """
    get the pricing engine
    method:        the prcing method
    process:       the process
    time_steps:    number of time steps
    grid_points:   number of grid points
    """
    #american PDE engine
    if method == "PDE":
        return ql.FDAmericanEngine(process, time_steps, grid_points)
    #binomial engines:
    return ql.BinomialVanillaEngine(process, method, time_steps)

def american_valuation(
        val_date,
        settle_date, 
        exercise_date,
        stock,
        strike,
        vol,
        put_call,
        risk_free,
        dividend,
        method, 
        time_steps,
        grid_points):
    """
    value an american option

    val_date:        the valuation date
    settle_date:     settlement date
    exercise_date:   option exercise date
    stock:           underlying stock price
    vol:             volatility
    put_call:        option put call
    strike:          the option strike
    risk_free:       risk free rate
    dividend:        dividend rate
    method:          valuation method
    time_steps:      finite difference time steps
    grid_points:     the grid points
    return:          return a dictionary with the inputs and outputs
    """
    #val date settings
    ql_val_date = datetime_to_ql(val_date)
    ql_settle_date = datetime_to_ql(settle_date)
    ql_exercise_date = datetime_to_ql(exercise_date)
    
    ql.Settings.instance().evaluationDate = ql_val_date

    #option parameters
    exercise = ql.AmericanExercise(ql_settle_date, ql_exercise_date)
    payoff = None
    if put_call == "put":
        payoff = ql.PlainVanillaPayoff(ql.Option.Put, strike)
    elif put_call == "Call":
        payoff = ql.PlainVanillaPayoff(ql.Option.Call, strike)
    else:
        raise ValueError("expecting put or call.")

    #market data
    underlying = ql.SimpleQuote(stock)
    volatility = ql.BlackConstantVol(ql_val_date, ql.TARGET(), vol, ql.Actual365Fixed())
    dividend_yield = ql.FlatForward(ql_settle_date, dividend, ql.Actual365Fixed())
    risk_free_rate = ql.FlatForward(ql_settle_date, risk_free, ql.Actual365Fixed())

    process = ql.BlackScholesMertonProcess(
            ql.QuoteHandle(underlying),
            ql.YieldTermStructureHandle(dividend_yield),
            ql.YieldTermStructureHandle(risk_free_rate),
            ql.BlackVolTermStructureHandle(volatility))

    option = ql.VanillaOption(payoff, exercise)

    #get the pricing engine
    #measure the time for setting up the engine and getting the PV
    start = timer()
    pricing_engine = _get_pricing_engine(method, process, time_steps, grid_points)
    option.setPricingEngine(pricing_engine)
    pv = option.NPV()
    delta = option.delta()
    gamma = option.gamma()
    end = timer()
    time_diff = end - start

    #dump input and outputs into a python dict
    res = {"ValDate": str(val_date),
           "SettleDate": str(settle_date),
           "ExerciseDate": str(exercise_date),
           "Stock": stock,
           "Strike": strike,
           "Vol": vol,
           "PutCall": put_call,
           "RiskFreeRate": risk_free,
           "Dividend": dividend,
           "Method": method,
           "TimeSteps": time_steps,
           "GridPoints": grid_points,
           "PV": pv,
           "Delta": delta,
           "Gamma": gamma,
           "Time": time_diff
            }

    return res

def gen_inputs():
    """
    generate one set of inputs to the american pricing
    """
    #generate dates
    d0 = date(1970, 1, 1)
    days = random.randint(1, 20000)
    val_date = d0 + timedelta(days=days)
    days = random.randint(1, 10)
    settle_date = val_date + timedelta(days=days)
    days = random.randint(1, 5000)
    exercise_date = settle_date + timedelta(days=days)
    
    #generate stock, strike, vol
    stock = random.uniform(0, 1000)
    strike = random.uniform(0, 1000)
    vol = random.uniform(0, 2)
    
    put_call = "put"
    risk_free = random.uniform(0, 1.0)
    dividend = random.uniform(0, 1.0)
    method = "PDE"
    time_steps = 800
    grid_points = 800
    return {"ValDate": val_date, 
            "SettleDate": settle_date,
            "ExerciseDate": exercise_date,
            "Stock": stock,
            "Strike": strike,
            "Vol": vol,
            "PutCall": put_call,
            "RiskFreeRate": risk_free,
            "Dividend": dividend,
            "Method": method,
            "TimeSteps": time_steps,
            "GridPoints": grid_points
            }

def gen_one_sample():
    """
    generate one data sample
    """
    inputs = gen_inputs()
    return american_valuation(inputs["ValDate"],
                              inputs["SettleDate"],
                              inputs["ExerciseDate"],
                              inputs["Stock"], 
                              inputs["Strike"], 
                              inputs["Vol"], 
                              inputs["PutCall"],
                              inputs["RiskFreeRate"],
                              inputs["Dividend"],
                              inputs["Method"],
                              inputs["TimeSteps"],
                              inputs["GridPoints"])

def gen_samples(n_files, samples_per_file, file_prefix="data/data_"):
    """
    generate samples in a single process
    """
    for i in range(0, n_files):
        results = []
        for j in range(0, samples_per_file):
            ires = gen_one_sample()
            results.append(ires)
        df = pd.DataFrame(results)
        df = df[["ValDate", "SettleDate", "ExerciseDate", "Stock", "Strike",
                 "Vol", "PutCall", "RiskFreeRate", "Dividend", "Method",
                 "TimeSteps", "GridPoints", 
                 "PV", "Delta", "Gamma", "Time"
                 ]]
        df.to_csv(file_prefix+str(i)+".csv")
        print("done file "+str(i))

def gen_samples_mp(file_id, samples_per_file=1000000, file_prefix="data/data_"):
    """
    generate samples using multiple process
    """
    results = []
    for j in range(0, samples_per_file):
        ires = gen_one_sample()
        results.append(ires)
    df = pd.DataFrame(results)
    df = df[["ValDate", "SettleDate", "ExerciseDate", "Stock", "Strike",
             "Vol", "PutCall", "RiskFreeRate", "Dividend", "Method",
             "TimeSteps", "GridPoints", 
             "PV", "Delta", "Gamma", "Time"
             ]]
    df.to_csv(file_prefix+str(file_id)+".csv")
    print("done file "+str(file_id))

if __name__ == "__main__":
    #gen_samples(100, 100000, file_prefix="data2/data_")
    def gen_func(file_id):
        print("start "+str(file_id))
        gen_samples_mp(file_id, samples_per_file=100000, file_prefix="data2/data2_")
    pool = Pool(os.cpu_count())
    pool.map(gen_func, range(0, 100))
