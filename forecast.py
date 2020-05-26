#!/usr/bin/env python3
import argparse
from cmath import sqrt

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.ar_model import AutoReg
from statsmodels.tsa.arima_model import ARIMA as arima_mod, ARMA as arma_mod
from statsmodels.tsa.holtwinters import ExponentialSmoothing as exp_mod
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning, HessianInversionWarning
warnings.simplefilter('ignore', ConvergenceWarning)
warnings.simplefilter('ignore', HessianInversionWarning)


def AR(cdf):
    country = cdf['Country'][0]
    data = cdf['AverageTemperatureCelsius'].to_list()
    model = AutoReg(data, lags=10)
    model_fit = model.fit()

    predictions = model_fit.predict(len(data), len(data) + 259)
    year_after_last = cdf['year'].max() + 1
    for i, prediction in enumerate(predictions):
        cdf = cdf.append({'Country': country, 'year': year_after_last + i, 'AverageTemperatureCelsius': prediction}, ignore_index=True)

    return cdf


def ExponentialSmoothing(cdf):
    country = cdf['Country'][0]
    data = cdf['AverageTemperatureCelsius'].to_list()
    model = exp_mod(data)
    model_fit = model.fit(optimized=True)

    predictions = model_fit.predict(len(data), len(data) + 259)
    year_after_last = cdf['year'].max() + 1
    for i, prediction in enumerate(predictions):
        cdf = cdf.append({'Country': country, 'year': year_after_last + i, 'AverageTemperatureCelsius': prediction}, ignore_index=True)

    return cdf


def ARIMA(cdf):
    country = cdf['Country'][0]
    data = cdf['AverageTemperatureCelsius'].to_list()
    model = arima_mod(data, order=(5, 1, 0))
    model_fit = model.fit(disp=False)
    output = model_fit.forecast(260)
    yhat = output[0]

    predictions = yhat
    year_after_last = cdf['year'].max() + 1
    for i, prediction in enumerate(predictions):
        cdf = cdf.append({'Country': country, 'year': year_after_last + i, 'AverageTemperatureCelsius': prediction}, ignore_index=True)

    return cdf


def fit(cdf, select_model):
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.metrics import mean_squared_error

    X = cdf['AverageTemperatureCelsius'].values

    tscv = TimeSeriesSplit(n_splits=5)
    rmse = []
    for train_index, test_index in tscv.split(X):
        train, test = X[train_index], X[test_index]
        history = [x for x in train]
        predictions = list()
        for t in range(len(test)):
            if select_model == 'ARIMA':
                model = arima_mod(history, order=(5, 1, 0))
                model_fit = model.fit(disp=0)
                output = model_fit.forecast()
                yhat = output[0]
            elif select_model == 'AR':
                model = AutoReg(history, lags=10)
                model_fit = model.fit()
                yhat = model_fit.predict(len(history), len(history))
            elif select_model == 'ES':
                model = exp_mod(history)
                model_fit = model.fit(optimized=True)
                output = model_fit.forecast()
                yhat = output[0]
            else:
                return

            predictions.append(yhat)
            obs = test[t]
            history.append(obs)
            # print('predicted=%f, expected=%f' % (yhat, obs))
        error = mean_squared_error(test, predictions)
        # print('Test MSE: %.3f' % error)
        rmse.append(error)

    print("RMSE: %.3f" % np.mean(rmse))


def plots(cdf, country, mode):
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.scatter(cdf['year'], cdf['AverageTemperatureCelsius'])
    pred = f' prediction, model = {mode}' if mode != 'avg' else ''
    ax.set_title(f'Average temperatures in {country}{pred}')
    ax.grid(b=True, which='major', linestyle='-')
    ax.grid(b=True, which='minor', linestyle='-', alpha=0.2)
    ax.set_xlim(x_range)
    ax.set_ylim(y_range)
    ax.set_ylabel('Average temperature in Celsius')
    ax.set_xlabel('Year')
    if out:
        plt.savefig(f'forecast/{mode.lower()}/{country}.png')
        print(f'[+] Saved: forecast/{mode.lower()}/{country}.png')
    else:
        plt.show()


def reg(reg_func = None):
    gdf = pd.read_csv('data/temperature_clean.csv').groupby(['Country', 'year'])[
        'AverageTemperatureCelsius'].mean().reset_index()
    countries = gdf['Country'].unique()

    if not reg_func:
        pass
    else:
        gdf = gdf.groupby('Country').apply(reg_func)
        gdf.reset_index(drop=True, inplace=True)

    global y_range, x_range
    y_range = (gdf['AverageTemperatureCelsius'].min() - 5, gdf['AverageTemperatureCelsius'].max() + 5)
    x_range = (gdf['year'].min() - 5, gdf['year'].max() + 5)

    for country in countries:
        cdf = gdf.groupby('Country').get_group(country)
        plots(cdf, country, reg_func.__name__ if reg_func else 'avg')
    plt.close('all')


def mod_fit():
    gdf = pd.read_csv('data/temperature_clean.csv').groupby(['Country', 'year'])[
        'AverageTemperatureCelsius'].mean().reset_index()
    countries = gdf['Country'].unique()

    for method in ['AR', 'ARIMA', 'ES']:
        for country in countries:
            cdf = gdf.groupby('Country').get_group(country)
            print(f'[{method}] {country}', end=': ')
            fit(cdf, method)


x_range = None
y_range = None
out = None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', action='store_true', help='store')
    parsed_args = parser.parse_args()
    out = parsed_args.output if parsed_args.output else None

    reg()
    reg(AR)
    reg(ExponentialSmoothing)
    reg(ARIMA)
    mod_fit()

