# https://www.nordpoolgroup.com/historical-market-data/

import numpy as np
import pandas as pd


def get_elspot_prices(start_time, end_time, regions = [], currency = 'EUR'):

    ## Example
    # from nordpool import get_elspot_prices
    
    # start_time = '2020-10-01 00:00'
    # end_time = '2020-12-15 23:00'  
    # regions = ['SE1']
    # currency = 'EUR' # 'EUR','SEK','NOK','DKK'
    # df = get_elspot_prices(start_time, end_time, regions = regions, currency = currency)  


    data_url = 'https://www.nordpoolgroup.com/globalassets/marketdata-excel-files/elspot-prices_%s_hourly_%s.xls'

    t1 = pd.to_datetime(start_time).tz_localize('UTC')
    t2 = pd.to_datetime(end_time).tz_localize('UTC') 

    t1_year = t1.tz_convert('CET').year
    t2_year = t2.tz_convert('CET').year

    years = np.arange(t1_year, t2_year+1)

    urls = [data_url % (year, currency.lower()) for year in years]

    # Download data
    df_update = []
    for url in urls:
        df_update_yr = pd.read_html(url, skiprows=2, header=0, index_col=[0, 1], decimal=',', thousands=' ')[0]
        time_vector = pd.to_datetime(df_update_yr.reset_index().apply(lambda r: '%s %s:00' % (r[0], r[1][:2]), axis=1), format="%d-%m-%Y %H:%M")
        df_update_yr.set_index(time_vector, inplace=True)
        df_update.append(df_update_yr)
    df_update = pd.concat(df_update, sort=True)

    df_update.dropna(inplace=True, how='all')
    df_update.index = df_update.index.tz_localize("CET", ambiguous='infer').tz_convert("UTC")
    df_update = df_update.sort_index()
    df_update.index.name = 'Timestamp'

    # Slice for periods and regions
    indx = (df_update.index >= t1) & (df_update.index <= t2)

    if len(regions) == 0:
        df = df_update.loc[indx]
    else:
        df = df_update.loc[indx,regions]
    
    return df



def get_elspot_volumes(start_time, end_time, regions = []):

    
    data_url = 'https://www.nordpoolgroup.com/globalassets/marketdata-excel-files/elspot-volumes_%s_hourly.xls'

    t1 = pd.to_datetime(start_time).tz_localize('UTC')
    t2 = pd.to_datetime(end_time).tz_localize('UTC') 

    t1_year = t1.tz_convert('CET').year
    t2_year = t2.tz_convert('CET').year

    years = np.arange(t1_year, t2_year+1)

    urls = [data_url % (year) for year in years]

    # Download data
    df_update = []
    for url in urls:
        df_update_yr = pd.read_html(url, skiprows=2, header=0, index_col=[0, 1], decimal=',', thousands=' ')[0]
        time_vector = pd.to_datetime(df_update_yr.reset_index().apply(lambda r: '%s %s:00' % (r[0], r[1][:2]), axis=1), format="%d-%m-%Y %H:%M")
        df_update_yr.set_index(time_vector, inplace=True)
        df_update.append(df_update_yr)
    df_update = pd.concat(df_update, sort=True)

    df_update.dropna(inplace=True, how='all')
    df_update.index = df_update.index.tz_localize("CET", ambiguous='infer').tz_convert("UTC")
    df_update = df_update.sort_index()
    df_update.index.name = 'Timestamp'

    
    # Set multilevel columns
    lst = list(df_update)
    la = list(filter(lambda k: 'Turnover' not in k, lst))
    lb = list(filter(lambda k: 'Turnover' in k, lst))
    
    cnames = [x.split() for x in la]
    cnames.append(lb)
    
    df_update.columns = pd.MultiIndex.from_tuples(cnames)

    # Slice for periods and regions
    indx = (df_update.index >= t1) & (df_update.index <= t2)

    if len(regions) == 0:
        df = df_update.loc[indx]
    else:
        df = df_update.loc[indx,regions]
    
    return df



def get_regulating_prices(start_time, end_time, regions = [], currency = 'EUR'):

    
    data_url = 'https://www.nordpoolgroup.com/globalassets/marketdata-excel-files/regulating-prices_%s_hourly_%s.xls'

    t1 = pd.to_datetime(start_time).tz_localize('UTC')
    t2 = pd.to_datetime(end_time).tz_localize('UTC') 

    t1_year = t1.tz_convert('CET').year
    t2_year = t2.tz_convert('CET').year

    years = np.arange(t1_year, t2_year+1)

    urls = [data_url % (year, currency.lower()) for year in years]

    # Download data
    df_update = []
    for url in urls:
        df_update_yr = pd.read_html(url, skiprows=2, header=[0, 1], index_col=[0, 1], decimal=',', thousands=' ')[0]
        time_vector = pd.to_datetime(df_update_yr.reset_index().apply(lambda r: '%s %s:00' % (r[0], r[1][:2]), axis=1), format="%d-%m-%Y %H:%M")
        df_update_yr.set_index(time_vector, inplace=True)
        df_update.append(df_update_yr)
    df_update = pd.concat(df_update, sort=True)

    df_update.dropna(inplace=True, how='all')
    df_update.index = df_update.index.tz_localize("CET", ambiguous='infer').tz_convert("UTC")
    df_update = df_update.sort_index()
    df_update.index.name = 'Timestamp'

    # Slice for periods and regions
    indx = (df_update.index >= t1) & (df_update.index <= t2)

    if len(regions) == 0:
        df = df_update.loc[indx]
    else:
        df = df_update.loc[indx,regions]
    
    return df



def get_regulating_volumes(start_time, end_time, regions = []):


    data_url = 'https://www.nordpoolgroup.com/globalassets/marketdata-excel-files/regulating-volumes_%s_hourly.xls'

    t1 = pd.to_datetime(start_time).tz_localize('UTC')
    t2 = pd.to_datetime(end_time).tz_localize('UTC') 

    t1_year = t1.tz_convert('CET').year
    t2_year = t2.tz_convert('CET').year

    years = np.arange(t1_year, t2_year+1)

    urls = [data_url % (year) for year in years]

    # Download data
    df_update = []
    for url in urls:
        df_update_yr = pd.read_html(url, skiprows=2, header=[0, 1], index_col=[0, 1], decimal=',', thousands=' ')[0]
        time_vector = pd.to_datetime(df_update_yr.reset_index().apply(lambda r: '%s %s:00' % (r[0], r[1][:2]), axis=1), format="%d-%m-%Y %H:%M")
        df_update_yr.set_index(time_vector, inplace=True)
        df_update.append(df_update_yr)
    df_update = pd.concat(df_update, sort=True)

    df_update.dropna(inplace=True, how='all')
    df_update.index = df_update.index.tz_localize("CET", ambiguous='infer').tz_convert("UTC")
    df_update = df_update.sort_index()
    df_update.index.name = 'Timestamp'

    # Slice for periods and regions
    indx = (df_update.index >= t1) & (df_update.index <= t2)

    if len(regions) == 0:
        df = df_update.loc[indx]
    else:
        df = df_update.loc[indx,regions]
    
    return df

