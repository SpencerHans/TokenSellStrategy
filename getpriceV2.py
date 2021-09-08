#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 20:14:47 2021

@author: hans
"""
from requests import Request, Session
import json
import pprint
import pandas as pd
from cryptocmd import CmcScraper
import datetime

FILE_NAME = "portfolio.csv"
df = pd.read_csv("/Users/hans/Documents/pycode/token_price/portfolio.csv")

### last price
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

headers = {
    'Accepts' : 'application/json' ,
    'X-CMC_PRO_API_KEY' : '404f95dd-659a-40f4-8f74-158bee2c0f41'
}

session = Session()
session.headers.update(headers)

for i in range(df.shape[0]):
    symbol = df.at[i, 'Symbol']

    parameters = {
        'symbol': symbol,
    }

    response = session.get(url, params=parameters).json()
    if "data" in response:
        price = response['data'][symbol]['quote']['USD']['price']
        print("Token " + symbol + " price is " + price.__str__())
        df.loc[i, 'Price'] = price
    else:
        print("Token " + symbol + " not found")
    


symbols = df['Symbol'].tolist()
list2 = []

for sb in symbols:
    
    e_date = datetime.datetime.today() - datetime.timedelta(1)
    b_date = e_date - datetime.timedelta(5)
    
    e_date_str = datetime.datetime.strftime(e_date, '%d-%m-%Y')
    b_date_str = datetime.datetime.strftime(b_date, '%d-%m-%Y')
    
    
    # initialise scraper with time interval
    scraper = CmcScraper(sb, b_date_str, e_date_str)
    
    # get raw data as list of list
    headers, data = scraper.get_data()
    
    try:
        # get data in a json format
        json_data = scraper.get_data("json")
    except:
        print(sb + 'No historical data')

        
    
    # get dataframe for the data
    df2_temp = scraper.get_dataframe()
    temp_mean = df2_temp.Close.mean()
    temp_last = df2_temp.Close.tolist()[0]
    temp_max = df2_temp.High.max()
    list2.append([sb, temp_mean, temp_max,temp_last])
    
df_2 = pd.DataFrame(list2, columns = ['Symbol','Five_day_mean','Five_day_max','Yesterday'])
df = df.set_index('Symbol')
df_2 = df_2.set_index('Symbol')
df_data = pd.concat([df_2,df],axis = 1)

# sell 1: 当前价格小于5日最高价8%
sell1 = df_data.Price < df_data.Five_day_max*0.8
# sell 2: 突破5日均线
sell2 = (df_data.Price > df_data.Five_day_mean * 1.1) & (df_data.Yesterday <= df_data.Five_day_mean)
# sell 3: 当前价格高于昨日收盘50%
sell3 = df_data.Price > df_data.Yesterday * 1.5


signal = pd.concat([sell1 * 1 ,sell2 * 0.5,sell3 * 0.5], axis = 1).max(1)
out_put = pd.concat([df_data.Price, signal], axis = 1)
out_put.columns = ['Price', 'signal']
print('#####################')
print(out_put)
out_put.to_csv('/Users/hans/Documents/pycode/token_price/daily_output.csv')
print('#####################')
print(e_date_str)